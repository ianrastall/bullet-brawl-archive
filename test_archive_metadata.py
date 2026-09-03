import unittest

from archive_metadata import archive_date, entry_metadata, pgn_metadata, render_metadata


class MetadataTests(unittest.TestCase):
    def test_supported_source_names(self):
        self.assertEqual(archive_date('Bullet_Brawl_2026-01-03-11-00.pgn'), '2026-01-03')
        self.assertEqual(
            archive_date('Bullet-Brawl-August-29-2026_2026-08-29-11-00.pgn'), '2026-08-29'
        )
        self.assertEqual(archive_date('2026-bullet-brawl-august-29.pgn'), '2026-08-29')
        self.assertEqual(archive_date('bullet-brawl-2026-08-29.zip'), '2026-08-29')

    def test_disagreeing_or_invalid_dates_fail(self):
        for filename in (
            'Bullet-Brawl-August-28-2026_2026-08-29-11-00.pgn',
            'Bullet_Brawl_2026-02-30-11-00.pgn',
            '../Bullet_Brawl_2026-01-03-11-00.pgn',
            'tournament.pgn',
        ):
            with self.assertRaises((ValueError, KeyError)):
                archive_date(filename)

    def test_incomplete_game_headers_fail(self):
        with self.assertRaises(ValueError):
            pgn_metadata(b'[Event "Live Chess"]\n[White "A"]\n')

    def test_game_records_are_counted(self):
        content = (
            b'[Event "Live Chess"]\n[White "A"]\n[Black "B"]\n[Result "1-0"]\n\n1-0\n'
            b'[Event "Live Chess"]\n[White "C"]\n[Black "D"]\n[Result "0-1"]\n\n0-1\n'
        )
        self.assertEqual(pgn_metadata(content), ('Live Chess', 2))

    def test_metadata_uses_canonical_names_and_urls(self):
        entry = entry_metadata('bullet-brawl-2026-08-29.zip',
                               'bullet-brawl-2026-08-29.pgn', 'Live Chess', 10, 'a' * 64)
        self.assertEqual(entry['event'], 'Bullet Brawl')
        self.assertEqual(entry['sourceEvent'], 'Live Chess')
        self.assertIn('/2026/bullet-brawl-', render_metadata([entry])['bb_links.txt'])
        self.assertNotIn('\\', entry['url'])


if __name__ == '__main__':
    unittest.main()

