# Licensing and provenance

BONES.OTF has deliberately separate licensing layers:

- Source code, validation scripts, metadata, documentation, and ontology files are MIT.
- Original BONES SVG artwork and the cleaned/traced BONES derivatives of the
  public-domain Gray's Anatomy plates are OFL-1.1.
- The historical Gray's Anatomy scans in `sources/gray-plates/raw/` are public
  domain in the United States; their individual Commons pages and the source
  edition are recorded in `sources/gray-plates.yaml`.
- The generated fonts also contain the vendored DejaVu Sans outline set used for ordinary prose and fallback text. Its upstream license is included at `font/sources/DEJAVU-LICENSE.txt` and remains applicable to those inherited outlines.
- UBERON identifiers and the OpenStax coverage reference are provenance records, not copied artwork or a wholesale export of either source.

The `.ttf` files are TrueType-outline OpenType fonts. The `.otf` files are CFF
OpenType fonts. Both carry the same BONES semantic glyph set, but users should
keep the upstream DejaVu notice when redistributing a complete font artifact.
