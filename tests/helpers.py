from __future__ import annotations

from pathlib import Path

from PIL import Image

RGBA = tuple[int, int, int, int]


def save_png(path: Path, size: tuple[int, int], pixels: list[RGBA]) -> None:
    image = Image.new("RGBA", size)
    image.putdata(pixels)
    image.save(path, format="PNG")
