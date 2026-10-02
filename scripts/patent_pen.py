"""A patent-drawing pen: every mark is a filled outline, so one drawing serves the SVG, mono font and color font.

Patent plates are line art: a heavy outline for the object, medium lines for its parts, fine lines for hatching and
texture. Fonts cannot stroke, so the pen turns every line into a thin filled shape with a known winding: ink is always
positive (shoelace > 0 in SVG coordinates), and the hole inside an outlined shape is always negative. Overlapping ink
therefore unions under the non-zero rule in every renderer (browsers, TrueType, CFF), and holes stay holes.

Canvas: 1000 x 1000, y down, artwork inside roughly 70..930.
"""

from __future__ import annotations

import math

HEAVY = 20   # the object's outline
MED = 12     # its parts
FINE = 7     # hatching, texture, pin rows

# muted plate tints for the color font (fills sit under the ink)
TINT = {
    "paper": "#f6f1e6", "pcb": "#cfe0d6", "copper": "#ecc9a8", "metal": "#dfe2dc", "silicon": "#c9d0d8",
    "gold": "#efd99a", "plastic": "#e4ddd0", "dark": "#b9c1c6", "red": "#ecc2b8", "blue": "#c8d8e6", "glass": "#e3eef2",
}
INK = "#17252c"


def _area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))


def _orient(pts, positive=True):
    return pts if (_area(pts) > 0) == positive else pts[::-1]


def _fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _poly_d(pts):
    return "M" + " L".join(f"{_fmt(x)} {_fmt(y)}" for x, y in pts) + " Z"


