from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from .content_manual import build_paper_review_pack, build_trends_pack
from .index_update import update_indexes
from .news_collect import NewsItem, collect_news
from .paper_collect import Paper, collect_papers
from .settings import load_paper_queries, load_site_config, load_sources, load_topics, repo_root
from .slugutil import slugify
from .template_manual import build_paper_review_template, build_trends_template
from .timeutil import draft_context, now_in_timezone
from .topics import classify_text


PULL_REQUEST_URL_PLACEHOLDER = "{PULL_REQUEST_URL}"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _latest_copy(src: Path, latest_path: Path) -> None:
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def _topic_slug_for_news(item: NewsItem, topics) -> str:
    slug = classify_text(f"{item.title} {item.summary}", topics)
    if slug and slug != "business":
        return slug
    if item.default_topics:
        return item.default_topics[0]
    return slug or "business"


def _topic_slug_for_paper(paper: Paper | None, topics) -> str:
    if paper is None:
        return "biofoundry_ai"
    slug = classify_text(f"{paper.title} {paper.abstract}", topics)
    return slug or "biofoundry_ai"


def _group_news_candidates(items: list[NewsItem], topics, limit_per_topic: int) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        slug = _topic_slug_for_news(item, topics)
        grouped[slug].append(
            {
                "title": item.title,
                "url": item.url,
                "published_date": item.published_at.date().isoformat(),
                "source_name": item.source_name,
                "entity_type": item.entity_type,
                "snippet": item.summary[:240],
            }
        )
    out: dict[str, list[dict]] = {}
    for slug, rows in grouped.items():
        out[slug] = rows[:limit_per_topic]
    ordered = [topic.slug for topic in topics if topic.slug in out]
    return {slug: out[slug] for slug in ordered}


def _build_notification_preview(
    *,
    date_str: str,
    kind: str,
    candidate_pack_rel: str,
    pr_target_paths: list[str],
    notification_body: str,
) -> str:
    lines = [
        f"# Candidate Pack Notification ({date_str})",
        "",
        notification_body.strip(),
        "",
        f"- Draft type: {kind}",
        f"- PR: {PULL_REQUEST_URL_PLACEHOLDER}",
        f"- Candidate pack: `{candidate_pack_rel}`",
        "",
        "## Target files",
    ]
    for path in pr_target_paths:
        lines.append(f"- `{path}`")
    lines += [
        "",
        "## Next step",
        "- Open the PR and the candidate pack.",
        "- Paste the candidate pack into ChatGPT web and draft the final KO/EN post.",
        "- Edit the target files in the PR, then merge to publish on GitBook.",
        "",
    ]
    return "\n".join(lines)


def _build_pr_body(*, date_str: str, kind: str, candidate_pack_rel: str, target_paths: list[str]) -> str:
    lines = [
        f"Candidate pack for {date_str} ({kind}).",
        "",
        f"- Candidate pack: `{candidate_pack_rel}`",
        "- This PR requires manual writing in ChatGPT web before merge.",
        "- GitBook publishing happens when this PR is merged.",
        "",
        "Target files:",
    ]
    for path in target_paths:
        lines.append(f"- `{path}`")
    return "\n".join(lines).rstrip() + "\n"


