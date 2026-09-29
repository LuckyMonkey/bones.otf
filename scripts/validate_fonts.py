#!/usr/bin/env python3
"""Run FontTools-level integrity checks on generated font artifacts."""

from pathlib import Path

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    for filename in ("BONES.ttf", "BONES.otf", "BONES-Color.ttf", "BONES-Color.otf", "BONES.woff2", "BONES-Color.woff2"):
        font = TTFont(str(ROOT / "dist" / filename), checkChecksums=2)
        cmap = font.getBestCmap()
        pua = [codepoint for codepoint in cmap if 0xE000 <= codepoint <= 0xF8FF]
        if len(pua) != 35:
            raise SystemExit(f"{filename}: expected 35 PUA mappings, got {len(pua)}")
        if filename.startswith("BONES-Color") and "COLR" not in font:
            raise SystemExit(f"{filename}: missing COLR")
    print("font validation OK: checksums, cmap, PUA, and color tables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

