import unittest
from pathlib import Path

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]


class FontTest(unittest.TestCase):
    def test_monochrome_artifacts_and_pua(self):
        font = TTFont(str(ROOT / "dist/BONES.ttf"))
        cmap = font.getBestCmap()
        self.assertEqual(font["name"].getDebugName(1), "BONES")
        self.assertEqual(cmap[0xE000], "anatomy_skull")
        self.assertEqual(cmap[0xE00B], "anatomy_femur")
        self.assertEqual(cmap[0xE022], "anatomy_skin")
        self.assertNotEqual(cmap[ord("A")], "anatomy_skull")
        self.assertNotIn("COLR", font)

    def test_color_artifacts_are_colrv1(self):
        font = TTFont(str(ROOT / "dist/BONES-Color.ttf"))
        self.assertIn("COLR", font)
        self.assertIn("CPAL", font)
        self.assertEqual(font["COLR"].version, 1)
        self.assertEqual(font.getBestCmap()[0xE012], "anatomy_heart")

    def test_woff2_artifacts_load(self):
        for name in ("BONES.woff2", "BONES-Color.woff2"):
            font = TTFont(str(ROOT / "dist" / name))
            self.assertIn("cmap", font)


if __name__ == "__main__":
    unittest.main()

