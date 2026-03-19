from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

from tools.publisher.discord_notify import build_message
from tools.publisher.send_preview_discord import main as send_preview_discord_main


class TestDiscordNotify(unittest.TestCase):
    def test_build_message_truncates(self) -> None:
        msg = "a" * 5000
        out = build_message(msg, limit=100)
        self.assertLessEqual(len(out), 200)  # allow suffix
        self.assertIn("truncated", out)

    def test_send_preview_discord_handles_network_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            preview = root / "previews" / "notifications"
            preview.mkdir(parents=True)
            (preview / "latest.md").write_text("Preview {PULL_REQUEST_URL}", encoding="utf-8")

            with patch("tools.publisher.send_preview_discord.repo_root", return_value=root), \
                patch("tools.publisher.send_preview_discord.send_discord", side_effect=URLError("bad webhook")), \
                patch.dict(
                    os.environ,
                    {
                        "DISCORD_WEBHOOK_URL": "https://discord.example/webhook",
                        "PULL_REQUEST_URL": "https://github.com/example/pr/1",
                    },
                    clear=False,
                ):
                result = send_preview_discord_main()

            self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
