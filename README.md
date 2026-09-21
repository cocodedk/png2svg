# png2svg

## Website

- [English](https://png2svg.cocode.dk/)
- [فارسی (Persian)](https://png2svg.cocode.dk/fa/)


`png2svg` converts every visible PNG pixel into SVG path geometry. It groups
adjacent pixels by RGBA color and splits oversized paths for viewer
compatibility, so the result contains no embedded raster image or base64 data.

This is lossless pixel tracing, which is especially useful for icons, sprites,
and pixel art. It deliberately preserves hard pixel edges; it does not fit
smooth Bézier curves to photographs or illustrations.

## Install

Python 3.10 or newer is required.

```console
python -m pip install .
```

For an isolated development environment:

```console
uv sync
```

## Use

Write beside the source as `icon.svg`:

```console
png2svg icon.png
```

Choose a destination and rendered scale:

```console
png2svg icon.png --output artwork.svg --scale 4
```

Set one dimension while preserving the source aspect ratio:

    png2svg icon.png --width 800
    png2svg icon.png --height 600

Set both dimensions for an exact output size:

    png2svg icon.png --width 800 --height 600

For a compact website asset, use the lossy web preset:

    png2svg large-logo.png --web --output logo.svg
    png2svg large-logo.png --web --width 256 --output logo.svg

Web mode traces at no more than 128 pixels on the longest side and reduces the
image to 16 RGB colors and four alpha levels. It remains vector-only and works
with `--width` or `--height`. Omit `--web` when exact pixel fidelity matters
more than file size.

Stream SVG to another command:

```console
png2svg icon.png --output -
```

Existing files are protected by default. Pass `--force` to replace an existing
SVG. The input PNG itself is never overwritten, even with `--force`.

## Develop

```console
python -m unittest discover -v
lintp . --strict --codes
```
