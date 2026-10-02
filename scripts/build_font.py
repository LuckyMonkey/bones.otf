#!/usr/bin/env python3
"""Compile BONES SVG masters into outline and COLRv1 OpenType fonts."""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

import yaml
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path.parser import parse_path
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = re.compile(r'<path\b([^>]*)\bd="([^"]+)"([^>]*)/?>')
FILL = re.compile(r'\bfill="([#A-Fa-f0-9]+)"')
ROLE = re.compile(r'\bdata-role="([a-z]+)"')
UPM = 2048


def objects() -> list[dict]:
    return yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())["objects"]


def project_version() -> str:
    return str(yaml.safe_load((ROOT / "project.yaml").read_text())["version"])


def svg_paths(path: Path) -> list[tuple[str, str, str]]:
    text = path.read_text(encoding="utf-8")
    result = []
    for match in SVG_PATH.finditer(text):
        attributes = match.group(1) + match.group(3)
        fill = FILL.search(attributes)
        role = ROLE.search(attributes)
        result.append((match.group(2), fill.group(1) if fill else "#17232b", role.group(1) if role else "body"))
    if not result:
        raise SystemExit(f"no path data in {path}")
    return result


CUBIC = False   # the CFF pass keeps Gray's cubic curves as drawn; the TrueType pass converts them


def glyph_from_paths(font: TTFont, paths: list[tuple[str, str, str]], knockouts: bool = False):
    """A TrueType glyph: Gray's cubic curves converted to quadratics (browsers reject the cubic-glyf extension).
    An engraving dense enough to pass TrueType's 65,535-point limit is converted with a looser tolerance."""
    for max_err in (1.0, 2.5, 6.0, 15.0):
        pen = TTGlyphPen(font.getGlyphSet())
        quad = pen if CUBIC else Cu2QuPen(pen, max_err=max_err * UPM / 1000, reverse_direction=False)
        transformed = TransformPen(quad, (UPM / 1000, 0, 0, -(UPM / 1000), 0, UPM))
        for data, _fill, role in paths:
            target = ReverseContourPen(transformed) if knockouts and role == "detail" else transformed
            parse_path(data, target)
        glyph = pen.glyph()
        if glyph.numberOfContours <= 0 or len(glyph.coordinates) < 60000:
            break
    glyph.recalcBounds(font["glyf"])
    return glyph


def add_outline_glyph(font: TTFont, name: str, paths: list[tuple[str, str, str]], advance: int = UPM, knockouts: bool = False) -> None:
    glyph = glyph_from_paths(font, paths, knockouts=knockouts)
    font["glyf"].glyphs[name] = glyph
    font["hmtx"].metrics[name] = (advance, 0)


def prepare_font() -> TTFont:
    font = TTFont(str(ROOT / "font/sources/DejaVuSans.ttf"))
    font.flavor = None
    font.recalcTimestamp = False
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
    font["name"].setName(f"Version {project_version()}", 5, 3, 1, 0x409)
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
        svg_path = ROOT / item["glyph"]["color" if color else "monochrome"]
        paths = svg_paths(svg_path)
        # Gray plate derivatives are already complete dark linework.  Their
        # small detail paths must remain ink in mono mode; reversing them into
        # holes would turn engraved hatching into accidental cut-outs.
        is_trace = 'data-source="gray-anatomy"' in svg_path.read_text(encoding="utf-8")
        add_outline_glyph(font, glyph_name, paths, knockouts=not color and not is_trace)
        order.append(glyph_name)
        if color:
            # COLRv1 layers are glyph references. Grouping the engraved paths
            # by fill keeps the detailed trace intact without creating one
            # TrueType glyph for every hatch contour (which can exceed the
            # 65,535 glyph limit on large anatomical plates).
            grouped: dict[str, list[tuple[str, str, str]]] = {}
            for path_data in paths:
                grouped.setdefault(path_data[1], []).append(path_data)
            layers = []
            for index, (color_value, grouped_paths) in enumerate(grouped.items()):
                layer_name = f"{glyph_name}_layer{index}"
                add_outline_glyph(font, layer_name, grouped_paths)
                order.append(layer_name)
                layers.append((layer_name, color_value))
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


def cff_font(font: TTFont, ps_name: str) -> TTFont:
    """Convert the finished TrueType outline font to a real CFF OpenType font."""
    buffer = BytesIO()
    font.flavor = None
    font.save(buffer)
    buffer.seek(0)
    converted = TTFont(buffer)
    glyph_set = converted.getGlyphSet()
    char_strings = {}
    for glyph_name in converted.getGlyphOrder():
        pen = T2CharStringPen(converted["head"].unitsPerEm, glyph_set)
        glyph_set[glyph_name].draw(pen)
        char_strings[glyph_name] = pen.getCharString()
    del converted["glyf"]
    del converted["loca"]
    converted["maxp"].tableVersion = 0x00005000
    builder = FontBuilder(converted["head"].unitsPerEm, isTTF=False)
    builder.font = converted
    builder.setupCFF(ps_name, {"FullName": ps_name, "FamilyName": ps_name, "Weight": "Regular"}, char_strings, {})
    converted.sfntVersion = "OTTO"
    converted.recalcTimestamp = False
    return converted


def save_variants(font: TTFont, stem: str) -> None:
    out = ROOT / "dist"
    out.mkdir(parents=True, exist_ok=True)
    font.flavor = None
    if CUBIC:     # the CFF font, straight from the cubic outlines (converting the quadratics back bloats charstrings)
        cff_font(font, f"{stem}-Regular").save(str(out / f"{stem}.otf"))
        return
    font.save(str(out / f"{stem}.ttf"))
    font.flavor = "woff2"             # the web font: quadratic TrueType, which browsers' sanitizer accepts
    font.save(str(out / f"{stem}.woff2"))
    font.flavor = None


def main() -> int:
    global CUBIC
    for CUBIC in (True, False):
        build(objects())
    print(f"built monochrome and COLRv1 color fonts for {len(objects())} anatomical glyphs (CFF cubic + TrueType quadratic)")
    return 0


def build(items) -> None:
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


if __name__ == "__main__":
    raise SystemExit(main())
