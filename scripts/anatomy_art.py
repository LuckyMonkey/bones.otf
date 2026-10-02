"""BONES glyph art: original patent-style anatomical drawings, one per object (Gray's plates are the reference only).

Series bones (hand, foot, ribs, vertebrae) are drawn in context, the way a patent figure points to one part: the
whole series in fine line, the object itself in a heavy outline with section hatching. Left-side objects mirror the
right (anatomical position: the body's right is the viewer's left). Organs and unique bones are drawn on their own.
"""

from __future__ import annotations

import math

from patent_pen import FINE, HEAVY, MED, TINT, Pen, mirror, smooth

TINT.update({"bone": "#efe1c3", "soft": "#f3e9e4", "organ": "#e9b9ad", "liver": "#d9a28f", "blood": "#e4a8a8",
             "vessel": "#bcc9e6", "lung": "#efc7c4", "brain": "#efd2cf", "bile": "#cfe0a8", "gut": "#f0cdb4",
             "kidney": "#d9a2a0", "gland": "#eac39b", "skin": "#f2d4bd", "fat": "#f6e7b3"})

ART: dict[str, callable] = {}


def art(*names):
    def wrap(fn):
        for n in names:
            ART[n] = fn
        return fn
    return wrap


def draw(base: str) -> Pen | None:
    fn = ART.get(base)
    if not fn:
        return None
    p = Pen()
    fn(p, base)
    return p


# ------------------------------------------------------------------------------------------------- shape builders
def long_bone(p0, p1, shaft, head0, head1, waist=0.0):
    """A long bone's outline along p0 -> p1: a shaft that flares into rounded ends."""
    (x0, y0), (x1, y1) = p0, p1
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    nx, ny = -uy, ux

    def half(s):
        w = shaft / 2 + (head0 - shaft) / 2 * math.exp(-(s / 0.13) ** 2) + (head1 - shaft) / 2 * math.exp(-((1 - s) / 0.13) ** 2)
        return w * (1 - waist * math.sin(math.pi * s))

    side_a, side_b = [], []
    steps = 14
    for i in range(steps + 1):
        s = i / steps
        cx, cy = x0 + (x1 - x0) * s, y0 + (y1 - y0) * s
        h = half(s)
        side_a.append((cx + nx * h, cy + ny * h))
        side_b.append((cx - nx * h, cy - ny * h))
    cap1 = [(x1 + ux * half(1) * .55 * math.cos(math.radians(a)) * 0 + (nx * math.cos(math.radians(a)) + ux * math.sin(math.radians(a))) * half(1),
             y1 + (ny * math.cos(math.radians(a)) + uy * math.sin(math.radians(a))) * half(1)) for a in (45, 90, 135)]
    cap0 = [(x0 + (-nx * math.cos(math.radians(a)) - ux * math.sin(math.radians(a))) * half(0),
             y0 + (-ny * math.cos(math.radians(a)) - uy * math.sin(math.radians(a))) * half(0)) for a in (45, 90, 135)]
    ctrl = side_a[::2] + cap1 + side_b[::-2] + cap0
    return smooth(ctrl, closed=True, per=6)


def blob(cx, cy, rx, ry, rot=0, wobble=(), seed=0):
    """A rounded bone or organ body: an ellipse with optional shape harmonics (k, amplitude, phase)."""
    pts = []
    n = 16
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + sum(amp * math.cos(k * a + ph) for k, amp, ph in wobble)
        x, y = rx * r * math.cos(a), ry * r * math.sin(a)
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return smooth(pts, closed=True, per=5)


def feature(p, outline, target, tint="bone"):
    """Context in fine line; the object itself heavy, hatched, tinted."""
    if target:
        p.outline(outline, HEAVY + 4, tint)
        p.hatch_poly(outline, 11, 45, FINE)
    else:
        p.outline(outline, FINE, "paper")


def flip(p, outlines_fn, left):
    """Draw with every point mirrored for the left side."""
    return (lambda pts: mirror(pts)) if left else (lambda pts: pts)


# ============================================================================================================ the hand
# right hand, dorsal view, fingers up (thumb on the viewer's left)
DIGITS = {  # metacarpal base, head; phalanx lengths
    "thumb": ((350, 700), (250, 545), [118, 0, 82]),
    "index": ((430, 655), (405, 425), [150, 92, 70]),
    "middle": ((495, 650), (500, 405), [165, 104, 74]),
    "ring": ((560, 655), (590, 425), [152, 98, 72]),
    "little": ((620, 675), (670, 480), [118, 74, 62]),
}
CARPALS = {   # centre, radii, rotation, wobble
    "scaphoid": ((395, 790), (44, 30), -35, ((2, .12, 0),)),
    "lunate": ((468, 806), (36, 32), 0, ((3, .08, 1),)),
    "triquetrum": ((536, 794), (34, 26), 20, ((2, .1, 1),)),
    "pisiform": ((580, 822), (18, 16), 0, ()),
    "trapezium": ((362, 724), (36, 30), -25, ((3, .07, 0),)),
    "trapezoid": ((420, 712), (26, 28), 0, ((4, .06, 0),)),
    "capitate": ((480, 718), (32, 44), 0, ((2, .1, 0),)),
    "hamate": ((546, 724), (34, 38), 15, ((3, .1, 2),)),
}


def _hand_parts():
    parts = {}
    for name, ((cx, cy), (rx, ry), rot, wob) in CARPALS.items():
        parts[name] = blob(cx, cy, rx, ry, rot, wob)
    for k, (digit, (base, head, lens)) in enumerate(DIGITS.items(), start=1):
        parts[f"metacarpal_{k}"] = long_bone(base, head, 26 if digit != "thumb" else 30, 40, 38, .1)
        ux, uy = head[0] - base[0], head[1] - base[1]
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        start = (head[0] + ux * 26, head[1] + uy * 26)
        names = ["proximal", "middle", "distal"]
        for ln, nm in zip(lens, names):
            if ln == 0:
                continue
            end = (start[0] + ux * ln, start[1] + uy * ln)
            w = {"proximal": 24, "middle": 20, "distal": 16}[nm] * (1.15 if digit == "thumb" else 1)
            parts[f"{digit}_{nm}_phalanx"] = long_bone(start, end, w, w * 1.45, w * (1.25 if nm != "distal" else 1.6), .08)
            start = (end[0] + ux * 16, end[1] + uy * 16)
    return parts


