#!/usr/bin/env python3
"""Create compact webfont subsets while retaining shortcode shaping and color layers."""

from __future__ import annotations

from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
UNICODES = list(range(0x20, 0x7F)) + list(range(0xE000, 0xE023))


def subset(source: Path, target: Path) -> None:
    font = TTFont(str(source))
    options = Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.glyph_names = True
    options.retain_gids = False
    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=UNICODES)
    subsetter.subset(font)
    font.recalcTimestamp = False
    font["head"].created = 2398377600
    font["head"].modified = 2398377600
    font.save(str(target))


def main() -> int:
    subset(ROOT / "dist/BONES.ttf", ROOT / "dist/BONES.woff2")
    subset(ROOT / "dist/BONES-Color.ttf", ROOT / "dist/BONES-Color.woff2")
    print("wrote compact BONES webfont subsets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
