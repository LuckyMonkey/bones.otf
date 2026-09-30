#!/usr/bin/env python3
"""Export deterministic monochrome/color preview PNGs from SVG masters."""

from __future__ import annotations

import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SIZES = (16, 20, 24, 32, 48, 64, 128, 256)


def rasterizer() -> str:
    for command in ("rsvg-convert", "magick", "convert"):
        if shutil.which(command):
            return command
    raise RuntimeError(
        "PNG export needs rsvg-convert or ImageMagick (magick/convert); "
        "install imagemagick and retry"
    )


def export(source: Path, target: Path, size: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    command = rasterizer()
    if command == "rsvg-convert":
        subprocess.run(["rsvg-convert", "--width", str(size), "--height", str(size), "--output", str(target), str(source)], check=True)
    else:
        subprocess.run([command, "-background", "none", "-resize", f"{size}x{size}", str(source), str(target)], check=True)


def main() -> int:
    data = yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())
    jobs = []
    for item in data["objects"]:
        name = item["id"].split(":", 1)[1]
        for variant, field in (("mono", "monochrome"), ("color", "color")):
            source = ROOT / item["glyph"][field]
            for size in SIZES:
                jobs.append((source, ROOT / "dist/png" / variant / f"{name}-{size}.png", size))
    workers = max(1, int(os.environ.get("BONES_PNG_WORKERS", os.cpu_count() or 4)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(lambda job: export(*job), jobs))
    count = len(jobs)
    print(f"exported {count} PNG previews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
