#!/usr/bin/env python3
"""Create compact webfont subsets while retaining shortcode shaping and color layers."""

from __future__ import annotations

from pathlib import Path

import yaml
from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
def unicode_inventory() -> list[int]:
    data = yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())
    return list(range(0x20, 0x7F)) + [int(item["unicode_pua"], 16) for item in data["objects"]]


def subset(source: Path, target: Path) -> None:
    font = TTFont(str(source))
    options = Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.glyph_names = True
    options.retain_gids = False
    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=unicode_inventory())
    subsetter.subset(font)
    font.recalcTimestamp = False
    font["head"].created = 2398377600
    font["head"].modified = 2398377600
    font.save(str(target))


def main() -> int:
    subset(ROOT / "dist/BONES.ttf", ROOT / "dist/BONES.woff2")              # quadratic TrueType (see build_font)
    subset(ROOT / "dist/BONES-Color.ttf", ROOT / "dist/BONES-Color.woff2")
    print("wrote compact BONES webfont subsets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
