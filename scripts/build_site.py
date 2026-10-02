#!/usr/bin/env python3
"""Assemble the small, deployable GitHub Pages artifact."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"


def copy_tree(source: Path, target: Path) -> None:
    shutil.copytree(source, target, dirs_exist_ok=True)


def main() -> int:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()

    # The root of Pages is the visual demo; the searchable specimen remains at /docs/.
    shutil.copy2(ROOT / "demo.html", SITE / "index.html")
    for filename in ("README.md", "CHANGELOG.md", "LICENSE"):
        shutil.copy2(ROOT / filename, SITE / filename)

    copy_tree(ROOT / "docs", SITE / "docs")
    copy_tree(ROOT / "glyphs/color", SITE / "glyphs/color")
    copy_tree(ROOT / "glyphs/assembly", SITE / "glyphs/assembly")   # the skeleton assembly's whole-region drawings
    copy_tree(ROOT / "sources", SITE / "sources")

    dist = SITE / "dist"
    dist.mkdir()
    for filename in ("BONES.woff2", "BONES-Color.woff2", "bones.css"):
        shutil.copy2(ROOT / "dist" / filename, dist / filename)

    print(f"wrote {SITE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
