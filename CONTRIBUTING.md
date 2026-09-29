# Contributing

The canonical object is the anatomy entry in `ontology/anatomy.yaml`; a glyph is
only one rendering of it. Add or revise the object first, record provenance, and
then add a vector design. Never recycle a released PUA codepoint. Use
`review_required: true` when an anatomical classification or outline needs
expert review.

Run `make test` before opening a change. Generated files are intentionally
reproducible and should be refreshed by the build rather than edited by hand.