def _forearm_ends(p):
    p.outline(long_bone((430, 990), (425, 860), 60, 70, 96), FINE, "paper")     # radius, distal end
    p.outline(long_bone((560, 990), (552, 870), 40, 46, 56), FINE, "paper")     # ulna, distal end


def hand(p, base):
    left = base.startswith("left_")
    key = base.split("_", 1)[1] if left or base.startswith("right_") else base
    m = mirror if left else (lambda pts: pts)
    _forearm_ends_m = Pen()
    for name, outline in _hand_parts().items():
        feature(p, m(outline), name == key)
    for nm, (pts, w) in {"radius": (((430, 990), (425, 860)), (60, 70, 96)), "ulna": (((560, 990), (552, 870)), (40, 46, 56))}.items():
        p.outline(m(long_bone(*pts, *w)), FINE, "paper")


# ============================================================================================================ the foot
# right foot, dorsal view, toes up (great toe on the viewer's left)
TOES = {
    "great_toe": ((418, 540), (400, 370), [104, 0, 74]),
    "second_toe": ((470, 535), (472, 345), [80, 44, 36]),
    "third_toe": ((520, 545), (532, 362), [72, 40, 34]),
    "fourth_toe": ((566, 560), (588, 385), [66, 36, 32]),
    "fifth_toe": ((610, 585), (640, 425), [58, 32, 30]),
}
TARSALS = {
    "calcaneus": ((548, 880), (64, 82), 6, ((2, .06, 0),)),
    "talus": ((500, 760), (66, 50), -6, ((2, .08, 0), (3, .04, 1))),
    "navicular": ((452, 672), (52, 26), -12, ((3, .05, 0),)),
    "cuboid": ((590, 672), (40, 46), 10, ((4, .05, 1),)),
    "medial_cuneiform": ((420, 598), (28, 40), -4, ()),
    "intermediate_cuneiform": ((472, 604), (22, 30), 0, ()),
    "lateral_cuneiform": ((524, 606), (24, 34), 4, ()),
}


def _foot_parts():
    parts = {}
    for name, ((cx, cy), (rx, ry), rot, wob) in TARSALS.items():
        parts[name] = blob(cx, cy, rx, ry, rot, wob)
    for k, (toe, (base, head, lens)) in enumerate(TOES.items(), start=1):
        great = toe == "great_toe"
        parts[f"metatarsal_{k}"] = long_bone(base, head, 40 if great else 26, 58 if great else 38, 52 if great else 36, .08)
        ux, uy = head[0] - base[0], head[1] - base[1]
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        start = (head[0] + ux * 30, head[1] + uy * 30)
        for ln, nm in zip(lens, ["proximal", "middle", "distal"]):
            if ln == 0:
                continue
            end = (start[0] + ux * ln, start[1] + uy * ln)
            w = {"proximal": 26, "middle": 22, "distal": 22}[nm] * (1.55 if great else 1)
            parts[f"{toe}_{nm}_phalanx"] = long_bone(start, end, w, w * 1.4, w * (1.2 if nm != "distal" else 1.4), .08)
            start = (end[0] + ux * 14, end[1] + uy * 14)
    return parts


def foot(p, base):
    left = base.startswith("left_")
    key = base.split("_", 1)[1]
    m = mirror if left else (lambda pts: pts)
    for name, outline in _foot_parts().items():
        feature(p, m(outline), name == key)


# ================================================================================================= the hand and foot
HAND_KEYS = list(CARPALS) + [f"metacarpal_{k}" for k in range(1, 6)] + [
    f"{d}_{n}_phalanx" for d in DIGITS for n in ("proximal", "middle", "distal") if not (d == "thumb" and n == "middle")]
FOOT_KEYS = list(TARSALS) + [f"metatarsal_{k}" for k in range(1, 6)] + [
    f"{t}_{n}_phalanx" for t in TOES for n in ("proximal", "middle", "distal") if not (t == "great_toe" and n == "middle")]
for _side in ("left_", "right_"):
    for _k in HAND_KEYS:
        ART[_side + _k] = hand
    for _k in FOOT_KEYS:
        ART[_side + _k] = foot


# ============================================================================================================ the ribs
def _rib_line(i, right=True):
    """Rib i (1..12), anterior view: from the spine, round the side, down to its front end."""
    s = -1 if right else 1                       # the body's right ribs sit on the viewer's left
    y0 = 150 + i * 40
    w = 110 + 30 * min(i, 7) - 10 * max(0, i - 9)
    if i <= 7:
        front = (500 + s * (36 + 3 * i), 250 + i * 40)
    elif i <= 10:
        front = (500 + s * (120 + 30 * (i - 7)), y0 + 120)
    else:
        front = (500 + s * (w - 20), y0 + 70)
    pts = [(500 + s * 22, y0), (500 + s * w * .55, y0 - 26), (500 + s * w, y0 + 20), (500 + s * (w - 10), y0 + 75),
           ((500 + s * (w - 10) + front[0]) / 2, (y0 + 90 + front[1]) / 2 + 12), front]
    return smooth(pts, closed=False, per=6), front


def _ribs(p, target=None):
    p.dashed(500, 150, 500, 760, FINE)          # the column behind
    for i in range(1, 13):
        for right in (True, False):
            if target == (i, right):
                continue
            line, front = _rib_line(i, right)
            p.ribbon(line, 12)
            if 8 <= i <= 10:
                p.curve([front, (500 + (-1 if right else 1) * (60 + (i - 8) * 10), 560 + (i - 8) * 6), (500 + (-1 if right else 1) * 30, 540)], FINE)   # costal margin
    p.outline(smooth([(470, 196), (530, 196), (542, 250), (524, 296), (532, 520), (514, 576), (500, 610), (486, 576), (468, 520), (476, 296), (458, 250)], per=5), MED, "bone")   # sternum


@art("rib")
def _(p, base):
    # a typical rib, seen from above: head, neck, tubercle, angle, shaft, costal groove
    outer = smooth([(170, 480), (210, 420), (300, 330), (450, 250), (620, 240), (760, 300), (850, 420), (870, 520),
                    (840, 540), (820, 440), (740, 340), (610, 290), (460, 300), (320, 380), (230, 470), (200, 520)], per=6)
    p.outline(outer, HEAVY, "bone")
    p.hatch_poly(outer, 20, 45, FINE)
    p.circle(185, 500, 32, MED)                                 # head
    p.circle(255, 440, 18, MED)                                 # tubercle
    p.curve([(300, 360), (470, 278), (640, 266), (780, 330), (850, 450)], FINE)    # costal groove


