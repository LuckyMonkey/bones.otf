#!/usr/bin/env python3
"""Compile BONES SVG masters into outline and COLRv1 OpenType fonts."""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path.parser import parse_path
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = re.compile(r'<path\b([^>]*)\bd="([^"]+)"([^>]*)/?>')
FILL = re.compile(r'\bfill="([#A-Fa-f0-9]+)"')
UPM = 2048


def objects() -> list[dict]:
    return yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())["objects"]


def svg_paths(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    result = []
    for match in SVG_PATH.finditer(text):
        attributes = match.group(1) + match.group(3)
        fill = FILL.search(attributes)
        result.append((match.group(2), fill.group(1) if fill else "#17232b"))
    if not result:
        raise SystemExit(f"no path data in {path}")
    return result


def glyph_from_paths(font: TTFont, paths: list[tuple[str, str]]):
    pen = TTGlyphPen(font.getGlyphSet())
    transformed = TransformPen(pen, (UPM / 1000, 0, 0, -(UPM / 1000), 0, UPM))
    for data, _fill in paths:
        parse_path(data, transformed)
    glyph = pen.glyph()
    glyph.recalcBounds(font["glyf"])
    return glyph


def add_outline_glyph(font: TTFont, name: str, paths: list[tuple[str, str]], advance: int = UPM) -> None:
    glyph = glyph_from_paths(font, paths)
    font["glyf"].glyphs[name] = glyph
    font["hmtx"].metrics[name] = (advance, 0)


def prepare_font() -> TTFont:
    font = TTFont(str(ROOT / "font/sources/DejaVuSans.ttf"))
    font.flavor = None
    if "GSUB" in font:
        del font["GSUB"]
    # Fixed Macintosh-epoch timestamps keep binaries reproducible without the
    # low-timestamp warning emitted for zero-valued head fields.
    font["head"].created = 2398377600
    font["head"].modified = 2398377600
    font["head"].fontRevision = 1.0
    replace_ids = {1, 2, 3, 4, 5, 6, 10, 16, 17, 18}
    font["name"].names = [record for record in font["name"].names if record.nameID not in replace_ids]
    font["name"].setName("BONES", 1, 3, 1, 0x409)
    font["name"].setName("Regular", 2, 3, 1, 0x409)
    font["name"].setName("BONES", 4, 3, 1, 0x409)
    font["name"].setName("BONES-Regular", 6, 3, 1, 0x409)
    font["name"].setName("BONES anatomical symbol system", 10, 3, 1, 0x409)
    font["name"].setName("Version 0.1.0", 5, 3, 1, 0x409)
    return font


def add_feature(font: TTFont, items: list[dict]) -> None:
    cmap = font.getBestCmap()
    lines = ["languagesystem DFLT dflt;", "feature liga {"]
    for item in items:
        sequence = []
        for character in item["ligature"]:
            glyph_name = cmap.get(ord(character))
            if glyph_name is None:
                raise SystemExit(f"base font has no component for {character!r}")
            sequence.append(glyph_name)
        output = "anatomy_" + item["id"].split(":", 1)[1]
        lines.append(f"  sub {' '.join(sequence)} by {output};")
    lines.extend(["} liga;", ""])
    feature_file = ROOT / "font/sources/ligatures.fea"
    feature_file.write_text("\n".join(lines), encoding="utf-8")
    addOpenTypeFeatures(font, str(feature_file), tables=["GSUB"])


def add_anatomical_glyphs(font: TTFont, items: list[dict], color: bool = False) -> dict[str, list[str]]:
    order = font.getGlyphOrder()
    color_layers: dict[str, list[str]] = {}
    for item in items:
        glyph_name = "anatomy_" + item["id"].split(":", 1)[1]
        paths = svg_paths(ROOT / item["glyph"]["color" if color else "monochrome"])
        add_outline_glyph(font, glyph_name, paths)
        order.append(glyph_name)
        if color:
            layers = []
            for index, path_data in enumerate(paths):
                layer_name = f"{glyph_name}_layer{index}"
                add_outline_glyph(font, layer_name, [path_data])
                order.append(layer_name)
                layers.append((layer_name, path_data[1]))
            color_layers[glyph_name] = layers
    font.setGlyphOrder(order)
    return color_layers


def update_cmap(font: TTFont, items: list[dict]) -> None:
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap = {codepoint: name for codepoint, name in table.cmap.items() if not 0xE000 <= codepoint <= 0xF8FF}
    for item in items:
        name = "anatomy_" + item["id"].split(":", 1)[1]
        codepoint = int(item["unicode_pua"], 16)
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap[codepoint] = name


def rgba(hex_color: str) -> tuple[float, float, float, float]:
    value = hex_color.lstrip("#")
    if len(value) == 3:
        value = "".join(character * 2 for character in value)
    return tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4)) + (1.0,)


def add_color(font: TTFont, layers: dict[str, list[tuple[str, str]]]) -> None:
    palette_colors: list[str] = []
    for entries in layers.values():
        for _glyph, color in entries:
            if color not in palette_colors:
                palette_colors.append(color)
    color_index = {color: index for index, color in enumerate(palette_colors)}
    color_glyphs = {}
    for base, entries in layers.items():
        color_glyphs[base] = {
            "Format": 1,
            "Layers": [
                {
                    "Format": 10,
                    "Paint": {"Format": 2, "PaletteIndex": color_index[color], "Alpha": 1.0},
                    "Glyph": glyph_name,
                }
                for glyph_name, color in entries
            ],
        }
    font["COLR"] = buildCOLR(color_glyphs, version=1, glyphMap=font.getReverseGlyphMap())
    font["CPAL"] = buildCPAL([[rgba(color) for color in palette_colors]])


def save_variants(font: TTFont, stem: str) -> None:
    out = ROOT / "dist"
    out.mkdir(parents=True, exist_ok=True)
    for suffix, flavor in ((".ttf", None), (".otf", None), (".woff2", "woff2")):
        font.flavor = flavor
        font.save(str(out / f"{stem}{suffix}"))
    font.flavor = None


def main() -> int:
    items = objects()
    mono = prepare_font()
    add_anatomical_glyphs(mono, items, color=False)
    update_cmap(mono, items)
    add_feature(mono, items)
    save_variants(mono, "BONES")

    color = prepare_font()
    layers = add_anatomical_glyphs(color, items, color=True)
    update_cmap(color, items)
    add_feature(color, items)
    add_color(color, layers)
    color["name"].names = [record for record in color["name"].names if record.nameID not in {1, 4, 6}]
    color["name"].setName("BONES Color", 1, 3, 1, 0x409)
    color["name"].setName("BONES Color", 4, 3, 1, 0x409)
    color["name"].setName("BONES Color-Regular", 6, 3, 1, 0x409)
    save_variants(color, "BONES-Color")
    print(f"built monochrome and COLRv1 color fonts for {len(items)} anatomical glyphs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
