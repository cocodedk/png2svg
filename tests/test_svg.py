from __future__ import annotations

import unittest

from png2svg.model import Layer, Run
from png2svg.svg import render_svg


class RenderSvgTests(unittest.TestCase):
    def test_renders_one_path_per_color(self) -> None:
        layers = [
            Layer((255, 0, 16, 255), (Run(0, 0, 2), Run(1, 1, 1))),
            Layer((0, 128, 255, 255), (Run(0, 1, 1),)),
        ]

        result = render_svg(width=2, height=2, layers=layers, scale=1)

        self.assertEqual(
            result,
            '<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2" '
            'viewBox="0 0 2 2" shape-rendering="crispEdges">\n'
            '  <path fill="#ff0010" d="M0 0h2v1h-2zM1 1h1v1h-1z"/>\n'
            '  <path fill="#0080ff" d="M0 1h1v1h-1z"/>\n'
            "</svg>\n",
        )

    def test_renders_fractional_alpha_and_scaled_dimensions(self) -> None:
        layers = [Layer((1, 2, 3, 128), (Run(0, 0, 1),))]

        result = render_svg(width=1, height=1, layers=layers, scale=2.5)

        self.assertIn('width="2.5" height="2.5"', result)
        self.assertIn('fill="#010203" fill-opacity="0.502"', result)

    def test_rejects_non_positive_scale(self) -> None:
        with self.assertRaisesRegex(ValueError, "scale must be positive"):
            render_svg(width=1, height=1, layers=[], scale=0)

    def test_splits_large_layers_into_renderer_friendly_paths(self) -> None:
        layer = Layer(
            (255, 0, 0, 255),
            (Run(0, 0, 1), Run(1, 0, 1), Run(2, 0, 1)),
        )

        result = render_svg(
            width=3,
            height=1,
            layers=[layer],
            scale=1,
            max_runs_per_path=2,
        )

        self.assertEqual(result.count('<path fill="#ff0000"'), 2)
        self.assertIn('d="M0 0h1v1h-1zM1 0h1v1h-1z"', result)
        self.assertIn('d="M2 0h1v1h-1z"', result)

    def test_rejects_non_positive_path_chunk_size(self) -> None:
        with self.assertRaisesRegex(ValueError, "max runs per path must be positive"):
            render_svg(
                width=1,
                height=1,
                layers=[],
                max_runs_per_path=0,
            )

    def test_explicit_width_preserves_aspect_ratio(self) -> None:
        result = render_svg(
            width=4,
            height=2,
            layers=[],
            output_width=10,
        )

        self.assertIn('width="10" height="5"', result)

    def test_explicit_width_and_height_set_exact_output_size(self) -> None:
        result = render_svg(
            width=4,
            height=2,
            layers=[],
            output_width=10,
            output_height=7,
        )

        self.assertIn('width="10" height="7"', result)

    def test_rejects_non_positive_output_dimension(self) -> None:
        with self.assertRaisesRegex(ValueError, "output dimensions must be positive"):
            render_svg(
                width=1,
                height=1,
                layers=[],
                output_width=0,
            )


if __name__ == "__main__":
    unittest.main()