def ribs_for(i, right):
    def fn(p, base):
        _ribs(p, (i, right))
        line, _ = _rib_line(i, right)
        from patent_pen import _ribbon
        poly = _ribbon(line, 34)
        p.outline(poly, HEAVY, "bone")
        p.hatch_poly(poly, 10, 45, FINE)
    return fn


for _i in range(1, 13):
    ART[f"right_rib_{_i}"] = ribs_for(_i, True)
    ART[f"left_rib_{_i}"] = ribs_for(_i, False)


# ======================================================================================================= the vertebrae
LEVELS = ["c1_atlas", "c2_axis", "c3", "c4", "c5", "c6", "c7"] + [f"t{i}" for i in range(1, 13)] + [f"l{i}" for i in range(1, 6)]


def _locator(p, level):
    """A small spinal column at the right edge: every level a block, this one solid."""
    x, y = 880, 120
    for k, name in enumerate(LEVELS):
        h = 20 if k < 7 else 24 if k < 19 else 30
        w = 40 if k < 7 else 50 if k < 19 else 62
        if name == level:
            p.fillrect(x - w / 2, y, w, h - 5, 3)
        else:
            p.rect(x - w / 2, y, w, h - 5, 3, FINE)
        y += h
    p.outline(smooth([(845, y + 4), (915, y + 4), (900, y + 80), (880, y + 110), (860, y + 80)], per=4), FINE)   # sacrum


def _vertebra(p, kind, cx=430, cy=520, s=1.0, bifid=True):
    """Superior view of a typical vertebra of each region."""
    def S(pts):
        return [(cx + x * s, cy + y * s) for x, y in pts]
    if kind == "cervical":
        body = smooth(S([(0, 190), (-130, 180), (-150, 110), (-120, 60), (0, 70), (120, 60), (150, 110), (130, 180)]))
        p.outline(body, HEAVY, "bone")
        p.hatch_poly(body, 18, 45, FINE)
        for sx in (-1, 1):
            p.ribbon(smooth(S([(sx * 120, 70), (sx * 190, 40), (sx * 250, 60)]), closed=False), 40)        # transverse process
            p.circle(cx + sx * 200 * s, cy + 50 * s, 22 * s, MED)                                           # transverse foramen
            p.outline(blob(cx + sx * 150 * s, cy - 40 * s, 46 * s, 36 * s), MED, "bone")                     # articular pillar
        p.ribbon(smooth(S([(-150, -20), (-90, -130), (0, -160), (90, -130), (150, -20)]), closed=False), 30)   # lamina
        for sx in (-1, 1) if bifid else ():
            p.ribbon(smooth(S([(0, -160), (sx * 30, -230), (sx * 60, -270)]), closed=False), 32)            # bifid spinous process
        p.outline(blob(cx, cy - 30 * s, 110 * s, 80 * s, 0, ((3, .06, 0),)), MED)                         # the wide triangular foramen
    elif kind == "thoracic":
        body = smooth(S([(0, 230), (-120, 210), (-150, 120), (-110, 50), (0, 70), (110, 50), (150, 120), (120, 210)]))
        p.outline(body, HEAVY, "bone")
        p.hatch_poly(body, 18, 45, FINE)
        for sx in (-1, 1):
            p.ribbon(smooth(S([(sx * 100, 60), (sx * 120, -20), (sx * 270, -60), (sx * 300, -100)]), closed=False), 38)   # transverse
            p.circle(cx + sx * 290 * s, cy - 92 * s, 18 * s, FINE)            # costal facet
        p.ribbon(smooth(S([(-110, -20), (-60, -110), (0, -140), (60, -110), (110, -20)]), closed=False), 30)
        p.ribbon(smooth(S([(0, -140), (0, -260), (0, -380)]), closed=False), 44)     # long spinous process
        p.outline(blob(cx, cy - 10 * s, 80 * s, 70 * s), MED)
    else:  # lumbar
        body = smooth(S([(0, 250), (-170, 230), (-210, 120), (-150, 40), (0, 70), (150, 40), (210, 120), (170, 230)]))
        p.outline(body, HEAVY, "bone")
        p.hatch_poly(body, 18, 45, FINE)
        for sx in (-1, 1):
            p.ribbon(smooth(S([(sx * 130, 40), (sx * 150, -40), (sx * 330, -70)]), closed=False), 40)
            p.circle(cx + sx * 140 * s, cy - 120 * s, 30 * s, MED)            # mammillary / superior facet
        p.ribbon(smooth(S([(-140, -40), (-80, -130), (0, -150), (80, -130), (140, -40)]), closed=False), 36)
        p.rect(cx - 35 * s, cy - 330 * s, 70 * s, 190 * s, 20 * s, HEAVY, "bone")    # square spinous process
        p.outline(blob(cx, cy - 30 * s, 95 * s, 70 * s, 0, ((3, .1, 0),)), MED)


def _atlas(p):
    ring = blob(430, 500, 330, 250)
    p.outline(ring, HEAVY, "bone")
    p.outline(blob(430, 470, 210, 150), MED)                              # the wide ring, no body
    for sx in (-1, 1):
        mass = blob(430 + sx * 230, 520, 90, 120, sx * 10)
        p.outline(mass, HEAVY, "bone")
        p.hatch_poly(mass, 16, 45, FINE)
        p.outline(blob(430 + sx * 230, 520, 50, 80, sx * 10), FINE)       # superior articular facets
        p.circle(430 + sx * 345, 470, 26, MED)                              # transverse foramen
    p.circle(430, 760, 30, MED)                                              # anterior tubercle
    p.line(330, 680, 530, 680, FINE)                                         # facet for the dens


def _axis(p):
    p.outline(blob(430, 620, 150, 110), HEAVY, "bone")
    dens = smooth([(370, 600), (370, 300), (400, 230), (460, 230), (490, 300), (490, 600)], per=5)
    p.outline(dens, HEAVY, "bone")
    p.hatch_poly(dens, 16, 45, FINE)
    for sx in (-1, 1):
        p.outline(blob(430 + sx * 190, 560, 90, 60, sx * 15), MED, "bone")
        p.circle(430 + sx * 290, 600, 22, MED)
    p.ribbon(smooth([(330, 700), (380, 820), (430, 860), (480, 820), (530, 700)], closed=False), 30)


