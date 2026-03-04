from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .frontmatter import split_frontmatter, render_frontmatter


@dataclass(frozen=True)
class PostRef:
    path: Path
    date_str: str
    title: str
    topics: tuple[str, ...]
    kind: str | None
    url_hint: str | None


def _scan_posts(root: Path) -> list[PostRef]:
    out: list[PostRef] = []
    for md_path in list(root.glob("ko/trends/*.md")) + list(root.glob("ko/paper-reviews/*.md")) + list(
        root.glob("en/trends/*.md")
    ) + list(root.glob("en/paper-reviews/*.md")):
        if md_path.name.lower() == "readme.md":
            continue
        text = md_path.read_text(encoding="utf-8")
        doc = split_frontmatter(text)
        fm = doc.frontmatter
        date_str = str(fm.get("date") or md_path.stem[:10])
        title = str(fm.get("title") or md_path.stem)
        topics_raw = fm.get("topics")
        topics: tuple[str, ...] = ()
        if isinstance(topics_raw, list):
            topics = tuple(str(x).strip() for x in topics_raw if str(x).strip())
        elif isinstance(fm.get("topic"), str):
            topics = (str(fm.get("topic")).strip(),)
        kind = fm.get("kind") or None
        url_hint = fm.get("gitbook_url") or None
        out.append(PostRef(path=md_path, date_str=date_str, title=title, topics=topics, kind=kind, url_hint=url_hint))
    out.sort(key=lambda r: (r.date_str, str(r.path)), reverse=True)
    return out


def update_indexes(root: Path) -> None:
    posts = _scan_posts(root)
    _update_section_index(root / "ko" / "trends" / "README.md", posts, prefix="ko/trends/", title="동향·소식")
    _update_section_index(root / "ko" / "paper-reviews" / "README.md", posts, prefix="ko/paper-reviews/", title="논문리뷰")
    _update_section_index(root / "en" / "trends" / "README.md", posts, prefix="en/trends/", title="Trends & News")
    _update_section_index(root / "en" / "paper-reviews" / "README.md", posts, prefix="en/paper-reviews/", title="Paper Reviews")
    _update_field_pages(root, posts)


def _update_section_index(path: Path, posts: list[PostRef], *, prefix: str, title: str) -> None:
    relevant = [p for p in posts if str(p.path).replace(str(path.parents[2]) + "/", "").startswith(prefix)]
    fm = {"title": title}
    lines = [f"# {title}", "", "## Latest", ""]
    for p in relevant[:60]:
        rel = str(p.path).replace(str(path.parents[2]) + "/", "")
        lines.append(f"- [{p.date_str}] [{p.title}]({rel})")
    content = render_frontmatter(fm) + "\n".join(lines).strip() + "\n"
    path.write_text(content, encoding="utf-8")


def _update_field_pages(root: Path, posts: list[PostRef]) -> None:
    # Field pages are per-language and keyed by "topic" in frontmatter of the post.
    for lang in ("ko", "en"):
        fields_dir = root / lang / "fields"
        for field_page in fields_dir.glob("*.md"):
            if field_page.name.lower() == "readme.md":
                continue
            text = field_page.read_text(encoding="utf-8")
            doc = split_frontmatter(text)
            topic_slug = str(doc.frontmatter.get("topic") or "").strip()
            if not topic_slug:
                continue
            title = str(doc.frontmatter.get("title") or field_page.stem)

            lines = [f"# {title}", "", "## Latest", ""]
            for p in posts:
                if topic_slug not in set(p.topics):
                    continue
                rel = str(p.path).replace(str(root) + "/", "")
                if not rel.startswith(f"{lang}/"):
                    continue
                lines.append(f"- [{p.date_str}] [{p.title}]({rel})")
                if len(lines) >= 2 + 3 + 1 + 25:
                    break
            if len(lines) <= 4:
                lines.append("- (No posts yet)")
            out = render_frontmatter({**doc.frontmatter, "title": title, "topic": topic_slug}) + "\n".join(lines).strip() + "\n"
            field_page.write_text(out, encoding="utf-8")
