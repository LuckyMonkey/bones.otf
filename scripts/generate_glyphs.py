#!/usr/bin/env python3
"""Generate deterministic mono/color SVG masters from the design table."""

from __future__ import annotations

import html
from pathlib import Path

import yaml

from glyph_designs import DESIGNS


ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "glyphs/gray-trace"


def anatomy() -> dict:
    return yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())


MONO_INK = "#17232b"
MONO_PAPER = "#f4f0e8"
BASE_FILLS = {parts[0][1] for parts in DESIGNS.values()}


def mono_parts(parts: list[tuple[str, str]]) -> list[tuple[str, str, str]]:
    """Keep body/detail roles visible in mono masters instead of flattening color."""
    result = []
    for index, (data, fill) in enumerate(parts):
        role = "body" if index == 0 or fill in BASE_FILLS else "detail"
        result.append((data, MONO_INK if role == "body" else MONO_PAPER, role))
    return result


def write_svg(path: Path, label: str, parts: list[tuple[str, str]], color: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    elements = []
    role_parts = [(data, fill, "body" if index == 0 else "detail") for index, (data, fill) in enumerate(parts)] if color else mono_parts(parts)
    for data, fill, role in role_parts:
        elements.append(f'  <path d="{html.escape(data, quote=True)}" fill="{fill}" data-role="{role}"/>')
    text = "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" role="img" aria-labelledby="title">',
        f"  <title id=\"title\">{html.escape(label)}</title>",
        '  <g fill-rule="evenodd" clip-rule="evenodd">',
        *elements,
        "  </g>",
        "</svg>",
        "",
    ])
    path.write_text(text, encoding="utf-8")


def write_trace_svg(path: Path, label: str, trace_path: Path, color: bool) -> None:
    """Install a source-derived Gray plate trace as a glyph master."""
    text = trace_path.read_text(encoding="utf-8")
    text = text.replace("<title id=\"title\">Gray's Anatomy plate derivative: ", '<title id="title">')
    title_end = text.find("</title>")
    if title_end < 0:
        raise SystemExit(f"trace master has no title: {trace_path}")
    title_start = text.find('<title id="title">') + len('<title id="title">')
    text = text[:title_start] + html.escape(label) + text[title_end:]
    if not color:
        text = text.replace('fill="#b4384c"', f'fill="{MONO_INK}"')
        # the mono glyph is Gray's ink alone; the paper silhouette is the color font's under-layer
        text = "\n".join(line for line in text.splitlines() if 'data-layer="paper"' not in line) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    data = anatomy()
    for item in data["objects"]:
        base = item["glyph"]["base"]
        # each object's own Gray figure (scripts/trace_gray_figures.py); organs fall back to their base trace
        trace_path = TRACE_DIR / f"{item['id'].split(':', 1)[1]}.svg"
        if not trace_path.is_file():
            trace_path = TRACE_DIR / f"{base}.svg"
        if trace_path.is_file():
            write_trace_svg(ROOT / item["glyph"]["monochrome"], item["label"], trace_path, color=False)
            write_trace_svg(ROOT / item["glyph"]["color"], item["label"], trace_path, color=True)
            continue
        if base not in DESIGNS:
            raise SystemExit(f"missing design for {item['id']}: {base}")
        parts = DESIGNS[base]
        write_svg(ROOT / item["glyph"]["monochrome"], item["label"], parts, color=False)
        write_svg(ROOT / item["glyph"]["color"], item["label"], parts, color=True)
    print(f"generated {len(data['objects'])} monochrome and color SVG masters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
