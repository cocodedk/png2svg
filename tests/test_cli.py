from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from png2svg.cli import main
from tests.helpers import save_png


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.source = self.directory / "icon.png"
        save_png(self.source, (1, 1), [(12, 34, 56, 255)])

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_cli(self, *arguments: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main(list(arguments))
        return status, stdout.getvalue(), stderr.getvalue()

    def test_writes_to_default_svg_path(self) -> None:
        status, stdout, stderr = self.run_cli(str(self.source))

        target = self.source.with_suffix(".svg")
        self.assertEqual((status, stdout, stderr), (0, "", ""))
        self.assertTrue(target.read_text(encoding="utf-8").startswith("<svg "))

    def test_writes_to_explicit_output_and_applies_scale(self) -> None:
        target = self.directory / "result.svg"

        status, _, _ = self.run_cli(str(self.source), "-o", str(target), "--scale", "4")

        self.assertEqual(status, 0)
        self.assertIn('width="4" height="4"', target.read_text(encoding="utf-8"))

    def test_width_preserves_aspect_ratio(self) -> None:
        save_png(self.source, (2, 1), [(12, 34, 56, 255), (12, 34, 56, 255)])

        status, _, _ = self.run_cli(str(self.source), "--width", "10")

        self.assertEqual(status, 0)
        svg = self.source.with_suffix(".svg").read_text(encoding="utf-8")
        self.assertIn('width="10" height="5"', svg)

    def test_height_preserves_aspect_ratio(self) -> None:
        save_png(self.source, (2, 1), [(12, 34, 56, 255), (12, 34, 56, 255)])

        status, _, _ = self.run_cli(str(self.source), "--height", "10")

        self.assertEqual(status, 0)
        svg = self.source.with_suffix(".svg").read_text(encoding="utf-8")
        self.assertIn('width="20" height="10"', svg)

    def test_width_and_height_set_exact_output_size(self) -> None:
        status, _, _ = self.run_cli(str(self.source), "--width", "10", "--height", "7")

        self.assertEqual(status, 0)
        svg = self.source.with_suffix(".svg").read_text(encoding="utf-8")
        self.assertIn('width="10" height="7"', svg)

    def test_rejects_scale_combined_with_output_size(self) -> None:
        status, _, stderr = self.run_cli(
            str(self.source), "--scale", "2", "--width", "10"
        )

        self.assertEqual(status, 1)
        self.assertIn("cannot combine --scale", stderr)

    def test_web_mode_reduces_svg_size(self) -> None:
        pixels = [(value, 255 - value, value // 2, 255) for value in range(256)]
        save_png(self.source, (256, 1), pixels)
        regular = self.directory / "regular.svg"
        web = self.directory / "web.svg"

        regular_status, _, _ = self.run_cli(str(self.source), "--output", str(regular))
        web_status, _, _ = self.run_cli(str(self.source), "--output", str(web), "--web")

        self.assertEqual((regular_status, web_status), (0, 0))
        self.assertLess(web.stat().st_size, regular.stat().st_size)
        self.assertIn(
            'viewBox="0 0 128 1"',
            web.read_text(encoding="utf-8"),
        )

    def test_writes_to_stdout_when_output_is_dash(self) -> None:
        status, stdout, stderr = self.run_cli(str(self.source), "--output", "-")

        self.assertEqual(status, 0)
        self.assertTrue(stdout.startswith("<svg "))
        self.assertEqual(stderr, "")

    def test_refuses_to_overwrite_without_force(self) -> None:
        target = self.source.with_suffix(".svg")
        target.write_text("keep me", encoding="utf-8")

        status, _, stderr = self.run_cli(str(self.source))

        self.assertEqual(status, 1)
        self.assertEqual(target.read_text(encoding="utf-8"), "keep me")
        self.assertIn("already exists", stderr)

    def test_force_allows_overwrite(self) -> None:
        target = self.source.with_suffix(".svg")
        target.write_text("replace me", encoding="utf-8")

        status, _, _ = self.run_cli(str(self.source), "--force")

        self.assertEqual(status, 0)
        self.assertTrue(target.read_text(encoding="utf-8").startswith("<svg "))

    def test_never_overwrites_the_source_png(self) -> None:
        original = self.source.read_bytes()

        status, _, stderr = self.run_cli(
            str(self.source), "--output", str(self.source), "--force"
        )

        self.assertEqual(status, 1)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertIn("same file", stderr)

    def test_reports_conversion_errors_without_traceback(self) -> None:
        missing = self.directory / "missing.png"

        status, stdout, stderr = self.run_cli(str(missing))

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("error: cannot read PNG", stderr)


if __name__ == "__main__":
    unittest.main()
