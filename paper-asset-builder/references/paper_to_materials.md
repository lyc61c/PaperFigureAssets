# Paper to Material Directory

Use this workflow before README generation when the user supplies a paper and asks for automatic asset extraction.

## Obtain and inspect the paper

Resolve an arXiv abstract page or publisher landing page to its accessible PDF. Reuse a local or attached PDF when supplied. Save the source as `paper.pdf` in the material directory, keeping an existing different file intact, and record the exact paper URL/version. If the full paper cannot be accessed, report that limitation rather than inventing assets from the abstract.

Read the abstract, method section, figure/table captions, and conclusions to identify representative assets. Render candidate pages for visual inspection. PDF image objects alone are not sufficient: diagrams and plots often combine vector paths, text, and several raster images; tables may contain no raster image at all.

Keep page review files and crop specifications in a temporary workspace directory such as `tmp/pdfs/<paper_id>/`, outside the material asset folders. The helper requires `pymupdf` (`import fitz`). Prefer the bundled Python runtime when it has this package; otherwise use an existing Python environment with PyMuPDF before installing dependencies. In this workspace, the current `python` command has PyMuPDF available.

```text
python <skill_dir>/scripts/pdf_asset_tools.py inspect --pdf <paper.pdf> --out <review_dir> --dpi 120
```

The helper writes numbered full-page previews and `pages.json` with text block coordinates. Use `--pages 1,3-5` to review selected pages. Page numbers are one-based; coordinates use PDF points, origin at the top-left, with page rotation normalized to zero. Convert preview pixels to PDF points with `points = pixels * 72 / preview_dpi`.

## Select attractive and useful assets

Use visual judgment rather than a fixed quota. A compact starting selection is one or two method diagrams, two or three complementary result plots, and one or two informative tables, when the paper provides suitable examples. Select fewer if those communicate the paper well; retain more when the user's request warrants it.

Prefer coordinated colors, clear hierarchy, readable text, balanced spacing, well-designed legends, and diagrams or plots that can inspire reusable scientific figures. Favor the main framework, a useful module detail, the main finding, an ablation or trade-off, and a well-structured comparison table. Avoid redundant panels, low-resolution image montages, tiny text, and dense tables that cannot be read at normal viewing size.

Classify by content:

- `method_figures/`: conceptual diagrams, architecture/framework overviews, pipelines, algorithm/module schematics.
- `result_figures/`: experimental plots, ablations, statistical distributions, comparisons, scaling or trade-off curves.
- `tables/`: actual row/column tables, including vector-text tables, not every rectangular figure.

Preserve the complete multi-panel figure when panels belong together. If an independently meaningful panel is selected, retain its panel label and all relevant axes/legends, and record which panel was used. Keep original figure/table numbering in descriptive filenames such as `fig1_framework.png`, `fig4_ablation.png`, and `table2_comparison.png`.

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
      "selection_reason": "Clear module hierarchy and coordinated colors."
    }
  ]
}
```

```text
python <skill_dir>/scripts/pdf_asset_tools.py crop --pdf <paper.pdf> --spec <regions.json> --out <material_dir> --dpi 300
```

Start with 300 DPI; use 450-600 DPI for small text when needed. Higher DPI cannot restore detail absent from a raster source. The helper creates only selected type folders and `source_assets.json`; it refuses invalid page/bounds, path traversal, duplicate destinations, and accidental overwrites. Use `--overwrite` only for correcting generated crops whose replacement is intentional. Include existing crops in the specification if intentionally regenerating the whole selected set, or merge source metadata for an incremental update without discarding prior provenance.

Open every final PNG for visual review. Correct clipped labels, excess body text, blank crops, and unreadable content before continuing. Verify that a crop is the actual selected figure/table, not merely a successfully rendered rectangle.

## Pause for user review, then resume paper-asset-builder

After extraction and visual QA, leave `source_assets.json` with `review.status` set to `pending`. Report the absolute material directory and per-type image counts, then stop for the user to inspect the local files. Do not copy assets into the paper entry or generate either README until the user explicitly confirms. Follow the User Review Checkpoint in `SKILL.md` for requested corrections and resume behavior.

After confirmation, rescan the local folders and process only their current images. The user may have deleted, replaced, renamed, or added files; do not rerun extraction or reinstate the original selection. Use matching provenance only, and record the confirmation and current relative image filenames in the manifest's `review` object. Use the source paper's exact values where available for plots/tables and explicitly label approximations otherwise. Preserve the canonical README layout, add valid source label/page attribution to asset tables, and update the root Paper Index by default.

Keep temporary inspection pages and crop specifications out of the paper gallery. Respect the repository's existing copyright policy when assets will be redistributed; local extraction does not establish redistribution permission.
