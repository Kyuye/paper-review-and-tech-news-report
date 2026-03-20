from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta
from html import unescape
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .settings import PaperJournal, PaperSearchConfig
from .urlutil import canonicalize_url


USER_AGENT = "paper-review-and-tech-news-report/1.0 (crossref metadata-only; contact: EMAIL_FROM)"
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class Paper:
    title: str
    abstract: str
    doi: str
    url: str
    published_date: str
    venue: str
    year: str
    authors: str
    source: str
    match_reason: str = ""
    neural_score: int = 0
    synbio_score: int = 0


def _get_json(url: str, params: dict, timeout: int = 20) -> dict:
    qs = urlencode(params, doseq=True)
    full = f"{url}?{qs}" if qs else url
    req = Request(full, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _clean_text(raw: str) -> str:
    text = TAG_RE.sub(" ", raw or "")
    text = unescape(text)
    return WHITESPACE_RE.sub(" ", text).strip()


def _extract_date(item: dict) -> str:
    for key in ("published-online", "published-print", "issued", "created"):
        payload = item.get(key) or {}
        date_parts = payload.get("date-parts") or []
        if not date_parts:
            continue
        first = date_parts[0] or []
        if not first:
            continue
        year = int(first[0])
        month = int(first[1]) if len(first) > 1 else 1
        day = int(first[2]) if len(first) > 2 else 1
        return f"{year:04d}-{month:02d}-{day:02d}"
    return ""


def _extract_authors(item: dict) -> str:
    names: list[str] = []
    for author in item.get("author") or []:
        if not isinstance(author, dict):
            continue
        given = str(author.get("given") or "").strip()
        family = str(author.get("family") or "").strip()
        full = " ".join(part for part in (given, family) if part)
        if full:
            names.append(full)
    return ", ".join(names[:8])


def _container_title(item: dict) -> str:
    titles = item.get("container-title") or []
    if isinstance(titles, list):
        for title in titles:
            cleaned = _clean_text(str(title))
            if cleaned:
                return cleaned
    return _clean_text(str(item.get("publisher") or ""))


def _normalize_venue(name: str) -> str:
    return WHITESPACE_RE.sub(" ", (name or "").strip()).lower()


def _matches_keywords(text: str, keywords: tuple[str, ...]) -> list[str]:
    haystack = text.lower()
    matches: list[str] = []
    for keyword in keywords:
        candidate = keyword.lower().strip()
        if candidate and candidate in haystack:
            matches.append(keyword)
    return matches


def _build_reason(neural_hits: list[str], synbio_hits: list[str]) -> str:
    neural_part = ", ".join(neural_hits[:3]) if neural_hits else "none"
    synbio_part = ", ".join(synbio_hits[:3]) if synbio_hits else "none"
    return f"Matched neural keywords: {neural_part}; matched synbio keywords: {synbio_part}."


def _paper_from_crossref(item: dict, journal: PaperJournal) -> Paper | None:
    title_list = item.get("title") or []
    title = _clean_text(str(title_list[0] if title_list else ""))
    if not title:
        return None

    doi = str(item.get("DOI") or "").strip()
    venue = _container_title(item)
    published = _extract_date(item)
    year = published[:4] if len(published) >= 4 else ""
    abstract = _clean_text(str(item.get("abstract") or ""))
    url = canonicalize_url(str(item.get("URL") or ""))
    if not url and doi:
        url = canonicalize_url(f"https://doi.org/{doi}")

    return Paper(
        title=title,
        abstract=abstract,
        doi=doi,
        url=url,
        published_date=published,
        venue=venue,
        year=year,
        authors=_extract_authors(item),
        source=journal.group,
    )


def _query_crossref(journal: PaperJournal, query: str, *, from_date: str, rows: int = 20) -> list[Paper]:
    base_url = "https://api.crossref.org/works"
    data = _get_json(
        base_url,
        {
            "filter": f"from-pub-date:{from_date}",
            "query.container-title": journal.name,
            "query.bibliographic": query,
            "rows": rows,
            "select": "DOI,title,abstract,container-title,published-online,published-print,issued,created,author,URL,publisher",
            "sort": "published",
            "order": "desc",
        },
    )
    items = (data.get("message") or {}).get("items") or []
    out: list[Paper] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        paper = _paper_from_crossref(item, journal)
        if paper:
            out.append(paper)
    return out


def _rank_papers(papers: list[Paper]) -> list[Paper]:
    return sorted(
        papers,
        key=lambda paper: (
            paper.published_date or "",
            paper.neural_score,
            paper.synbio_score,
            paper.venue.lower(),
            paper.title.lower(),
        ),
        reverse=True,
    )


def _apply_filters(papers: list[Paper], config: PaperSearchConfig) -> list[Paper]:
    whitelist = {_normalize_venue(journal.name): journal for journal in config.journals}
    filtered: list[Paper] = []

    for paper in papers:
        venue_key = _normalize_venue(paper.venue)
        journal = whitelist.get(venue_key)
        if journal is None:
            continue
        text = f"{paper.title}\n{paper.abstract}"
        neural_hits = _matches_keywords(text, config.neural_keywords)
        synbio_hits = _matches_keywords(text, config.synbio_keywords)
        if not neural_hits or not synbio_hits:
            continue
        filtered.append(
            replace(
                paper,
                source=journal.group,
                match_reason=_build_reason(neural_hits, synbio_hits),
                neural_score=len(neural_hits),
                synbio_score=len(synbio_hits),
            )
        )

    dedup: dict[str, Paper] = {}
    for paper in filtered:
        key = f"doi:{paper.doi.lower()}" if paper.doi else f"url:{paper.url}|{paper.title.lower()}"
        existing = dedup.get(key)
        if existing is None or (paper.published_date, paper.neural_score, paper.synbio_score) > (
            existing.published_date,
            existing.neural_score,
            existing.synbio_score,
        ):
            dedup[key] = paper
    return _rank_papers(list(dedup.values()))


def _iso_from_days_ago(days: int, today: date | None = None) -> str:
    today = today or date.today()
    return (today - timedelta(days=days)).isoformat()


def collect_papers(*, config: PaperSearchConfig, lookback_days: int = 14) -> list[Paper]:
    from_date = _iso_from_days_ago(lookback_days)
    candidates: list[Paper] = []
    for journal in config.journals:
        for query in config.search_queries:
            try:
                candidates.extend(_query_crossref(journal, query, from_date=from_date))
            except Exception:
                continue
    return _apply_filters(candidates, config)
