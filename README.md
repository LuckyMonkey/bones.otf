# BONES.OTF 🦴

[![Validate BONES](https://github.com/LuckyMonkey/bones.otf/actions/workflows/ci.yml/badge.svg)](https://github.com/LuckyMonkey/bones.otf/actions/workflows/ci.yml)
[![Deploy demo](https://github.com/LuckyMonkey/bones.otf/actions/workflows/pages.yml/badge.svg)](https://github.com/LuckyMonkey/bones.otf/actions/workflows/pages.yml)
[![Live demo](https://img.shields.io/badge/demo-live-b54c4e)](https://luckymonkey.github.io/bones.otf/)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Font: OFL](https://img.shields.io/badge/font-OFL--1.1-gold.svg)](font/OFL.txt)

BONES.OTF is an open anatomical symbol system.

Human anatomy has rich semantic identity but very little general-purpose
typographic representation. BONES gives anatomical structures stable object
identities, Unicode-compatible representations, semantic text aliases, vector
glyphs, and emoji-like rendering.

It is not Wingdings. 🧬

Ordinary letters are never repurposed. Authors write `:femur:` or
`:left_kidney:`; without BONES installed, that text remains exactly meaningful.
With BONES selected, a shaping engine turns the colon-delimited token into the
corresponding anatomical glyph. Direct PUA characters are available when a
machine-readable single character is required, but a PUA codepoint is not an
official Unicode Consortium anatomical character.

## What is in 0.1.0

The 0.1.0 release proved the complete path with 35 objects: 17 skeletal
objects (including left/right femur identities) and 18 organs/tissues. Every
object has a canonical ID, provenance, stable PUA assignment, shortcode,
monochrome SVG, color SVG, font glyph, accessible label, and generated metadata.

The current development tree expands that vertical slice to 204 objects: 186
bones, 17 organs, and one tissue. It includes named cranial/facial bones,
individual C1–C7, T1–T12, and L1–L5 vertebral levels, sacrum, coccyx, numbered
ribs, carpals, metacarpals, hand phalanges, tarsals, metatarsals, and foot
phalanges.

Artifacts include `dist/BONES.otf`, `dist/BONES.ttf`, `dist/BONES-Color.otf`,
`dist/BONES-Color.ttf`, WOFF2 files, SVG assets, PNG exports, a zero-framework
specimen site in `docs/`, and a small JavaScript package in `packages/js/`.

Open [`demo.html`](demo.html) for the standalone live rendering demo, or
[`docs/index.html`](docs/index.html) for the full searchable specimen registry.

## See it live 🚀

- **[Open the BONES demo](https://luckymonkey.github.io/bones.otf/)** — the
  x-ray assembly, color glyphs, semantic playground, and anatomy cards.
- **[Search the full specimen registry](https://luckymonkey.github.io/bones.otf/docs/)**
  — filter bones, organs, and tissues; copy shortcodes or PUA characters.
- **[Download the WOFF2 webfonts](https://github.com/LuckyMonkey/bones.otf/tree/main/dist)**
  — use the monochrome or COLRv1 color renderer in your own page.

The smallest honest demo is:

```text
🦴 Fracture of the :left_femur:.
🧠 :brain:  🫀 :heart:  🫁 :left_lung:
```

The emoji are ordinary Unicode examples. The colon-delimited names are BONES
semantic text; the font turns them into detailed anatomy glyphs when selected.
If the font is missing, the source still says what the author meant. 🎨

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

For the user-facing examples and accessibility rules, read
[`docs/using.md`](docs/using.md). ♿

## Usage

```html
<link rel="stylesheet" href="./dist/bones.css">
<span class="bones" aria-label="Femur">:femur:</span>
<span class="bones" role="img" aria-label="Left kidney">:left_kidney:</span>

<!-- A readable semantic fallback plus a color/emoji-like renderer. -->
<span class="bones-emoji" role="img" aria-label="Heart">:heart:</span>
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
[`docs/accessibility.md`](docs/accessibility.md) and
[`docs/anatomical-review.md`](docs/anatomical-review.md).

## Repository map 📚

- `ontology/` — canonical anatomy objects and provenance.
- `registry/` — append-only PUA assignments, aliases, and ligatures.
- `glyphs/` — deterministic monochrome and color SVG masters.
- `dist/` — font release artifacts and webfont CSS.
- `packages/js/` — generated JavaScript/TypeScript metadata API.
- `docs/` — searchable specimen site and project guidance.
- `.github/workflows/` — reproducible validation and Pages deployment.

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
coverage reference. The representative bone and organ glyphs are derived from
cleaned, thresholded traces of public-domain 1918 Gray's Anatomy plates hosted
by Wikimedia Commons; the plate manifest, raw scans, crop recipes, and
deterministic trace script are kept under `sources/gray-plates/`. BONES ships
vector derivatives, not proprietary modern medical illustrations. See
`docs/artwork-sources.md` for the provenance and regeneration path.

## Project status

The current tree is an independently usable expanded slice, not a claim that
every adult skeletal substructure or view is clinically complete. Repeated
carpals, phalanges, ribs, and tarsals have distinct canonical identities and
may explicitly share a small-size glyph master. `review_required` identifies
where an anatomy expert should review classification or outline before 1.0.

The public demo is a release-quality MVP, not a clinical reference tool. Please
report anatomical corrections with sources; stable object IDs and released PUA
assignments are never casually recycled. 🔬
