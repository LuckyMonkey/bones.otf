# Using BONES.OTF 🦴

BONES has two interfaces: readable semantic text and direct Unicode-compatible
Private Use Area characters. The semantic form is the portable default:

```text
🦴 Fracture of the :left_femur:.
🫀 The :heart: is a canonical anatomy object.
🧠 Search for :brain:, :pancreas:, or :left_kidney:.
```

Without the font, those colon-delimited names remain readable. With the font,
the `liga` feature shapes them into anatomical glyphs. The familiar emoji above
are ordinary standardized Unicode examples; BONES symbols are emoji-like font
renderings and are not official Unicode emoji. 🎨

## Webfont

```html
<link rel="stylesheet" href="dist/bones.css">

<p class="bones" aria-label="Fracture of the left femur">
  Fracture of the :left_femur:.
</p>
```

For a direct character, resolve the canonical object first and keep the label:

```html
<span class="bones-emoji" role="img" aria-label="Heart">&#xE010;</span>
```

Do not put a bare PUA character in accessible prose. A screen reader cannot
infer that `U+E010` means “heart”; the semantic source or an explicit
`aria-label` is required. See [accessibility.md](accessibility.md). ♿

## JavaScript metadata

```js
import { get, resolveShortcode, unicodeFor } from "bones-otf";

const femur = get("anatomy:femur");
resolveShortcode(":heart:");
unicodeFor("anatomy:left_kidney");
```

Each record includes the stable ID, label, category, shortcode, PUA codepoint,
SVG locations, provenance, and accessible label. The object ID is canonical;
the glyph, filename, and codepoint are renderers or registry assignments. 🔖

## Source artwork

The representative vector masters are deterministic traces of public-domain
1918 Gray's Anatomy plates hosted by Wikimedia Commons. They are simplified for
font use, not clinical diagnostic illustrations. Read
[artwork-sources.md](artwork-sources.md) before redistributing derivatives. 🫁

## Build locally

```sh
make install   # once
make test      # build everything and run validation
make site      # write the deployable Pages artifact to _site/
```

The generated artifact contains the live demo at `index.html` and the searchable
registry at `docs/index.html`. 🚀
