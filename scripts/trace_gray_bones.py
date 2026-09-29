#!/usr/bin/env python3
"""Trace Gray's Anatomy plate scans into deterministic BONES SVG masters.

This is a source-art step, not part of the normal font build.  The downloaded
plate scans remain in sources/gray-plates/raw/ and this script turns their
engraved linework into clean filled paths suitable for fontTools.

OpenCV is intentionally an optional source dependency.  Once generated, the
SVG masters are committed and normal builds remain portable and offline.
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "sources/gray-plates/raw"
OUT = ROOT / "glyphs/gray-trace"


# Coordinates are source-image pixels.  The forearm and lower-leg plates are
# shared deliberately: separate crops preserve semantic identity without
# pretending that the underlying reference drawing is the same object.
PLATES = {
    "skull": ("skull.png", (0, 0, 500, 463), "Gray188.png"),
    "mandible": ("mandible.png", (0, 0, 600, 402), "Gray176.png"),
    "clavicle": ("clavicle.png", (0, 0, 600, 205), "Gray201.png"),
    "scapula": ("scapula.png", (0, 0, 281, 650), "Gray205 left scapula lateral view.png"),
    "sternum": ("sternum.png", (0, 0, 330, 579), "Gray116.png"),
    "rib": ("rib.png", (0, 0, 410, 315), "First rib Gray.png"),
    "vertebra": ("vertebra.png", (0, 0, 270, 553), "Gray314.png"),
    "humerus": ("humerus.png", (0, 0, 256, 1000), "Gray208.png"),
    "radius": ("radius.png", (0, 0, 251, 400), "Gray217.png"),
    "ulna": ("forearm.png", (300, 0, 590, 1254), "Gray214.png"),
    "pelvis": ("pelvis.png", (0, 0, 1000, 808), "Gray241.png"),
    "femur": ("femur.png", (0, 0, 467, 1253), "Femur front.png"),
    "patella": ("patella.png", (0, 0, 196, 200), "Gray256.png"),
    "tibia": ("lower_leg.gif", (105, 0, 346, 1000), "Unterschenkel.gif"),
    "fibula": ("lower_leg.gif", (10, 0, 185, 1000), "Unterschenkel.gif"),
}

# Historical plates vary in scan contrast.  Lowering the cutoff on the skull
# and pelvis avoids filling their broad shaded regions; long-bone plates need
# the higher cutoff to retain the engraved surface detail.
THRESHOLDS = {
    "skull": 145,
    "pelvis": 150,
    "femur": 190,
    "humerus": 185,
    "radius": 185,
    "ulna": 185,
    "tibia": 185,
    "fibula": 185,
}


def crop_image(name: str) -> tuple[np.ndarray, str]:
    filename, box, plate = PLATES[name]
    image = cv2.imread(str(RAW / filename), cv2.IMREAD_COLOR)
    if image is None:
        raise SystemExit(f"cannot read source plate: {RAW / filename}")
    x0, y0, x1, y1 = box
    height, width = image.shape[:2]
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise SystemExit(f"crop outside {filename}: {box} for {width}x{height}")
    return image[y0:y1, x0:x1], plate


def masks(image: np.ndarray, threshold: int) -> tuple[np.ndarray, np.ndarray]:
    """Return monochrome ink and red accent masks from a color scan."""
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Engraved ink and red anatomical annotations survive this threshold while
    # the paper background is discarded.  A small opening removes scan dust.
    ink = (gray < threshold).astype(np.uint8) * 255
    red = (
        (rgb[:, :, 0] > 95)
        & (rgb[:, :, 0] > rgb[:, :, 1] * 1.18)
        & (rgb[:, :, 0] > rgb[:, :, 2] * 1.18)
        & ((rgb[:, :, 0].astype(np.int16) - rgb[:, :, 1].astype(np.int16)) > 24)
    ).astype(np.uint8) * 255
    kernel = np.ones((2, 2), np.uint8)
    ink = cv2.morphologyEx(ink, cv2.MORPH_OPEN, kernel)
    red = cv2.morphologyEx(red, cv2.MORPH_OPEN, kernel)
    # Keep red plate annotations out of the dark ink layer so color masters
    # retain the restrained red/black atlas language.
    ink = cv2.bitwise_and(ink, cv2.bitwise_not(red))
    return ink, red


def trim(ink: np.ndarray, red: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    union = cv2.bitwise_or(ink, red)
    points = cv2.findNonZero(union)
    if points is None:
        raise SystemExit("plate crop contains no traceable ink")
    x, y, w, h = cv2.boundingRect(points)
    pad = 4
    x0, y0 = max(0, x - pad), max(0, y - pad)
    x1, y1 = min(union.shape[1], x + w + pad), min(union.shape[0], y + h + pad)
    return ink[y0:y1, x0:x1], red[y0:y1, x0:x1]


def path_data(mask: np.ndarray) -> list[str]:
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        return []
    paths: list[str] = []
    for index, contour in enumerate(contours):
        if hierarchy[0][index][3] >= 0:
            continue
        if cv2.contourArea(contour) < 1.0 or cv2.arcLength(contour, True) < 4.0:
            continue
        outer = cv2.approxPolyDP(contour, 0.7, True).reshape(-1, 2)
        if len(outer) < 3:
            continue
        rings = [outer]
        child = hierarchy[0][index][2]
        while child >= 0:
            hole = cv2.approxPolyDP(contours[child], 0.7, True).reshape(-1, 2)
            if len(hole) >= 3:
                rings.append(hole)
            child = hierarchy[0][child][0]
        commands = []
        for ring in rings:
            commands.append("M " + " ".join(f"{int(px)},{int(py)}" for px, py in ring) + " Z")
        paths.append(" ".join(commands))
    return paths


def render_svg(name: str, ink: np.ndarray, red: np.ndarray, plate: str) -> tuple[str, int, int]:
    height, width = ink.shape[:2]
    scale = 900.0 / max(width, height)
    offset_x = (1000.0 - width * scale) / 2.0
    offset_y = (1000.0 - height * scale) / 2.0

    def transform(path: str) -> str:
        tokens = path.replace("M ", "M ").replace(" Z", " Z").split()
        output = []
        for token in tokens:
            if token in {"M", "Z"}:
                output.append(token)
                continue
            if "," not in token:
                output.append(token)
                continue
            px, py = token.rstrip("Z").split(",")
            output.append(f"{float(px) * scale + offset_x:.2f},{float(py) * scale + offset_y:.2f}")
        return " ".join(output)

    ink_paths = [transform(path) for path in path_data(ink)]
    red_paths = [transform(path) for path in path_data(red)]
    elements = [
        f'  <path d="{html.escape(path, quote=True)}" fill="#17232b" data-role="body"/>'
        for path in ink_paths
    ]
    elements.extend(
        f'  <path d="{html.escape(path, quote=True)}" fill="#b4384c" data-role="detail"/>'
        for path in red_paths
    )
    svg = "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" role="img" aria-labelledby="title" data-source="gray-anatomy">',
            f'  <title id="title">Gray\'s Anatomy plate derivative: {html.escape(name.title())}</title>',
            f'  <metadata>Source plate: {html.escape(plate)}</metadata>',
            '  <g fill-rule="evenodd" clip-rule="evenodd">',
            *elements,
            "  </g>",
            "</svg>",
            "",
        ]
    )
    return svg, len(ink_paths), len(red_paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", choices=sorted(PLATES), help="specific bone bases; default is all")
    args = parser.parse_args()
    names = args.names or list(PLATES)
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names:
        image, plate = crop_image(name)
        ink, red = masks(image, THRESHOLDS.get(name, 165))
        ink, red = trim(ink, red)
        svg, black_count, red_count = render_svg(name, ink, red, plate)
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"{name}: {black_count} ink paths, {red_count} accent paths")
    print(f"wrote {len(names)} Gray's Anatomy trace masters to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
