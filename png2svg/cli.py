"""Command-line interface for png2svg."""

from __future__ import annotations

import argparse
import math
import sys
from collections.abc import Sequence
from pathlib import Path

from png2svg.converter import ConversionError, convert_png


def _positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as error:
        msg = "must be a number"
        raise argparse.ArgumentTypeError(msg) from error
    if not math.isfinite(number) or number <= 0:
        msg = "must be positive"
        raise argparse.ArgumentTypeError(msg)
    return number


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="png2svg",
        description="Convert PNG pixels into vector-only SVG paths.",
    )
    parser.add_argument("input", type=Path, help="source PNG file")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="output SVG path; use - for stdout (default: INPUT.svg)",
    )
    parser.add_argument(
        "--scale",
        type=_positive_float,
        default=1.0,
        help="multiply rendered width and height (default: 1)",
    )
    parser.add_argument(
        "--width",
        type=_positive_float,
        help="rendered width; preserves aspect ratio if height is omitted",
    )
    parser.add_argument(
        "--height",
        type=_positive_float,
        help="rendered height; preserves aspect ratio if width is omitted",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="make a lossy, compact web SVG (128px, 16 colors)",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )
    return parser


def _target(source: Path, output: str | None) -> Path | None:
    if output == "-":
        return None
    if output is None:
        return source.with_suffix(".svg")
    return Path(output)


def _error(message: str) -> int:
    print(f"png2svg: error: {message}", file=sys.stderr)
    return 1


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process status."""
    options = _parser().parse_args(arguments)
    if options.scale != 1.0 and (
        options.width is not None or options.height is not None
    ):
        return _error("cannot combine --scale with --width or --height")

    target = _target(options.input, options.output)

    if target is not None:
        if target.resolve() == options.input.resolve():
            return _error("input and output refer to the same file")
        if target.exists() and not options.force:
            return _error(f"output '{target}' already exists; use --force")

    try:
        svg = convert_png(
            options.input,
            scale=options.scale,
            output_width=options.width,
            output_height=options.height,
            web=options.web,
        )
        if target is None:
            sys.stdout.write(svg)
        else:
            target.write_text(svg, encoding="utf-8", newline="\n")
    except ConversionError as error:
        return _error(str(error))
    except OSError as error:
        return _error(f"cannot write SVG: {error}")
    return 0


def entrypoint() -> None:
    """Run the installed console script."""
    raise SystemExit(main())
