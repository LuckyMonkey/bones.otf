# BONES.OTF

BONES.OTF is an open anatomical symbol system.

Human anatomy has rich semantic identity but very little general-purpose
typographic representation. BONES gives anatomical structures stable object
identities, Unicode-compatible representations, semantic text aliases, vector
glyphs, and emoji-like rendering.

It is not Wingdings.

Ordinary letters are never repurposed. Authors write `:femur:` or
`:left_kidney:`; without BONES installed, that text remains exactly meaningful.
With BONES selected, a shaping engine turns the colon-delimited token into the
corresponding anatomical glyph. Direct PUA characters are available when a
machine-readable single character is required, but a PUA codepoint is not an
official Unicode Consortium anatomical character.

## What is in 0.1.0

The first release proves the complete path with 35 objects: 17 skeletal
objects (including left/right femur identities) and 18 organs/tissues. Every
object has a canonical ID, provenance, stable PUA assignment, shortcode,
monochrome SVG, color SVG, font glyph, accessible label, and generated metadata.

Artifacts include `dist/BONES.otf`, `dist/BONES.ttf`, `dist/BONES-Color.otf`,
`dist/BONES-Color.ttf`, WOFF2 files, SVG assets, PNG exports, a zero-framework
specimen site in `docs/`, and a small JavaScript package in `packages/js/`.

Open `demo.html` for the standalone live rendering demo, or `docs/index.html`
for the full searchable specimen registry.

## Build

```sh
make install       # once, creates .venv and installs open build dependencies
make build         # validate, generate, compile, export, and build the specimen
make test          # build plus ontology, font, shaping, and web checks
make clean
```

The project version is authoritative in `project.yaml`; generated package and
font metadata derive from it. The build uses the vendored DejaVu Sans base only for ordinary prose glyphs.
This means `Fracture of the :left_femur:.` retains readable surrounding text
when BONES is selected, while the semantic token shapes through a `liga`
feature. The anatomical glyphs themselves originate only from the checked-in
generated SVG vector sources. FontTools creates TrueType-outline `.ttf`, CFF
`.otf`, compact WOFF2, and COLRv1 palette layers; no proprietary font
application is required. See `docs/licensing.md` for the mixed provenance of
the inherited prose outlines and original BONES glyphs.

## Usage

```html
<link rel="stylesheet" href="./dist/bones.css">
<span class="bones" aria-label="Femur">:femur:</span>
<span class="bones" role="img" aria-label="Left kidney">:left_kidney:</span>
```

The JavaScript helper resolves both semantic IDs and shortcodes:

```js
import { get, unicodeFor, resolveShortcode } from "bones-otf";
get("anatomy:femur");
unicodeFor("anatomy:femur");
resolveShortcode(":heart:");
```

Private-use characters need an explicit accessible label in HTML. Do not expose
`U+E00B` to a screen reader as if it were a standard Unicode character. See
`docs/accessibility.md` and `docs/anatomical-review.md`.

## Identity and Unicode

The anatomy object is canonical. Its ID survives changes to filenames, labels,
glyph outlines, and language. `registry/codepoints.csv` is append-only after a
release: released PUA codepoints are never reassigned. The current range starts
at U+E000, reserved inside this project only. `unicode-proposal/` documents how
the same IDs could later map to official Unicode characters without changing
the object model.

## Sources and scope

The ontology records UBERON identifiers where an exact open term is available,
and the project records OpenStax Anatomy & Physiology as the human-skeletal
coverage reference. Bone glyphs are now derived from cleaned, thresholded traces
of public-domain 1918 Gray's Anatomy plates hosted by Wikimedia Commons; the
plate manifest, raw scans, crop recipes, and deterministic trace script are kept
under `sources/gray-plates/`. BONES ships vector derivatives, not proprietary
modern medical illustrations. See `docs/artwork-sources.md` for the provenance
and regeneration path.

## Project status

0.1.0 is an independently usable vertical slice, not a claim of complete adult
skeletal coverage. The registry deliberately marks future individual carpals,
metacarpals, tarsals, phalanges, ribs, and vertebral levels for expansion rather
than assigning guessed identities. The initial objects are fully wired end to
end and `review_required` identifies where an anatomy expert should review the
classification or outline before a 1.0 release.
