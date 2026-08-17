"""Lossy raster preparation for compact web SVG output."""

from __future__ import annotations

from PIL import Image

WEB_MAX_DIMENSION = 128
WEB_COLORS = 16
WEB_ALPHA_STEP = 85
WEB_ALPHA_LEVELS = frozenset(range(0, 256, WEB_ALPHA_STEP))


def _target_size(size: tuple[int, int]) -> tuple[int, int]:
    width, height = size
    longest = max(size)
    if longest <= WEB_MAX_DIMENSION:
        return size
    ratio = WEB_MAX_DIMENSION / longest
    return max(1, round(width * ratio)), max(1, round(height * ratio))


def _quantize_alpha(value: int) -> int:
    rounded = ((value + (WEB_ALPHA_STEP // 2)) // WEB_ALPHA_STEP) * WEB_ALPHA_STEP
    return min(255, rounded)


def optimize_for_web(image: Image.Image) -> Image.Image:
    """Reduce dimensions and palettes before vector tracing."""
    rgba = image.convert("RGBA")
    target_size = _target_size(rgba.size)
    if target_size != rgba.size:
        rgba = rgba.resize(target_size, Image.Resampling.LANCZOS)

    quantized = rgba.convert("RGB").quantize(
        colors=WEB_COLORS,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )
    red, green, blue = quantized.convert("RGB").split()
    alpha = rgba.getchannel("A").point(_quantize_alpha)
    return Image.merge("RGBA", (red, green, blue, alpha))
