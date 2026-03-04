from __future__ import annotations

import unittest

from tools.publisher.urlutil import canonicalize_url


class TestUrlutil(unittest.TestCase):
    def test_canonicalize_url_drops_utm_and_fragment(self) -> None:
        url = "https://Example.com/path?a=1&utm_source=x#section"
        self.assertEqual(canonicalize_url(url), "https://example.com/path?a=1")

    def test_canonicalize_url_sorts_query(self) -> None:
        url = "https://example.com/x?b=2&a=1"
        self.assertEqual(canonicalize_url(url), "https://example.com/x?a=1&b=2")


if __name__ == "__main__":
    unittest.main()
