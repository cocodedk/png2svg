"""Shared immutable types for traced images."""

from __future__ import annotations

from dataclasses import dataclass

RGBA = tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class Run:
    """A horizontal run of pixels."""

    x: int
    y: int
    length: int


@dataclass(frozen=True, slots=True)
class Layer:
    """All visible runs sharing one RGBA color."""

    color: RGBA
    runs: tuple[Run, ...]
