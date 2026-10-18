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

`selection=curated` is the default for a new paper: complete inventory → region extraction/inspection → content and visual/reuse screening → selected local images → human approval. Include appendix labels such as Figure A.1 and Table S2 in the inventory even when excluded from the selected set. This is an agent preselection, not a replacement for the human's final choice. An unresolved crop is a coverage gap, not an aesthetic exclusion.

`selection=all` is the explicit opt-out: extract every recoverable numbered figure/table without aesthetic or quantitative-only filtering. Ordinary tables and qualitative examples are included in this mode. A user can also explicitly keep individual exceptions. Neither mode authorizes pruning user-prepared images, already approved material, or old library entries. Apply a new screening rule to those only when requested.

Use visual judgment without a quota. Do not choose a fixed number per paper, force every category to be populated, or require colorful/complex artwork. Keep the full inventory and a concrete item-level reason for every keep/exclude decision so users can request an excluded item later.

Classify by content:

- `method_figures/`: conceptual diagrams, architecture/framework overviews, pipelines, algorithm/module schematics, and designed concept/task/capability overviews meeting the criteria below. For a non-architecture overview, record `asset_role=conceptual_overview` and retain its actual semantic title.
- `result_figures/`: quantitative experimental plots, ablations, statistical distributions, comparisons, scaling or trade-off curves.
- `tables/`: actual row/column tables with reusable structural or visual design, including vector-text tables, not every rectangular figure.

Routine qualitative result grids, one-off examples/error cases, and code/configuration screenshots are classified as result assets for the inventory, but excluded from default curated output. They may enter `result_figures/` with explicit selection or `selection=all`; never invent numeric data to make them qualify. Do not reject a designed concept/task/capability overview merely because it contains generated images, photographs or qualitative examples: judge its primary explanatory purpose and reusable composition under the overview criteria below. Do not relabel an ordinary comparison grid as a method just to bypass screening or obtain a PPT. A quantitative plot embedded in a larger screenshot does not automatically qualify the entire screenshot. For mixed panels, retain the complete figure only when quantitative comparison, method structure or a qualifying conceptual overview is its primary purpose; explain the choice. An explicitly selected standalone chart panel must retain labels/axes/legends and be recorded as a partial scope, not full-figure coverage. Do not duplicate a source item in counts. Algorithm boxes without a Figure/Table label are optional extras.

Preserve complete multi-panel figures. For a figure spanning multiple pages, save ordered parts and map all parts to the same inventory item; count images and numbered source items separately. A panel-only selection is appropriate only when requested or in curated mode; retain panel labels, axes/legends, and record its scope. Use original numbering in filenames such as `fig1_framework.png`, `fig_a1_error_cases.png`, and `table_s2_comparison.png`.

## Content gates and visual/reuse screening

Inspect the actual full-page artwork and candidate crops, not filenames or captions alone. Apply content gates before judging beauty:

| Category | Keep by default | Exclude by default |
|---|---|---|
| Method / conceptual overview | Readable architectures, pipelines or concept/task/capability overviews with meaningful grouping, explanatory hierarchy, consistent panels and useful relationships/process cues | Pure decoration, undifferentiated image montages or routine qualitative comparison grids without an explanatory overview; irreparably unreadable diagrams |
| Result | Quantitative charts whose measured variables/comparisons are identifiable: curves, bars, scatter, distributions, numeric heatmaps, scaling/trade-off plots | Photo/video grids, generated-answer dialogues, memory notes, qualitative case studies, code snippets/diffs and configuration screenshots, even with attractive colors |
| Table | Distinctive, meaningful reusable design: integrated bars/heatmaps/glyphs, intentional visual grouping, unusually clear hierarchical/matrix organization or coherent semantic highlighting | Routine three-line/booktabs or grid tables, plain parameter/data lists; bold best values, basic merged headers or extra rows alone do not make a table distinctive |

For candidates passing the content gate, assess **layout/hierarchy**, **legibility**, **color or monochrome contrast**, and **reusable design value**. State what is actually useful (for example, aligned comparison panels, semantic palette, clear legend/axes, or integrated quantitative encoding); avoid an unexplained beauty score. A simple well-spaced line chart can qualify. A monochrome table with genuinely distinctive organization can qualify. A colorful but generic table need not qualify. Repair a poor crop before judging the original design; a repairable crop defect is not a reason to reject the source artwork.

### Designed overview / research teaser gate

Include visually rich concept, task or capability overviews even when they are non-quantitative, provided the actual artwork has all of these qualities:

- A coherent explanatory purpose: it maps the paper's ideas, task families or capabilities rather than only showing outputs for the same prompt across models.
- Deliberate information organization: meaningful categories, readable labels and a clear hierarchy or relationships/process cues; example images support the explanation rather than replace it.
- Reusable visual composition: intentional panel alignment, typography, spacing and contrast or semantic color roles that would be useful to adapt in another research figure.

Richness and beauty are valid selection signals, but a central logo, many images or bright colors alone are not sufficient. An overview need not contain implementation modules or numerical axes to qualify. Explain the visible design value in its keep rationale, record `reason_code=designed_overview` and `asset_role=conceptual_overview`, and put it in `method_figures/`. Describe it as a concept/task/capability overview, not as an implementation architecture or experimental chart. On approval, reconstruct its full composition as editable PPT, preserving complex local imagery separately; do not fabricate numerical plotting code.

