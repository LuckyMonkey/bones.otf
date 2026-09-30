# Changelog

## Unreleased

- Added public-repository release plumbing: reproducible CI, GitHub Pages
  deployment, a trimmed deployable site artifact, README badges, issue templates,
  security policy, citation metadata, and emoji-forward usage documentation.
- Updated the demo skeleton assembly without changing its x-ray frame or splayed layout:
  added the 24-rib cage, individually placed C1–L5 vertebral levels, mandible,
  sacrum/coccyx, hand anchors, and foot anchors, with an expanded object index.
- Expanded the skeletal ontology from 17 to 186 bone objects: named cranial and
  facial bones, C1–C7, T1–T12, L1–L5, sacrum, coccyx, numbered ribs, carpals,
  metacarpals, hand phalanges, tarsals, metatarsals, and foot phalanges.
- Added 15 Gray-derived trace families for the new small-bone and vertebral
  masters, with append-only PUA assignments through U+E0CB and explicit shared
  glyph-base declarations for repeated structures.
- Replaced the initial symbolic bone silhouettes with deterministic, source-derived
  Gray's Anatomy plate trace masters for the representative bone set, including
  separate radius/ulna and tibia/fibula crops, preserved engraved detail, and
  restrained red plate accents in color output.
- Extended the same source-derived vector treatment to the representative organ
  and tissue set: brain, heart, lungs, liver, gallbladder, pancreas, spleen,
  stomach, intestines, kidneys, bladder, thyroid, esophagus, trachea, and skin.
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
