from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from .content_review import generate_paper_review
from .content_trends import generate_trends_markdown
from .index_update import update_indexes
from .news_collect import collect_news
from .paper_collect import collect_papers
from .settings import load_paper_queries, load_site_config, load_sources, load_topics, repo_root
from .slugutil import slugify
from .svg_templates import render_svg
from .timeutil import draft_context, now_in_timezone
from .topics import classify_text
from .mdutil import ensure_contains, ensure_frontmatter


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _latest_copy(src: Path, latest_path: Path) -> None:
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def _build_email_preview(*, ctx, kind: str, ko_path: str, en_path: str, linkedin_ko_path: str, linkedin_en_path: str, errors: list[str]) -> str:
    lines = [
        "# GitBook 업로드 미리보기",
        "",
        f"- 날짜: {ctx.date_str} ({ctx.weekday})",
        f"- 타입: {kind}",
        f"- PR: {PULL_REQUEST_URL_PLACEHOLDER}",
        "",
        "## 생성 파일",
        f"- KO: {ko_path}",
        f"- EN: {en_path}",
        "",
        "## LinkedIn 미리보기 (KO)",
        f"(파일: {linkedin_ko_path})",
        "```",
        Path(repo_root(), linkedin_ko_path).read_text(encoding='utf-8').strip(),
        "```",
        "",
        "## LinkedIn 미리보기 (EN)",
        f"(파일: {linkedin_en_path})",
        "```",
        Path(repo_root(), linkedin_en_path).read_text(encoding='utf-8').strip(),
        "```",
    ]
    if errors:
        lines += ["", "## 수집 경고", *[f"- {e}" for e in errors]]
    lines += [
        "",
        "## 승인/게시 방법",
        "- PR 내용을 확인한 뒤 **Merge**하면 GitBook에 게시되고, LinkedIn도 자동 포스트됩니다.",
        "",
    ]
    return "\n".join(lines)


PULL_REQUEST_URL_PLACEHOLDER = "{PULL_REQUEST_URL}"


