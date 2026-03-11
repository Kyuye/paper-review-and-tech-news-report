from __future__ import annotations

from typing import Any

from .frontmatter import render_frontmatter, split_frontmatter


def ensure_frontmatter(md: str, *, required: dict[str, Any]) -> str:
    doc = split_frontmatter(md or "")
    merged = dict(doc.frontmatter)
    merged.update(required)
    body = (doc.body or "").lstrip()
    return (render_frontmatter(merged) + body).rstrip() + "\n"


def ensure_contains(md: str, snippet: str, *, after_heading: str | None = None) -> str:
    if snippet in (md or ""):
        return (md or "").rstrip() + "\n"

    text = md or ""
    if after_heading:
        if after_heading == "FIRST_H1":
            lines = text.splitlines(True)
            for i, line in enumerate(lines):
                if line.lstrip().startswith("# "):
                    # Insert after this line.
                    prefix = "".join(lines[: i + 1])
                    suffix = "".join(lines[i + 1 :])
                    return (prefix + "\n" + snippet + "\n" + suffix).rstrip() + "\n"
        elif after_heading in text:
            idx = text.find(after_heading)
            # Insert right after the heading line.
            end = text.find("\n", idx)
            if end != -1:
                insert_at = end + 1
                return (text[:insert_at] + "\n" + snippet + "\n" + text[insert_at:]).rstrip() + "\n"
    return (snippet + "\n\n" + text).rstrip() + "\n"
