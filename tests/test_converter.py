from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from png2svg.converter import ConversionError, convert_png
from tests.helpers import save_png


class ConvertPngTests(unittest.TestCase):
    def test_converts_rgba_png_to_vector_only_svg(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "tiny.png"
            save_png(source, (2, 1), [(255, 0, 0, 255), (0, 0, 0, 0)])

            result = convert_png(source, scale=3)

        self.assertIn('width="6" height="3"', result)
        self.assertIn('<path fill="#ff0000"', result)
        self.assertNotIn("image", result)
        self.assertNotIn("base64", result)

    def test_reports_invalid_png(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "broken.png"
            source.write_text("not a PNG", encoding="utf-8")

            with self.assertRaisesRegex(ConversionError, "cannot read PNG"):
                convert_png(source)


if __name__ == "__main__":
    unittest.main()
