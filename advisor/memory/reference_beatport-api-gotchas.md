---
name: beatport-api-gotchas
description: Beatport catalog API auth quirks in tagslut — which endpoint works with the search bearer, and the catalog_get_track 403->session-dead trap
metadata:
  type: reference
---

Beatport catalog API via `BeatportProvider` (`slut/tagslut/metadata/providers/beatport.py`), verified 2026-07-10:

- **`catalog_list_tracks({"isrc": X})` WORKS with only the search bearer** (`ts-auth beatport`). This is `GET /v4/catalog/tracks/?isrc=` — the ISRC search. Returns raw `results[]` with **nested numeric IDs** (`key.id`, `genre.id`, `release.id`, `release.label.id`) that `search_by_isrc`→`ProviderTrack` DISCARDS. Use `_api_client.catalog_list_tracks(...)` directly when you need the numeric IDs for `ref_bp_track` (mapping validated 100% on an 84-row same-track oracle). ~1 call/ISRC (list already carries nested IDs; no per-track hydrate needed).
- **`catalog_get_track(bp_id)` 403s** with only the search bearer (single-track GET `/v4/catalog/tracks/{id}/` needs real catalog auth = session cookie/basic). Worse: the first 403 sets `self._session_dead=True`, so **every subsequent call short-circuits to "session marked dead"** — one bad call silently kills a whole batch. **Never fetch by bp_id via get_track in a loop.** If you have a bp_id and need the payload, fetch by the Beatport ISRC via `catalog_list_tracks({isrc})` and pick the result whose `id` matches.
- Auth reconciliation: `auth_kind="catalog"` falls back to the **search bearer** if no session cookie/basic (`beatport.py:292`). So the "ISRC search needs the search bearer" (prompt) and "catalog endpoint" (code) framings agree — it's not a contradiction. A stale bearer → `BeatportAuthError`; run `ts-auth beatport`. Precondition-check auth BEFORE any fill loop.
- Repo python is `.venv/bin/python` (3.14). The `ts-auth`/`ts-get` shell functions point at a STALE path (`/Users/georgeskhawam/...`) on this machine — the real entrypoints are `slut/tools/auth` / `slut/tools/get`.

Used by `slut/tools/v4/gap_close_beatport_refs.py` and `recover_beatport_by_identity.py`. See [[provider-matching-method]].
