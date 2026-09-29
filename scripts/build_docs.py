#!/usr/bin/env python3
"""Write the small webfont CSS package after font artifacts exist."""

import re
import shutil
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    (ROOT / "dist").mkdir(exist_ok=True)
    css = """@font-face {\n  font-family: \"BONES\";\n  src: url(\"./BONES.woff2\") format(\"woff2\");\n  font-weight: 400;\n  font-style: normal;\n  font-display: swap;\n}\n@font-face {\n  font-family: \"BONES Color\";\n  src: url(\"./BONES-Color.woff2\") format(\"woff2\");\n  font-weight: 400;\n  font-style: normal;\n  font-display: swap;\n}\n.bones { font-family: \"BONES\", sans-serif; font-variant-ligatures: common-ligatures; }\n.bones-emoji { font-family: \"BONES Color\", \"BONES\", sans-serif; font-variant-ligatures: common-ligatures; }\n"""
    (ROOT / "dist/bones.css").write_text(css, encoding="utf-8")
    docs_assets = ROOT / "docs/assets"
    docs_assets.mkdir(parents=True, exist_ok=True)
    for filename in ("BONES.woff2", "BONES-Color.woff2"):
        shutil.copy2(ROOT / "dist" / filename, docs_assets / filename)
    docs_assets.joinpath("bones.css").write_text(css, encoding="utf-8")
    index = ROOT / "docs/index.html"
    text = index.read_text(encoding="utf-8")
    version = yaml.safe_load((ROOT / "project.yaml").read_text())["version"]
    text = re.sub(r"BONES\.OTF / [0-9]+\.[0-9]+\.[0-9]+", f"BONES.OTF / {version}", text)
    index.write_text(text, encoding="utf-8")
    print("wrote dist/bones.css")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
