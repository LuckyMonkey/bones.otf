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
    project = yaml.safe_load((ROOT / "project.yaml").read_text())
    if str(data.get("version")) != str(project.get("version")):
        fail("ontology version must match project.yaml")
    groups = data.get("groups")
    if not isinstance(groups, list) or not groups:
        fail("groups must be a non-empty list")
    group_ids: set[str] = set()
    for group in groups:
        identifier = group.get("id") if isinstance(group, dict) else None
        if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier) or identifier in group_ids:
            fail(f"bad or duplicate group ID: {identifier}")
        group_ids.add(identifier)
        if not group.get("label"):
            fail(f"group missing label: {identifier}")
    if "anatomy:human_body" not in group_ids:
        fail("groups must include anatomy:human_body")
    for group in groups:
        parent = group.get("parent")
        if parent is not None and parent not in group_ids:
            fail(f"unknown group parent {parent} for {group['id']}")
    objects = data.get("objects")
    if not isinstance(objects, list) or not objects:
        fail("objects must be a non-empty list")
    ids: set[str] = set()
    object_ids = {item.get("id") for item in objects if isinstance(item, dict)}
    codepoints: dict[str, str] = {}
    tokens: set[str] = set()
    for item in objects:
        if not isinstance(item, dict):
            fail("every object must be a mapping")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier) or identifier in ids:
            fail(f"bad or duplicate object ID: {identifier}")
        ids.add(identifier)
        for key in ("label", "category", "system", "unicode_pua", "ligature", "shortcode", "sources", "external_ids", "glyph", "review_required"):
            if key not in item:
                fail(f"{identifier} missing {key}")
        if not isinstance(item["review_required"], bool):
            fail(f"review_required must be boolean: {identifier}")
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
        if item.get("parent") not in object_ids | group_ids:
            fail(f"unknown parent {item.get('parent')} for {identifier}")
    registry = ROOT / "registry/codepoints.csv"
    if registry.exists():
        with registry.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        old_ids: dict[str, str] = {}
        old_codepoints: dict[str, str] = {}
        for row in rows:
            old = row.get("codepoint", "").upper().removeprefix("U+")
            old_id = row.get("id", "")
            if old_id in old_ids and old_ids[old_id] != old:
                fail(f"registry contains conflicting codepoints for {old_id}")
            if old in old_codepoints and old_codepoints[old] != old_id:
                fail(f"released codepoint reused: {old}")
            old_ids[old_id] = old
            old_codepoints[old] = old_id
        current_codepoints = {item["id"]: str(item["unicode_pua"]).upper() for item in objects}
        for old_id, old_codepoint in old_ids.items():
            if old_id not in ids:
                fail(f"released object disappeared: {old_id}")
            if current_codepoints[old_id] != old_codepoint:
                fail(f"released object moved codepoint: {old_id} ({old_codepoint})")
        for codepoint, identifier in old_codepoints.items():
            if codepoint in codepoints and codepoints[codepoint] != identifier:
                fail(f"released codepoint reused: {codepoint}")
    counts = {category: sum(item["category"] == category for item in objects) for category in ("bone", "organ", "tissue")}
    print(f"ontology OK: {len(objects)} objects ({counts['bone']} bones, {counts['organ']} organs, {counts['tissue']} tissues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