Positive example: **Mind-Brush Figure 1** organizes distinct knowledge/reasoning task families into labeled, semantically colored cards with prompt-to-search/reason-to-generation cues around a shared concept illustration. Keep it for its capability overview and reusable card composition. Contrast **Mind-Brush Figure 4**, a routine model-output comparison grid: colorful correctness borders and generated images alone do not qualify it as an overview. Judge future papers from their actual artwork, not by figure number or resemblance to this one paper. Explicit user selection still overrides these defaults.

Record `keep`, `exclude`, or `needs_review` per item, with a reason code and a short visible-content rationale. Suggested codes include `method_structure`, `designed_overview`, `quantitative_chart`, `distinctive_table`, `ordinary_table`, `non_quantitative_result`, `low_visual_reuse`, and `unresolved_crop`. Borderline overview candidates can remain pending human review with a concrete explanation; do not use this state to admit ordinary tables or routine qualitative results automatically. When no candidate qualifies, report zero selected images and stop; do not pad the selection.

Keep excluded generated crops recoverable outside the material directory, for example under `tmp/pdfs/<paper_id>/excluded/`, and record their archive paths when present. For a fresh paper, stage candidate crops in the review workspace and copy only the selected set into the three material folders. No fourth asset folder is needed. For an existing pending extraction, move only generated files whose identity matches their recorded SHA-256; preserve unknown/modified/user-supplied files and ask about conflicts. Validate exact source/destination paths, do not overwrite a conflicting archive, and never recursively delete a material directory. If a file has already been removed by the user, record it as missing/removed and do not re-extract it, even if it would pass the new criteria. Explicit restoration requires a user request.

These are default intake criteria, not a retroactive cleanup mandate. Human-confirmed images remain authoritative on resume, including explicitly retained exceptions.

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
      "selection_reason": "Retained after visual screening: readable framework with aligned modules and traceable flows."
    }
  ]
}
```

```text
python <skill_dir>/scripts/pdf_asset_tools.py crop --pdf <paper.pdf> --spec <regions.json> --out <material_dir> --dpi 300
```

Start with 300 DPI; use 450-600 DPI for small text when needed. Higher DPI cannot restore detail absent from a raster source. The helper creates only selected type folders and `source_assets.json`; it refuses invalid page/bounds, path traversal, duplicate destinations, and accidental overwrites. It does not detect captions, judge beauty, apply the content gates, or verify inventory completeness automatically; screening is the agent's visual task. In curated mode, use a review-workspace `--out` for unfiltered candidates, then transfer selected images and matching provenance to the material directory. After cropping, extend its manifest with inventory/coverage fields below. Use `--overwrite` only for intentionally correcting generated crops. For incremental updates, merge source metadata without discarding prior provenance or user review history.

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

Each numbered item needs a label, kind, pages, target category, status, and matching output files or a reason at the time of extraction. Use `extracted`, `unresolved`, or `skipped_curated` at that stage; record observed user removals/changes in review history on each rescan, including while approval is pending. Coverage describes the extraction snapshot, not a promise that the human-selected library still includes every source item. Complete extraction means all pages were inspected and every numbered item has a verified complete crop; if there is a gap, report it explicitly. Do not turn caption-number continuity alone into proof of completeness. Preserve exact PDF version and hash when available so the inventory can be reproduced.

For curated runs, add a `curation` object with `mode`, `criteria_version`, per-item `decisions` (label, decision, reason code, rationale, source hash, and archive path when available), and `current_images` (current relative path and hash). Report `kept_items`, `excluded_items`, and `needs_review_items` separately from `unresolved_items`. A screened subset is not "all images extracted" just because every page was inspected. Distinguish `inventory_complete` (all pages/items inspected), `selected_complete` (all retained crops verified), and full-extraction `complete`. Intentionally skipped items are not unresolved crop failures. Keep `review.status=pending`; screening completion is not human approval.

When changing the selection of an existing extraction, preserve its original `assets`, inventory and coverage as a labeled historical extraction snapshot rather than rewriting history or claiming removed files still exist. Add current screening decisions and current file hashes separately, and record already absent files in review history immediately, even while approval is pending. Use only the current directory on resume. Do not overwrite a user-modified manifest or attach an original hash to replacement pixels.

For incremental recropping, render only the requested correction into a fresh review-workspace directory and merge its matching provenance. Do not rerun an old full crop specification with `--overwrite` against the material directory: the basic helper replaces its manifest and does not merge review/curation history or protect human-deleted selections.

## Pause for user review, then resume paper-asset-builder

After extraction, screening and visual QA, leave `source_assets.json` with `review.status` set to `pending`. Report the actual absolute material directory, current per-type image counts, inventoried/retained/excluded counts, and any unresolved items, then stop for local human review. Users may delete, replace, rename, reclassify, add or explicitly restore images. Do not copy assets into the paper entry or generate either README until explicit confirmation. Follow the User Review Checkpoint in `SKILL.md` for requested corrections and resume behavior.

After confirmation, rescan the local folders and process only their current images. The user may have deleted, replaced, renamed, or added files; do not rerun extraction or reinstate the original selection. Use matching provenance only, and record the confirmation and current relative image filenames in the manifest's `review` object. Use the source paper's exact values where available for plots/tables and explicitly label approximations otherwise. Preserve the canonical README layout, add valid source label/page attribution to asset tables, and update the approved Paper Index selected by `SKILL.md` (normally `PAPER_INDEX.md`) by default.

Keep temporary inspection pages and crop specifications out of the paper gallery. After README/index generation, rebuild `website/build.py` if present, without silently publishing it. Respect the repository's copyright policy when assets will be redistributed; local extraction or a public PDF does not establish redistribution permission.
