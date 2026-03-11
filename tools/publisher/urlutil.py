from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


_DROP_PARAMS_PREFIXES = ("utm_",)
_DROP_PARAMS = {"gclid", "fbclid", "mc_cid", "mc_eid"}


def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    p = urlparse(url.strip())
    query_pairs = []
    for k, v in parse_qsl(p.query, keep_blank_values=True):
        lk = (k or "").lower()
        if lk in _DROP_PARAMS or any(lk.startswith(prefix) for prefix in _DROP_PARAMS_PREFIXES):
            continue
        query_pairs.append((k, v))
    query_pairs.sort(key=lambda kv: (kv[0].lower(), kv[1]))
    cleaned = p._replace(
        scheme=p.scheme or "https",
        netloc=(p.netloc or "").lower(),
        fragment="",
        query=urlencode(query_pairs, doseq=True),
    )
    return urlunparse(cleaned)

