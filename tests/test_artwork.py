import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class GrayArtworkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())
        cls.bones = [item for item in cls.data["objects"] if item["category"] == "bone"]

    def test_every_object_has_its_own_original_drawing(self):
        import hashlib
        import re
        seen = {}
        for item in self.data["objects"]:
            name = item["id"].split(":", 1)[1]
            mono = (ROOT / item["glyph"]["monochrome"]).read_text()
            color = (ROOT / item["glyph"]["color"]).read_text()
            self.assertIn('data-source="bones-patent-art"', mono, item["id"])
            self.assertIn('data-source="bones-patent-art"', color, item["id"])
            self.assertEqual(set(re.findall(r'fill="(#[0-9a-f]{6})"', mono)), {"#17252c"}, item["id"])   # mono: one ink
            digest = hashlib.sha256("".join(re.findall(r' d="([^"]+)"', mono)).encode()).hexdigest()
            self.assertNotIn(digest, seen, f"{name} draws exactly like {seen.get(digest)}")
            seen[digest] = name

    def test_left_and_right_mirror(self):
        import re
        left = (ROOT / "glyphs/mono/left_scaphoid.svg").read_text()
        right = (ROOT / "glyphs/mono/right_scaphoid.svg").read_text()
        self.assertNotEqual(left, right)

    def test_raw_plate_provenance_is_present(self):
        manifest = yaml.safe_load((ROOT / "sources/gray-plates.yaml").read_text())
        self.assertEqual(manifest["license"], "Public domain")
        self.assertGreaterEqual(len(manifest["plates"]), 15)
        self.assertGreaterEqual(len(manifest["organs"]), 18)
        self.assertGreaterEqual(len(list((ROOT / "sources/gray-plates/raw").iterdir())), 14)
        self.assertGreaterEqual(len(list((ROOT / "sources/gray-plates/raw/organs").iterdir())), 16)


if __name__ == "__main__":
    unittest.main()