def rrect_pts(x, y, w, h, r=0, seg=6):
    r = max(0, min(r, w / 2, h / 2))
    if r == 0:
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    pts = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def circle_pts(cx, cy, r, seg=None):
    seg = seg or max(16, min(72, int(r / 3)))
    return [(cx + r * math.cos(2 * math.pi * i / seg), cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


def _dedupe(pts, eps=0.5):
    out = []
    for q in pts:
        if not out or math.hypot(q[0] - out[-1][0], q[1] - out[-1][1]) > eps:
            out.append(q)
    while len(out) > 2 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= eps:
        out.pop()
    return out


def offset_poly(pts, d):
    """Grow (d > 0) or shrink (d < 0) a convex-ish closed polygon by d (miter joins, clamped)."""
    pts = _orient(_dedupe(pts), True)
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        e1 = (p1[0] - p0[0], p1[1] - p0[1])
        e2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1 = math.hypot(*e1) or 1
        l2 = math.hypot(*e2) or 1
        # outward normals for a positive (y-down shoelace > 0) polygon point to the left of travel: (e.y, -e.x)
        n1 = (e1[1] / l1, -e1[0] / l1)
        n2 = (e2[1] / l2, -e2[0] / l2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, by) or 1
        cos_half = max(0.35, (n1[0] * bx + n1[1] * by) / bl)
        k = d / cos_half
        out.append((p1[0] + bx / bl * k, p1[1] + by / bl * k))
    return out


class Pen:
    """Collects ink (and, for the color font, tinted fills under it)."""

    def __init__(self):
        self.ink: list[str] = []     # path data, ink
        self.fills: list[tuple[str, str]] = []  # (path data, tint)

    # ---- low level -------------------------------------------------------------------------------------------
    def _ink(self, *contours):
        self.ink.append(" ".join(contours))

    def solid(self, pts, tint=None):
        self._ink(_poly_d(_orient(pts, True)))
        if tint:
            self.fills.append((_poly_d(_orient(pts, True)), TINT[tint]))

    def ring(self, pts, t, tint=None):
        """An outlined closed shape: the line straddles pts, t wide."""
        outer = offset_poly(pts, t / 2)
        inner = offset_poly(pts, -t / 2)
        self._ink(_poly_d(_orient(outer, True)) + " " + _poly_d(_orient(inner, False)))
        if tint:
            self.fills.append((_poly_d(_orient(pts, True)), TINT[tint]))

    # ---- shapes ----------------------------------------------------------------------------------------------
    def rect(self, x, y, w, h, r=0, t=MED, tint=None):
        self.ring(rrect_pts(x, y, w, h, r), t, tint)

    def box(self, x, y, w, h, r=0, tint=None):
        self.rect(x, y, w, h, r, HEAVY, tint)

    def fillrect(self, x, y, w, h, r=0):
        self.solid(rrect_pts(x, y, w, h, r))

    def circle(self, cx, cy, r, t=MED, tint=None):
        self.ring(circle_pts(cx, cy, r), t, tint)

    def dot(self, cx, cy, r):
        self.solid(circle_pts(cx, cy, r))

    def shape(self, pts, t=MED, tint=None):
        self.ring(pts, t, tint)

    def line(self, x1, y1, x2, y2, t=MED, cap=True):
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length * t / 2, dx / length * t / 2
        ex, ey = (dx / length * t / 2, dy / length * t / 2) if cap else (0, 0)
        self.solid([(x1 + nx - ex, y1 + ny - ey), (x2 + nx + ex, y2 + ny + ey), (x2 - nx + ex, y2 - ny + ey), (x1 - nx - ex, y1 - ny - ey)])

    def path(self, pts, t=MED, closed=False):
        for a, b in zip(pts, pts[1:] + ([pts[0]] if closed else [])):
            self.line(a[0], a[1], b[0], b[1], t)
        for p in pts[1:-1] if not closed else pts:
            self.dot(p[0], p[1], t / 2)

    def arc(self, cx, cy, r, a0, a1, t=MED, seg=None):
        seg = seg or max(6, int(abs(a1 - a0) / 6))
        pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / seg)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / seg))) for i in range(seg + 1)]
        self.path(pts, t)

    def dashed(self, x1, y1, x2, y2, t=FINE, dash=22, gap=14):
        length = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        s = 0.0
        while s < length:
            e = min(length, s + dash)
            self.line(x1 + ux * s, y1 + uy * s, x1 + ux * e, y1 + uy * e, t, cap=False)
            s += dash + gap

    def dashed_rect(self, x, y, w, h, t=FINE):
        for a, b in (((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)), ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))):
            self.dashed(*a, *b, t=t)

    def hatch(self, x, y, w, h, gap=26, angle=45, t=FINE):
        """Section lines clipped to a rectangle (the patent-plate cut-surface convention)."""
        a = math.radians(angle)
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        ps = [c[0] * nx + c[1] * ny for c in corners]
        k = math.floor(min(ps) / gap) * gap
        while k <= max(ps):
            # the line {p : p.n = k}, clipped to the rectangle
            px, py = nx * k, ny * k
            ts = []
            for (cx0, cy0), (cx1, cy1) in zip(corners, corners[1:] + corners[:1]):
                ex, ey = cx1 - cx0, cy1 - cy0
                den = dx * ey - dy * ex
                if abs(den) < 1e-9:
                    continue
                tt = ((cx0 - px) * ey - (cy0 - py) * ex) / den
                u = ((cx0 - px) * dy - (cy0 - py) * dx) / den
                if -1e-9 <= u <= 1 + 1e-9:
                    ts.append(tt)
            if len(ts) >= 2:
                t0, t1 = min(ts), max(ts)
                if t1 - t0 > 2:
                    self.line(px + dx * t0, py + dy * t0, px + dx * t1, py + dy * t1, t, cap=False)
            k += gap

    def hatch_circle(self, cx, cy, r, gap=24, angle=45, t=FINE):
        a = math.radians(angle)
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        k = -r + gap / 2
        while k < r:
            half = math.sqrt(max(0, r * r - k * k))
            px, py = cx + nx * k, cy + ny * k
            if half > 3:
                self.line(px - dx * half, py - dy * half, px + dx * half, py + dy * half, t, cap=False)
            k += gap

    # ---- recurring parts -------------------------------------------------------------------------------------
    def pins_row(self, x0, y, n, pitch, w, h, t=FINE, tint="metal"):
        for i in range(n):
            self.rect(x0 + i * pitch, y, w, h, min(w, h) / 4, t, tint)

    def grid_dots(self, x0, y0, nx, ny, pitch, r, skip=None):
        for i in range(nx):
            for j in range(ny):
                if skip and skip(i, j):
                    continue
                self.circle(x0 + i * pitch, y0 + j * pitch, r, FINE)

    def screw(self, cx, cy, r=26):
        self.circle(cx, cy, r, MED, "metal")
        self.line(cx - r * .6, cy, cx + r * .6, cy, FINE)
        self.line(cx, cy - r * .6, cx, cy + r * .6, FINE)

    def chip(self, x, y, w, h, tint="silicon", dot=True):
        self.rect(x, y, w, h, 6, MED, tint)
        if dot:
            self.circle(x + 18, y + 18, 7, FINE)

    def arrow(self, x1, y1, x2, y2, t=MED, head=34):
        self.line(x1, y1, x2, y2, t)
        a = math.atan2(y2 - y1, x2 - x1)
        for s in (-1, 1):
            self.line(x2, y2, x2 - head * math.cos(a + s * .45), y2 - head * math.sin(a + s * .45), t)

    def gold_fingers(self, x0, y, n, pitch, w, h, notch=None):
        for i in range(n):
            if notch is not None and abs(x0 + i * pitch - notch) < pitch * 1.2:
                continue
            self.rect(x0 + i * pitch, y, w, h, 2, FINE, "gold")


