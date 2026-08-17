"""Trace a raster into color-grouped horizontal runs."""

from __future__ import annotations

from collections.abc import Iterable

from png2svg.model import RGBA, Layer, Run


def trace_pixels(pixels: Iterable[RGBA], width: int, height: int) -> list[Layer]:
    """Return one layer per visible color, preserving first-seen order."""
    if width <= 0 or height <= 0:
        msg = "image dimensions must be positive"
        raise ValueError(msg)

    pixel_values = tuple(pixels)
    if len(pixel_values) != width * height:
        msg = "pixel count does not match image dimensions"
        raise ValueError(msg)

    grouped: dict[RGBA, list[Run]] = {}
    for y in range(height):
        x = 0
        while x < width:
            color = pixel_values[(y * width) + x]
            end = x + 1
            while end < width and pixel_values[(y * width) + end] == color:
                end += 1
            if color[3] > 0:
                grouped.setdefault(color, []).append(Run(x, y, end - x))
            x = end

    return [Layer(color, tuple(runs)) for color, runs in grouped.items()]
