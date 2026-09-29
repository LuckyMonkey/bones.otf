#!/usr/bin/env python3
"""Export deterministic monochrome/color preview PNGs from SVG masters."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SIZES = (16, 20, 24, 32, 48, 64, 128, 256)


def export(source: Path, target: Path, size: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "--width", str(size), "--height", str(size), "--output", str(target), str(source)], check=True)
    else:
        subprocess.run(["convert", "-background", "none", "-resize", f"{size}x{size}", str(source), str(target)], check=True)


def main() -> int:
    data = yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())
    count = 0
    for item in data["objects"]:
        name = item["id"].split(":", 1)[1]
        for variant, field in (("mono", "monochrome"), ("color", "color")):
            source = ROOT / item["glyph"][field]
            for size in SIZES:
                export(source, ROOT / "dist/png" / variant / f"{name}-{size}.png", size)
                count += 1
    print(f"exported {count} PNG previews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

