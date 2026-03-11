from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .urlutil import canonicalize_url


USER_AGENT = "paper-review-and-tech-news-report/1.0 (metadata-only; contact: EMAIL_FROM)"


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


def _get_json(url: str, params: dict, timeout: int = 20) -> dict:
    qs = urlencode(params, doseq=True)
    full = f"{url}?{qs}" if qs else url
    req = Request(full, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def search_europepmc(query: str, *, from_date: str, page_size: int = 25) -> list[Paper]:
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    full_query = f"({query}) AND FIRST_PDATE:[{from_date} TO *]"
    params = {"query": full_query, "format": "json", "pageSize": page_size}
    data = _get_json(base_url, params)
    out: list[Paper] = []
    for it in (data.get("resultList") or {}).get("result", []) or []:
        doi = (it.get("doi") or "").strip()
        title = (it.get("title") or "").strip()
        abstract = (it.get("abstractText") or "").strip()
        published = (it.get("firstPublicationDate") or "")[:10]
        year = published[:4] if len(published) >= 4 else ""
        venue = (it.get("journalTitle") or "").strip() or (it.get("journalInfo", "") or "")
        authors = (it.get("authorString") or "").strip()
        url = ""
        if doi:
            url = f"https://doi.org/{doi}"
        else:
            src = (it.get("source") or "").strip()
            pid = (it.get("id") or "").strip()
            if src and pid:
                url = f"https://europepmc.org/article/{src}/{pid}"
        out.append(
            Paper(
                title=title,
                abstract=abstract,
                doi=doi,
                url=canonicalize_url(url),
                published_date=published,
                venue=venue,
                year=year,
                authors=authors,
                source="europepmc",
            )
        )
    return out


def _iso_from_days_ago(days: int, today: date | None = None) -> str:
    today = today or date.today()
    return (today - timedelta(days=days)).isoformat()


def collect_papers(*, queries: list[dict[str, str]], lookback_days: int = 14) -> list[Paper]:
    from_date = _iso_from_days_ago(lookback_days)
    all_items: list[Paper] = []
    for q in queries:
        try:
            all_items.extend(search_europepmc(q["query"], from_date=from_date, page_size=25))
        except Exception:
            continue

    # Dedupe by DOI if present else URL+title.
    dedup: dict[str, Paper] = {}
    for p in all_items:
        key = f"doi:{p.doi.lower()}" if p.doi else f"url:{p.url}|{p.title.lower()}"
        dedup[key] = p
    out = list(dedup.values())
    out.sort(key=lambda x: (x.published_date, x.doi, x.title), reverse=True)
    return out

