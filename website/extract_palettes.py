#!/usr/bin/env python3
"""Sample representative figure colors without modifying an image or README.

Pillow is an optional authoring dependency; the static site builder does not use
this module. Only explicitly supplied files are opened. Output is written to
stdout, so a human can inspect it before adding a canonical README palette.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import colorsys
import json
import math
from pathlib import Path
import sys


SAMPLING_NOTE = "Representative colors sampled from the original image; HEX values are approximate."


class PaletteError(ValueError):
    """An explicit input could not be safely sampled."""


def _distance(a, b):
    # Weighted RGB is intentionally deterministic and dependency-free. It is a
    # distinct-color heuristic, not a claim of calibrated perceptual distance.
    return math.sqrt(sum(w * (x - y) ** 2 for x, y, w in zip(a, b, (0.3, 0.59, 0.11))))


def _hsv(rgb):
    return colorsys.rgb_to_hsv(*(value / 255 for value in rgb))


def _different(a, b, support, old_support):
    ah, ass, av = _hsv(a)
    bh, bs, bv = _hsv(b)
    hue_gap = min(abs(ah - bh), 1 - abs(ah - bh)) * 360
    # White-edge antialiasing changes saturation but not hue: don't promote it
    # into another palette entry. Deliberately dark/light variants may remain.
    if _distance(a, b) < (13 if hue_gap >= 35 else 23):
        return False
    if hue_gap >= 18:
        return True
    if (ass >= 0.85 or bs < 0.15) and ass - bs >= 0.15:
        return True
    return support >= max(12, old_support * 0.12) and (abs(ass - bs) >= 0.12 or abs(av - bv) >= 0.14)


def _name(rgb):
    hue, saturation, value = _hsv(rgb)
    if saturation < 0.045:
        return "Gray"
    degrees = hue * 360
    if degrees < 16 or degrees >= 345:
        return "Red"
    if degrees < 48:
        return "Brown" if value < 0.66 else "Orange"
    if degrees < 72:
        return "Yellow"
    if degrees < 165:
        return "Green"
    if degrees < 200:
        return "Teal"
    if degrees < 255:
        return "Blue"
    if degrees < 300:
        return "Purple"
    return "Pink"


def extract_image_palette(image, max_colors=7):
    """Return actual source-pixel colors; never invent a minimum color quota.

    Fully/mostly transparent pixels are ignored, rather than composited into
    artificial white shades. Near-white backgrounds, near-black text and low-
    saturation grids are excluded when chromatic data exist. On grayscale
    images, well-supported middle grays are retained with an explicit note.
    """
    if not 1 <= max_colors <= 12:
        raise PaletteError("max_colors must be between 1 and 12")
    if image.width * image.height > 25_000_000:
        raise PaletteError("Image exceeds the 25-million-pixel sampling limit")
    from PIL import ImageChops, ImageFilter
    rgba = image.convert("RGBA")
    original_histogram = rgba.getcolors(maxcolors=rgba.width * rgba.height) or []
    red, green, blue, alpha_channel = rgba.split()
    high_channel = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    low_channel = ImageChops.darker(ImageChops.darker(red, green), blue)
    neutral = ImageChops.subtract(high_channel, low_channel).point(lambda value: 255 if value < 18 else 0)
    dark = high_channel.point(lambda value: 255 if value < 115 else 0)
    # Subpixel-rendered black text often leaves false orange/cyan fringes.
    # Suppress its immediate neighborhood, not legitimate colored interiors.
    text_neighborhood = ImageChops.multiply(neutral, dark).filter(ImageFilter.MaxFilter(5))
    rgba.putalpha(ImageChops.subtract(alpha_channel, text_neighborhood))
    histogram = rgba.getcolors(maxcolors=rgba.width * rgba.height) or []
    chromatic = Counter()
    gray = Counter()
    opaque_pixels = sum(count for count, pixel in original_histogram if pixel[3] >= 192)
    for count, pixel in histogram:
        r, g, b, alpha = pixel
        if alpha < 192:
            continue
        rgb = (r, g, b)
        high, low = max(rgb), min(rgb)
        if 0.3 * r + 0.59 * g + 0.11 * b < 20 or high < 64 or low > 245:
            continue
        saturation = (high - low) / high if high else 0
        if (r + g + b) / 3 > 236 and saturation < 0.2:
            continue
        if high - low >= 10 and saturation >= 0.045:
            chromatic[rgb] += count
    for count, pixel in original_histogram:
        r, g, b, alpha = pixel
        if alpha >= 192 and max(r, g, b) - min(r, g, b) < 10 and 50 <= (r + g + b) / 3 <= 205:
            gray[(r, g, b)] += count
    # Coarse buckets consolidate raster noise. Each representative remains an
    # exact image pixel, selected as the most frequent color in its bucket.
    def supported_candidates(source, is_chromatic):
        buckets = defaultdict(Counter)
        for rgb, count in source.items():
            key = tuple(channel // 16 for channel in rgb) if is_chromatic else (round(sum(rgb) / 3 / 24),)
            buckets[key][rgb] += count
        candidates = []
        peak_support = max((sum(colors.values()) for colors in buckets.values()), default=0)
        coherence_needed = {}
        for key, colors in buckets.items():
            representative = min(colors, key=lambda rgb: (-colors[rgb], rgb))
            exact_count = colors[representative]
            support = sum(colors.values())
            if exact_count < 8:
                continue
            if is_chromatic and support < 64 and _hsv(representative)[1] < 0.72:
                continue
            candidates.append((support, representative, key))
            if is_chromatic and (exact_count < 24 or support < peak_support * 0.05):
                coherence_needed[key] = min(64, max(8, math.ceil(support * 0.8)))
        candidates.sort(key=lambda item: (-item[0], item[1]))
        # Bound expensive inspection on photographic inputs. A representative
        # palette does not need to search thousands of tiny quantization bins.
        candidates = candidates[:128]
        wanted = {key for _, _, key in candidates if key in coherence_needed}
        positions = {key: set() for key in wanted}
        if wanted:
            for position, (r, g, b, alpha) in enumerate(rgba.getdata()):
                key = (r // 16, g // 16, b // 16)
                if alpha >= 192 and key in positions:
                    positions[key].add(position)
        def coherent(key):
            points = positions[key]
            required = coherence_needed[key]
            while points:
                pending = [points.pop()]
                count = 0
                while pending:
                    position = pending.pop()
                    count += 1
                    if count >= required:
                        return True
                    column = position % rgba.width
                    for dy in (-rgba.width, 0, rgba.width):
                        for dx in (-1, 0, 1):
                            if (column == 0 and dx == -1) or (column == rgba.width - 1 and dx == 1):
                                continue
                            neighbor = position + dy + dx
                            if neighbor in points:
                                points.remove(neighbor)
                                pending.append(neighbor)
            return False
        # Color fringes are often scattered over glyphs. Require one supported
        # connected patch for rare candidates, while preserving a real 12-pixel
        # thin line without a global minimum percentage of the image.
        return [(count, rgb) for count, rgb, key in candidates if key not in wanted or coherent(key)]
    # This tiny absolute support floor keeps rare thin lines. A global pixel-
    # percentage cutoff would erase small but meaningful plotted series.
    supported = supported_candidates(chromatic, True)
    mode = "chromatic"
    if not supported:
        supported = supported_candidates(gray, False)
        mode = "grayscale" if supported else "empty"
    selected = []
    for count, rgb in supported:
        different = all(_different(rgb, old, count, old_count) for old_count, old in selected) if mode == "chromatic" else all(_distance(rgb, old) >= 24 for _, old in selected)
        if different:
            selected.append((count, rgb))
        if len(selected) == max_colors:
            break
    rows = []
    for index, (count, rgb) in enumerate(selected, 1):
        rows.append({"role": f"Representative color {index}", "color": _name(rgb),
                     "hex": "#" + "".join(f"{value:02X}" for value in rgb), "support_pixels": count})
    note = SAMPLING_NOTE
    if mode == "grayscale":
        note += " This image has no supported chromatic palette; the listed middle grays are visible tonal samples, not inferred data-series colors."
    elif mode == "empty":
        note += " No supported colors remain after excluding transparency, near-white backgrounds and near-black text."
    return {"mode": mode, "colors": rows, "note": note, "opaque_pixels": opaque_pixels}


def extract_palette(path, max_colors=7):
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise PaletteError("Optional dependency Pillow is missing. Install it with: python -m pip install Pillow") from exc
    path = Path(path)
    if not path.is_file():
        raise PaletteError(f"Not an image file: {path}")
    try:
        with Image.open(path) as image:
            result = extract_image_palette(image, max_colors)
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise PaletteError(f"Cannot read image {path}: {exc}") from exc
    return {"path": str(path), **result}


def markdown(result):
    lines = ["### Color Palette", "", result["note"], "", "| Role | Swatch | Color | Hex |", "|---|---|---|---|"]
    for row in result["colors"]:
        value = row["hex"]
        token = value[1:]
        lines.append(f'| {row["role"]} | ![{value}](https://placehold.co/20x20/{token}/{token}.svg) | {row["color"]} | `{value}` |')
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path, help="Explicit image paths (directories are not scanned)")
    parser.add_argument("--max-colors", type=int, default=7, choices=range(1, 13), metavar="1..12")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args(argv)
    try:
        results = [extract_palette(path, args.max_colors) for path in args.images]
    except PaletteError as exc:
        parser.exit(2, f"palette extraction: {exc}\n")
    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("\n\n".join(markdown(result) for result in results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
