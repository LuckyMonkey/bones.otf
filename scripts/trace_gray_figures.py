#!/usr/bin/env python3
"""Trace Gray's Anatomy (1918) figures into BONES glyph masters: one bone, one figure, one glyph.

Each object uses the figure Gray drew of that bone (sources/gray-plates/figures.yaml: file, crop, mirror). The
engraving is kept as engraving - every hatch line becomes vector outlines - and only what is not the drawing is
removed:

    figure scan -> crop -> remove Gray's red attachment lines -> 4x upscale -> ink (dark, unsaturated)
                -> bone mask (close + fill + open: drops text labels and the leader lines pointing at the bone)
                -> ink inside the mask -> potrace (Bezier outlines) -> fit to the 1000-unit em, mirrored if asked

Output: glyphs/gray-trace/<object>.svg (mono ink + a paper-tint silhouette for the color font).

This is a source-art step (OpenCV + potracer):  ~/.venvs/trace/bin/python scripts/trace_gray_figures.py [names…]
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

import cv2
import numpy as np
import potrace
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "sources/gray-plates/raw/figures"
OUT = ROOT / "glyphs/gray-trace"
INK = "#17232b"
PAPER = "#efe3c8"
SCALE = 4


def load(spec: dict) -> np.ndarray:
    img = cv2.imread(str(FIG / spec["file"]), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise SystemExit(f"cannot read {spec['file']}")
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.shape[2] == 4:                                   # transparent PNG: composite on white
        a = img[:, :, 3:4] / 255.0
        img = (img[:, :, :3] * a + 255 * (1 - a)).astype(np.uint8)
    if "highlight" in spec:
        # Commons has versions of the hand plate with one family of bones in yellow; the pick-th yellow island
        # (left to right) is this bone: crop to it, and keep only the ink over it
        hi = cv2.imread(str(FIG / spec["highlight"]))
        b, g, r = [c.astype(int) for c in cv2.split(hi)]
        yellow = ((r > 190) & (g > 170) & (b < 120)).astype(np.uint8) * 255
        n, labels, stats, cent = cv2.connectedComponentsWithStats(yellow)
        islands = sorted([i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > 60], key=lambda i: cent[i][0])
        i = islands[spec["pick"]]
        x, y, w, h = stats[i, :4]
        m = 8
        x0, y0, x1, y1 = max(0, x - m), max(0, y - m), min(img.shape[1], x + w + m), min(img.shape[0], y + h + m)
        region = (labels == i).astype(np.uint8)[y0:y1, x0:x1] * 255
        spec["_region"] = cv2.dilate(region, np.ones((7, 7), np.uint8))
        return img[y0:y1, x0:x1]
    if "crop" in spec:
        x0, y0, x1, y1 = spec["crop"]
        img = img[y0:y1, x0:x1]
    return img


def text_boxes(gray: np.ndarray, spec: dict) -> list:
    """Gray's figures are labelled; the labels are not the bone. Tesseract finds the words (upright and sideways);
    only confident, word-like finds count. Returns boxes in source pixels."""
    import subprocess
    import tempfile
    boxes = []
    k = 2
    Ho, Wo = gray.shape
    for rot in (None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE):
        view = gray if rot is None else cv2.rotate(gray, rot)
        big = cv2.resize(view, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            cv2.imwrite(f.name, big)
            tsv = subprocess.run(["tesseract", f.name, "stdout", "--psm", "11", "tsv"], capture_output=True, text=True,
                                 env={**__import__("os").environ, "OMP_THREAD_LIMIT": "1"}).stdout   # the pool already uses every core
        H, W = view.shape
        for row in tsv.splitlines()[1:]:
            c = row.split("\t")
            if len(c) < 12 or not c[11].strip():
                continue
            word, conf = c[11].strip(), float(c[10])
            if conf < spec.get("ocr_conf", 25) or sum(ch.isalpha() for ch in word) < 2:
                continue
            x, y, w, h = (int(v) // k for v in c[6:10])
            if h > 40 or w > W * 0.5:
                continue
            pad = 2
            x0, y0, x1, y1 = x - pad, y - pad, x + w + pad, y + h + pad
            if rot is None:
                boxes.append((x0, y0, x1, y1))
            elif rot == cv2.ROTATE_90_CLOCKWISE:            # view(x, y) = src(y, Ho - 1 - x)
                boxes.append((y0, Ho - x1, y1, Ho - x0))
            else:                                            # view(x, y) = src(Wo - 1 - y, x)
                boxes.append((Wo - y1, x0, Wo - y0, x1))
    return boxes


def drop_letters(ink: np.ndarray, boxes: list) -> np.ndarray:
    """Inside a word's box, the pieces of ink that fit entirely in it are its letters: remove those, keep any line
    that runs through."""
    if not boxes:
        return ink
    n, labels, stats, _ = cv2.connectedComponentsWithStats(ink)
    out = ink.copy()
    for i in range(1, n):
        x, y, w, h = stats[i, :4]
        for (bx0, by0, bx1, by1) in boxes:
            if x >= bx0 * SCALE and y >= by0 * SCALE and x + w <= bx1 * SCALE and y + h <= by1 * SCALE:
                out[labels == i] = 0
                break
    return out


def ink_of(img: np.ndarray, spec: dict) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # darkness = the brightest channel (HSV value): a pastel tint on a coloured plate stays bright in some channel,
    # engraved ink is dark in all of them (for a black-and-white plate this is just the grey level)
    gray = hsv[:, :, 2].copy()
    b, g, r = [c.astype(int) for c in cv2.split(img)]
    red = (r - np.maximum(g, b) > 45)                        # Gray's red attachment outlines: not the bone
    gray = gray.copy()
    gray[red] = 255
    boxes = text_boxes(gray, spec) if spec.get("ocr", True) else []
    big = cv2.resize(gray, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_CUBIC)
    sat = cv2.resize(hsv[:, :, 1], None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_LINEAR)
    big = cv2.GaussianBlur(big, (3, 3), 0)
    t = spec.get("threshold") or min(170, cv2.threshold(big, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0])
    ink = (big < t) & ((sat < spec.get("sat", 45)) | (big < t - 70))   # tinted fills (a coloured plate) are not ink
    return drop_letters(ink.astype(np.uint8) * 255, boxes)


def bone_mask(ink: np.ndarray, spec: dict) -> np.ndarray:
    k = spec.get("close", 10) * SCALE
    closed = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    # fill enclosed holes: whatever the border cannot reach is inside the bone
    flood = closed.copy()
    h, w = flood.shape
    cv2.floodFill(flood, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 255)
    filled = closed | cv2.bitwise_not(flood)
    o = spec.get("open", 5) * SCALE
    opened = cv2.morphologyEx(filled, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (o, o)))
    n, labels, stats, cent = cv2.connectedComponentsWithStats(opened)
    if n <= 1:
        return filled
    if "segment" in spec:    # a column of bones (a toe): the pieces split at the joints, counted from the top
        big = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 0.12 * stats[1:, cv2.CC_STAT_AREA].max()]
        big.sort(key=lambda i: cent[i][1])
        pick = big[min(spec["segment"], len(big) - 1)]
        d = spec.get("grow", 3) * SCALE
        return cv2.dilate((labels == pick).astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d, d)))
    areas = stats[1:, cv2.CC_STAT_AREA]
    keep = spec.get("keep", 0.2)
    mask = np.zeros_like(opened)
    for i, a in enumerate(areas, start=1):
        if a >= keep * areas.max():
            mask[labels == i] = 255
    if "_region" in spec:    # a highlighted bone: only the ink over its island
        region = cv2.resize(spec["_region"], (mask.shape[1], mask.shape[0]), interpolation=cv2.INTER_NEAREST)
        return region
    if spec.get("hull"):     # an open plate (the frontal's broad surface): the bone is the hull of its outline
        pts = cv2.findNonZero(mask)
        hull = cv2.convexHull(pts)
        mask = np.zeros_like(mask)
        cv2.fillConvexPoly(mask, hull, 255)
    d = spec.get("grow", 3) * SCALE
    return cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d, d)))


def trace(bitmap: np.ndarray, turd: int) -> list:
    bm = potrace.Bitmap(bitmap == 0)                 # potracer traces the zero pixels: hand it the ink as zeros
    return bm.trace(turdsize=turd, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=1.0, opticurve=True, opttolerance=0.25)


def to_d(path, fit) -> str:
    def P(pt):
        x, y = fit(pt.x, pt.y)
        return f"{x:.1f} {y:.1f}"
    parts = []
    for curve in path:
        parts.append("M" + P(curve.start_point))
        for seg in curve.segments:
            if seg.is_corner:
                parts.append("L" + P(seg.c) + " L" + P(seg.end_point))
            else:
                parts.append("C" + P(seg.c1) + " " + P(seg.c2) + " " + P(seg.end_point))
        parts.append("Z")
    return " ".join(parts)


def trace_figure(spec: dict) -> dict:
    """Trace one figure once; return the path data both ways round (as drawn, and mirrored)."""
    spec = dict(spec)
    img = load(spec)
    ink = ink_of(img, spec)
    mask = bone_mask(ink, spec)
    art = cv2.bitwise_and(ink, mask)
    ys, xs = np.nonzero(mask)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    s = 880 / max(x1 - x0, y1 - y0)
    ox = 500 - (x0 + x1) / 2 * s
    oy = 500 - (y0 + y1) / 2 * s
    ink_path = trace(art, spec.get("turd", 6 * SCALE))
    sil_path = trace(cv2.erode(mask, np.ones((2 * SCALE, 2 * SCALE), np.uint8)), 400)
    out = {}
    for mirror in (False, True):
        def fit(x, y, mirror=mirror):
            X, Y = x * s + ox, y * s + oy
            return (1000 - X if mirror else X), Y
        out[mirror] = (to_d(ink_path, fit), to_d(sil_path, fit))
    return out


def svg_for(label: str, figure: str, ink_d: str, sil_d: str) -> str:
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" role="img" aria-labelledby="title" data-source="gray-anatomy" data-figure="{html.escape(figure)}">',
        f'  <title id="title">Gray\'s Anatomy plate derivative: {html.escape(label)}</title>',
        '  <g fill-rule="nonzero">',
        f'  <path d="{sil_d}" fill="{PAPER}" data-role="detail" data-layer="paper"/>',
        f'  <path d="{ink_d}" fill="{INK}" data-role="body" data-layer="ink"/>',
        "  </g>",
        "</svg>",
        "",
    ])


def _key(spec: dict) -> str:
    return yaml.safe_dump({k: v for k, v in spec.items() if k != "mirror"}, sort_keys=True)


def _job(args):
    key, spec = args
    return key, trace_figure(spec)


def main(argv) -> int:
    specs = yaml.safe_load((ROOT / "sources/gray-plates/figures.yaml").read_text())["objects"]
    labels = {o["id"].split(":", 1)[1]: o["label"] for o in yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())["objects"]}
    names = argv or list(specs)
    OUT.mkdir(parents=True, exist_ok=True)
    unique = {}
    for n in names:
        unique.setdefault(_key(specs[n]), specs[n])
    from multiprocessing import Pool
    traced = {}
    with Pool() as pool:
        for key, result in pool.imap_unordered(_job, list(unique.items())):
            traced[key] = result
            print(f"traced {yaml.safe_load(key)['file']}", flush=True)
    for n in names:
        ink_d, sil_d = traced[_key(specs[n])][bool(specs[n].get("mirror"))]
        svg = svg_for(labels.get(n, n), specs[n]["file"].rsplit(".", 1)[0], ink_d, sil_d)
        target = (ROOT / "glyphs/assembly" / f"{n[len('assembly_'):]}.svg") if n.startswith("assembly_") else (OUT / f"{n}.svg")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(svg, encoding="utf-8")
        print(f"{n:<34} {ink_d.count('M'):>5} contours  {len(svg) // 1024:>4} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
