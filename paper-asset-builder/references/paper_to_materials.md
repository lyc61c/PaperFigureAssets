# Paper to Material Directory

Use this workflow before README generation when the user supplies a paper and asks for automatic asset extraction.

## Obtain and inspect the paper

Accept a title, URL, or attached/local PDF. Resolve a title by searching authoritative publisher, arXiv, or author project pages and checking title/authors before download. If distinct papers remain plausible, ask the user to choose; do not guess a match. Resolve the landing page to its accessible PDF. Save it as `paper.pdf` in the material directory, keeping an existing different file intact, and record the exact paper URL/version. If the full paper cannot be accessed, report that limitation rather than inventing assets from the abstract.

Read the abstract and method section for semantics, then inspect every PDF page and caption, including supplementary/appendix pages in the supplied PDF. Build a numbered figure/table inventory before choosing crop regions. PDF image objects alone are not sufficient: diagrams and plots often combine vector paths, text, and several raster images; tables may contain no raster image at all. Record non-numbered illustrations separately when useful, but do not count them as satisfying a missing numbered item.

Keep page review files and crop specifications in a temporary workspace directory such as `tmp/pdfs/<paper_id>/`, outside the material asset folders. The helper requires `pymupdf` (`import fitz`). Prefer an available compatible bundled/runtime environment, otherwise an existing Python with PyMuPDF; check the active machine rather than assuming a particular global `python` installation. When installation is needed, prefer a project-local environment.

```text
python <skill_dir>/scripts/pdf_asset_tools.py inspect --pdf <paper.pdf> --out <review_dir> --dpi 120
```

The helper writes numbered full-page previews and `pages.json` with text block coordinates. In default whole-paper mode, inspect all pages rather than only a promising subset. Use `--pages 1,3-5` for incremental reinspection. Page numbers are one-based; coordinates use PDF points, origin at the top-left, with page rotation normalized to zero. Convert preview pixels to PDF points with `points = pixels * 72 / preview_dpi`.

## Inventory first, then apply the requested selection mode

`selection=all` is the default for a new paper. Extract every recoverable numbered figure and table, including appendix items such as Figure A.1 and Table S2. Human review, not an agent's aesthetic preference, decides which images enter the library. Do not silently reduce a long paper to one or two framework diagrams. An unresolved crop is a coverage gap to report, not an item to omit from the inventory.

`selection=curated` is an explicit alternative: use visual judgment to choose a useful subset without a fixed quota. Keep all inventoried items and mark unselected ones with `skipped_curated` and a concrete reason. This allows users to understand what is absent and request it later.

In curated mode, prefer coordinated colors, clear hierarchy, readable text, balanced spacing, useful legends, and reusable scientific layouts. In all mode these qualities help flag recommended picks for the user, but are not a reason to drop numbered assets.

Classify by content:

- `method_figures/`: conceptual diagrams, architecture/framework overviews, pipelines, algorithm/module schematics.
- `result_figures/`: experimental plots, ablations, statistical distributions, comparisons, scaling or trade-off curves.
- `tables/`: actual row/column tables, including vector-text tables, not every rectangular figure.

Qualitative result grids, examples, error cases, and statistical data visualizations belong in `result_figures/`, even when they cannot be recreated as a numeric plot. For a mixed framework/result figure, retain the complete figure in its primary category and record the classification rationale; do not duplicate it in counts by default. If a paper has algorithm boxes but no numbered figure/table label, treat extraction as an optional extra, not mandatory inventory coverage.

Preserve complete multi-panel figures. For a figure spanning multiple pages, save ordered parts and map all parts to the same inventory item; count images and numbered source items separately. A panel-only selection is appropriate only when requested or in curated mode; retain panel labels, axes/legends, and record its scope. Use original numbering in filenames such as `fig1_framework.png`, `fig_a1_error_cases.png`, and `table_s2_comparison.png`.

## Extract complete regions

Crop from the rendered PDF region rather than copying isolated image objects. Include the full artwork, labels, arrows, axes, legends, colorbars, and table headers/notes with modest whitespace. Normally exclude nearby body text and the external caption; keep the caption in the source metadata. Never crop through figure content to make it look cleaner.

