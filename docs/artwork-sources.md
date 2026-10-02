# Anatomical artwork sources

## Every bone is its own figure from Gray's (since 0.2)

Each of the 186 bone objects is traced from the figure Gray drew of *that bone* - the atlas from Fig. 86, the
lunate from Fig. 222, the third metatarsal from Fig. 286 - not a crop shared with its neighbours. The table is
`sources/gray-plates/figures.yaml` (figure, crop, mirror); the scans are in `sources/gray-plates/raw/figures/`
with their Commons URLs in `index.json`. Where Gray drew one bone for a series (C3-C6, T2-T8, the central ribs)
those objects share his figure; where he drew them apart (T1, T9-T12, the first and the 10th-12th ribs) they are
apart. Gray's carpal, metacarpal, tarsal and metatarsal figures are left bones; the right ones are mirrored. Hand
phalanges are cut from Fig. 220 with Commons' highlighted versions of that plate; toe phalanges from Fig. 268,
split at the joints.

```text
figure scan -> crop -> remove Gray's red attachment lines -> 4x upscale -> ink (dark in every channel)
            -> drop label letters (Tesseract word boxes; only ink wholly inside a word is removed)
            -> bone mask (close + fill + open: drops the labels' leader lines) -> ink inside the mask
            -> potrace Bezier outlines -> 1000-unit em; mono = ink, color = ink over a paper silhouette
```

Run it with OpenCV, Tesseract and potracer: `~/.venvs/trace/bin/python scripts/trace_gray_figures.py [names]`.
The engraving is kept as engraving - every hatch line is an outline - so a glyph holds hundreds to thousands of
contours; that is the point (the font is a vector source for graphics pipelines, not a set of icons).

## The 0.1 plate traces

The representative bone and organ set uses a visual language based on the public-domain
1918 U.S. 20th edition of *Gray's Anatomy of the Human Body*. The scans are from
Wikimedia Commons and are retained as provenance references in
`sources/gray-plates/raw/`. The exact file page for each source, edition, and
license note is in `sources/gray-plates.yaml`. The current source set covers
186 bone objects across 48 source-derived glyph bases and the existing
organ/tissue vertical slice, including
brain, heart, lungs, liver, gallbladder, pancreas, spleen, stomach, intestines,
kidneys, bladder, thyroid, esophagus, trachea, and skin.

The repository does not load raster images into the font. The source-art step is:

```text
public-domain plate scan
        ↓ crop per anatomical object
        ↓ grayscale threshold + red-accent separation
        ↓ contour cleanup
        ↓ deterministic SVG paths
        ↓ BONES mono / COLRv1 font glyphs
```

Run the optional trace step with a Python environment containing OpenCV:

```sh
make trace
make build
```

The generated `glyphs/gray-trace/*.svg` files are the committed vector masters
used by normal builds. Crops are intentionally separate for semantically
distinct objects even where one plate contains several structures. The
derivative artwork is simplified for font rendering and is not a clinical or
diagnostic image.

The source edition is public domain in the United States. The project still
keeps the source URLs and attribution trail because historical plate copyright
status and reuse rules can vary by jurisdiction.
