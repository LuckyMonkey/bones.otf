# Bone artwork sources

The representative bone set uses a visual language based on the public-domain
1918 U.S. 20th edition of *Gray's Anatomy of the Human Body*. The scans are from
Wikimedia Commons and are retained as provenance references in
`sources/gray-plates/raw/`. The exact file page for each source, edition, and
license note is in `sources/gray-plates.yaml`.

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
distinct objects even where one plate contains several bones. The derivative
artwork is simplified for font rendering and is not a clinical or diagnostic
image.

The source edition is public domain in the United States. The project still
keeps the source URLs and attribution trail because historical plate copyright
status and reuse rules can vary by jurisdiction.