def _level(p, base):
    if base == "c1_atlas":
        _atlas(p)
    elif base == "c2_axis":
        _axis(p)
    else:
        _vertebra(p, {"c": "cervical", "t": "thoracic", "l": "lumbar"}[base[0]], s=0.92)
    _locator(p, base)


for _lv in LEVELS:
    ART[_lv] = _level


@art("vertebra")
def _(p, base):
    _vertebra(p, "thoracic", 500, 520, 1.05)


@art("sacrum")
def _(p, base):
    out = smooth([(250, 180), (750, 180), (720, 360), (640, 600), (560, 800), (500, 860), (440, 800), (360, 600), (280, 360)], per=6)
    p.outline(out, HEAVY, "bone")
    p.hatch_poly(out, 22, 45, FINE)
    p.outline(blob(500, 220, 120, 40), MED)                                  # promontory / S1 body
    for k in range(4):
        y = 330 + k * 120
        w = 160 - k * 30
        p.line(500 - w, y, 500 + w, y, MED)                                  # transverse ridges (fused segments)
        for sx in (-1, 1):
            p.circle(500 + sx * (w + 40), y + 50, 22 - 3 * k, MED)          # anterior sacral foramina
    for sx in (-1, 1):
        p.outline(smooth([(500 + sx * 250, 180), (500 + sx * 330, 220), (500 + sx * 300, 380), (500 + sx * 220, 360)], per=4), MED, "bone")   # alae


@art("coccyx")
def _(p, base):
    sizes = ((360, 190), (270, 150), (190, 115), (120, 80))
    for k, (w, h) in enumerate(sizes):
        y = 130 + sum(hh + 24 for _, hh in sizes[:k])
        seg = blob(500, y + h / 2, w / 2, h / 2, 0, ((2, .05, 0),))
        p.outline(seg, HEAVY if k == 0 else MED, "bone")
        p.hatch_poly(seg, 18, 45, FINE)
    for sx in (-1, 1):
        p.ribbon(smooth([(500 + sx * 150, 150), (500 + sx * 230, 100), (500 + sx * 220, 60)], closed=False), 34)   # cornua


def _c7(p, base):
    _vertebra(p, "cervical", s=0.92, bifid=False)
    p.ribbon(smooth([(430, 375), (430, 230), (432, 120)], closed=False, per=4), 46)    # vertebra prominens: long, single
    p.circle(432, 115, 26, MED)
    _locator(p, base)


ART["c7"] = _c7


# ============================================================================================================ the skull
# lateral view, face to the viewer's left
SKULL_REGIONS = {
    "frontal": [(250, 430), (252, 330), (290, 230), (360, 160), (450, 128), (468, 200), (474, 300), (452, 380), (420, 420),
                (380, 405), (330, 392), (285, 405)],
    "parietal": [(450, 128), (560, 112), (690, 140), (712, 230), (700, 330), (690, 430), (600, 400), (520, 410), (474, 420),
                 (452, 380), (474, 300), (468, 200)],
    "occipital": [(690, 140), (770, 200), (820, 300), (836, 410), (816, 510), (770, 590), (722, 570), (708, 480), (700, 330), (712, 230)],
    "temporal": [(474, 420), (520, 410), (600, 400), (690, 430), (708, 480), (722, 570), (700, 650), (668, 640), (640, 600),
                 (600, 560), (540, 535), (470, 530), (470, 500), (480, 470)],
    "sphenoid": [(420, 420), (452, 380), (474, 420), (480, 470), (470, 500), (440, 510), (415, 480)],
    "zygomatic": [(300, 500), (360, 478), (415, 480), (440, 510), (470, 500), (470, 530), (420, 548), (360, 566), (318, 556)],
    "maxilla": [(232, 520), (285, 500), (300, 500), (318, 556), (360, 566), (420, 548), (452, 600), (440, 660), (410, 700),
                (270, 700), (238, 650), (226, 580)],
    "nasal": [(250, 430), (268, 432), (250, 520), (232, 520), (226, 488)],
    "lacrimal": [(272, 418), (292, 414), (296, 452), (276, 458)],
    "ethmoid": [(292, 404), (326, 398), (330, 448), (296, 452)],
}
HIDDEN = {   # inside the skull: drawn in hidden (dashed) line, the patent convention
    "vomer": [(240, 560), (300, 540), (330, 600), (300, 660), (250, 650)],
    "palatine": [(380, 640), (450, 630), (460, 676), (390, 686)],
}


def _mandible_outline(dx=0, dy=0, k=1.0, ky=None):
    ky = ky or k
    pts = [(600, 600), (628, 612), (618, 680), (600, 760), (580, 812), (500, 832), (380, 840), (300, 836), (262, 806), (258, 760),
           (276, 718), (440, 716), (500, 690), (528, 640), (548, 612), (566, 650), (580, 640)]
    return smooth([(dx + 500 + (x - 500) * k, dy + 500 + (y - 500) * ky) for x, y in pts], per=5)


def _teeth(p, x0, x1, y, h, up=True):
    n = 8
    w = (x1 - x0) / n
    for i in range(n):
        p.rect(x0 + i * w + 3, y - (h if up else 0), w - 6, h, 8, FINE, "paper")


