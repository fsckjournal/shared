#!/usr/bin/env python3
"""Read-only inventory of metadata, playlist, and DJ-software exports.

The scanner does not call provider APIs, open audio files, follow symlinks, or
modify anything below the search roots. It records file metadata and small
structural clues (headers, JSON keys, XML roots, archive members, and optional
read-only SQLite table names) so a later pass can build a source-aware dataset.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import stat
import sys
import tarfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote
from xml.etree import ElementTree


DATA_EXTENSIONS = {
    ".csv", ".tsv", ".txt", ".text", ".json", ".jsonl", ".ndjson",
    ".xml", ".m3u", ".m3u8", ".pls", ".xlsx", ".xls", ".ods",
    ".parquet", ".zip", ".tar", ".tgz", ".gz", ".bz2", ".sqlite",
    ".sqlite3", ".db", ".db3", ".mikdb", ".db-wal", ".db-shm",
    ".cue", ".log", ".yaml", ".yml",
}

MEDIA_EXTENSIONS = {
    ".flac", ".mp3", ".m4a", ".aac", ".wav", ".aiff", ".aif", ".ogg",
    ".opus", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".dylib",
    ".so", ".bin", ".app", ".exe", ".plist", ".pyc",
}

PRUNE_DIR_NAMES = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__",
    ".cache", "cache", "caches", "temporaryitems", ".trash", "deriveddata",
    "build", "dist", "target", "pods",
}

SOURCE_RULES = {
    "soundiiz": ("soundiiz", "trackscsv", "playlist missing"),
    "tunemymusic": ("tunemymusic", "tune my music"),
    "songshift": ("songshift",),
    "roon": ("roon", "roonmount", "roonstorage", "roon backup", "roonided"),
    "listenbrainz": ("listenbrainz", "listen history", "listens"),
    "spotify": ("spotify", "audio_features", "spotify-aa"),
    "musicbrainz": ("musicbrainz", "mbid", "mb_isrc", "picard"),
    "acoustid": ("acoustid", "chromaprint", "acoustic_fp", "fpcalc"),
    "lexicon": ("lexicon",),
    "mixed_in_key": ("mixedinkey", "mixed in key", "collection11", "mikdb"),
    "rekordbox": ("rekordbox", "pioneer", "djmdcontent", "master.backup"),
    "beatport": ("beatport",),
    "tidal": ("tidal",),
    "qobuz": ("qobuz",),
    "apple_music": ("apple music", "applemusic"),
    "deezer": ("deezer",),
    "traxsource": ("traxsource",),
}

HEADER_RULES = {
    "spotify": ("spotify_track_id", "spotify_id", "spotify_album_id"),
    "beatport": ("beatport_track_id", "beatport_id", "beatport_album_id"),
    "tidal": ("tidal_track_id", "tidal_id"),
    "qobuz": ("qobuz_track_id", "qobuz_id"),
    "musicbrainz": ("musicbrainz", "mbid", "recording_mbid", "release_mbid"),
    "isrc_identity": ("isrc", "isrcs"),
    "transfer_export": ("serviceid", "service_id", "platform", "trackid", "url"),
    "mixed_in_key": ("zkey", "zenergy", "zenergysegment", "mik"),
    "rekordbox": ("djmdcontent", "rekordbox", "cuepoint", "beatgrid"),
    "lexicon": ("lexicon", "rating", "energy", "camelot"),
}

CSV_FIELDS = [
    "path", "name", "extension", "kind", "source_guess", "source_hits",
    "source_evidence", "content_hints", "size_bytes", "mtime_utc", "mode", "sample_sha256",
    "sha256", "delimiter", "columns", "sample_rows", "json_keys", "xml_root",
    "xml_tags", "sheet_names", "archive_members", "sqlite_tables", "magic",
    "read_error",
]


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def compact_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def utc_mtime(timestamp: float) -> str:
    return dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).isoformat()


def hash_sample(path: Path, chunk_size: int = 65536) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        first = handle.read(chunk_size)
        hasher.update(first)
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        if size > chunk_size:
            handle.seek(max(0, size - chunk_size))
            hasher.update(handle.read(chunk_size))
    return hasher.hexdigest()


def hash_full(path: Path, chunk_size: int = 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def read_prefix(path: Path, limit: int = 256 * 1024) -> bytes:
    with path.open("rb") as handle:
        return handle.read(limit)


def source_hits(path: Path, content_tokens: Iterable[str] = ()) -> tuple[list[str], list[str], list[str]]:
    path_text = normalize(str(path))
    name_text = normalize(path.name)
    compact_path = compact_token(str(path))
    hits: list[str] = []
    evidence: list[str] = []
    hints: list[str] = []
    for source, markers in SOURCE_RULES.items():
        for marker in markers:
            marker_norm = normalize(marker)
            marker_compact = compact_token(marker)
            if (marker_norm and marker_norm in path_text) or (marker_compact and marker_compact in compact_path):
                hits.append(source)
                evidence.append(f"path:{source}:{marker}")
                break
    for token in content_tokens:
        token = compact_token(token)
        if not token:
            continue
        for source, markers in HEADER_RULES.items():
            if any(token == compact_token(marker) or token.startswith(compact_token(marker)) for marker in markers):
                if source in SOURCE_RULES:
                    hits.append(source)
                hints.append(source)
                evidence.append(f"content:{source}:{token}")
                break
    # Preserve rule order: an explicit Soundiiz/Rekordbox path wins over a
    # generic content clue such as ISRC or platform.
    return list(dict.fromkeys(hits)), list(dict.fromkeys(evidence)), list(dict.fromkeys(hints))


def classify_kind(path: Path, prefix: bytes) -> tuple[str, str]:
    ext = path.suffix.casefold()
    if prefix.startswith(b"SQLite format 3"):
        return "sqlite", "sqlite"
    if prefix.startswith(b"PAR1") or path.name.casefold().endswith(".parquet"):
        return "parquet", "parquet"
    if prefix.startswith(b"PK\x03\x04"):
        return ("spreadsheet", "zip") if ext in {".xlsx", ".ods"} else ("archive", "zip")
    if prefix.startswith(b"ustar") or ext in {".tar", ".tgz", ".gz", ".bz2"}:
        return "archive", "tar"
    if ext in {".csv", ".tsv"}:
        return "delimited", ""
    if ext in {".json", ".jsonl", ".ndjson"}:
        return "json", ""
    if ext == ".xml":
        return "xml", ""
    if ext in {".xlsx", ".xls", ".ods"}:
        return "spreadsheet", ""
    if ext in {".m3u", ".m3u8", ".pls"}:
        return "playlist", ""
    if ext in {".sqlite", ".sqlite3", ".db", ".db3", ".mikdb"}:
        return "database", ""
    if ext in {".txt", ".text", ".cue", ".log", ".yaml", ".yml"}:
        return "text", ""
    return "unknown", ""


def decode_text(prefix: bytes) -> str:
    return prefix.decode("utf-8-sig", errors="replace")


def inspect_delimited(text: str) -> dict[str, Any]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return {}
    sample = "\n".join(lines[:20])
    delimiter = ""
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = "\t" if "\t" in lines[0] else ","
    try:
        rows = list(csv.reader(lines[:20], delimiter=delimiter))
    except csv.Error:
        rows = []
    columns = rows[0] if rows else []
    return {
        "delimiter": delimiter,
        "columns": columns[:100],
        "sample_rows": max(0, len(rows) - 1),
    }


def inspect_json(text: str, kind: str) -> dict[str, Any]:
    if kind == "json":
        try:
            value = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return {}
        if isinstance(value, dict):
            return {"json_keys": sorted(str(key) for key in value.keys())[:100]}
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return {"json_keys": sorted(str(key) for key in value[0].keys())[:100], "sample_rows": len(value[:20])}
        return {"json_keys": [], "sample_rows": len(value) if isinstance(value, list) else 0}
    keys: set[str] = set()
    rows = 0
    for line in text.splitlines()[:20]:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        rows += 1
        if isinstance(value, dict):
            keys.update(str(key) for key in value.keys())
    return {"json_keys": sorted(keys)[:100], "sample_rows": rows}


def inspect_xml(text: str) -> dict[str, Any]:
    root_match = re.search(r"<([A-Za-z_][\w:.-]*)\b", text)
    result: dict[str, Any] = {"xml_root": root_match.group(1) if root_match else ""}
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError:
        return result
    tags = {element.tag.rsplit("}", 1)[-1] for element in root.iter()}
    result["xml_tags"] = sorted(tags)[:100]
    return result


def inspect_zip(path: Path, spreadsheet: bool) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            result: dict[str, Any] = {"archive_members": names[:100]}
            if spreadsheet:
                workbook = next((name for name in names if name.endswith("workbook.xml")), None)
                if workbook:
                    try:
                        root = ElementTree.fromstring(archive.read(workbook))
                        sheets = []
                        for element in root.iter():
                            if element.tag.rsplit("}", 1)[-1] == "sheet":
                                name = element.attrib.get("name")
                                if name:
                                    sheets.append(name)
                        result["sheet_names"] = sheets[:100]
                    except (ElementTree.ParseError, KeyError):
                        pass
            return result
    except (OSError, zipfile.BadZipFile):
        return {}


def inspect_archive(path: Path, kind: str) -> dict[str, Any]:
    if kind == "zip":
        return inspect_zip(path, spreadsheet=False)
    try:
        mode = "r:gz" if path.suffix.casefold() == ".tgz" else "r:*"
        with tarfile.open(path, mode) as archive:
            return {"archive_members": archive.getnames()[:100]}
    except (OSError, tarfile.TarError):
        return {}


def inspect_sqlite(path: Path) -> dict[str, Any]:
    uri = f"file:{quote(str(path))}?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True, timeout=0.25)
        try:
            rows = connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name LIMIT 200"
            )
            return {"sqlite_tables": [row[0] for row in rows]}
        finally:
            connection.close()
    except (OSError, sqlite3.Error):
        return {}


def content_tokens(metadata: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    for key in ("columns", "json_keys", "xml_tags", "archive_members", "sqlite_tables"):
        values = metadata.get(key) or []
        if isinstance(values, list):
            tokens.extend(str(value) for value in values)
    tokens.extend([str(metadata.get("xml_root", ""))])
    return tokens


def record_file(path: Path, hash_mode: str, full_hash_limit: int, inspect_databases: bool) -> dict[str, Any]:
    row: dict[str, Any] = {field: "" for field in CSV_FIELDS}
    row.update({"path": str(path), "name": path.name, "extension": path.suffix.casefold()})
    try:
        info = path.stat()
        row["size_bytes"] = info.st_size
        row["mtime_utc"] = utc_mtime(info.st_mtime)
        row["mode"] = stat.filemode(info.st_mode)
        prefix = read_prefix(path)
        kind, magic = classify_kind(path, prefix)
        row["kind"] = kind
        row["magic"] = magic
        if hash_mode != "none":
            row["sample_sha256"] = hash_sample(path)
            if hash_mode == "all" or (hash_mode == "small" and info.st_size <= full_hash_limit):
                row["sha256"] = hash_full(path)

        parsed: dict[str, Any] = {}
        if kind == "delimited":
            parsed = inspect_delimited(decode_text(prefix))
        elif kind == "json":
            parsed = inspect_json(decode_text(prefix), "jsonl" if path.suffix.casefold() in {".jsonl", ".ndjson"} else "json")
        elif kind == "xml":
            parsed = inspect_xml(decode_text(prefix))
        elif kind == "spreadsheet" and magic == "zip":
            parsed = inspect_zip(path, spreadsheet=True)
        elif kind == "archive":
            parsed = inspect_archive(path, magic)
        elif kind == "sqlite" and inspect_databases:
            parsed = inspect_sqlite(path)
        row.update({key: value for key, value in parsed.items() if key in row})
        hits, evidence, hints = source_hits(path, content_tokens(row))
        row["source_hits"] = hits
        row["source_evidence"] = evidence
        row["content_hints"] = hints
        row["source_guess"] = hits[0] if hits else "unknown"
    except (OSError, ValueError, UnicodeError) as error:
        row["read_error"] = f"{type(error).__name__}: {error}"
        row["source_hits"], row["source_evidence"], row["content_hints"] = source_hits(path)
        row["source_guess"] = row["source_hits"][0] if row["source_hits"] else "unknown"
    return row


def should_prune(directory: Path) -> bool:
    return directory.name.casefold() in PRUNE_DIR_NAMES


def should_record(path: Path) -> bool:
    extension = path.suffix.casefold()
    if extension in DATA_EXTENSIONS:
        return True
    if extension in MEDIA_EXTENSIONS:
        return False
    path_norm = normalize(str(path))
    return any(normalize(marker) in path_norm for markers in SOURCE_RULES.values() for marker in markers)


def iter_candidate_files(roots: Iterable[Path]) -> tuple[Iterable[Path], list[str]]:
    errors: list[str] = []

    def generator() -> Iterable[Path]:
        seen_paths: set[str] = set()
        for root in roots:
            root = root.expanduser().resolve()
            if not root.exists():
                errors.append(f"missing root: {root}")
                continue
            for current, directories, filenames in os.walk(root, topdown=True, followlinks=False):
                current_path = Path(current)
                directories[:] = [name for name in directories if not should_prune(current_path / name)]
                for name in filenames:
                    path = current_path / name
                    normalized = str(path)
                    if normalized in seen_paths or not should_record(path):
                        continue
                    seen_paths.add(normalized)
                    try:
                        if not stat.S_ISREG(path.stat(follow_symlinks=False).st_mode):
                            continue
                    except OSError as error:
                        errors.append(f"stat failed: {path}: {error}")
                        continue
                    yield path
    return generator(), errors


def scan(roots: Iterable[Path], hash_mode: str, full_hash_limit: int, inspect_databases: bool, max_files: int | None) -> tuple[list[dict[str, Any]], list[str]]:
    candidates, errors = iter_candidate_files(roots)
    rows: list[dict[str, Any]] = []
    for path in candidates:
        if max_files is not None and len(rows) >= max_files:
            break
        rows.append(record_file(path, hash_mode, full_hash_limit, inspect_databases))
    return rows, errors


def json_value(value: Any) -> str:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=True, sort_keys=True)
    return str(value)


def write_outputs(out_dir: Path, rows: list[dict[str, Any]], errors: list[str], roots: Iterable[Path]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "files.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")
    with (out_dir / "files.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: json_value(row.get(field, "")) for field in CSV_FIELDS})
    (out_dir / "scan_errors.log").write_text("\n".join(errors) + ("\n" if errors else ""), encoding="utf-8")

    by_source: Counter[str] = Counter()
    by_kind: Counter[str] = Counter()
    bytes_by_source: defaultdict[str, int] = defaultdict(int)
    for row in rows:
        by_kind[str(row.get("kind") or "unknown")] += 1
        hits = row.get("source_hits") or ["unknown"]
        for source in hits:
            by_source[str(source)] += 1
            bytes_by_source[str(source)] += int(row.get("size_bytes") or 0)

    lines = [
        "# Source and export inventory",
        "",
        f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}",
        f"Roots: {', '.join(str(root) for root in roots)}",
        f"Candidate files: {len(rows)}",
        f"Scan errors: {len(errors)}",
        "",
        "This is a read-only structural inventory. It contains paths, file metadata, and small schema clues; it does not copy, mutate, or upload source files.",
        "",
        "## By source",
        "",
        "| source | files | bytes |",
        "|---|---:|---:|",
    ]
    for source, count in by_source.most_common():
        lines.append(f"| {source} | {count} | {bytes_by_source[source]} |")
    lines += ["", "## By file kind", "", "| kind | files |", "|---|---:|"]
    for kind, count in by_kind.most_common():
        lines.append(f"| {kind} | {count} |")
    lines += ["", "## Highest-signal candidates", ""]
    high_signal = sorted(
        rows,
        key=lambda row: (len(row.get("source_hits") or []), int(row.get("size_bytes") or 0)),
        reverse=True,
    )
    for row in high_signal[:100]:
        hits = ", ".join(row.get("source_hits") or ["unknown"])
        clues = []
        for key in ("columns", "json_keys", "sheet_names", "xml_root", "sqlite_tables"):
            value = row.get(key)
            if value:
                clues.append(f"{key}={json_value(value)[:300]}")
        suffix = f"; {'; '.join(clues)}" if clues else ""
        lines.append(f"- `{row['path']}` [{row['kind']}; {hits}; {row['size_bytes']} bytes]{suffix}")
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def default_roots() -> list[Path]:
    roots = [Path.home(), Path("/Volumes")]
    return [root for root in roots if root.exists()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inventory provider/software exports without modifying source files.")
    parser.add_argument("--root", action="append", type=Path, help="Root to scan; repeatable. Defaults to home and /Volumes.")
    parser.add_argument("--out-dir", type=Path, required=True, help="Directory for REPORT.md, files.csv, files.jsonl, and scan_errors.log.")
    parser.add_argument("--hash-mode", choices=("none", "small", "all"), default="small", help="Hash candidates: none, files up to the limit, or all. Default: small.")
    parser.add_argument("--full-hash-limit", type=int, default=256 * 1024 * 1024, help="Maximum size in bytes for --hash-mode small. Default: 256 MiB.")
    parser.add_argument("--inspect-sqlite", action="store_true", help="Read SQLite schemas with mode=ro. Never writes; omit for a faster signature-only scan.")
    parser.add_argument("--max-files", type=int, help="Stop after this many candidates; useful for a smoke test.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    roots = args.root or default_roots()
    rows, errors = scan(roots, args.hash_mode, args.full_hash_limit, args.inspect_sqlite, args.max_files)
    write_outputs(args.out_dir, rows, errors, roots)
    print(f"indexed {len(rows)} candidate files")
    print(f"wrote {args.out_dir / 'REPORT.md'}")
    if errors:
        print(f"encountered {len(errors)} scan errors; see {args.out_dir / 'scan_errors.log'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
