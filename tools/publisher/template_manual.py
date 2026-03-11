from __future__ import annotations

from .frontmatter import render_frontmatter
from .paper_collect import Paper
from .settings import Topic


def _topic_lookup(topics: list[Topic]) -> dict[str, Topic]:
    return {topic.slug: topic for topic in topics}


def build_trends_template(
    *,
    date_str: str,
    lang: str,
    gitbook_url: str,
    topics: list[Topic],
    active_topic_slugs: list[str],
    items_by_topic: dict[str, list[dict]],
    candidate_pack_rel: str,
) -> str:
    lookup = _topic_lookup(topics)
    if lang == "ko":
        title = f"동향·소식 ({date_str})"
        intro_heading = "## 도입"
        notes_heading = "## 작성 가이드"
        candidate_heading = "## 후보 링크"
        empty_message = "후보 없음"
    else:
        title = f"Trends & News ({date_str})"
        intro_heading = "## Intro"
        notes_heading = "## Writing guide"
        candidate_heading = "## Candidate links"
        empty_message = "No candidates"

    fm = {
        "title": title,
        "date": date_str,
        "kind": "trends",
        "topics": active_topic_slugs,
        "gitbook_url": gitbook_url,
    }

    lines = [
        render_frontmatter(fm).rstrip(),
        f"# {title}",
        "",
        notes_heading,
        "",
        f"- Candidate pack: `{candidate_pack_rel}`",
        "- Use ChatGPT web to turn the candidate pack into final prose.",
        "- Replace placeholders before merge.",
        "",
        intro_heading,
        "",
        "<Write 2-3 sentence introduction here>",
        "",
    ]

    for slug in active_topic_slugs:
        topic = lookup.get(slug)
        topic_title = topic.ko if lang == "ko" else topic.en if topic else slug
        lines += [f"## {topic_title}", "", "<Write this section here>", "", candidate_heading, ""]
        candidates = items_by_topic.get(slug) or []
        if not candidates:
            lines.append(f"- {empty_message}")
        for item in candidates:
            lines.append(f"- [{item['title']}]({item['url']}) | {item['source_name']} | {item['published_date']}")
        lines.append("")

    if not active_topic_slugs:
        lines += ["## Notes", "", "- No candidates found for this day.", ""]

    return "\n".join(lines).rstrip() + "\n"


def build_paper_review_template(
    *,
    date_str: str,
    lang: str,
    gitbook_url: str,
    candidate_pack_rel: str,
    topic_slug: str,
    main_paper: Paper | None,
    recommended: list[Paper],
) -> str:
    if lang == "ko":
        title = f"논문리뷰 ({date_str})"
        summary_label = "## 5줄 요약"
        novelty_label = "## 무엇이 새롭나"
        methods_label = "## 방법 개요"
        results_label = "## 결과/한계"
        rec_label = "## 추천 논문"
        empty_text = "후보 논문 없음"
    else:
        title = f"Paper Review ({date_str})"
        summary_label = "## 5-line summary"
        novelty_label = "## What's new"
        methods_label = "## Method overview"
        results_label = "## Results / limitations"
        rec_label = "## Recommended papers"
        empty_text = "No paper candidate"

    fm = {
        "title": title,
        "date": date_str,
        "kind": "paper_review",
        "topic": topic_slug,
        "doi": main_paper.doi if main_paper else "",
        "gitbook_url": gitbook_url,
    }

    lines = [
        render_frontmatter(fm).rstrip(),
        f"# {title}",
        "",
        "## Writing guide",
        "",
        f"- Candidate pack: `{candidate_pack_rel}`",
        "- Use ChatGPT web with the candidate pack and replace placeholders before merge.",
        "",
        summary_label,
        "",
        "<Write here>",
        "",
        novelty_label,
        "",
        "<Write here>",
        "",
        methods_label,
        "",
        "<Write here>",
        "",
        results_label,
        "",
        "<Write here>",
        "",
        rec_label,
        "",
    ]

    if main_paper:
        lines += [
            f"### Main candidate: {main_paper.title}",
            f"- Venue: {main_paper.venue}",
            f"- Date: {main_paper.published_date}",
            f"- DOI: {main_paper.doi}",
            f"- URL: {main_paper.url}",
            "",
        ]
    else:
        lines += [f"- {empty_text}", ""]

    for paper in recommended:
        lines += [f"- [{paper.title}]({paper.url}) | {paper.venue} | {paper.published_date}"]

    return "\n".join(lines).rstrip() + "\n"
