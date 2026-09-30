# Release checklist 🚀

This is the operational checklist for turning the public MVP into a stable 1.0
release. The repository already builds and deploys; these items are the remaining
release gates, not hidden dependencies.

## Before a tagged release

- [ ] Review every `review_required: true` object with an anatomy-aware reviewer.
- [ ] Run `make test` from a clean checkout and keep the generated-file diff empty.
- [ ] Open the Pages demo in Chromium, Firefox, and a mobile viewport.
- [ ] Test `:femur:`, `:heart:`, and `:left_kidney:` with surrounding prose.
- [ ] Test missing-font fallback, screen-reader labels, copy shortcode, and copy PUA.
- [ ] Verify the Gray's Anatomy provenance and license notices for redistributed assets.
- [ ] Decide whether the JavaScript package should be published to npm as `bones-otf`.
- [ ] Update `project.yaml`, `CHANGELOG.md`, and `CITATION.cff` together.

## 1.0 invariants

After 1.0, released anatomy IDs and PUA pairs are append-only. Labels and aliases
may improve, and glyph geometry may be refined, but a released codepoint must never
be reused for another object. Official Unicode standardization is optional and does
not replace the canonical BONES object ID. 🔒

## Deployment

The `main` branch runs `.github/workflows/ci.yml` and
`.github/workflows/pages.yml`. Pages publishes the x-ray demo at the repository
root and the searchable registry under `/docs/`; it copies only webfont, SVG, and
source-reference assets, not the large PNG export directory.
