import json
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

from inventory_source_exports import scan, write_outputs


class SourceInventoryTests(unittest.TestCase):
    def test_classifies_provider_and_software_exports(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soundiiz = root / "Downloads" / "Soundiiz"
            soundiiz.mkdir(parents=True)
            (soundiiz / "TracksForSoundiiz.csv").write_text(
                "title;artist;album;isrc;platform;trackId\nTrack;Artist;Album;GBAAA0000001;spotify;abc\n",
                encoding="utf-8",
            )
            (root / "rekordbox_export.xml").write_text(
                "<?xml version=\"1.0\"?><DJ_PLAYLISTS><PRODUCT Name=\"rekordbox\"><TRACK TrackID=\"1\"/></PRODUCT></DJ_PLAYLISTS>",
                encoding="utf-8",
            )
            (root / "listenbrainz.jsonl").write_text(
                json.dumps({"mbid_mapping": {"recording_mbid": "mbid"}, "additional_info": {"spotify_track_id": "sp"}}) + "\n",
                encoding="utf-8",
            )
            rows, errors = scan([root], "small", 1024 * 1024, False, None)
            self.assertEqual(errors, [])
            by_name = {row["name"]: row for row in rows}
            self.assertEqual(by_name["TracksForSoundiiz.csv"]["source_guess"], "soundiiz")
            self.assertEqual(by_name["TracksForSoundiiz.csv"]["delimiter"], ";")
            self.assertIn("transfer_export", by_name["TracksForSoundiiz.csv"]["content_hints"])
            self.assertIn("rekordbox", by_name["rekordbox_export.xml"]["source_hits"])
            self.assertEqual(by_name["rekordbox_export.xml"]["xml_root"], "DJ_PLAYLISTS")
            self.assertIn("listenbrainz", by_name["listenbrainz.jsonl"]["source_hits"])
            self.assertIn("musicbrainz", by_name["listenbrainz.jsonl"]["source_hits"])

    def test_inspects_xlsx_and_sqlite_only_read_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workbook = root / "Mixed In Key" / "Collection.xlsx"
            workbook.parent.mkdir()
            with zipfile.ZipFile(workbook, "w") as archive:
                archive.writestr(
                    "xl/workbook.xml",
                    "<workbook xmlns=\"urn:schemas-microsoft-com:office:spreadsheet\"><sheets><sheet name=\"Tracks\"/></sheets></workbook>",
                )
            database = root / "Rekordbox" / "master.backup.db"
            database.parent.mkdir()
            connection = sqlite3.connect(database)
            connection.execute("CREATE TABLE djmdContent (TrackID INTEGER)")
            connection.commit()
            connection.close()
            rows, errors = scan([root], "none", 0, True, None)
            self.assertEqual(errors, [])
            by_name = {row["name"]: row for row in rows}
            self.assertEqual(by_name["Collection.xlsx"]["sheet_names"], ["Tracks"])
            self.assertIn("mixed_in_key", by_name["Collection.xlsx"]["source_hits"])
            self.assertEqual(by_name["master.backup.db"]["kind"], "sqlite")
            self.assertEqual(by_name["master.backup.db"]["sqlite_tables"], ["djmdContent"])
            self.assertIn("rekordbox", by_name["master.backup.db"]["source_hits"])

    def test_writes_machine_and_human_reports(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "input"
            root.mkdir()
            (root / "export.csv").write_text("title,artist\nA,B\n", encoding="utf-8")
            rows, errors = scan([root], "none", 0, False, None)
            out = Path(temporary) / "out"
            write_outputs(out, rows, errors, [root])
            self.assertTrue((out / "REPORT.md").exists())
            self.assertTrue((out / "files.csv").exists())
            self.assertEqual(len((out / "files.jsonl").read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