def _skull(p, target=None):
    cranium = smooth([(250, 430), (252, 330), (290, 230), (360, 160), (450, 128), (560, 112), (690, 140), (770, 200), (820, 300),
                      (836, 410), (816, 510), (770, 590), (700, 650), (668, 640), (640, 600), (600, 560), (540, 535),
                      (470, 530), (452, 600), (440, 660), (410, 700), (270, 700), (238, 650), (226, 580), (232, 520), (226, 488)], per=5)
    p.outline(cranium, HEAVY if not target else MED, "bone")
    for name, poly in SKULL_REGIONS.items():
        outline = smooth(poly, per=4)
        if name == target:
            p.outline(outline, HEAVY + 4, "bone")
            p.hatch_poly(outline, 11, 45, FINE)
        else:
            p.outline(outline, FINE)
    for name, poly in HIDDEN.items():
        outline = smooth(poly, per=4)
        for a, b in zip(outline, outline[1:] + outline[:1]):
            pass
        if name == target:
            p.hatch_poly(outline, 11, 45, FINE)
            p.outline(outline, MED)
        else:
            pts = outline + outline[:1]
            for i in range(0, len(pts) - 1, 2):
                p.line(*pts[i], *pts[i + 1], FINE, cap=False)
    p.circle(330, 440, 62, MED)                                            # orbit
    p.outline(smooth([(232, 528), (262, 540), (268, 600), (246, 630), (226, 600)], per=4), MED)      # nasal aperture
    p.circle(632, 540, 22, MED)                                            # external acoustic meatus
    p.ribbon(smooth([(440, 520), (520, 528), (600, 545)], closed=False), 26)   # zygomatic arch
    _teeth(p, 268, 440, 700, 34, up=False)
    mand = _mandible_outline()
    p.outline(mand, MED if target else HEAVY, "bone")
    _teeth(p, 276, 440, 718, 30)


for _n in list(SKULL_REGIONS) + list(HIDDEN):
    ART[_n] = (lambda name: (lambda p, base: _skull(p, name)))(_n)


@art("skull")
def _(p, base):
    _skull(p, None)
    p.hatch_poly(smooth(SKULL_REGIONS["temporal"], per=4), 26, 45, FINE)   # section tone on the squama
    p.circle(330, 440, 40, FINE)


@art("mandible")
def _(p, base):
    k, ky, dx, dy = 1.75, 2.4, 115, -620
    T = lambda x, y: (500 + (x - 500) * k + dx, 500 + (y - 500) * ky + dy)
    outline = _mandible_outline(dx, dy, k, ky)
    p.outline(outline, HEAVY, "bone")
    p.hatch_poly(outline, 22, 45, FINE)
    x0, y0 = T(276, 718)
    x1, _ = T(440, 718)
    _teeth(p, x0, x1, y0, 52)
    p.circle(*T(330, 780), 18, MED)                                         # mental foramen
    p.circle(*T(560, 700), 20, MED)                                         # mandibular foramen
    p.outline(blob(*T(612, 600), 34, 24, 20), MED)                          # condyle head


@art("hyoid")
def _(p, base):
    body = smooth([(380, 560), (500, 600), (620, 560), (640, 500), (500, 520), (360, 500)], per=5)
    p.outline(body, HEAVY, "bone")
    p.hatch_poly(body, 16, 45, FINE)
    for sx in (-1, 1):
        p.ribbon(smooth([(500 + sx * 120, 520), (500 + sx * 240, 420), (500 + sx * 330, 330)], closed=False), 30)   # greater horns
        p.circle(500 + sx * 335, 322, 20, MED)
        p.circle(500 + sx * 110, 490, 18, MED)                             # lesser horns


# ======================================================================================================= limb bones
def _femur_outline(dx=0, k=1.0, left=False):
    pts = [(600, 120), (650, 140), (655, 220), (600, 300), (585, 360), (575, 600), (585, 780), (640, 840), (650, 900),
           (600, 935), (530, 915), (500, 885), (470, 915), (400, 935), (350, 900), (360, 840), (430, 780), (450, 600),
           (452, 380), (430, 330), (380, 290), (330, 255), (300, 205), (310, 150), (360, 120), (410, 135), (440, 180),
           (500, 225), (560, 200)]
    pts = [(500 + (x - 500) * k + dx, 500 + (y - 500) * k) for x, y in pts]
    return smooth(mirror(pts) if left else pts, per=5)


@art("femur")
def _(p, base):
    o = _femur_outline()
    p.outline(o, HEAVY, "bone")
    p.hatch_poly(o, 22, 45, FINE)
    p.circle(360, 185, 62, MED)                                            # head
    p.dot(345, 175, 8)                                                      # fovea
    p.curve([(455, 300), (500, 280), (575, 300)], FINE)                     # intertrochanteric line
    p.curve([(500, 900), (510, 860), (520, 900)], FINE)                     # intercondylar notch
    p.dashed(515, 320, 515, 780, FINE)                                       # linea aspera, behind


def _limbs(p, target_right=None):
    """Pelvis and both femurs, anterior view; one femur in heavy line."""
    pel = smooth([(300, 120), (500, 180), (700, 120), (760, 220), (700, 300), (600, 330), (560, 380), (500, 400), (440, 380),
                  (400, 330), (300, 300), (240, 220)], per=4)
    p.outline(pel, FINE, "paper")
    for right in (True, False):
        o = _femur_outline(0, 0.62, left=not right)
        o = [(x + (-150 if right else 150), y + 90) for x, y in o]
        if target_right is right:
            p.outline(o, HEAVY + 4, "bone")
            p.hatch_poly(o, 12, 45, FINE)
        else:
            p.outline(o, FINE, "paper")


ART["right_femur"] = lambda p, base: _limbs(p, True)
ART["left_femur"] = lambda p, base: _limbs(p, False)


def _long(p, top, bottom, shaft, h0, h1, extras=None):
    o = long_bone(top, bottom, shaft, h0, h1, .06)
    p.outline(o, HEAVY, "bone")
    p.hatch_poly(o, 22, 45, FINE)
    if extras:
        extras(p)


@art("humerus")
def _(p, base):
    _long(p, (500, 150), (500, 860), 70, 190, 220)
    p.circle(450, 160, 70, MED)                                             # head
    p.circle(560, 175, 30, FINE)                                            # greater tubercle
    p.curve([(430, 860), (470, 890), (530, 890), (570, 860)], MED)          # trochlea / capitulum
    p.circle(500, 815, 30, FINE)                                            # olecranon fossa (behind)


@art("radius")
def _(p, base):
    _long(p, (520, 140), (470, 870), 50, 80, 160)
    p.circle(520, 140, 40, MED)                                             # head
    p.circle(530, 230, 22, FINE)                                            # radial tuberosity
    p.line(410, 880, 400, 920, MED)                                         # styloid process


@art("ulna")
def _(p, base):
    _long(p, (480, 160), (520, 880), 44, 150, 70)
    p.arc(470, 190, 60, 300, 420, MED)                                       # trochlear notch
    p.circle(530, 890, 20, FINE)                                            # head
    p.line(545, 895, 560, 930, MED)                                         # styloid


