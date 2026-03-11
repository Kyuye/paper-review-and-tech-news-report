from __future__ import annotations

import os
from pathlib import Path

from .emailer import send_email
from .settings import repo_root


def main() -> int:
    root = repo_root()
    pr_url = (os.getenv("PULL_REQUEST_URL") or "").strip()
    if not pr_url:
        raise RuntimeError("Missing PULL_REQUEST_URL")

    preview_path = root / "previews" / "email" / "latest.md"
    body = preview_path.read_text(encoding="utf-8") if preview_path.exists() else ""
    body = body.replace("{PULL_REQUEST_URL}", pr_url).strip() + "\n"

    subject = (os.getenv("EMAIL_SUBJECT") or "[Draft] GitBook 업데이트 미리보기").strip()
    send_email(subject=subject, body=body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

