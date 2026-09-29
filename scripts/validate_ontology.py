#!/usr/bin/env python3
"""Validate the canonical anatomy model and append-only PUA registry rules."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^anatomy:[a-z0-9_]+$")
TOKEN_RE = re.compile(r"^:[a-z0-9_]+:$")
PUA_RE = re.compile(r"^E[0-9A-F]{3,5}$")


def fail(message: str) -> None:
    raise SystemExit(f"ontology validation failed: {message}")


def main() -> int:
    source = ROOT / "ontology/anatomy.yaml"
    data = yaml.safe_load(source.read_text())
    if not isinstance(data, dict) or data.get("namespace") != "anatomy":
        fail("namespace must be anatomy")
    objects = data.get("objects")
    if not isinstance(objects, list) or not objects:
        fail("objects must be a non-empty list")
    ids: set[str] = set()
    codepoints: dict[str, str] = {}
    tokens: set[str] = set()
    for item in objects:
        if not isinstance(item, dict):
            fail("every object must be a mapping")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier) or identifier in ids:
            fail(f"bad or duplicate object ID: {identifier}")
        ids.add(identifier)
        for key in ("label", "category", "system", "unicode_pua", "ligature", "shortcode", "sources", "external_ids", "glyph"):
            if key not in item:
                fail(f"{identifier} missing {key}")
        codepoint = str(item["unicode_pua"]).upper()
        if not PUA_RE.fullmatch(codepoint) or codepoint in codepoints:
            fail(f"bad or duplicate PUA codepoint: {codepoint}")
        codepoints[codepoint] = identifier
        if not TOKEN_RE.fullmatch(item["ligature"]) or item["ligature"] != item["shortcode"]:
            fail(f"ligature/shortcode mismatch: {identifier}")
        if item["ligature"] in tokens:
            fail(f"duplicate shortcode: {item['ligature']}")
        tokens.add(item["ligature"])
        if item["category"] not in {"bone", "organ", "tissue"}:
            fail(f"unknown category: {identifier}")
        if not item["external_ids"]:
            fail(f"no provenance ID: {identifier}")
        glyph = item["glyph"]
        if not all(glyph.get(key) for key in ("base", "monochrome", "color")):
            fail(f"incomplete glyph mapping: {identifier}")
        if item.get("laterality") not in (None, "left", "right"):
            fail(f"invalid laterality: {identifier}")
        if item["paired"] and not item["laterality_supported"]:
            fail(f"paired object must support laterality: {identifier}")
    registry = ROOT / "registry/codepoints.csv"
    if registry.exists():
        with registry.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            old = row.get("codepoint", "").upper()
            if old in codepoints and codepoints[old] != row.get("id"):
                fail(f"released codepoint reused: {old}")
    counts = {category: sum(item["category"] == category for item in objects) for category in ("bone", "organ", "tissue")}
    print(f"ontology OK: {len(objects)} objects ({counts['bone']} bones, {counts['organ']} organs, {counts['tissue']} tissues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

