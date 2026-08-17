from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
WEBSITE = ROOT / "website"


def _luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92
        if value <= 0.04045
        else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class SiteAccessibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.english = (WEBSITE / "index.html").read_text(encoding="utf-8")
        self.persian = (WEBSITE / "fa" / "index.html").read_text(encoding="utf-8")
        self.css = (WEBSITE / "styles.css").read_text(encoding="utf-8")

    def test_terminal_transcript_and_controls_are_truthful(self) -> None:
        for document in (self.english, self.persian):
            self.assertNotIn("wrote logo.svg", document)
            self.assertNotIn("<button", document)

    def test_normal_text_palette_meets_wcag_aa_contrast(self) -> None:
        tokens = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6});", self.css))
        required = {"paper", "muted", "coral", "on-coral", "mint", "note-ink"}
        self.assertTrue(required.issubset(tokens))
        self.assertGreaterEqual(_contrast(tokens["muted"], tokens["paper"]), 4.5)
        self.assertGreaterEqual(_contrast(tokens["on-coral"], tokens["coral"]), 4.5)
        self.assertGreaterEqual(_contrast(tokens["note-ink"], tokens["mint"]), 4.5)
        self.assertIn("--card-copy: var(--on-coral)", self.css)
        self.assertIn(".note .eyebrow { color: var(--note-ink); }", self.css)
        self.assertIn("--card-code-ink: var(--on-coral)", self.css)

    def test_persian_cli_tokens_are_isolated_left_to_right(self) -> None:
        code_tags = re.findall(r"<code[^>]*>", self.persian)
        self.assertGreaterEqual(len(code_tags), 5)
        self.assertTrue(all('class="cli-token"' in tag for tag in code_tags))
        self.assertIn("direction: ltr", self.css)
        self.assertIn("unicode-bidi: isolate", self.css)
        self.assertIn('<div class="proof-strip" dir="rtl">', self.persian)
        self.assertIn('<bdi dir="ltr">SVG</bdi>', self.persian)


if __name__ == "__main__":
    unittest.main()