@art("tibia")
def _(p, base):
    _long(p, (500, 130), (510, 880), 70, 260, 150)
    for sx in (-1, 1):
        p.outline(blob(500 + sx * 70, 110, 70, 26), MED)                    # condyles' plateaus
    p.circle(510, 230, 26, FINE)                                            # tibial tuberosity
    p.line(450, 880, 440, 930, MED)                                         # medial malleolus


@art("fibula")
def _(p, base):
    _long(p, (500, 120), (500, 900), 34, 80, 90)
    p.circle(500, 110, 34, MED)                                             # head
    p.line(500, 910, 510, 940, MED)                                         # lateral malleolus


@art("patella")
def _(p, base):
    o = smooth([(500, 200), (650, 260), (720, 420), (680, 620), (560, 800), (500, 830), (440, 800), (320, 620), (280, 420), (350, 260)], per=5)
    p.outline(o, HEAVY, "bone")
    p.hatch_poly(o, 18, 45, FINE)
    p.curve([(380, 300), (500, 270), (620, 300)], FINE)                     # quadriceps attachment
    p.outline(blob(500, 470, 150, 170), FINE)


@art("clavicle")
def _(p, base):
    centre = smooth([(130, 560), (260, 520), (420, 560), (580, 520), (760, 440), (870, 430)], closed=False)
    from patent_pen import _ribbon
    o = _ribbon(centre, 80)
    p.outline(o, HEAVY, "bone")
    p.hatch_poly(o, 18, 45, FINE)
    p.outline(blob(130, 560, 50, 60), MED, "bone")                          # sternal end
    p.outline(blob(880, 430, 40, 30), MED, "bone")                          # acromial end


@art("scapula")
def _(p, base):
    o = smooth([(260, 220), (520, 180), (700, 170), (760, 230), (720, 330), (520, 820), (470, 860), (430, 820), (240, 330)], per=5)
    p.outline(o, HEAVY, "bone")
    p.hatch_poly(o, 22, 45, FINE)
    p.ribbon(smooth([(270, 330), (480, 300), (680, 250), (800, 210)], closed=False), 46)   # the spine of the scapula
    p.outline(blob(820, 210, 70, 40, -15), MED, "bone")                     # acromion
    p.outline(blob(760, 300, 40, 60), MED)                                 # glenoid (seen edge-on)
    p.ribbon(smooth([(700, 200), (760, 140), (800, 150)], closed=False), 30)   # coracoid


@art("sternum")
def _(p, base):
    man = smooth([(400, 120), (600, 120), (640, 200), (580, 280), (420, 280), (360, 200)], per=5)
    body = smooth([(430, 290), (570, 290), (590, 500), (560, 700), (440, 700), (410, 500)], per=5)
    xi = smooth([(460, 710), (540, 710), (520, 820), (500, 860), (480, 820)], per=5)
    for o, t in ((man, HEAVY), (body, HEAVY), (xi, MED)):
        p.outline(o, t, "bone")
        p.hatch_poly(o, 18, 45, FINE)
    p.arc(500, 115, 40, 0, 180, MED)                                        # jugular notch
    for k in range(7):
        y = 230 + k * 70
        for sx in (-1, 1):
            p.line(500 + sx * 80, y, 500 + sx * 130, y - 10, FINE)          # costal notches


@art("pelvis")
def _(p, base):
    for sx in (-1, 1):
        ilium = smooth([(500 + sx * 60, 300), (500 + sx * 170, 160), (500 + sx * 330, 140), (500 + sx * 380, 240),
                        (500 + sx * 300, 420), (500 + sx * 280, 560), (500 + sx * 200, 700), (500 + sx * 40, 720),
                        (500 + sx * 40, 600), (500 + sx * 120, 480)], per=5)
        p.outline(ilium, HEAVY, "bone")
        p.hatch_poly(ilium, 22, 45, FINE)
        p.outline(blob(500 + sx * 170, 600, 60, 70), MED, "paper")         # obturator foramen
        p.circle(500 + sx * 290, 480, 56, MED)                              # acetabulum
    sac = smooth([(430, 300), (570, 300), (550, 460), (500, 540), (450, 460)], per=4)
    p.outline(sac, MED, "bone")
    p.line(500, 650, 500, 720, MED)                                          # pubic symphysis


# ============================================================================================================= organs
def _organ(p, pts, tint, hatch=26, per=5):
    o = smooth(pts, per=per)
    p.outline(o, HEAVY, tint)
    if hatch:
        p.hatch_poly(o, hatch, 45, FINE)
    return o


@art("brain")
def _(p, base):
    o = smooth([(170, 520), (190, 380), (280, 260), (420, 200), (580, 200), (720, 250), (820, 360), (840, 480), (800, 560),
                (700, 600), (640, 640), (520, 640), (420, 600), (300, 600), (210, 580)], per=6)
    p.outline(o, HEAVY, "brain")
    p.curve([(470, 205), (500, 330), (560, 420), (640, 470)], MED)                 # central sulcus
    p.curve([(280, 520), (400, 470), (560, 490), (700, 520)], MED)                 # lateral sulcus
    for pts in ([(250, 330), (330, 380), (300, 450)], [(360, 240), (400, 330), (360, 420)], [(600, 230), (620, 330), (700, 380)],
                [(700, 300), (760, 380), (800, 460)], [(560, 560), (620, 600)], [(350, 560), (430, 580)], [(260, 440), (220, 500)]):
        p.curve(pts, FINE)                                                          # gyri
    cb = smooth([(640, 640), (760, 610), (820, 660), (780, 730), (680, 730), (620, 690)], per=5)   # cerebellum
    p.outline(cb, MED, "brain")
    for k in range(4):
        p.curve([(650, 650 + k * 20), (720, 640 + k * 22), (800, 660 + k * 18)], FINE)
    p.ribbon(smooth([(600, 640), (590, 760), (580, 860)], closed=False), 60)        # brainstem


