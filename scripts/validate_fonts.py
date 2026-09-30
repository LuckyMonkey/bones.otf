#!/usr/bin/env python3
"""Run FontTools-level integrity checks on generated font artifacts."""

from pathlib import Path

import yaml
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ontology = yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())
    expected_pua = len(ontology["objects"])
    for filename in ("BONES.ttf", "BONES.otf", "BONES-Color.ttf", "BONES-Color.otf", "BONES.woff2", "BONES-Color.woff2"):
        font = TTFont(str(ROOT / "dist" / filename), checkChecksums=2)
        cmap = font.getBestCmap()
        pua = [codepoint for codepoint in cmap if 0xE000 <= codepoint <= 0xF8FF]
        if len(pua) != expected_pua:
            raise SystemExit(f"{filename}: expected {expected_pua} PUA mappings, got {len(pua)}")
        if filename.startswith("BONES-Color") and "COLR" not in font:
            raise SystemExit(f"{filename}: missing COLR")
        if filename.endswith(".otf") and (font.sfntVersion != "OTTO" or "CFF " not in font):
            raise SystemExit(f"{filename}: expected CFF OpenType outlines")
    print("font validation OK: checksums, cmap, PUA, and color tables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
