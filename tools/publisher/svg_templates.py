from __future__ import annotations

import html


def _esc(s: str) -> str:
    return html.escape((s or "").strip())


def render_svg(template: str, *, title: str, boxes: list[str], footer: str = "") -> str:
    # Simple, GitBook-friendly SVG with fixed layout per template.
    template = (template or "").strip().lower()
    if template not in {"dbtl", "gene_circuit", "metabolic_pathway", "cell_free", "therapeutics"}:
        template = "dbtl"

    w, h = 960, 540
    title = _esc(title)
    footer = _esc(footer)
    boxes = [(_esc(b) or "…") for b in boxes][:6]
    while len(boxes) < 4:
        boxes.append("…")

    def rect(x: int, y: int, text: str) -> str:
        return (
            f'<rect x="{x}" y="{y}" rx="18" ry="18" width="220" height="90" fill="#0B1220" stroke="#2DD4BF" stroke-width="2"/>'
            f'<text x="{x+110}" y="{y+52}" text-anchor="middle" font-family="Inter, Arial, sans-serif" '
            f'font-size="18" fill="#E5E7EB">{text}</text>'
        )

    def arrow(x1: int, y1: int, x2: int, y2: int) -> str:
        return (
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#94A3B8" stroke-width="3" marker-end="url(#arrow)"/>'
        )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L0,6 L9,3 z" fill="#94A3B8"/>',
        "</marker>",
        "</defs>",
        '<rect x="0" y="0" width="960" height="540" fill="#020617"/>',
        f'<text x="40" y="56" font-family="Inter, Arial, sans-serif" font-size="28" fill="#F8FAFC">{title}</text>',
        '<text x="40" y="84" font-family="Inter, Arial, sans-serif" font-size="14" fill="#94A3B8">Abstract-based explanatory diagram (author-generated)</text>',
    ]

    if template == "dbtl":
        parts += [
            rect(90, 160, boxes[0]),
            rect(350, 160, boxes[1]),
            rect(610, 160, boxes[2]),
            rect(350, 300, boxes[3]),
            arrow(310, 205, 350, 205),
            arrow(570, 205, 610, 205),
            arrow(720, 250, 470, 300),
            arrow(350, 345, 200, 250),
        ]
    elif template == "gene_circuit":
        parts += [
            rect(90, 220, boxes[0]),
            rect(350, 220, boxes[1]),
            rect(610, 220, boxes[2]),
            arrow(310, 265, 350, 265),
            arrow(570, 265, 610, 265),
        ]
    elif template == "metabolic_pathway":
        parts += [
            rect(90, 220, boxes[0]),
            rect(350, 180, boxes[1]),
            rect(350, 300, boxes[2]),
            rect(610, 220, boxes[3]),
            arrow(310, 265, 350, 225),
            arrow(310, 265, 350, 345),
            arrow(570, 225, 610, 265),
            arrow(570, 345, 610, 265),
        ]
    elif template == "cell_free":
        parts += [
            rect(90, 220, boxes[0]),
            rect(350, 220, boxes[1]),
            rect(610, 220, boxes[2]),
            arrow(310, 265, 350, 265),
            arrow(570, 265, 610, 265),
        ]
    else:  # therapeutics
        parts += [
            rect(90, 220, boxes[0]),
            rect(350, 220, boxes[1]),
            rect(610, 220, boxes[2]),
            arrow(310, 265, 350, 265),
            arrow(570, 265, 610, 265),
        ]

    if footer:
        parts.append(
            f'<text x="40" y="510" font-family="Inter, Arial, sans-serif" font-size="14" fill="#94A3B8">{footer}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"

