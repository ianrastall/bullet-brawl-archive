# bullet-brawl-archive

Chess.com Bullet Brawl games, renamed and organized for the Chess Nerd archive.
The collection currently covers January 2023 through August 2026 and can be
expanded with older events as their PGNs are collected.

## Data and naming

ZIPs live in year folders. Each ZIP contains one matching PGN, for example:

`2026/cc_bullet-brawl_260829.zip` → `cc_bullet-brawl_260829.pgn`

Filenames follow `cc_bullet-brawl_YYMMDD.(zip|pgn)`. One event per date; no
suffix is used.

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
- `bullet-brawl-YYYY-MM-DD.pgn` (legacy canonical)
- `cc_bullet-brawl_YYMMDD.pgn` (current canonical)

Rebuild metadata without adding files with `python archive_metadata.py --write`.
Run validation tests with `python -m unittest test_archive_metadata`.

## Current collection

The archive contains 167 Bullet Brawl events from January 28, 2023, through
August 29, 2026: 497,835 games. Coverage is complete for 2024-2026 except
January 27 and October 26, 2024, where no source file is currently available;
2023 is partial (30 events, roughly weekly from July onward with occasional
earlier dates). Community Bullet Brawl is a separate competition and is not
included.
