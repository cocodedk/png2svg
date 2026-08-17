# png2svg

Convert PNG pixels into vector-only SVG paths. Python CLI, entrypoint `png2svg`.

## Architecture

- Pillow normalizes PNG inputs to RGBA.
- The tracer groups same-colour horizontal runs into bounded SVG path chunks.
- Fully transparent pixels produce no geometry; partial alpha uses `fill-opacity`.
- `png2svg.cli` owns overwrite protection, stdout output, scaling, and errors.
- Web mode performs lossy 128px, 16-colour, four-alpha-level preprocessing.

## Decided, and visible in `pyproject.toml`

- Python >= 3.10, target `py310`.
- **Pillow is the only dependency.** No `potrace`, no `vtracer`, no external binary.
  Tracing is pure Python. Adding a native dependency reverses this decision.
- Packaged with hatchling; the wheel ships the `png2svg` package.
- `mypy` strict over `png2svg`. `ruff` at line-length 88. Run them with `lintp`;
  the project pins the settings, not a separate linter.

## Ask before

- Putting colour in scope, if the tracer starts black-and-white.
- Adding any second runtime dependency.
- Changing the output fidelity target, once one is set.

## Long tasks

`NOTES.md` does not exist yet. Create it at the repo root on the first task that spans
more than one session; the format is in the user-level agent config.