def _write_pr_metadata(*, root: Path, date_str: str, title: str, body: str, ctx_payload: dict) -> None:
    pr_dir = root / "previews" / "pr"
    previews_dir = root / "previews"
    _write(pr_dir / f"{date_str}_title.txt", title + "\n")
    _write(pr_dir / f"{date_str}_body.md", body)
    _latest_copy(pr_dir / f"{date_str}_title.txt", pr_dir / "latest_title.txt")
    _latest_copy(pr_dir / f"{date_str}_body.md", pr_dir / "latest_body.md")
    _write(previews_dir / "draft_meta.json", json.dumps(ctx_payload, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    cfg = load_site_config()
    root = repo_root()

    override_iso = os.getenv("RUN_DATETIME_OVERRIDE")
    now_local = now_in_timezone(cfg.timezone, override_iso=override_iso)
    ctx = draft_context(now_local)
    if not ctx:
        return 0

    topics = load_topics()
    previews_dir = root / "previews"
    notifications_dir = previews_dir / "notifications"

    if ctx.kind == "trends":
        sources = load_sources()
        items, errors = collect_news(
            sources=sources,
            now_utc=datetime.now(timezone.utc),
            lookback_days=cfg.news_lookback_days,
        )
        grouped = _group_news_candidates(items, topics, cfg.news_per_topic_max)
        active_topic_slugs = [topic.slug for topic in topics if topic.slug in grouped]

        candidate_pack_rel = f"previews/manual/{ctx.date_str}-trends.md"
        pack = build_trends_pack(
            date_str=ctx.date_str,
            topics=topics,
            items_by_topic=grouped,
            pack_rel=candidate_pack_rel,
        )
        _write(root / candidate_pack_rel, pack.markdown)

        ko_rel = f"ko/trends/{ctx.date_str}.md"
        en_rel = f"en/trends/{ctx.date_str}.md"
        _write(
            root / ko_rel,
            build_trends_template(
                date_str=ctx.date_str,
                lang="ko",
                gitbook_url=ko_rel,
                topics=topics,
                active_topic_slugs=active_topic_slugs,
                items_by_topic=grouped,
                candidate_pack_rel=candidate_pack_rel,
            ),
        )
        _write(
            root / en_rel,
            build_trends_template(
                date_str=ctx.date_str,
                lang="en",
                gitbook_url=en_rel,
                topics=topics,
                active_topic_slugs=active_topic_slugs,
                items_by_topic=grouped,
                candidate_pack_rel=candidate_pack_rel,
            ),
        )

        update_indexes(root)

        pr_title = f"[Draft] {ctx.date_str} (Trends candidates)"
        target_paths = [ko_rel, en_rel]
        pr_body = _build_pr_body(
            date_str=ctx.date_str,
            kind="trends",
            candidate_pack_rel=candidate_pack_rel,
            target_paths=target_paths,
        )
        _write_pr_metadata(
            root=root,
            date_str=ctx.date_str,
            title=pr_title,
            body=pr_body,
            ctx_payload={"ctx": asdict(ctx), "pr_title": pr_title},
        )

        notification_rel = f"previews/notifications/{ctx.date_str}.md"
        notification_text = _build_notification_preview(
            date_str=ctx.date_str,
            kind="trends",
            candidate_pack_rel=candidate_pack_rel,
            pr_target_paths=target_paths,
            notification_body="\n".join([pack.notification.strip(), *[f"- Warning: {err}" for err in errors]]).strip(),
        )
        _write(root / notification_rel, notification_text)
        _latest_copy(root / notification_rel, notifications_dir / "latest.md")
        return 0

    queries = load_paper_queries()
    papers = collect_papers(queries=queries, lookback_days=cfg.paper_lookback_days)
    main_paper = papers[0] if papers else None
    recommended = papers[1 : 1 + cfg.paper_recommend_count] if len(papers) > 1 else []

    candidate_pack_rel = f"previews/manual/{ctx.date_str}-paper-review.md"
    pack = build_paper_review_pack(
        date_str=ctx.date_str,
        deep_paper=main_paper,
        recommended=recommended,
        pack_rel=candidate_pack_rel,
    )
    _write(root / candidate_pack_rel, pack.markdown)

    topic_slug = _topic_slug_for_paper(main_paper, topics)
    slug = slugify(main_paper.title if main_paper else f"paper-review-{ctx.date_str}", fallback="paper-review")
    ko_rel = f"ko/paper-reviews/{ctx.date_str}-{slug}.md"
    en_rel = f"en/paper-reviews/{ctx.date_str}-{slug}.md"

    _write(
        root / ko_rel,
        build_paper_review_template(
            date_str=ctx.date_str,
            lang="ko",
            gitbook_url=ko_rel,
            candidate_pack_rel=candidate_pack_rel,
            topic_slug=topic_slug,
            main_paper=main_paper,
            recommended=recommended,
        ),
    )
    _write(
        root / en_rel,
        build_paper_review_template(
            date_str=ctx.date_str,
            lang="en",
            gitbook_url=en_rel,
            candidate_pack_rel=candidate_pack_rel,
            topic_slug=topic_slug,
            main_paper=main_paper,
            recommended=recommended,
        ),
    )

    update_indexes(root)

    pr_title = f"[Draft] {ctx.date_str} (Paper review candidates)"
    target_paths = [ko_rel, en_rel]
    pr_body = _build_pr_body(
        date_str=ctx.date_str,
        kind="paper_review",
        candidate_pack_rel=candidate_pack_rel,
        target_paths=target_paths,
    )
    _write_pr_metadata(
        root=root,
        date_str=ctx.date_str,
        title=pr_title,
        body=pr_body,
        ctx_payload={"ctx": asdict(ctx), "pr_title": pr_title, "slug": slug},
    )

    notification_rel = f"previews/notifications/{ctx.date_str}.md"
    notification_text = _build_notification_preview(
        date_str=ctx.date_str,
        kind="paper_review",
        candidate_pack_rel=candidate_pack_rel,
        pr_target_paths=target_paths,
        notification_body=pack.notification,
    )
    _write(root / notification_rel, notification_text)
    _latest_copy(root / notification_rel, notifications_dir / "latest.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
