#!/usr/bin/env python3
"""Write the small webfont CSS package after font artifacts exist."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist/bones.css").write_text("""@font-face {\n  font-family: \"BONES\";\n  src: url(\"./BONES.woff2\") format(\"woff2\");\n  font-weight: 400;\n  font-style: normal;\n  font-display: swap;\n}\n@font-face {\n  font-family: \"BONES Color\";\n  src: url(\"./BONES-Color.woff2\") format(\"woff2\");\n  font-weight: 400;\n  font-style: normal;\n  font-display: swap;\n}\n.bones { font-family: \"BONES\", sans-serif; font-variant-ligatures: common-ligatures; }\n.bones-emoji { font-family: \"BONES Color\", \"BONES\", sans-serif; font-variant-ligatures: common-ligatures; }\n""", encoding="utf-8")
    print("wrote dist/bones.css")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

