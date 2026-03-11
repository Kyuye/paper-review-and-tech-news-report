from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class DraftContext:
    kind: str  # "trends" | "paper_review"
    date_str: str  # YYYY-MM-DD in local timezone
    weekday: str  # mon..sun


def now_in_timezone(tz_name: str, *, override_iso: str | None = None) -> datetime:
    tz = ZoneInfo(tz_name)
    if override_iso:
        parsed = datetime.fromisoformat(override_iso)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=tz)
        return parsed.astimezone(tz)
    return datetime.now(tz)


def draft_context(now_local: datetime) -> DraftContext | None:
    day_tokens = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
    weekday = day_tokens[now_local.weekday()]
    date_str = now_local.date().isoformat()

    if weekday in {"sat", "sun"}:
        return None
    if weekday in {"tue", "thu"}:
        return DraftContext(kind="paper_review", date_str=date_str, weekday=weekday)
    if weekday in {"mon", "wed", "fri"}:
        return DraftContext(kind="trends", date_str=date_str, weekday=weekday)
    return None

