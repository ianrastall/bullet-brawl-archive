#!/usr/bin/env python3
"""Build Bullet Brawl metadata and optionally import selected PGNs."""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import re
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CANONICAL_NAME = re.compile(r'^cc_bullet-brawl_(\d{2})(\d{2})(\d{2})\.(?:pgn|zip)$', re.I)
LEGACY_NAME = re.compile(r'^bullet-brawl-(\d{4}-\d{2}-\d{2})\.(?:pgn|zip)$', re.I)
TIMED_NAME = re.compile(r'^Bullet_Brawl_(\d{4}-\d{2}-\d{2})-\d{2}-\d{2}\.pgn$', re.I)
DESCRIPTIVE_NAME = re.compile(
    r'^Bullet-Brawl-([A-Za-z]+)-(\d{2})-(\d{4})_(\d{4}-\d{2}-\d{2})-\d{2}-\d{2}\.pgn$', re.I
)
EXPORT_NAME = re.compile(r'^(\d{4})-bullet-brawl-([a-z]+)-(\d{1,2})\.pgn$', re.I)
HEADER = re.compile(rb'^\[([A-Za-z0-9_]+) "([^"\r\n]*)"\]\s*$', re.M)


def archive_date(filename: str) -> str:
    match = CANONICAL_NAME.fullmatch(filename)
    if match:
        return date(2000 + int(match[1]), int(match[2]), int(match[3])).isoformat()
    match = LEGACY_NAME.fullmatch(filename)
    if match:
        return date.fromisoformat(match[1]).isoformat()
    match = TIMED_NAME.fullmatch(filename)
    if match:
        return date.fromisoformat(match[1]).isoformat()
    match = DESCRIPTIVE_NAME.fullmatch(filename)
    if match:
        months = {name.lower(): number for number, name in enumerate(calendar.month_name) if name}
        written = date(int(match[3]), months[match[1].lower()], int(match[2]))
        embedded = date.fromisoformat(match[4])
        if written != embedded:
            raise ValueError(f'Filename dates disagree: {filename}')
        return embedded.isoformat()
    match = EXPORT_NAME.fullmatch(filename)
    if match:
        months = {name.lower(): number for number, name in enumerate(calendar.month_name) if name}
        return date(int(match[1]), months[match[2].lower()], int(match[3])).isoformat()
    raise ValueError(f'Unrecognized Bullet Brawl filename: {filename}')


def pgn_metadata(content: bytes) -> tuple[str, int]:
    tags: dict[bytes, list[bytes]] = {}
    for name, value in HEADER.findall(content.removeprefix(b'\xef\xbb\xbf')):
        tags.setdefault(name, []).append(value)
    events = tags.get(b'Event', [])
    if not events:
        raise ValueError('PGN has no Event headers.')
    for name in (b'White', b'Black', b'Result'):
        if len(tags.get(name, [])) != len(events):
            raise ValueError(f'PGN has missing or duplicate {name.decode()} headers.')
    return events[0].decode('utf-8').strip(), len(events)


def entry_metadata(filename: str, pgn: str, source_event: str, games: int, sha256: str) -> dict:
    event_date = archive_date(filename)
    year = int(event_date[:4])
    return {
        'pgn': pgn,
        'zip': filename,
        'year': year,
        'date': event_date,
        'event': 'Bullet Brawl',
        'sourceEvent': source_event,
        'games': games,
        'url': f'https://github.com/ianrastall/bullet-brawl-archive/raw/main/{year}/{filename}',
        'sha256': sha256,
    }


def read_zip(path: Path) -> dict:
    event_date = archive_date(path.name)
    if path.parent.name != event_date[:4]:
        raise ValueError(f'Wrong year folder: {path}')
    expected = path.with_suffix('.pgn').name
    with zipfile.ZipFile(path) as archive:
        names = [item.filename for item in archive.infolist() if not item.is_dir()]
        if names != [expected]:
            raise ValueError(f'Expected one canonical PGN in {path}: {names}')
        source_event, games = pgn_metadata(archive.read(expected))
    return entry_metadata(path.name, expected, source_event, games, hashlib.sha256(path.read_bytes()).hexdigest())


def render_metadata(entries: list[dict]) -> dict[str, str]:
    entries = sorted(entries, key=lambda entry: entry['zip'])
    return {
        'bb_manifest.json': json.dumps(entries, ensure_ascii=False, indent=2) + '\n',
        'bb_links.txt': ''.join(f"{entry['url']}\n" for entry in entries),
        'bb_events.txt': ''.join(f"{entry['pgn']}: {entry['event']}\n" for entry in entries),
        'bb_game_counts.txt': ''.join(f"{entry['pgn']}: {entry['games']}\n" for entry in entries),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-pgn', type=Path, nargs='+', default=[],
                        help='Selected PGNs; their filenames determine event dates.')
    parser.add_argument('--write', action='store_true',
                        help='Create new ZIPs and write metadata. Otherwise preview only.')
    args = parser.parse_args()

    entries = [read_zip(path) for path in sorted(ROOT.glob('20[0-9][0-9]/*.zip'))]
    known = {entry['zip'] for entry in entries}
    pending = []
    for source in args.import_pgn:
        event_date = archive_date(source.name)
        filename = f'cc_bullet-brawl_{event_date[2:4]}{event_date[5:7]}{event_date[8:10]}.zip'
        if filename in known:
            raise ValueError(f'Archive already exists or was selected twice: {filename}')
        content = source.read_bytes()
        source_event, games = pgn_metadata(content)
        known.add(filename)
        pending.append((source, filename, source_event, games, hashlib.sha256(content).hexdigest()))
        print(f'{source.name} -> {filename}: {games:,} games', flush=True)

    if not args.write:
        print(f'Validated {len(entries)} existing ZIPs and {len(pending)} new PGNs. Add --write to save.')
        return

    for source, filename, source_event, games, digest in pending:
        content = source.read_bytes()
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError(f'Source changed during import: {source}')
        event_date = archive_date(filename)
        destination = ROOT / event_date[:4] / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix('.zip.tmp')
        pgn = filename.removesuffix('.zip') + '.pgn'
        with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            archive.writestr(pgn, content)
        with zipfile.ZipFile(temporary) as archive:
            if archive.namelist() != [pgn] or archive.read(pgn) != content:
                raise ValueError(f'ZIP verification failed: {destination}')
        temporary.rename(destination)
        entries.append(entry_metadata(filename, pgn, source_event, games,
                                      hashlib.sha256(destination.read_bytes()).hexdigest()))

    for name, content in render_metadata(entries).items():
        target = ROOT / name
        if target.exists() and target.read_text(encoding='utf-8-sig') == content:
            continue
        temporary = target.with_suffix(target.suffix + '.tmp')
        temporary.write_text(content, encoding='utf-8', newline='\n')
        temporary.replace(target)
    print(f'Wrote {len(entries)} events and {sum(entry["games"] for entry in entries):,} games.')


if __name__ == '__main__':
    main()

