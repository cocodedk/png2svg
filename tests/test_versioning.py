from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.versioning import VersioningError, next_version, stamp_version


class NextVersionTests(unittest.TestCase):
    def test_bootstraps_and_applies_each_semver_bump(self) -> None:
        self.assertEqual(next_version("", "patch"), "0.0.1")
        self.assertEqual(next_version("v0.9.9", "minor"), "0.10.0")
        self.assertEqual(next_version("v1.2.3", "major"), "2.0.0")

    def test_rejects_invalid_tags_and_bumps(self) -> None:
        with self.assertRaisesRegex(VersioningError, "invalid semantic version"):
            next_version("v1.2-beta", "patch")
        with self.assertRaisesRegex(VersioningError, "invalid bump"):
            next_version("v1.2.3", "banana")

    def test_rejects_an_unanchored_version(self) -> None:
        with self.assertRaises(VersioningError):
            next_version("release-v1.2.3", "patch")


class StampVersionTests(unittest.TestCase):
    def test_stamps_build_metadata_without_committing_a_version_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "png2svg"
            package.mkdir()
            (root / "pyproject.toml").write_text(
                'name = "example"\nversion = "0.1.0"\n',
                encoding="utf-8",
            )
            (package / "__init__.py").write_text(
                '__version__ = "0.1.0"\n',
                encoding="utf-8",
            )

            stamp_version("1.4.0", root)

            pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
            init = (package / "__init__.py").read_text(encoding="utf-8")
            self.assertIn('version = "1.4.0"', pyproject)
            self.assertIn('__version__ = "1.4.0"', init)

    def test_rejects_an_invalid_target_version(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaisesRegex(VersioningError, "invalid semantic version"),
        ):
            stamp_version("latest", Path(directory))

    def test_repository_has_no_second_canonical_version_file(self) -> None:
        root = Path(__file__).parents[1]
        self.assertFalse((root / "version.txt").exists())


class ReleaseWorkflowTests(unittest.TestCase):
    def test_release_is_manual_tag_driven_and_idempotent(self) -> None:
        workflow = (
            Path(__file__).parents[1] / ".github" / "workflows" / "release.yml"
        ).read_text(encoding="utf-8")

        required = [
            "workflow_dispatch:",
            "fetch-depth: 0",
            "persist-credentials: false",
            "github.event.repository.default_branch",
            "github.ref_name",
            "VALID_TAGS",
            "grep -E '^v(0|[1-9][0-9]*)",
            "publish_tag=",
            "git/tags",
            "git/refs",
            "--sort=-version:refname",
            "scripts/versioning.py next",
            "scripts/versioning.py stamp",
            "git rev-parse",
            "python -m build",
            "gh release create",
            "generate-notes",
            "gh release upload",
            "gh release edit",
            "attest-build-provenance",
            "METADATA",
            "PKG-INFO",
            "sha256sum -c SHA256SUMS",
            "python -m pip install .",
            "cancel-in-progress: false",
        ]
        self.assertTrue(all(token in workflow for token in required))
        stable_artifacts = [
            "png2svg-cli-dist.zip",
            "png2svg-cli-dist.zip.sha256",
            "SHA256SUMS",
        ]
        self.assertTrue(all(name in workflow for name in stable_artifacts))
        self.assertNotIn("\n  push:", workflow)
        self.assertNotIn("\nenv:\n  GH_TOKEN:", workflow)
        self.assertNotIn("git push origin", workflow)
        self.assertLess(
            workflow.index("python -m pip install ."),
            workflow.index("python -m unittest discover -v"),
        )

    def test_every_release_shell_block_parses(self) -> None:
        workflow = (
            Path(__file__).parents[1] / ".github" / "workflows" / "release.yml"
        ).read_text(encoding="utf-8")
        lines = workflow.splitlines()
        scripts: list[str] = []
        for index, line in enumerate(lines):
            indent = len(line) - len(line.lstrip())
            if line.strip() == "run: |":
                block: list[str] = []
                for candidate in lines[index + 1 :]:
                    candidate_indent = len(candidate) - len(candidate.lstrip())
                    if candidate.strip() and candidate_indent <= indent:
                        break
                    block.append(candidate[indent + 2 :])
                scripts.append("\n".join(block))
            elif line.strip().startswith("run: "):
                scripts.append(line.strip().removeprefix("run: "))

        self.assertGreaterEqual(len(scripts), 7)
        for script in scripts:
            sanitized = re.sub(r"\$\{\{.*?\}\}", "value", script)
            result = subprocess.run(
                ["/usr/bin/bash", "-n"],
                input=sanitized,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
