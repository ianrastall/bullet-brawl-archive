# bullet-brawl-archive

Chess.com Bullet Brawl games, renamed and organized for the Chess Nerd archive.
The collection currently covers October 2024 through August 2026 and can be
expanded with older events as their PGNs are collected.

## Data and naming

ZIPs live in year folders. Each ZIP contains one matching PGN, for example:

`2026/bullet-brawl-2026-08-29.zip` → `bullet-brawl-2026-08-29.pgn`

`bb_manifest.json` is the structured source for the future Chess Nerd archive
page. `bb_links.txt`, `bb_events.txt`, and `bb_game_counts.txt` are generated
compatibility exports. Dates come from the downloaded filenames because the
PGNs use the generic `Live Chess` Event tag.

## Import PGNs

Use Python 3.10 or newer. Preview selected files first:

```powershell
python archive_metadata.py --import-pgn D:\dev\pgn\bb\Bullet_Brawl_2026-01-03-11-00.pgn
```

Add `--write` to create the ZIPs and regenerate metadata. Multiple paths can
follow `--import-pgn`. The importer preserves each source file and copies its PGN
bytes into the ZIP unchanged. It checks game headers, verifies each ZIP after
writing, and refuses duplicate dates.

Accepted source filename forms:

- `Bullet_Brawl_YYYY-MM-DD-HH-MM.pgn`
- `Bullet-Brawl-Month-DD-YYYY_YYYY-MM-DD-HH-MM.pgn`
- `YYYY-bullet-brawl-month-DD.pgn`
- `bullet-brawl-YYYY-MM-DD.pgn`

Rebuild metadata without adding files with `python archive_metadata.py --write`.
Run validation tests with `python -m unittest test_archive_metadata`.

## Current collection

The archive contains 99 Bullet Brawl events from October 5, 2024, through August
29, 2026: 318,952 games. Community Bullet Brawl is a separate competition and
is not included.
