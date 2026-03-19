from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable
from urllib.error import URLError
from urllib.request import Request, urlopen

from .rss import parse_feed
from .settings import Source
from .urlutil import canonicalize_url


USER_AGENT = "paper-review-and-tech-news-report/1.0 (rss; contact: EMAIL_FROM)"


@dataclass(frozen=True)
class NewsItem:
    title: str
    url: str
    published_at: datetime
    source_name: str
    entity_type: str
    summary: str
    default_topics: tuple[str, ...]


def _fetch(url: str, timeout: int = 20) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def collect_news(
    *,
    sources: Iterable[Source],
    now_utc: datetime,
    lookback_days: int = 3,
) -> tuple[list[NewsItem], list[str]]:
    since = now_utc - timedelta(days=lookback_days)
    items: list[NewsItem] = []
    errors: list[str] = []

    for src in sources:
        try:
            xml = _fetch(src.feed_url)
            entries = parse_feed(xml)
        except URLError as exc:
            errors.append(f"{src.name}: fetch_error={exc}")
            continue
        except Exception as exc:
            errors.append(f"{src.name}: parse_error={exc}")
            continue

        for e in entries:
            if not e.published_at:
                continue
            published = e.published_at
            published_utc = published if published.tzinfo else published.replace(tzinfo=now_utc.tzinfo)
            if published_utc < since:
                continue
            url = canonicalize_url(e.url)
            if not url:
                continue
            items.append(
                NewsItem(
                    title=e.title.strip(),
                    url=url,
                    published_at=published,
                    source_name=src.name,
                    entity_type=src.entity_type,
                    summary=e.summary.strip(),
                    default_topics=src.default_topics,
                )
            )

    # Dedupe by URL.
    dedup: dict[str, NewsItem] = {}
    for it in items:
        dedup[it.url] = it
    out = list(dedup.values())
    out.sort(key=lambda x: (x.published_at.isoformat(), x.source_name, x.title), reverse=True)
    return out, errors
