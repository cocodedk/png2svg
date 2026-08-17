from __future__ import annotations

import re
import unittest
from pathlib import Path

from PIL import Image

from png2svg.converter import convert_png

ROOT = Path(__file__).parents[1]
WEBSITE = ROOT / "website"


class PublicSiteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.english = (WEBSITE / "index.html").read_text(encoding="utf-8")
        self.persian = (WEBSITE / "fa" / "index.html").read_text(encoding="utf-8")

    def test_has_every_deployable_site_asset(self) -> None:
        expected = [
            WEBSITE / "styles.css",
            WEBSITE / "favicon.svg",
            WEBSITE / "og.png",
            WEBSITE / "robots.txt",
            WEBSITE / "sitemap.xml",
            WEBSITE / "og-image.html",
            ROOT / ".github" / "workflows" / "deploy-pages.yml",
        ]

        self.assertTrue(all(path.is_file() for path in expected))

    def test_english_page_has_complete_seo_stack(self) -> None:
        required = [
            '<html lang="en">',
            '<meta name="description"',
            '<meta name="robots" content="index, follow">',
            '<link rel="canonical" href="https://cocodedk.github.io/png2svg/">',
            '<meta property="og:image"',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            '<meta property="og:locale" content="en_US">',
            '<meta name="twitter:card" content="summary_large_image">',
            'hreflang="x-default"',
            '"@type": "SoftwareApplication"',
            '"applicationCategory": "DeveloperApplication"',
            'href="fa/"',
            'href="favicon.svg"',
            'href="styles.css"',
        ]

        self.assertTrue(all(token in self.english for token in required))
        self.assertEqual(self.english.count("<h1"), 1)

    def test_persian_page_has_rtl_localized_seo(self) -> None:
        required = [
            '<html lang="fa" dir="rtl">',
            'hreflang="en"',
            'hreflang="fa"',
            '<meta property="og:locale" content="fa_IR">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            '<meta name="twitter:card" content="summary_large_image">',
            '"@type": "SoftwareApplication"',
            '"inLanguage": "fa"',
            'href="../favicon.svg"',
            'href="../styles.css"',
            'href="../"',
        ]

        self.assertIn("تبدیل PNG به SVG", self.persian)
        self.assertTrue(all(token in self.persian for token in required))
        self.assertEqual(self.persian.count("<h1"), 1)

    def test_localized_search_copy_meets_keyword_and_length_contract(self) -> None:
        cases = [
            (self.english, "PNG to SVG CLI"),
            (self.persian, "تبدیل PNG به SVG"),
        ]
        for document, keyword in cases:
            with self.subTest(keyword=keyword):
                title = re.search(r"<title>([^<]+)</title>", document)
                description = re.search(
                    r'<meta name="description" content="([^"]+)">',
                    document,
                )
                heading = re.search(r"<h1>(.*?)</h1>", document, re.DOTALL)
                if title is None or description is None or heading is None:
                    self.fail("required localized search markup is missing")
                title_text = title.group(1)
                description_text = description.group(1)
                heading_text = re.sub(r"<[^>]+>", "", heading.group(1))
                self.assertIn(keyword, heading_text)
                self.assertLessEqual(50, len(title_text))
                self.assertLessEqual(len(title_text), 60)
                self.assertLessEqual(140, len(description_text))
                self.assertLessEqual(len(description_text), 160)
                self.assertIn("primary=", document)
                self.assertIn("secondary=", document)
                self.assertIn("intent=", document)

    def test_latest_release_copy_is_version_neutral(self) -> None:
        combined = self.english + self.persian

        self.assertNotIn('"softwareVersion"', combined)
        self.assertNotIn("Download v0.1.0", self.english)
        self.assertIn("Download latest", self.english)
        self.assertIn("دریافت آخرین نسخه", self.persian)

    def test_cocodedk_identity_is_exact_and_bilingual(self) -> None:
        linkedin = (
            'href="https://linkedin.com/in/babakbandpey" '
            'target="_blank" rel="noreferrer"'
        )
        company = 'href="https://cocode.dk" target="_blank" rel="noreferrer"'
        for document in (self.english, self.persian):
            self.assertIn(linkedin, document)
            self.assertIn(company, document)
            self.assertNotIn("www.linkedin.com", document)
        self.assertIn("© ۱۴۰۵", self.persian)
        self.assertNotIn('rel="preload"', self.english)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[فارسی (Persian)]", readme)

    def test_demo_uses_a_real_deterministic_conversion_pair(self) -> None:
        source = WEBSITE / "demo-input.png"
        output = WEBSITE / "demo-output.svg"

        self.assertTrue(source.is_file())
        self.assertTrue(output.is_file())
        with Image.open(source) as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.size, (1236, 1273))
        self.assertLess(source.stat().st_size, 1_200_000)
        self.assertLess(output.stat().st_size, 200_000)

        svg = output.read_text(encoding="utf-8")
        self.assertEqual(svg, convert_png(source, web=True, output_width=512))
        self.assertNotIn("<image", svg)
        self.assertNotIn("data:image", svg)

        references = [
            (self.english, 'src="demo-input.png"', 'src="demo-output.svg"'),
            (self.persian, 'src="../demo-input.png"', 'src="../demo-output.svg"'),
        ]
        for document, source_ref, output_ref in references:
            with self.subTest(source=source_ref):
                self.assertIn(source_ref, document)
                self.assertIn(output_ref, document)
                self.assertIn('class="comparison" dir="ltr"', document)
                self.assertNotIn('class="pixels"', document)
                self.assertNotIn('d="M18 18h56v28h28v56H46V74H18z"', document)

    def test_og_image_has_social_preview_dimensions(self) -> None:
        with Image.open(WEBSITE / "og.png") as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.size, (1200, 630))

    def test_search_crawler_files_target_pages_url(self) -> None:
        robots = (WEBSITE / "robots.txt").read_text(encoding="utf-8")
        sitemap = (WEBSITE / "sitemap.xml").read_text(encoding="utf-8")

        self.assertIn("https://cocodedk.github.io/png2svg/sitemap.xml", robots)
        self.assertIn("https://cocodedk.github.io/png2svg/", sitemap)

    def test_pages_workflow_is_path_scoped_and_manually_runnable(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "deploy-pages.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("website/**", workflow)
        self.assertIn("pages: write", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertNotIn("cancel-in-progress: true", workflow)


if __name__ == "__main__":
    unittest.main()