Prepare a JSON crop specification after inspecting the pages. Each entry specifies a one-based page, `[x0, y0, x1, y1]` in PDF points, one of the three asset types, a descriptive PNG filename, the original label/caption, and why the asset was selected:

```json
{
  "source_url": "https://arxiv.org/abs/<paper-id>",
  "assets": [
    {
      "page": 3,
      "bbox": [40, 80, 550, 320],
      "type": "method_figures",
      "filename": "fig1_framework.png",
      "label": "Figure 1",
      "caption": "Original caption from the paper.",
      "selection_reason": "Numbered Figure 1 retained by selection=all."
    }
  ]
}
```

```text
python <skill_dir>/scripts/pdf_asset_tools.py crop --pdf <paper.pdf> --spec <regions.json> --out <material_dir> --dpi 300
```

Start with 300 DPI; use 450-600 DPI for small text when needed. Higher DPI cannot restore detail absent from a raster source. The helper creates only selected type folders and `source_assets.json`; it refuses invalid page/bounds, path traversal, duplicate destinations, and accidental overwrites. It does not detect captions, select all figures, or verify inventory completeness automatically. After cropping, extend its manifest with inventory/coverage fields below. Use `--overwrite` only for intentionally correcting generated crops. For incremental updates, merge source metadata without discarding prior provenance or user review history.

Open every final PNG for visual review. Correct clipped labels, excess body text, blank crops, and unreadable content before continuing. Verify that a crop is the actual selected figure/table, not merely a successfully rendered rectangle.

## Coverage record in source_assets.json

Preserve the helper's existing `assets` records, including page/bbox/label/caption/path/hash, and add an auditable inventory. The agent maintains this extension; the crop helper currently emits only basic crop provenance. Example fields:

```json
{
  "selection": "all",
  "coverage": {
    "pages_total": 24,
    "pages_inspected": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
    "numbered_items_total": 2,
    "extracted_items": 1,
    "unresolved_items": 1,
    "complete": false
  },
  "inventory": [
    {"label": "Figure 1", "kind": "figure", "pages": [3], "type": "method_figures", "status": "extracted", "files": ["method_figures/fig1_framework.png"]},
    {"label": "Table A.1", "kind": "table", "pages": [24], "type": "tables", "status": "unresolved", "files": [], "reason": "The final column is missing from the supplied PDF."}
  ],
  "review": {"status": "pending"}
}
```

Each numbered item needs a label, kind, pages, target category, status, and matching current output files or a reason. Use `extracted`, `unresolved`, or `skipped_curated` at the extraction stage; record user removals/changes in review history after confirmation. Coverage describes the extraction snapshot, not a promise that the human-selected library still includes every source item. Complete extraction means all pages were inspected and every numbered item has a verified complete crop; if there is a gap, report it explicitly. Do not turn caption-number continuity alone into proof of completeness. Preserve exact PDF version and hash when available so the inventory can be reproduced.

## Pause for user review, then resume paper-asset-builder

After extraction and visual QA, leave `source_assets.json` with `review.status` set to `pending`. Report the actual absolute material directory, per-type image counts, numbered-item coverage, and any unresolved/skipped items, then stop for local human review. Users may delete, replace, rename, reclassify, or add images. Do not copy assets into the paper entry or generate either README until explicit confirmation. Follow the User Review Checkpoint in `SKILL.md` for requested corrections and resume behavior.

After confirmation, rescan the local folders and process only their current images. The user may have deleted, replaced, renamed, or added files; do not rerun extraction or reinstate the original selection. Use matching provenance only, and record the confirmation and current relative image filenames in the manifest's `review` object. Use the source paper's exact values where available for plots/tables and explicitly label approximations otherwise. Preserve the canonical README layout, add valid source label/page attribution to asset tables, and update the approved Paper Index selected by `SKILL.md` (normally `PAPER_INDEX.md`) by default.

Keep temporary inspection pages and crop specifications out of the paper gallery. After README/index generation, rebuild `website/build.py` if present, without silently publishing it. Respect the repository's copyright policy when assets will be redistributed; local extraction or a public PDF does not establish redistribution permission.
