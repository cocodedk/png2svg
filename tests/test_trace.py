from __future__ import annotations

import unittest

from png2svg.model import Layer, Run
from png2svg.trace import trace_pixels


class TracePixelsTests(unittest.TestCase):
    def test_groups_runs_by_color_and_ignores_fully_transparent_pixels(self) -> None:
        red = (255, 0, 0, 255)
        clear = (99, 88, 77, 0)
        pixels = [red, red, clear, red, clear, red]

        result = trace_pixels(pixels, width=3, height=2)

        self.assertEqual(
            result,
            [Layer(red, (Run(0, 0, 2), Run(0, 1, 1), Run(2, 1, 1)))],
        )

    def test_preserves_first_seen_order_and_distinguishes_alpha(self) -> None:
        faded_blue = (0, 0, 255, 128)
        green = (0, 255, 0, 255)

        result = trace_pixels([faded_blue, green, faded_blue], width=3, height=1)

        self.assertEqual(
            result,
            [
                Layer(faded_blue, (Run(0, 0, 1), Run(2, 0, 1))),
                Layer(green, (Run(1, 0, 1),)),
            ],
        )

    def test_rejects_a_pixel_count_that_does_not_match_dimensions(self) -> None:
        with self.assertRaisesRegex(ValueError, "pixel count"):
            trace_pixels([(0, 0, 0, 255)], width=2, height=1)


if __name__ == "__main__":
    unittest.main()
