# Anatomical artwork sources

## The glyph art (since 0.2): original patent-style drawings

Every object has its own original line drawing in `scripts/anatomy_art.py`, drawn with the pen in
`scripts/patent_pen.py` (every line is a filled outline, so one drawing is the SVG, the mono glyph and the color
layers). Patent-plate conventions: heavy outline, medium detail, fine section hatching, dashed hidden lines (the
vomer and palatine inside the skull). Series bones are drawn in context - the whole hand, foot, rib cage, spinal
column or skull in fine line, the object heavy and hatched - and left-side objects mirror the right (anatomical
position). Vertebral levels carry a small spinal column with their level filled in.

Earlier releases traced Gray's plates directly; those traces shared one crop between many objects (every phalanx
showed the same hand plate) and carried plate noise. The plates below remain the anatomical reference.

## Reference: Gray's Anatomy (1918)

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
