from __future__ import annotations

import unittest

from tools.publisher.rss import parse_feed


class TestRss(unittest.TestCase):
    def test_parse_rss2_items(self) -> None:
        xml = """<?xml version="1.0"?>
        <rss version="2.0">
          <channel>
            <title>Test</title>
            <item>
              <title>Hello</title>
              <link>https://example.com/a?utm_source=x</link>
              <pubDate>Mon, 02 Mar 2026 09:00:00 +0000</pubDate>
              <description><![CDATA[<p>Summary</p>]]></description>
            </item>
          </channel>
        </rss>
        """
        entries = parse_feed(xml)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "Hello")
        self.assertTrue(entries[0].url.startswith("https://example.com/"))
        self.assertIsNotNone(entries[0].published_at)
        self.assertIn("Summary", entries[0].summary)

    def test_parse_atom_entries(self) -> None:
        xml = """<?xml version="1.0"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <title>Test</title>
          <entry>
            <title>Atom Post</title>
            <id>https://example.com/atom</id>
            <updated>2026-03-02T09:00:00Z</updated>
            <link rel="alternate" href="https://example.com/atom?utm_campaign=x"/>
            <summary>Hi</summary>
          </entry>
        </feed>
        """
        entries = parse_feed(xml)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "Atom Post")
        self.assertIsNotNone(entries[0].published_at)


if __name__ == "__main__":
    unittest.main()
