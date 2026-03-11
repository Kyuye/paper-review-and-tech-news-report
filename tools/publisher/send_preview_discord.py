from __future__ import annotations

import os
from pathlib import Path

from .discord_notify import send_discord
from .settings import repo_root


def main() -> int:
    webhook_url = (os.getenv("DISCORD_WEBHOOK_URL") or "").strip()
    if not webhook_url:
        print("Discord notify skipped: missing DISCORD_WEBHOOK_URL")
        return 0

    pr_url = (os.getenv("PULL_REQUEST_URL") or "").strip()
    if not pr_url:
        raise RuntimeError("Missing PULL_REQUEST_URL")

    root = repo_root()
    preview_path = root / "previews" / "email" / "latest.md"
    if preview_path.exists():
        body = preview_path.read_text(encoding="utf-8")
        text = body.replace("{PULL_REQUEST_URL}", pr_url).strip() + "\n"
    else:
        text = f"GitBook draft PR created:\n{pr_url}\n"

    res = send_discord(webhook_url=webhook_url, text=text)
    if not res.ok:
        # Don't fail the workflow for notification issues.
        print(f"Discord notify failed (non-fatal): {res.response_text}")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

