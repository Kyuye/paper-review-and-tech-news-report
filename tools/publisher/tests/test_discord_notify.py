from __future__ import annotations

import unittest

from tools.publisher.discord_notify import build_message


class TestDiscordNotify(unittest.TestCase):
    def test_build_message_truncates(self) -> None:
        msg = "a" * 5000
        out = build_message(msg, limit=100)
        self.assertLessEqual(len(out), 200)  # allow suffix
        self.assertIn("truncated", out)


if __name__ == "__main__":
    unittest.main()