def main() -> int:
    cfg = load_site_config()
    root = repo_root()

    override_iso = os.getenv("RUN_DATETIME_OVERRIDE")
    now_local = now_in_timezone(cfg.timezone, override_iso=override_iso)
    ctx = draft_context(now_local)
    if not ctx:
        # Not a scheduled day; no-op.
        return 0

    topics = load_topics()

    previews_dir = root / "previews"
    pr_dir = previews_dir / "pr"
    linkedin_dir = previews_dir / "linkedin"
    email_dir = previews_dir / "email"

    if ctx.kind == "trends":
        sources = load_sources()
        items, errors = collect_news(sources=sources, now_utc=datetime.now(timezone.utc), lookback_days=cfg.news_lookback_days)

        grouped: dict[str, list[dict]] = defaultdict(list)
        for it in items:
            topic_slug = classify_text(f"{it.title} {it.summary}", topics)
            grouped[topic_slug].append(
                {
                    "title": it.title,
                    "url": it.url,
                    "published_date": it.published_at.date().isoformat(),
                    "source_name": it.source_name,
                    "entity_type": it.entity_type,
                    "snippet": it.summary[:240],
                }
            )

        # Apply per-topic cap.
        capped: dict[str, list[dict]] = {}
        for slug, rows in grouped.items():
            capped[slug] = rows[: cfg.news_per_topic_max]

        llm = generate_trends_markdown(
            date_str=ctx.date_str,
            topics=topics,
            items_by_topic=dict(capped),
            gitbook_base_url=cfg.gitbook_base_url,
        )

        ko_rel = f"ko/trends/{ctx.date_str}.md"
        en_rel = f"en/trends/{ctx.date_str}.md"
        ko_url = f"{cfg.gitbook_base_url}/{ko_rel.replace('.md','')}"
        en_url = f"{cfg.gitbook_base_url}/{en_rel.replace('.md','')}"
        active_topics = sorted(set(capped.keys()))
        ko_md = llm.ko_markdown.replace("{GITBOOK_URL}", ko_url)
        en_md = llm.en_markdown.replace("{GITBOOK_URL}", en_url)
        ko_md = ensure_frontmatter(
            ko_md,
            required={"date": ctx.date_str, "kind": "trends", "title": f"동향·소식 ({ctx.date_str})", "topics": active_topics, "gitbook_url": ko_rel},
        )
        en_md = ensure_frontmatter(
            en_md,
            required={"date": ctx.date_str, "kind": "trends", "title": f"Trends & News ({ctx.date_str})", "topics": active_topics, "gitbook_url": en_rel},
        )
        _write(root / ko_rel, ko_md)
        _write(root / en_rel, en_md)

        linkedin_ko_rel = f"previews/linkedin/{ctx.date_str}_ko.txt"
        linkedin_en_rel = f"previews/linkedin/{ctx.date_str}_en.txt"
        _write(root / linkedin_ko_rel, llm.linkedin_ko)
        _write(root / linkedin_en_rel, llm.linkedin_en)
        _latest_copy(root / linkedin_ko_rel, linkedin_dir / "latest_ko.txt")
        _latest_copy(root / linkedin_en_rel, linkedin_dir / "latest_en.txt")

        update_indexes(root)

        pr_title = f"[Draft] {ctx.date_str} (Trends)"
        pr_body = "\n".join(
            [
                f"Draft for {ctx.date_str} trends/news.",
                "",
                f"<!-- publisher:kind=trends -->",
                f"<!-- publisher:date={ctx.date_str} -->",
                f"<!-- publisher:gitbook_ko={ko_rel} -->",
                f"<!-- publisher:gitbook_en={en_rel} -->",
                f"<!-- publisher:linkedin_ko={linkedin_ko_rel} -->",
                f"<!-- publisher:linkedin_en={linkedin_en_rel} -->",
                "",
                "Merge = publish to GitBook + post to LinkedIn.",
            ]
        ).strip() + "\n"

        _write(pr_dir / f"{ctx.date_str}_title.txt", pr_title + "\n")
        _write(pr_dir / f"{ctx.date_str}_body.md", pr_body)
        _latest_copy(pr_dir / f"{ctx.date_str}_title.txt", pr_dir / "latest_title.txt")
        _latest_copy(pr_dir / f"{ctx.date_str}_body.md", pr_dir / "latest_body.md")

        # Email preview
        email_preview = _build_email_preview(
            ctx=ctx,
            kind="trends",
            ko_path=ko_rel,
            en_path=en_rel,
            linkedin_ko_path=linkedin_ko_rel,
            linkedin_en_path=linkedin_en_rel,
            errors=errors,
        )
        _write(email_dir / f"{ctx.date_str}.md", email_preview)
        _latest_copy(email_dir / f"{ctx.date_str}.md", email_dir / "latest.md")

        _write(previews_dir / "draft_meta.json", json.dumps({"ctx": asdict(ctx), "pr_title": pr_title}, ensure_ascii=False, indent=2) + "\n")
        return 0

    # paper_review
    queries = load_paper_queries()
    papers = collect_papers(queries=queries, lookback_days=cfg.paper_lookback_days)
    if not papers:
        raise RuntimeError("No papers collected. Check config/paper_queries.yaml or API availability.")

    deep = papers[0]
    rec = papers[1 : 1 + cfg.paper_recommend_count]
    llm = generate_paper_review(
        date_str=ctx.date_str,
        deep_paper=deep,
        recommended=rec,
        gitbook_base_url=cfg.gitbook_base_url,
    )

    slug = slugify(llm.slug or deep.title or "paper", fallback="paper")
    img_rel = f"assets/images/{ctx.date_str}/{slug}.svg"
    svg = render_svg(
        llm.svg_template,
        title=deep.title[:60],
        boxes=llm.svg_boxes or ["Design", "Build", "Test", "Learn"],
        footer=f"DOI: {deep.doi}" if deep.doi else "",
    )
    _write(root / img_rel, svg)

    ko_rel = f"ko/paper-reviews/{ctx.date_str}-{slug}.md"
    en_rel = f"en/paper-reviews/{ctx.date_str}-{slug}.md"
    ko_md = llm.ko_markdown.replace("{DATE}", ctx.date_str).replace("{SLUG}", slug)
    en_md = llm.en_markdown.replace("{DATE}", ctx.date_str).replace("{SLUG}", slug)
    ko_md = ko_md.replace("{GITBOOK_URL}", f"{cfg.gitbook_base_url}/{ko_rel.replace('.md','')}")
    en_md = en_md.replace("{GITBOOK_URL}", f"{cfg.gitbook_base_url}/{en_rel.replace('.md','')}")
    ko_md = ensure_frontmatter(
        ko_md,
        required={
            "date": ctx.date_str,
            "kind": "paper_review",
            "title": f"논문리뷰: {deep.title[:80]}",
            "doi": deep.doi,
            "gitbook_url": ko_rel,
        },
    )
    en_md = ensure_frontmatter(
        en_md,
        required={
            "date": ctx.date_str,
            "kind": "paper_review",
            "title": f"Paper review: {deep.title[:80]}",
            "doi": deep.doi,
            "gitbook_url": en_rel,
        },
    )
    image_snippet = f"![diagram]({img_rel})"
    ko_md = ensure_contains(ko_md, image_snippet, after_heading="FIRST_H1")
    en_md = ensure_contains(en_md, image_snippet, after_heading="FIRST_H1")
    _write(root / ko_rel, ko_md)
    _write(root / en_rel, en_md)

    linkedin_ko_rel = f"previews/linkedin/{ctx.date_str}_ko.txt"
    linkedin_en_rel = f"previews/linkedin/{ctx.date_str}_en.txt"
    _write(root / linkedin_ko_rel, llm.linkedin_ko)
    _write(root / linkedin_en_rel, llm.linkedin_en)
    _latest_copy(root / linkedin_ko_rel, linkedin_dir / "latest_ko.txt")
    _latest_copy(root / linkedin_en_rel, linkedin_dir / "latest_en.txt")

    update_indexes(root)

    pr_title = f"[Draft] {ctx.date_str} (Paper review)"
    pr_body = "\n".join(
        [
            f"Draft for {ctx.date_str} paper review.",
            "",
            f"<!-- publisher:kind=paper_review -->",
            f"<!-- publisher:date={ctx.date_str} -->",
            f"<!-- publisher:gitbook_ko={ko_rel} -->",
            f"<!-- publisher:gitbook_en={en_rel} -->",
            f"<!-- publisher:linkedin_ko={linkedin_ko_rel} -->",
            f"<!-- publisher:linkedin_en={linkedin_en_rel} -->",
            "",
            "Merge = publish to GitBook + post to LinkedIn.",
        ]
    ).strip() + "\n"

    _write(pr_dir / f"{ctx.date_str}_title.txt", pr_title + "\n")
    _write(pr_dir / f"{ctx.date_str}_body.md", pr_body)
    _latest_copy(pr_dir / f"{ctx.date_str}_title.txt", pr_dir / "latest_title.txt")
    _latest_copy(pr_dir / f"{ctx.date_str}_body.md", pr_dir / "latest_body.md")

    email_preview = _build_email_preview(
        ctx=ctx,
        kind="paper_review",
        ko_path=ko_rel,
        en_path=en_rel,
        linkedin_ko_path=linkedin_ko_rel,
        linkedin_en_path=linkedin_en_rel,
        errors=[],
    )
    _write(email_dir / f"{ctx.date_str}.md", email_preview)
    _latest_copy(email_dir / f"{ctx.date_str}.md", email_dir / "latest.md")

    _write(previews_dir / "draft_meta.json", json.dumps({"ctx": asdict(ctx), "pr_title": pr_title, "slug": slug}, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
