#!/usr/bin/env python3
"""Check SVG masters for the stable canvas and path-only vector source rules."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SVG_RE = re.compile(r'<svg[^>]+viewBox="0 0 1000 1000"')
PATH_RE = re.compile(r'<path\b[^>]*\bd="[^"]+"')


def main() -> int:
    data = yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())
    checked = 0
    for item in data["objects"]:
        for key in ("monochrome", "color"):
            path = ROOT / item["glyph"][key]
            if not path.is_file():
                raise SystemExit(f"missing SVG: {path}")
            text = path.read_text(encoding="utf-8")
            if not SVG_RE.search(text) or not PATH_RE.search(text) or "<image" in text:
                raise SystemExit(f"invalid vector SVG: {path}")
            checked += 1
    print(f"SVG masters OK: {checked} vector files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

