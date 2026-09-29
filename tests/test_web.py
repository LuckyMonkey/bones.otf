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

    def test_generated_metadata_is_accessible(self):
        metadata = (ROOT / "packages/js/index.js").read_text()
        self.assertIn("accessible_label", metadata)
        self.assertIn("anatomy:left_femur", metadata)


if __name__ == "__main__":
    unittest.main()