@art("heart")
def _(p, base):
    _organ(p, [(500, 860), (330, 700), (250, 520), (290, 360), (400, 320), (500, 380), (620, 320), (730, 380), (760, 540),
               (680, 720)], "organ", 0)
    p.curve([(470, 400), (540, 560), (520, 760)], MED)                               # anterior interventricular groove
    p.ribbon(smooth([(520, 340), (520, 220), (600, 140), (700, 150), (720, 230)], closed=False), 60)   # aortic arch
    for x in (560, 610, 660):
        p.line(x, 170, x - 10, 90, MED)                                              # arch branches
    p.ribbon(smooth([(420, 360), (380, 250), (300, 220)], closed=False), 52)          # pulmonary trunk
    p.ribbon(smooth([(330, 380), (300, 200), (300, 110)], closed=False), 40)          # superior vena cava
    p.hatch_poly(smooth([(500, 860), (330, 700), (300, 560), (430, 560), (520, 760)], per=4), 20, 45, FINE)


def _lung(p, right):
    s = -1 if right else 1      # the body's right lung sits on the viewer's left
    pts = [(500 + s * 60, 140), (500 + s * 160, 150), (500 + s * 300, 320), (500 + s * 360, 620), (500 + s * 340, 860),
           (500 + s * 200, 820), (500 + s * 80, 860), (500 + s * 40, 640), (500 + s * 30, 300)]
    if not right:                # the left lung's cardiac notch
        pts = pts[:7] + [(500 + s * 80, 700), (500 + s * 140, 600), (500 + s * 60, 480)] + pts[8:]
    o = _organ(p, pts, "lung", 0)
    p.curve([(500 + s * 50, 330), (500 + s * 200, 520), (500 + s * 330, 760)], MED)  # oblique fissure
    if right:
        p.curve([(500 + s * 140, 470), (500 + s * 260, 470), (500 + s * 350, 480)], MED)   # horizontal fissure: three lobes
    p.hatch_poly(o, 30, 45, FINE)
    p.ribbon(smooth([(500, 60), (500, 180), (500 + s * 40, 260)], closed=False), 40)  # bronchus


ART["right_lung"] = lambda p, base: _lung(p, True)
ART["left_lung"] = lambda p, base: _lung(p, False)


@art("liver")
def _(p, base):
    o = _organ(p, [(110, 380), (300, 250), (560, 240), (800, 300), (900, 400), (760, 520), (560, 640), (380, 700), (230, 640),
                   (130, 520)], "liver", 30)
    p.curve([(560, 245), (520, 420), (480, 650)], MED)                               # falciform ligament line
    p.outline(blob(400, 640, 50, 80, 20), MED, "bile")                              # gallbladder peeking
    p.ribbon(smooth([(560, 600), (600, 700), (640, 820)], closed=False), 26)         # common bile duct


@art("gallbladder")
def _(p, base):
    o = _organ(p, [(420, 180), (560, 200), (640, 380), (650, 600), (600, 720), (500, 740), (420, 640), (380, 420)], "bile", 24)
    p.ribbon(smooth([(450, 190), (400, 110), (330, 110), (300, 180), (300, 330)], closed=False), 30)   # cystic duct
    for k in range(4):
        p.curve([(430 + k * 30, 260), (450 + k * 30, 400), (440 + k * 30, 600)], FINE)


@art("pancreas")
def _(p, base):
    o = _organ(p, [(150, 560), (200, 440), (330, 420), (480, 470), (650, 420), (820, 330), (880, 370), (820, 460), (660, 540),
                   (480, 580), (330, 640), (220, 680)], "gland", 0)
    for k in range(10):
        x = 230 + k * 62
        p.curve([(x, 470 + (k % 3) * 10), (x + 30, 520), (x + 10, 580)], FINE)      # lobulation
    p.curve([(200, 600), (400, 530), (600, 490), (830, 400)], MED)                  # pancreatic duct


@art("spleen")
def _(p, base):
    _organ(p, [(300, 260), (520, 170), (720, 240), (780, 420), (700, 680), (520, 820), (360, 760), (420, 600), (380, 480),
               (300, 420)], "blood", 24)
    p.curve([(420, 480), (470, 520), (440, 600)], MED)                               # hilum
    p.line(440, 540, 340, 560, MED)


@art("stomach")
def _(p, base):
    o = _organ(p, [(420, 100), (470, 100), (480, 220), (600, 200), (760, 300), (800, 480), (720, 680), (520, 790), (330, 790),
                   (220, 720), (230, 640), (360, 660), (520, 620), (600, 480), (520, 380), (430, 300)], "gut", 0)
    for k in range(6):
        p.curve([(520 + k * 40, 260 + k * 30), (560 + k * 30, 420 + k * 20), (480 + k * 30, 640 + k * 10)], FINE)   # rugae
    p.ribbon(smooth([(445, 40), (445, 110)], closed=False), 50)                     # oesophagus
    p.ribbon(smooth([(230, 680), (150, 690), (120, 760)], closed=False), 50)        # duodenum


@art("small_intestine")
def _(p, base):
    p.outline(blob(500, 520, 330, 300), FINE)
    pts = []
    for row in range(6):
        y = 280 + row * 90
        xs = range(220, 790, 70) if row % 2 == 0 else range(780, 210, -70)
        for x in xs:
            pts.append((x, y + 24 * math.sin(x / 30)))
    from patent_pen import _ribbon
    tube = _ribbon(smooth(pts, closed=False, per=4), 52)
    p.outline(tube, MED, "gut")                                                   # the coiled tube, outlined
    p.curve(pts, FINE)                                                            # its lumen


@art("large_intestine")
def _(p, base):
    path = [(300, 880), (280, 740), (270, 520), (280, 300), (350, 220), (500, 230), (650, 220), (720, 300), (730, 520),
            (720, 720), (650, 800), (560, 780), (520, 860)]
    line = smooth(path, closed=False, per=6)
    from patent_pen import _ribbon
    o = _ribbon(line, 110)
    p.outline(o, HEAVY, "gut")
    for i in range(4, len(line) - 4, 7):
        (x0, y0), (x1, y1) = line[i - 1], line[i + 1]
        L = math.hypot(x1 - x0, y1 - y0) or 1
        nx, ny = -(y1 - y0) / L * 55, (x1 - x0) / L * 55
        p.line(line[i][0] - nx, line[i][1] - ny, line[i][0] + nx, line[i][1] + ny, FINE)   # haustra
    p.ribbon(smooth([(300, 880), (330, 940), (310, 980)], closed=False), 26)          # appendix


