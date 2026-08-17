"""Compute and stamp canonical Git-tag versions for release builds."""

from __future__ import annotations

import argparse
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Final

SEMVER: Final = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")


class VersioningError(ValueError):
    """Raised when release version input or package metadata is invalid."""


def _parts(value: str, *, tag: bool) -> tuple[int, int, int]:
    candidate = value[1:] if tag and value.startswith("v") else value
    match = SEMVER.fullmatch(candidate)
    if match is None:
        msg = f"invalid semantic version: {value!r}"
        raise VersioningError(msg)
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def next_version(latest_tag: str, bump: str) -> str:
    """Return the requested SemVer successor of the latest version tag."""
    if bump not in {"patch", "minor", "major"}:
        msg = f"invalid bump: {bump!r}"
        raise VersioningError(msg)

    major, minor, patch = _parts(latest_tag or "v0.0.0", tag=True)
    if bump == "major":
        major, minor, patch = major + 1, 0, 0
    elif bump == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def _replace_exact(path: Path, pattern: str, replacement: str) -> None:
    original = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, original, flags=re.MULTILINE)
    if count != 1:
        msg = f"expected one version field in {path}, found {count}"
        raise VersioningError(msg)
    path.write_text(updated, encoding="utf-8")


def stamp_version(version: str, root: Path) -> None:
    """Stamp a validated release version into build metadata."""
    _parts(version, tag=False)
    _replace_exact(
        root / "pyproject.toml",
        r'^version = "[^"]+"$',
        f'version = "{version}"',
    )
    _replace_exact(
        root / "png2svg" / "__init__.py",
        r'^__version__ = "[^"]+"$',
        f'__version__ = "{version}"',
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    next_parser = commands.add_parser("next")
    next_parser.add_argument("latest_tag")
    next_parser.add_argument("bump", choices=("patch", "minor", "major"))
    stamp_parser = commands.add_parser("stamp")
    stamp_parser.add_argument("version")
    stamp_parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the release version helper."""
    args = _parser().parse_args(argv)
    if args.command == "next":
        print(next_version(args.latest_tag, args.bump))
    else:
        stamp_version(args.version, args.root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
