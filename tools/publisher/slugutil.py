from __future__ import annotations

import re
import unicodedata


_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify(text: str, *, fallback: str = "post") -> str:
    raw = (text or "").strip().lower()
    if not raw:
        return fallback
    raw = unicodedata.normalize("NFKD", raw)
    raw = raw.encode("ascii", errors="ignore").decode("ascii")
    raw = _NON_ALNUM.sub("-", raw).strip("-")
    return raw or fallback

