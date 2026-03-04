from __future__ import annotations

import json
from dataclasses import dataclass

from .openai_client import chat_complete
from .paper_collect import Paper
from .jsonutil import loads_first_object


@dataclass(frozen=True)
class ReviewLLMResult:
    slug: str
    svg_template: str
    svg_boxes: list[str]
    ko_markdown: str
    en_markdown: str
    linkedin_ko: str
    linkedin_en: str


def generate_paper_review(
    *,
    date_str: str,
    deep_paper: Paper,
    recommended: list[Paper],
    gitbook_base_url: str,
) -> ReviewLLMResult:
    system = (
        "You are a cautious synthetic biology paper reviewer. "
        "Use ONLY provided metadata/abstracts. "
        "No overclaiming; mark uncertainty explicitly. "
        "Avoid any procedural lab steps; keep high-level and conceptual."
    )
    user = (
        "Task: Create TWO Markdown pages (Korean + English) for a paper review post, plus an SVG diagram plan.\n"
        f"Date: {date_str}\n"
        f"GitBook base URL: {gitbook_base_url}\n\n"
        "Deep review paper (metadata/abstract-only):\n"
        f"{json.dumps(deep_paper.__dict__, ensure_ascii=False)}\n\n"
        "Recommended 3 papers:\n"
        f"{json.dumps([p.__dict__ for p in recommended], ensure_ascii=False)}\n\n"
        "Output MUST be strict JSON with keys:\n"
        "- slug: url-safe slug for the deep paper (lowercase, hyphen, ascii if possible)\n"
        "- svg_template: one of [dbtl, gene_circuit, metabolic_pathway, cell_free, therapeutics]\n"
        "- svg_boxes: 4 short labels (<= 24 chars each) for the diagram boxes\n"
        "- ko_markdown: markdown string\n"
        "- en_markdown: markdown string\n"
        "- linkedin_ko: short LinkedIn post in Korean (<= 900 chars) with GitBook link placeholder {GITBOOK_URL}\n"
        "- linkedin_en: short LinkedIn post in English (<= 900 chars) with GitBook link placeholder {GITBOOK_URL}\n\n"
        "Rules for the Markdown pages:\n"
        "- Start with YAML frontmatter: date, kind=paper_review, title, topic (one of taxonomy slugs if confident else biofoundry_ai), doi, gitbook_url\n"
        "- Include the explanatory SVG via markdown image: ![diagram](assets/images/{DATE}/{SLUG}.svg)\n"
        "- Sections: 5-line summary, What's new, Method overview (high-level), Results (abstract-based), Limitations/counterpoints, Why it matters, Links.\n"
        "- End with 'Also worth reading' list for recommended papers.\n"
    )

    raw = chat_complete(system=system, user=user, temperature=0.2)
    data = loads_first_object(raw)
    return ReviewLLMResult(
        slug=str(data["slug"]).strip(),
        svg_template=str(data["svg_template"]).strip(),
        svg_boxes=[str(x).strip() for x in (data.get("svg_boxes") or [])][:4],
        ko_markdown=str(data["ko_markdown"]).strip() + "\n",
        en_markdown=str(data["en_markdown"]).strip() + "\n",
        linkedin_ko=str(data["linkedin_ko"]).strip() + "\n",
        linkedin_en=str(data["linkedin_en"]).strip() + "\n",
    )
