"""Render traced color layers as SVG."""

from __future__ import annotations

import math
from collections.abc import Iterable

from png2svg.model import RGBA, Layer, Run

DEFAULT_MAX_RUNS_PER_PATH = 2_048


def _number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _fill(color: RGBA) -> str:
    red, green, blue, _ = color
    return f"#{red:02x}{green:02x}{blue:02x}"


def _opacity(alpha: int) -> str:
    return f"{alpha / 255:.3f}".rstrip("0").rstrip(".")


def _path(run: Run) -> str:
    return f"M{run.x} {run.y}h{run.length}v1h-{run.length}z"


def _output_size(
    width: int,
    height: int,
    scale: float,
    output_width: float | None,
    output_height: float | None,
) -> tuple[float, float]:
    for dimension in (output_width, output_height):
        if dimension is not None and (not math.isfinite(dimension) or dimension <= 0):
            msg = "output dimensions must be positive"
            raise ValueError(msg)

    if output_width is None and output_height is None:
        return width * scale, height * scale
    if output_width is None:
        requested_height = output_height if output_height is not None else 0.0
        return width * requested_height / height, requested_height
    if output_height is None:
        return output_width, height * output_width / width
    return output_width, output_height


def render_svg(  # noqa: PLR0913, PLR0917
    width: int,
    height: int,
    layers: Iterable[Layer],
    scale: float = 1.0,
    output_width: float | None = None,
    output_height: float | None = None,
    max_runs_per_path: int = DEFAULT_MAX_RUNS_PER_PATH,
) -> str:
    """Render layers using compact, vector-only path elements."""
    if not math.isfinite(scale) or scale <= 0:
        msg = "scale must be positive"
        raise ValueError(msg)
    if max_runs_per_path <= 0:
        msg = "max runs per path must be positive"
        raise ValueError(msg)

    rendered_width, rendered_height = _output_size(
        width,
        height,
        scale,
        output_width,
        output_height,
    )
    width_attribute = _number(rendered_width)
    height_attribute = _number(rendered_height)
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width_attribute}" height="{height_attribute}" '
        f'viewBox="0 0 {width} {height}" shape-rendering="crispEdges">'
    ]
    for layer in layers:
        attributes = f'fill="{_fill(layer.color)}"'
        if layer.color[3] < 255:
            attributes += f' fill-opacity="{_opacity(layer.color[3])}"'
        for start in range(0, len(layer.runs), max_runs_per_path):
            chunk = layer.runs[start : start + max_runs_per_path]
            path_data = "".join(_path(run) for run in chunk)
            lines.append(f'  <path {attributes} d="{path_data}"/>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"
