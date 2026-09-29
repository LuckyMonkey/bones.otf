import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class GrayArtworkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())
        cls.bones = [item for item in cls.data["objects"] if item["category"] == "bone"]

    def test_every_bone_uses_a_trace_master(self):
        bases = {item["glyph"]["base"] for item in self.bones}
        self.assertEqual(len(bases), 15)
        for base in bases:
            trace = ROOT / "glyphs/gray-trace" / f"{base}.svg"
            self.assertTrue(trace.is_file(), base)
        for item in self.bones:
            mono = (ROOT / item["glyph"]["monochrome"]).read_text()
            color = (ROOT / item["glyph"]["color"]).read_text()
            self.assertIn('data-source="gray-anatomy"', mono, item["id"])
            self.assertIn('data-source="gray-anatomy"', color, item["id"])
            self.assertNotIn('#b4384c', mono, item["id"])

    def test_raw_plate_provenance_is_present(self):
        manifest = yaml.safe_load((ROOT / "sources/gray-plates.yaml").read_text())
        self.assertEqual(manifest["license"], "Public domain")
        self.assertGreaterEqual(len(manifest["plates"]), 15)
        self.assertGreaterEqual(len(list((ROOT / "sources/gray-plates/raw").iterdir())), 14)


if __name__ == "__main__":
    unittest.main()
