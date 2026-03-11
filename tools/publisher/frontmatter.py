from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

from .mini_yaml import dump_yaml_mapping, load_yaml


_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclass(frozen=True)
class FrontmatterDoc:
    frontmatter: dict[str, Any]
    body: str


def split_frontmatter(md: str) -> FrontmatterDoc:
    m = _FM_RE.match(md or "")
    if not m:
        return FrontmatterDoc(frontmatter={}, body=md or "")
    raw = m.group(1)
    fm = load_yaml(raw) or {}
    if not isinstance(fm, dict):
        fm = {}
    body = (md or "")[m.end() :]
    return FrontmatterDoc(frontmatter=fm, body=body)


def render_frontmatter(fm: dict[str, Any]) -> str:
    dumped = dump_yaml_mapping(fm).strip()
    return f"---\n{dumped}\n---\n\n"
