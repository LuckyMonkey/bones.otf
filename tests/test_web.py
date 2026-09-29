import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WebPackageTest(unittest.TestCase):
    def test_css_and_specimen_exist(self):
        css = (ROOT / "dist/bones.css").read_text()
        html = (ROOT / "docs/index.html").read_text()
        self.assertIn('font-family: "BONES"', css)
        self.assertIn("BONES-Color.woff2", css)
        self.assertIn("Search anatomy", html)
        self.assertIn("Copy shortcode", (ROOT / "docs/app.js").read_text())
        self.assertIn('item.color_svg', (ROOT / "docs/app.js").read_text())
        self.assertIn('data-bones-asset-prefix="../"', html)

    def test_generated_metadata_is_accessible(self):
        metadata = (ROOT / "packages/js/index.js").read_text()
        self.assertIn("accessible_label", metadata)
        self.assertIn("anatomy:left_femur", metadata)
        self.assertIn("Object.values(item.external_ids", metadata)
        self.assertIn("anatomy:lower_limb", (ROOT / "registry/groups.csv").read_text())

    def test_pages_site_has_local_webfont_assets(self):
        self.assertTrue((ROOT / "docs/assets/BONES.woff2").is_file())
        self.assertIn('url("./BONES.woff2")', (ROOT / "docs/assets/bones.css").read_text())

    def test_root_demo_page_is_wired(self):
        demo = (ROOT / "demo.html").read_text()
        self.assertIn('href="dist/bones.css"', demo)
        self.assertIn('src="docs/registry.js"', demo)
        self.assertIn('glyphs/mono/femur.svg', demo)
        self.assertIn('id="organ-atlas"', demo)
        self.assertIn('renderOrganAtlas', (ROOT / "docs/app.js").read_text())
        self.assertIn('id="playground"', demo)


if __name__ == "__main__":
    unittest.main()
