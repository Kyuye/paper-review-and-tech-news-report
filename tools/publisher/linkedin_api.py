from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class LinkedInResult:
    ok: bool
    id: str
    raw: dict


def post_text(*, access_token: str, author_urn: str, text: str) -> LinkedInResult:
    url = "https://api.linkedin.com/v2/ugcPosts"
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        method="POST",
        data=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    with urlopen(req, timeout=30) as resp:
        raw_text = resp.read().decode("utf-8", errors="replace").strip() or "{}"
        try:
            data = json.loads(raw_text)
        except Exception:
            data = {"raw": raw_text}
        # LinkedIn often returns an empty body with the created id in headers.
        post_id = resp.headers.get("x-restli-id") or data.get("id") or ""
        return LinkedInResult(ok=True, id=str(post_id), raw=data if isinstance(data, dict) else {"data": data})