def _kidney(p, right):
    s = -1 if right else 1
    pts = [(500, 140), (640, 180), (720, 360), (720, 640), (640, 820), (500, 860), (420, 760), (450, 600), (380, 500),
           (450, 400), (420, 240)]
    pts = [(1000 - x, y) for x, y in pts] if right else pts   # hilum faces the midline
    o = smooth(pts, per=5)
    p.outline(o, HEAVY, "kidney")
    cx = 450 if not right else 550
    for k in range(5):
        y = 300 + k * 90
        p.outline(blob(cx + s * 150, y, 46, 30, s * 20), FINE)                     # pyramids
    p.ribbon(smooth([(cx + s * 40, 420), (cx - s * 20, 500), (cx - s * 40, 900)], closed=False), 30)   # ureter
    p.ribbon(smooth([(cx - s * 30, 460), (cx - s * 200, 440)], closed=False), 30)                      # renal vessels


ART["right_kidney"] = lambda p, base: _kidney(p, True)
ART["left_kidney"] = lambda p, base: _kidney(p, False)


@art("urinary_bladder")
def _(p, base):
    o = _organ(p, [(500, 220), (680, 300), (760, 480), (700, 680), (560, 780), (440, 780), (300, 680), (240, 480), (320, 300)], "soft", 0)
    for k in range(5):
        p.curve([(320 + k * 20, 400 + k * 60), (500, 380 + k * 70), (680 - k * 20, 400 + k * 60)], FINE)   # detrusor folds
    for sx in (-1, 1):
        p.ribbon(smooth([(500 + sx * 120, 330), (500 + sx * 240, 180), (500 + sx * 260, 60)], closed=False), 26)   # ureters
    p.ribbon(smooth([(500, 780), (500, 930)], closed=False), 34)                    # urethra


@art("thyroid")
def _(p, base):
    for sx in (-1, 1):
        _organ(p, [(500 + sx * 40, 520), (500 + sx * 150, 640), (500 + sx * 230, 560), (500 + sx * 240, 380), (500 + sx * 170, 260),
                   (500 + sx * 110, 330), (500 + sx * 80, 470)], "gland", 22)
    _organ(p, [(440, 500), (560, 500), (560, 580), (440, 580)], "gland", 0)          # isthmus
    p.ribbon(smooth([(500, 80), (500, 920)], closed=False), 120) if False else None
    for y in range(140, 900, 70):
        p.rect(440, y, 120, 36, 18, FINE)                                            # trachea behind


@art("esophagus")
def _(p, base):
    line = smooth([(500, 60), (490, 300), (470, 520), (500, 700), (560, 860), (600, 920)], closed=False, per=6)
    from patent_pen import _ribbon
    o = _ribbon(line, 90)
    p.outline(o, HEAVY, "gut")
    p.hatch_poly(o, 24, 45, FINE)
    for y, w in ((280, 120), (560, 130)):
        p.line(500 - w, y, 500 + w, y, FINE)                                         # constrictions
    p.outline(blob(660, 900, 110, 60, 20), MED, "gut")                               # cardia of the stomach


@art("trachea")
def _(p, base):
    p.outline(smooth([(440, 80), (560, 80), (560, 620), (440, 620)], per=3), HEAVY, "soft")
    for y in range(110, 600, 40):
        p.rect(442, y, 116, 24, 10, MED, "paper")                                   # C-shaped cartilage rings
    for sx in (-1, 1):
        p.ribbon(smooth([(500 + sx * 20, 620), (500 + sx * 120, 760), (500 + sx * 220, 900)], closed=False), 70)   # main bronchi
        for k in range(4):
            y = 680 + k * 50
            p.line(500 + sx * (80 + k * 40), y - 30, 500 + sx * (130 + k * 40), y + 20, FINE)


@art("skin")
def _(p, base):
    p.box(120, 200, 760, 600, 0, "skin")
    p.curve([(120, 300), (250, 280), (380, 310), (520, 280), (660, 310), (880, 290)], MED)    # dermal papillae / epidermis
    p.hatch(120, 200, 760, 90, 14, 45)                                                     # epidermis
    p.line(120, 560, 880, 560, MED)                                                        # dermis | hypodermis
    for x in range(160, 880, 80):
        for y in (620, 700):
            p.circle(x + (y % 3) * 10, y + 20, 30, FINE)                                   # fat lobules
    p.ribbon(smooth([(420, 120), (430, 220), (440, 380), (440, 480)], closed=False), 14)    # hair shaft
    p.outline(blob(440, 500, 40, 60), MED)                                                 # follicle bulb
    p.outline(blob(500, 420, 40, 24), FINE)                                                # sebaceous gland
    p.curve([(680, 200), (690, 300), (660, 380), (700, 440), (670, 500)], MED)              # sweat duct
    p.outline(blob(680, 520, 40, 30), FINE)


# ================================================================== whole regions, for the demo's skeleton assembly
def _region_hand(p):
    for outline in _hand_parts().values():
        p.outline(outline, MED, "bone")


def _region_foot(p):
    for outline in _foot_parts().values():
        p.outline(outline, MED, "bone")


def _region_ribcage(p):
    for i in range(1, 13):
        for right in (True, False):
            line, front = _rib_line(i, right)
            p.ribbon(line, 18)
            if i <= 7:
                p.line(front[0], front[1], 500 + (-24 if right else 24), 230 + i * 42, FINE)
    p.outline(smooth([(470, 196), (530, 196), (542, 250), (524, 296), (532, 520), (514, 576), (500, 610), (486, 576), (468, 520),
                      (476, 296), (458, 250)], per=5), MED, "bone")


def _region_spine(p):
    """The column from the front: 24 vertebral bodies, their transverse processes, sacrum and coccyx."""
    y = 40
    for k, name in enumerate(LEVELS):
        h = 26 if k < 7 else 32 if k < 19 else 42
        w = 46 + k * 2.6
        p.rect(500 - w / 2, y, w, h - 6, 6, MED, "bone")
        tw = w / 2 + (26 if k < 7 else 40 if k < 19 else 52)
        p.line(500 - tw, y + h / 2 - 3, 500 + tw, y + h / 2 - 3, MED)
        y += h
    p.outline(smooth([(410, y + 4), (590, y + 4), (560, y + 110), (500, y + 160), (440, y + 110)], per=4), MED, "bone")


REGIONS = {"hand": _region_hand, "foot": _region_foot, "ribcage": _region_ribcage, "spine": _region_spine}


def draw_region(name: str) -> Pen:
    p = Pen()
    REGIONS[name](p)
    return p
