from __future__ import annotations

import json
from dataclasses import dataclass

from .openai_client import chat_complete
from .settings import Topic
from .jsonutil import loads_first_object


@dataclass(frozen=True)
class TrendsLLMResult:
    ko_markdown: str
    en_markdown: str
    linkedin_ko: str
    linkedin_en: str


def generate_trends_markdown(
    *,
    date_str: str,
    topics: list[Topic],
    items_by_topic: dict[str, list[dict]],
    gitbook_base_url: str,
) -> TrendsLLMResult:
    topic_lookup = {t.slug: t for t in topics}
    payload = []
    for slug, items in items_by_topic.items():
        t = topic_lookup.get(slug)
        payload.append(
            {
                "topic_slug": slug,
                "topic_ko": t.ko if t else slug,
                "topic_en": t.en if t else slug,
                "items": items,
            }
        )

    system = (
        "You are a cautious synthetic biology news editor. "
        "Write concise, non-sensational summaries. "
        "Do not add claims not supported by provided snippets. "
        "Avoid procedural biological instructions; keep high-level."
    )
    user = (
        "Task: Generate TWO Markdown pages (Korean + English) for a daily synthetic biology trends/news report.\n"
        f"Date: {date_str}\n"
        f"GitBook base URL: {gitbook_base_url}\n\n"
        "Input is grouped by topic. Each item has: title, url, published_date, source_name, entity_type, snippet.\n\n"
        "Output MUST be strict JSON with keys:\n"
        "- ko_markdown: markdown string\n"
        "- en_markdown: markdown string\n"
        "- linkedin_ko: short LinkedIn post in Korean (<= 900 chars) with 3 highlights + GitBook link placeholder {GITBOOK_URL}\n"
        "- linkedin_en: short LinkedIn post in English (<= 900 chars) with 3 highlights + GitBook link placeholder {GITBOOK_URL}\n\n"
        "Rules for the Markdown pages:\n"
        "- Start with YAML frontmatter: date, kind=trends, title, topics=[...], gitbook_url\n"
        "- Then a short intro (2-3 lines)\n"
        "- For each topic section: heading + 1-2 bullets per item. Each bullet: Title (Source, date) — one-liner. Link.\n"
        "- Add '오늘의 관찰' (3 bullets) in KO and 'Observations' (3 bullets) in EN.\n"
        "- Add '다음에 볼 키워드' / 'Next keywords' (3 items).\n\n"
        "Here is the grouped input JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False)}\n"
    )

    raw = chat_complete(system=system, user=user, temperature=0.2)
    data = loads_first_object(raw)
    return TrendsLLMResult(
        ko_markdown=str(data["ko_markdown"]).strip() + "\n",
        en_markdown=str(data["en_markdown"]).strip() + "\n",
        linkedin_ko=str(data["linkedin_ko"]).strip() + "\n",
        linkedin_en=str(data["linkedin_en"]).strip() + "\n",
    )
