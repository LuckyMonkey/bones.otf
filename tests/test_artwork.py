import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class GrayArtworkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())
        cls.bones = [item for item in cls.data["objects"] if item["category"] == "bone"]

    def test_every_anatomy_object_uses_a_trace_master(self):
        for item in self.data["objects"]:
            mono = (ROOT / item["glyph"]["monochrome"]).read_text()
            color = (ROOT / item["glyph"]["color"]).read_text()
            self.assertIn('data-source="gray-anatomy"', mono, item["id"])
            self.assertIn('data-source="gray-anatomy"', color, item["id"])
            self.assertNotIn('#b4384c', mono, item["id"])
            self.assertNotIn('data-layer="paper"', mono, item["id"])        # mono is Gray's ink alone

    def test_every_bone_is_traced_from_its_own_gray_figure(self):
        figures = yaml.safe_load((ROOT / "sources/gray-plates/figures.yaml").read_text())["objects"]
        for item in self.bones:
            name = item["id"].split(":", 1)[1]
            self.assertIn(name, figures, f"{name} has no Gray figure")
            spec = figures[name]
            self.assertTrue((ROOT / "sources/gray-plates/raw/figures" / spec["file"]).is_file(), spec["file"])
            mono = (ROOT / item["glyph"]["monochrome"]).read_text()
            self.assertIn(f'data-figure="{spec["file"].rsplit(".", 1)[0]}"', mono, name)
            self.assertGreater(mono.count(" M"), 3, f"{name}: an empty or failed trace")

    def test_mirrored_pairs_differ(self):
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
