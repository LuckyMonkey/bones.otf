# Changelog

## Unreleased

- Replaced the initial symbolic bone silhouettes with deterministic, source-derived
  Gray's Anatomy plate trace masters for the representative bone set, including
  separate radius/ulna and tibia/fibula crops, preserved engraved detail, and
  restrained red plate accents in color output.
- Added public-domain plate provenance, raw source scans, crop manifest, and the
  optional OpenCV trace step under `sources/gray-plates/`.
- Added explicit anatomy grouping nodes and review flags to the canonical ontology.
- Hardened append-only PUA validation against moved or deleted released objects.
- Preserved mono glyph detail with body/detail roles and knockout contours.
- Added UBERON-aware search, compact reproducible webfonts, real CFF `.otf` output,
  GitHub Pages-local assets, and parallel PNG export.

## 0.1.0 - 2026-09-29

- Initial vertical slice: 35 canonical human anatomy objects across bones and organs.
- Stable PUA registry, colon-delimited ligatures, monochrome and COLRv1 color fonts.
- Deterministic SVG, PNG, font, WOFF2, metadata package, and specimen-site build.
- Ontology provenance, accessibility guidance, shaping tests, and validation scripts.
