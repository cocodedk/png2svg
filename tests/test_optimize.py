from __future__ import annotations

import unittest

from PIL import Image

from png2svg.optimize import WEB_ALPHA_LEVELS, WEB_COLORS, optimize_for_web


class OptimizeForWebTests(unittest.TestCase):
    def test_downsamples_longest_dimension_to_web_limit(self) -> None:
        image = Image.new("RGBA", (256, 64), (255, 0, 0, 255))

        result = optimize_for_web(image)

        self.assertEqual(result.size, (128, 32))

    def test_reduces_color_and_alpha_palettes(self) -> None:
        image = Image.new("RGBA", (32, 1))
        pixels = [
            (value * 8, 255 - (value * 8), value * 4, value * 8) for value in range(32)
        ]
        image.putdata(pixels)

        result = optimize_for_web(image)
        colors = {(red, green, blue) for red, green, blue, _ in result.getdata()}
        alphas = {alpha for _, _, _, alpha in result.getdata()}

        self.assertLessEqual(len(colors), WEB_COLORS)
        self.assertTrue(alphas.issubset(WEB_ALPHA_LEVELS))


if __name__ == "__main__":
    unittest.main()
