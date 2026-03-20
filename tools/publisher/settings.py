from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mini_yaml import load_yaml as _load_yaml_text


def repo_root() -> Path:
    # tools/publisher/settings.py -> tools/publisher -> tools -> repo
    return Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = _load_yaml_text(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping YAML at {path}")
    return data


@dataclass(frozen=True)
class Topic:
    slug: str
    ko: str
    en: str
    priority: int
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class Source:
    name: str
    feed_url: str
    entity_type: str
    default_topics: tuple[str, ...] = ()


@dataclass(frozen=True)
class SiteConfig:
    gitbook_base_url: str
    timezone: str
    news_lookback_days: int
    news_per_topic_max: int
    paper_lookback_days: int
    paper_deep_review_count: int
    paper_recommend_count: int


@dataclass(frozen=True)
class PaperJournal:
    name: str
    group: str


@dataclass(frozen=True)
class PaperSearchConfig:
    journals: tuple[PaperJournal, ...]
    search_queries: tuple[str, ...]
    synbio_keywords: tuple[str, ...]
    neural_keywords: tuple[str, ...]


def load_site_config() -> SiteConfig:
    root = repo_root()
    raw = load_yaml(root / "config" / "site.yaml")
    gitbook = raw.get("gitbook") or {}
    drafts = raw.get("drafts") or {}
    return SiteConfig(
        gitbook_base_url=str(gitbook.get("base_url") or "").rstrip("/"),
        timezone=str(gitbook.get("timezone") or "Asia/Seoul"),
        news_lookback_days=int(drafts.get("news_lookback_days") or 3),
        news_per_topic_max=int(drafts.get("news_per_topic_max") or 2),
        paper_lookback_days=int(drafts.get("paper_lookback_days") or 14),
        paper_deep_review_count=int(drafts.get("paper_deep_review_count") or 1),
        paper_recommend_count=int(drafts.get("paper_recommend_count") or 3),
    )


def load_topics() -> list[Topic]:
    root = repo_root()
    raw = load_yaml(root / "config" / "topics.yaml")
    topics = raw.get("topics") or []
    if not isinstance(topics, list):
        raise ValueError("config/topics.yaml: topics must be a list")
    out: list[Topic] = []
    for it in topics:
        if not isinstance(it, dict):
            continue
        out.append(
            Topic(
                slug=str(it.get("slug") or "").strip(),
                ko=str(it.get("ko") or "").strip(),
                en=str(it.get("en") or "").strip(),
                priority=int(it.get("priority") or 0),
                keywords=tuple(str(x) for x in (it.get("keywords") or []) if str(x).strip()),
            )
        )
    out = [t for t in out if t.slug]
    out.sort(key=lambda t: (t.priority, t.slug), reverse=True)
    return out


def load_sources() -> list[Source]:
    root = repo_root()
    raw = load_yaml(root / "config" / "sources.yaml")
    sources = raw.get("sources") or []
    if not isinstance(sources, list):
        raise ValueError("config/sources.yaml: sources must be a list")
    out: list[Source] = []
    for it in sources:
        if not isinstance(it, dict):
            continue
        out.append(
            Source(
                name=str(it.get("name") or "").strip(),
                feed_url=str(it.get("feed_url") or "").strip(),
                entity_type=str(it.get("entity_type") or "").strip(),
                default_topics=tuple(str(x) for x in (it.get("default_topics") or []) if str(x).strip()),
            )
        )
    return [s for s in out if s.name and s.feed_url]


def load_paper_search_config() -> PaperSearchConfig:
    root = repo_root()
    raw = load_yaml(root / "config" / "paper_queries.yaml")
    journals_raw = raw.get("journals") or []
    queries_raw = raw.get("search_queries") or []
    keywords_raw = raw.get("keywords") or {}

    if not isinstance(journals_raw, list):
        raise ValueError("config/paper_queries.yaml: journals must be a list")
    if not isinstance(queries_raw, list):
        raise ValueError("config/paper_queries.yaml: search_queries must be a list")
    if not isinstance(keywords_raw, dict):
        raise ValueError("config/paper_queries.yaml: keywords must be a mapping")

    journals: list[PaperJournal] = []
    for it in journals_raw:
        if not isinstance(it, dict):
            continue
        name = str(it.get("name") or "").strip()
        group = str(it.get("group") or "").strip()
        if name and group:
            journals.append(PaperJournal(name=name, group=group))

    search_queries = tuple(str(it).strip() for it in queries_raw if str(it).strip())
    synbio_keywords = tuple(str(it).strip() for it in (keywords_raw.get("synbio") or []) if str(it).strip())
    neural_keywords = tuple(str(it).strip() for it in (keywords_raw.get("neural") or []) if str(it).strip())

    if not journals:
        raise ValueError("config/paper_queries.yaml: at least one journal is required")
    if not search_queries:
        raise ValueError("config/paper_queries.yaml: at least one search query is required")
    if not synbio_keywords or not neural_keywords:
        raise ValueError("config/paper_queries.yaml: synbio and neural keywords are required")

    return PaperSearchConfig(
        journals=tuple(journals),
        search_queries=search_queries,
        synbio_keywords=synbio_keywords,
        neural_keywords=neural_keywords,
    )
