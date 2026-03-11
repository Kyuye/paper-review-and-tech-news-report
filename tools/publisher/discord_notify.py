from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.request import Request, urlopen


DISCORD_MAX_CHARS = 2000
DEFAULT_SAFE_LIMIT = 1800


@dataclass(frozen=True)
class DiscordResult:
    ok: bool
    status: int
    response_text: str


def build_message(text: str, *, limit: int = DEFAULT_SAFE_LIMIT) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    if len(raw) <= limit:
        return raw
    suffix = "\n\n…(truncated, see PR for full details)"
    keep = max(0, limit - len(suffix))
    return raw[:keep].rstrip() + suffix


def send_discord(*, webhook_url: str, text: str, timeout: int = 20) -> DiscordResult:
    webhook_url = (webhook_url or "").strip()
    if not webhook_url:
        return DiscordResult(ok=False, status=0, response_text="missing_webhook_url")

    content = build_message(text, limit=min(DEFAULT_SAFE_LIMIT, DISCORD_MAX_CHARS))
    payload = {"content": content or "(empty message)"}
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        webhook_url,
        method="POST",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(req, timeout=timeout) as resp:
        resp_text = resp.read().decode("utf-8", errors="replace")
        return DiscordResult(ok=True, status=int(getattr(resp, "status", 200)), response_text=resp_text)

