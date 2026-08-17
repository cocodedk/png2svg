"""PNG loading and conversion orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from PIL import Image, UnidentifiedImageError

from png2svg.model import RGBA
from png2svg.optimize import optimize_for_web
from png2svg.svg import render_svg
from png2svg.trace import trace_pixels


class ConversionError(Exception):
    """Raised when an input cannot be converted."""


def convert_png(
    source: str | Path,
    *,
    scale: float = 1.0,
    output_width: float | None = None,
    output_height: float | None = None,
    web: bool = False,
) -> str:
    """Load a PNG and return its vector-only SVG representation."""
    source_path = Path(source)
    try:
        with Image.open(source_path) as image:
            if image.format != "PNG":
                msg = "file is not a PNG"
                raise ValueError(msg)
            rgba = image.convert("RGBA")
            if web:
                rgba = optimize_for_web(rgba)
            width, height = rgba.size
            pixels = [cast("RGBA", pixel) for pixel in rgba.getdata()]
    except (OSError, UnidentifiedImageError, ValueError) as error:
        msg = f"cannot read PNG '{source_path}': {error}"
        raise ConversionError(msg) from error

    layers = trace_pixels(pixels, width, height)
    return render_svg(
        width,
        height,
        layers,
        scale=scale,
        output_width=output_width,
        output_height=output_height,
    )
