from __future__ import annotations

from dataclasses import dataclass

from .settings import Topic


@dataclass(frozen=True)
class TopicMatch:
    slug: str
    score: int


def classify_text(text: str, topics: list[Topic]) -> str:
    lower = (text or "").lower()
    best = TopicMatch(slug="business", score=0)
    for t in topics:
        hits = 0
        for kw in t.keywords:
            if kw.lower() in lower:
                hits += 1
        if hits <= 0:
            continue
        score = hits * 10 + int(t.priority)
        if score > best.score:
            best = TopicMatch(slug=t.slug, score=score)
    return best.slug if best.score > 0 else (topics[0].slug if topics else "business")