# ---- anatomy: smooth outlines and shading inside any outline ------------------------------------------------------
def smooth(pts, closed=True, per=8):
    """A Catmull-Rom curve through the control points, as a dense polyline (closed by default)."""
    n = len(pts)
    out = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[(i + 1) % n] if closed else pts[i + 1]
        p3 = pts[(i + 2) % n] if closed else pts[min(i + 2, n - 1)]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    if not closed:
        out.append(pts[-1])
    return out


def mirror(pts, axis=500):
    return [(2 * axis - x, y) for x, y in pts]


def _hatch_poly(pen, poly, gap, angle, t):
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    ks = [x * nx + y * ny for x, y in poly]
    k = math.floor(min(ks) / gap) * gap + gap / 2
    n = len(poly)
    while k < max(ks):
        hits = []
        for i in range(n):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
            k0, k1 = x0 * nx + y0 * ny, x1 * nx + y1 * ny
            if (k0 - k) * (k1 - k) < 0:
                u = (k - k0) / (k1 - k0)
                px, py = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
                hits.append(px * dx + py * dy)
        hits.sort()
        bx, by = nx * k, ny * k
        for s0, s1 in zip(hits[::2], hits[1::2]):
            if s1 - s0 > 4:
                pen.line(bx + dx * s0, by + dy * s0, bx + dx * s1, by + dy * s1, t, cap=False)
        k += gap


def _poly_ring(pts, t):
    """An outline along an arbitrary (possibly concave) smooth polygon: a ribbon of segments, unioned."""
    return pts


Pen.hatch_poly = lambda self, poly, gap=22, angle=45, t=FINE: _hatch_poly(self, poly, gap, angle, t)


def _outline(self, pts, t=MED, tint=None):
    """A smooth closed outline (concave is fine while its curves are wider than the line): one ring, two contours."""
    self.ring(pts, t, tint)


def _ribbon(pts, t):
    """An open polyline as one polygon: offset left, then back along the right."""
    pts = _dedupe(pts)
    left, right = [], []
    n = len(pts)
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length * t / 2, dx / length * t / 2
        left.append((pts[i][0] + nx, pts[i][1] + ny))
        right.append((pts[i][0] - nx, pts[i][1] - ny))
    return left + right[::-1]


def _curve(self, pts, t=MED, closed=False, taper=False):
    line = smooth(pts, closed)
    if closed:
        self.ring(line, t)
    else:
        self.solid(_ribbon(line, t))


Pen.outline = _outline
Pen.curve = _curve
Pen.ribbon = lambda self, pts, t=MED: self.solid(_ribbon(pts, t))
