from __future__ import annotations

from dataclasses import dataclass

from .paper_collect import Paper
from .settings import Topic


@dataclass(frozen=True)
class ManualPack:
    markdown: str
    notification: str


def _topic_map(topics: list[Topic]) -> dict[str, Topic]:
    return {topic.slug: topic for topic in topics}


def build_trends_pack(
    *,
    date_str: str,
    topics: list[Topic],
    items_by_topic: dict[str, list[dict]],
    pack_rel: str,
) -> ManualPack:
    topic_lookup = _topic_map(topics)
    lines = [
        f"# Trends Candidate Pack ({date_str})",
        "",
        f"- Candidate pack path: `{pack_rel}`",
        "- Purpose: paste this into ChatGPT web to draft GitBook posts manually.",
        "",
        "## Korean prompt",
        "```text",
        "역할: 너는 합성생물학 전문 에디터다.",
        f"목표: 아래 후보 링크를 바탕으로 {date_str} 동향 글을 한국어로 작성해라.",
        "형식:",
        "- 도입 2~3문장",
        "- 분야별 섹션",
        "- 각 섹션당 핵심 포인트 1~2개",
        "- 과장 금지, 링크에 없는 내용 추정 금지",
        "- 마지막에 오늘의 관찰 3줄 추가",
        "```",
        "",
        "## English prompt",
        "```text",
        "Role: You are a synthetic biology editor.",
        f"Goal: write an English trends post for {date_str} using the candidate links below.",
        "Format:",
        "- 2-3 sentence intro",
        "- field-by-field sections",
        "- 1-2 key points per section",
        "- avoid overclaiming; use only the provided snippets",
        "- end with 3 short observations",
        "```",
        "",
        "## Candidates by field",
        "",
    ]

    notification_lines = [
        f"GitBook candidate pack ready: {date_str} (trends)",
        f"- Candidate pack: `{pack_rel}`",
    ]

    shown = 0
    ordered_slugs = [topic.slug for topic in topics if topic.slug in items_by_topic]
    for slug in ordered_slugs:
        items = items_by_topic.get(slug) or []
        topic = topic_lookup.get(slug)
        title_ko = topic.ko if topic else slug
        title_en = topic.en if topic else slug
        lines += [f"## {title_ko} / {title_en}", ""]
        if not items:
            lines.append("- No candidates")
            lines.append("")
            continue
        for item in items:
            lines.append(
                f"- {item['title']} | {item['source_name']} | {item['published_date']} | {item['url']}"
            )
            if item.get("snippet"):
                lines.append(f"  - Snippet: {item['snippet']}")
            lines.append("")
            if shown < 5:
                notification_lines.append(f"- {title_ko}: {item['title']} ({item['source_name']})")
                shown += 1

    if shown == 0:
        notification_lines.append("- No strong candidates found")

    return ManualPack(markdown="\n".join(lines).rstrip() + "\n", notification="\n".join(notification_lines).rstrip() + "\n")


def build_paper_review_pack(
    *,
    date_str: str,
    deep_paper: Paper | None,
    recommended: list[Paper],
    pack_rel: str,
) -> ManualPack:
    lines = [
        f"# Paper Review Candidate Pack ({date_str})",
        "",
        f"- Candidate pack path: `{pack_rel}`",
        "- Purpose: paste this into ChatGPT web to draft a paper review manually.",
        "",
        "## Korean prompt",
        "```text",
        "역할: 너는 합성생물학 논문 리뷰 에디터다.",
        f"목표: 아래 메인 논문과 추천 논문을 바탕으로 {date_str} 논문리뷰 글을 한국어로 작성해라.",
        "형식:",
        "- 5줄 요약",
        "- 무엇이 새롭나",
        "- 방법 개요(고수준)",
        "- 결과/한계",
        "- 추천 논문 3편 짧은 코멘트",
        "- 초록/메타데이터 기반으로만 작성",
        "```",
        "",
        "## English prompt",
        "```text",
        "Role: You are a synthetic biology paper review editor.",
        f"Goal: write an English paper review for {date_str} using the main paper and recommended papers below.",
        "Format:",
        "- 5-line summary",
        "- what's new",
        "- high-level method overview",
        "- results/limitations",
        "- 3 short recommended-paper notes",
        "- use metadata/abstract only",
        "```",
        "",
    ]

    notification_lines = [
        f"GitBook candidate pack ready: {date_str} (paper review)",
        f"- Candidate pack: `{pack_rel}`",
    ]

    if deep_paper is None:
        lines += ["## Main candidate", "", "- No paper candidates found", ""]
        notification_lines.append("- No paper candidates found")
    else:
        lines += [
            "## Main candidate",
            "",
            f"- Title: {deep_paper.title}",
            f"- Venue: {deep_paper.venue}",
            f"- Date: {deep_paper.published_date}",
            f"- DOI: {deep_paper.doi}",
            f"- URL: {deep_paper.url}",
            f"- Authors: {deep_paper.authors}",
            "",
            "### Abstract",
            deep_paper.abstract or "(no abstract)",
            "",
        ]
        notification_lines.append(f"- Main: {deep_paper.title} ({deep_paper.venue})")

    lines += ["## Recommended papers", ""]
    if not recommended:
        lines.append("- No recommended papers")
    for paper in recommended:
        lines += [
            f"- {paper.title} | {paper.venue} | {paper.published_date} | {paper.url}",
            f"  - Abstract hint: {(paper.abstract or '(no abstract)')[:280]}",
            "",
        ]
        if len(notification_lines) < 5:
            notification_lines.append(f"- Rec: {paper.title}")

    return ManualPack(markdown="\n".join(lines).rstrip() + "\n", notification="\n".join(notification_lines).rstrip() + "\n")
