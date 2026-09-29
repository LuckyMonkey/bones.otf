# Future Unicode standardization

BONES currently assigns project-stable Private Use Area codepoints beginning at
U+E000. These characters are Unicode-encoded, but they are not official Unicode
Consortium anatomical characters and have no portable meaning without BONES.

The canonical identity remains `anatomy:femur` (or another registry ID). A
future mapping table may connect one object to its BONES PUA, an official
Unicode codepoint if one is ever accepted, and any platform-specific emoji
presentation. No released PUA assignment will be reused.

Evidence for a proposal should include:

- stable object and shortcode demand;
- cross-platform use cases;
- existing generic Unicode anatomy coverage and the gap;
- clear glyph semantics and accessibility behavior;
- a public registry and a compatibility plan.

The generated snapshot in `statistics.json` records the current object/category,
system, PUA, shortcode, and external-identifier counts without pretending that
the PUA assignments are standardized Unicode characters.
