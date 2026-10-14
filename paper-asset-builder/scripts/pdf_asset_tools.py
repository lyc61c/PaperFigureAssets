"""Render paper pages and crop selected complete figures/tables from a PDF."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import fitz


ASSET_TYPES = {"method_figures", "result_figures", "tables"}


def parse_pages(value, count):
    if not value:
        return list(range(count))
    pages = set()
    for part in value.split(","):
        bounds = part.strip().split("-")
        if len(bounds) not in (1, 2):
            raise ValueError("Use one-based pages, e.g. 1,3-5.")
        start, end = int(bounds[0]), int(bounds[-1])
        if start < 1 or end < start or end > count:
            raise ValueError(f"Page range must be within 1-{count}.")
        pages.update(range(start - 1, end))
    return sorted(pages)


def upright_page(document, index):
    page = document[index]
    page.set_rotation(0)  # Normalize coordinates in memory; never save the source PDF.
    return page


def check_dpi(dpi):
    if not isinstance(dpi, int) or not 36 <= dpi <= 1200:
        raise ValueError("DPI must be an integer between 36 and 1200.")


def inspect_document(document, out, dpi=120, pages=None):
    check_dpi(dpi)
    indices = parse_pages(pages, len(document))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for index in indices:
        page = upright_page(document, index)
        filename = f"page_{index + 1:03d}.png"
        pixmap = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
        pixmap.save(out / filename)
        blocks = [
            {"bbox": list(block[:4]), "text": block[4]}
            for block in page.get_text("blocks")
            if block[6] == 0
        ]
        records.append({
            "page": index + 1,
            "width": page.rect.width,
            "height": page.rect.height,
            "preview": filename,
            "preview_dpi": dpi,
            "text_blocks": blocks,
        })
    (out / "pages.json").write_text(
        json.dumps({"page_count": len(document), "pages": records},
                   ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return records


def crop_document(document, specification, out, source_pdf, dpi=300, overwrite=False):
    check_dpi(dpi)
    out = Path(out).resolve()
    entries = specification.get("assets")
    if not isinstance(entries, list) or not entries:
        raise ValueError("The crop specification must contain a non-empty assets list.")
    manifest_path = out / "source_assets.json"
    if manifest_path.exists() and not overwrite:
        raise FileExistsError(f"Preserve existing provenance: {manifest_path}")
    prepared = []
    targets = set()
    for entry in entries:
        kind, filename = entry.get("type"), entry.get("filename")
        if kind not in ASSET_TYPES:
            raise ValueError(f"Unknown asset type: {kind}")
        if (not isinstance(filename, str) or not filename
                or "/" in filename or "\\" in filename or ":" in filename
                or Path(filename).suffix.lower() != ".png"):
            raise ValueError("Each asset filename must be a plain PNG filename.")
        page_number = entry.get("page")
        if type(page_number) is not int or not 1 <= page_number <= len(document):
            raise ValueError(f"Invalid one-based page: {page_number}")
        coords = entry.get("bbox")
        if (not isinstance(coords, list) or len(coords) != 4
                or any(type(v) not in (int, float) or not math.isfinite(v) for v in coords)):
            raise ValueError("Each bbox must contain four finite numbers.")
        page = upright_page(document, page_number - 1)
        clip = fitz.Rect(coords)
        if clip.is_empty or clip.is_infinite or not page.rect.contains(clip):
            raise ValueError(f"Crop bounds must be non-empty and inside page {page_number}.")
        target = (out / kind / filename).resolve()
        if not target.is_relative_to(out / kind):
            raise ValueError("The crop destination must stay inside its asset folder.")
        key = str(target).casefold()
        if key in targets:
            raise ValueError(f"Duplicate crop destination: {target}")
        targets.add(key)
        if target.exists() and not overwrite:
            raise FileExistsError(f"Preserve existing asset: {target}")
        prepared.append((entry, target, clip))
    # Validate the entire specification before writing any crops.
    records = []
    for entry, target, clip in prepared:
        page = upright_page(document, entry["page"] - 1)
        pixmap = page.get_pixmap(clip=clip, dpi=dpi, colorspace=fitz.csRGB, alpha=False)
        target.parent.mkdir(parents=True, exist_ok=True)
        pixmap.save(target)
        records.append({**entry, "path": target.relative_to(out).as_posix(),
                        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                        "dpi": dpi, "width_px": pixmap.width, "height_px": pixmap.height})
    manifest = {"source_pdf": str(Path(source_pdf).resolve()),
                "source_url": specification.get("source_url"),
                "review": {"status": "pending"}, "assets": records}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Render pages with text coordinates.")
    inspect.add_argument("--pdf", type=Path, required=True)
    inspect.add_argument("--out", type=Path, required=True)
    inspect.add_argument("--pages", help="One-based page selection, e.g. 1,3-5.")
    inspect.add_argument("--dpi", type=int, default=120)
    crop = commands.add_parser("crop", help="Render selected complete regions as PNGs.")
    crop.add_argument("--pdf", type=Path, required=True)
    crop.add_argument("--out", type=Path, required=True)
    crop.add_argument("--spec", type=Path, required=True)
    crop.add_argument("--dpi", type=int, default=300)
    crop.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        with fitz.open(args.pdf) as document:
            if document.needs_pass:
                raise ValueError("The PDF requires a password.")
            if args.command == "inspect":
                result = inspect_document(document, args.out, args.dpi, args.pages)
                print(f"Rendered {len(result)} pages into {args.out}")
            else:
                specification = json.loads(args.spec.read_text(encoding="utf-8-sig"))
                result = crop_document(document, specification, args.out, args.pdf,
                                       args.dpi, args.overwrite)
                print(f"Extracted {len(result['assets'])} assets into {args.out}")
    except (ValueError, OSError, RuntimeError, TypeError, AttributeError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
