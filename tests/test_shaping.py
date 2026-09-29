import unittest
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]


class ShapingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / "dist/BONES.ttf"
        cls.data = cls.path.read_bytes()
        cls.face = hb.Face(cls.data)
        cls.hb_font = hb.Font(cls.face)
        cls.hb_font.scale = (2048, 2048)
        cls.font = TTFont(str(cls.path))
        cls.order = cls.font.getGlyphOrder()

    def shape_names(self, text):
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(self.hb_font, buffer)
        return [self.order[info.codepoint] for info in buffer.glyph_infos]

    def test_semantic_ligatures(self):
        self.assertEqual(self.shape_names(":femur:"), ["anatomy_femur"])
        self.assertEqual(self.shape_names(":heart:"), ["anatomy_heart"])
        self.assertEqual(self.shape_names(":left_kidney:"), ["anatomy_left_kidney"])

    def test_surrounding_prose_survives(self):
        names = self.shape_names("Fracture of the :left_femur:.")
        self.assertIn("anatomy_left_femur", names)
        self.assertNotIn(".notdef", names)
        self.assertNotIn("anatomy_femur", self.shape_names("femur"))


if __name__ == "__main__":
    unittest.main()

