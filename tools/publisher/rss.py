from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
import html
import re
from xml.etree import ElementTree as ET


_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    if not text:
        return ""
    # Best-effort HTML cleanup for RSS descriptions.
    unescaped = html.unescape(text)
    cleaned = _TAG_RE.sub(" ", unescaped)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _parse_date(raw: str) -> datetime | None:
    if not raw:
        return None
    raw = raw.strip()
    try:
        # Atom often uses ISO8601; RSS often uses RFC822.
        if "T" in raw:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return dt
    except Exception:
        pass
    try:
        return parsedate_to_datetime(raw)
    except Exception:
        return None


@dataclass(frozen=True)
class FeedEntry:
    title: str
    url: str
    published_at: datetime | None
    summary: str


def parse_feed(xml_text: str) -> list[FeedEntry]:
    if not xml_text.strip():
        return []
    root = ET.fromstring(xml_text)

    # Atom
    if root.tag.endswith("feed"):
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        out: list[FeedEntry] = []
        for entry in root.findall("atom:entry", ns):
            title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
            published_raw = (
                (entry.findtext("atom:published", default="", namespaces=ns) or "").strip()
                or (entry.findtext("atom:updated", default="", namespaces=ns) or "").strip()
            )
            published_at = _parse_date(published_raw)

            href = ""
            for link in entry.findall("atom:link", ns):
                rel = (link.attrib.get("rel") or "alternate").lower()
                if rel == "alternate" and link.attrib.get("href"):
                    href = link.attrib["href"]
                    break
            if not href:
                href = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()

            summary = (
                (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
                or (entry.findtext("atom:content", default="", namespaces=ns) or "").strip()
            )
            out.append(FeedEntry(title=title, url=href, published_at=published_at, summary=_strip_html(summary)))
        return out

    # RSS2 (no namespaces assumed)
    channel = root.find("channel")
    if channel is None:
        return []

    out = []
    for item in channel.findall("item"):
        title = (item.findtext("title", default="") or "").strip()
        url = (item.findtext("link", default="") or "").strip()
        pub_raw = (item.findtext("pubDate", default="") or "").strip()
        published_at = _parse_date(pub_raw)
        summary = (item.findtext("description", default="") or "").strip()
        out.append(FeedEntry(title=title, url=url, published_at=published_at, summary=_strip_html(summary)))
    return out

