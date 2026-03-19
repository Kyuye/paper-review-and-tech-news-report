from __future__ import annotations

import os
from pathlib import Path
from urllib.error import HTTPError, URLError

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
    preview_path = root / "previews" / "notifications" / "latest.md"
    if preview_path.exists():
        body = preview_path.read_text(encoding="utf-8")
        text = body.replace("{PULL_REQUEST_URL}", pr_url).strip() + "\n"
    else:
        text = f"GitBook candidate pack PR created:\n{pr_url}\n"

    try:
        res = send_discord(webhook_url=webhook_url, text=text)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"Discord notify failed (non-fatal): HTTP {exc.code} {detail}".strip())
        return 0
    except URLError as exc:
        print(f"Discord notify failed (non-fatal): {exc}")
        return 0
    except Exception as exc:
        print(f"Discord notify failed (non-fatal): {exc}")
        return 0

    if not res.ok:
        # Don't fail the workflow for notification issues.
        print(f"Discord notify failed (non-fatal): {res.response_text}")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
