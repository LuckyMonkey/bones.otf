import csv
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class OntologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load((ROOT / "ontology/anatomy.yaml").read_text())
        with (ROOT / "registry/codepoints.csv").open(newline="", encoding="utf-8") as handle:
            cls.codepoints = list(csv.DictReader(handle))

    def test_vertical_slice_counts(self):
        objects = self.data["objects"]
        self.assertEqual(len(objects), 204)
        self.assertEqual(sum(item["category"] == "bone" for item in objects), 186)
        self.assertEqual(sum(item["category"] == "organ" for item in objects), 17)
        self.assertEqual(sum(item["category"] == "tissue" for item in objects), 1)

    def test_registry_is_one_to_one(self):
        objects = self.data["objects"]
        self.assertEqual({item["id"] for item in objects}, {row["id"] for row in self.codepoints})
        self.assertEqual(len({item["unicode_pua"] for item in objects}), len(objects))
        self.assertIn("anatomy:femur", {item["id"] for item in objects})
        self.assertIn("anatomy:left_kidney", {item["id"] for item in objects})
        self.assertIn("anatomy:left_scaphoid", {item["id"] for item in objects})
        self.assertIn("anatomy:right_fifth_toe_distal_phalanx", {item["id"] for item in objects})

    def test_assets_and_labels_exist(self):
        for item in self.data["objects"]:
            self.assertTrue((ROOT / item["glyph"]["monochrome"]).is_file(), item["id"])
            self.assertTrue((ROOT / item["glyph"]["color"]).is_file(), item["id"])
            self.assertEqual(item["shortcode"], item["ligature"])
            self.assertTrue(item["external_ids"], item["id"])
            self.assertIsInstance(item["review_required"], bool)

    def test_parent_graph_resolves(self):
        known = {group["id"] for group in self.data["groups"]} | {item["id"] for item in self.data["objects"]}
        self.assertTrue(all(item["parent"] in known for item in self.data["objects"]))


if __name__ == "__main__":
    unittest.main()
