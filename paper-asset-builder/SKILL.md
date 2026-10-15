---
name: paper-asset-builder
description: Build a personal Figarium paper-figure library from a paper title, URL/PDF, or material directory. Extract and classify whole-paper figures and tables, pause for human selection, then reconstruct Method Figures as visually faithful editable PowerPoint decks, generate README source, and update the index and gallery.
---

# Figarium · Paper Asset Builder

Build a library the user can curate and reproduce, not merely a screenshot collection. Figarium (Figure + Herbarium, 图圃) is the project brand; keep the compatible invocation name `paper-asset-builder`. Do not rename the user's checkout, GitHub repository, or remote as part of using this skill.

Accept a paper title, URL, attached/local PDF, or a paper with a prepared material directory. For a new paper, inventory and extract all numbered figures and tables throughout the PDF, including appendices, by default. Report the actual local directory and stop for human selection. Resume reconstruction, README/index, and available static-site generation only after confirmation; natural-language confirmation is sufficient.

For first-time setup or a request to build a personal library, also read `references/library_workflow.md`. The website is a static viewer; the local coding agent runs this skill. Do not imply a deployed gallery can execute the skill or compile visitor-supplied code.

## Invocation

Invocation depends on the host:

- In Codex, skills are not UI slash commands. Use natural language or `$paper-asset-builder`.
- In Claude Code, skills installed under `.claude/skills/` or `~/.claude/skills/` can be invoked directly with `/paper-asset-builder`.

Codex call style:

```text
使用 paper-asset-builder paper=https://arxiv.org/abs/2501.01234
```

Also valid:

```text
$paper-asset-builder material_dir=/path/to/material_dir paper=https://arxiv.org/abs/2501.01234
```

Also accept a paper title, URL or attached/local PDF in natural language when the user asks for automatic figure extraction, classification, and library creation. Resolve a title to an authoritative paper landing page/PDF; ask only if distinct plausible matches cannot be disambiguated from the context. Never invent a paper identity or PDF URL.

Accepted parameters:

```text
material_dir=...      Optional. Use existing images here; otherwise prepare this directory from the paper.
paper=...             Required unless discoverable. Paper title, arXiv/publisher URL, or local PDF path.
repo_root=...         Optional. Target Figarium/PaperFigureAssets repository root; discover it from the workspace when omitted.
paper_id=...          Optional. Output folder name under papers/.
extract_assets=...    Optional. auto (default), true (inspect/extract from the paper), or false (use supplied images only).
selection=...         Optional. all (default: every numbered figure/table, including appendices) or curated (agent-selected subset).
latex_test=...        Optional. auto (default), online, local, or off. Online testing requires authorization to send table source to the selected service.
method_pptx=...       Optional. on (default) or off. After image approval, reconstruct every Method Figure as editable PPTX; off explicitly skips this deliverable.
update_index=false    Optional. Skip the repository's paper index update only when explicitly false.
force=true            Optional. Overwrite an existing paper README when intentional.
```

Also accept positional style:

```text
使用 paper-asset-builder /path/to/material_dir https://arxiv.org/abs/2501.01234
```

Claude Code call style:

```text
/paper-asset-builder material_dir=/path/to/material_dir paper=https://arxiv.org/abs/2501.01234
```

## Material Directory

When `material_dir` is omitted, use `<repo_root>/../materials/<paper_id>/`. Resolve and report the absolute path for the active machine; do not hard-code this project's Windows paths into another user's library. Derive a stable paper ID from the paper metadata before creating the directory. Do not use the literal example name `NewPaper` for every paper.

The prepared directory may contain any non-empty subset of the three asset folders:

```text
<material_dir>/
├── method_figures/   # optional
├── result_figures/   # optional
├── tables/           # optional
└── paper.pdf or paper_url.txt or arxiv.txt
```

Do not require missing asset folders and do not create them merely to satisfy the layout. Require at least one supported asset image before README generation, after any automatic extraction. Treat a missing asset type as a zero-count type and keep its canonical README section empty.

If `paper=` is omitted, discover the paper source from `paper.pdf`, `paper_url.txt`, `arxiv.txt`, or `url.txt`.

Supported image extensions are `.png`, `.jpg`, `.jpeg`, `.svg`, and `.webp`. Method figures may include same-basename `.pptx` files.

## Automatic Paper Asset Preparation

Read `references/paper_to_materials.md` when selecting or extracting assets from a paper.

- In `auto` mode, use supplied images when any exist. When no supported images exist, obtain the paper PDF and prepare the material directory automatically.
- With `extract_assets=true`, inspect the PDF and select assets even if the material directory already contains images. Preserve existing user files; do not silently replace colliding filenames or duplicate the same source figure.
- With `extract_assets=false`, require prepared images and report the missing input if none exist.
- In default `selection=all`, inspect the whole PDF, including appendices, and inventory every numbered figure and table before cropping. Extract all recoverable inventory items, not just attractive examples or raster image objects. Record inaccessible/ambiguous items and reasons; never claim complete coverage when any item is unresolved.
- Use `selection=curated` only when requested. Choose attractive, useful examples without a fixed quota, while retaining the full inventory and explicit skip reasons so the subset is auditable.
- Render complete figure/table regions at sufficient resolution, preserving vector labels, legends, and table text. Use `scripts/pdf_asset_tools.py` for repeatable page inspection and region cropping when PyMuPDF is available; it is a crop helper, not an automatic caption detector or completeness verifier.
- Save PNGs in the appropriate asset folders and record original labels, pages, captions, crop coordinates, hashes, inventory status, and coverage in `source_assets.json` as specified in `references/paper_to_materials.md`.
- Inspect the final crops, then follow User Review Checkpoint. Do not continue directly into README or root index generation after extraction.

## User Review Checkpoint

After collecting or revising extracted assets:

1. Mark the extraction's `source_assets.json` review status as `pending`.
2. Report the actual absolute material directory as a clickable local link, with the counts of method figures, result figures, and tables; include extraction coverage and any unresolved inventory items. Tell the user they may delete, replace, rename, reclassify, or add images before confirming.
3. End the turn and wait for the user to explicitly confirm the images, for example `检查好了，继续` or `用这个目录里的图片生成 README`. Do not create/update the paper entry or either README during this checkpoint. Elapsed time, existing images, or an earlier request to run the whole workflow is not review confirmation.
4. If the user requests extraction/crop changes, make those changes and return to this checkpoint before downstream generation.

On explicit confirmation, rescan the approved local directory and use its current files as the source of truth. Bypass automatic extraction on this resume, including when `extract_assets=true` appeared in the original invocation. Do not restore deleted images or overwrite user replacements. Use recorded SHA-256 hashes to identify unchanged extracted images, including renamed/moved copies; re-inspect changed/new images and do not attach stale provenance to replacements. Ignore metadata for removed files. If no supported images remain, report that condition instead of silently extracting again.

When the manifest exists, set `review.status` to `approved`, record the user's confirmation and current relative image filenames in `review.approved_images`, and record the current SHA-256 for each retained image in `review.current_images` (objects with `path`, `sha256`, and unchanged/replaced/new provenance status). Preserve the extraction snapshot; add removed/renamed/replaced files to review history rather than attaching old source metadata to new pixels. Then continue with asset processing and README/index generation. A pending review remains pending even if a later invocation supplies `material_dir` and would normally reuse existing images. User-prepared directories that have no pending extraction review can follow the existing direct-generation workflow.

## Core Behavior

Do the work directly as a skill. Do not require the user to run a Python command.

Infer missing semantic fields instead of asking for them:

- **Title:** infer from arXiv/PDF metadata, paper text, or filename.
- **Topic:** summarize from the paper title, abstract, introduction, and asset contents as one concise research topic phrase.
- **Venue/Year:** infer from the paper source or use `Unknown` if not available.
- **Paper ID:** derive from year, venue/source, and short title unless `paper_id=` is given.
- **Figure titles:** inspect each image and filename; use natural academic labels such as `Framework Overview`, `Agent Pipeline`, `Module Detail`, `Ablation Study`, `Accuracy-Latency Trade-off`, `Scaling Curve`, `Error Analysis`, `Main Results`, `Dataset Statistics`, or better content-specific titles.
- **Asset ordering:** use natural sort order, then adjust only when visual numbering clearly indicates a better order.

## Canonical Layout

Do not edit this file:

```text
paper-asset-builder/templates/canonical_paper_readme.md
```

Generated paper READMEs must preserve that template's structure:

- top-right Back to Home link
- centered paper title
- Paper Information table
- HTML Asset Preview Gallery
- Method Figures section
- Result Analysis Figures section
- Paper Tables section

Use the template as the visual contract, not as disposable output.

## Workflow

1. Parse the invocation and locate the target repository root. Use `repo_root=` when provided; otherwise discover a workspace directory containing `papers/`, the root `README.md`, and an approved index in `PAPER_INDEX.md` (or the marked root README in legacy libraries). Follow Paper Index Update below to select the index. Do not write `papers/` beside the repository merely because the workspace opened one level above it.
2. Resolve the paper source from `paper=...` (title, link, or PDF), an attachment, or an existing material directory.
3. Read the paper to infer title, topic, venue, year, and a stable paper ID; locate or derive `material_dir`.
4. Inspect existing asset folders and apply Automatic Paper Asset Preparation according to `extract_assets`. Verify that at least one supported image exists after preparation.
5. If assets were extracted/revised or their extraction review is pending, follow User Review Checkpoint and stop. On user confirmation, rescan that directory and resume at the next step without repeating extraction.
6. Create or update `<repo_root>/papers/<paper_id>/`; reuse an existing entry for the same paper.
7. Synchronize only the approved directory's current images and method `.pptx` files into the paper asset folders. When updating an existing entry, identify old generated assets now absent from the approved selection so they do not remain in gallery/index counts. Remove only known generated files belonging to this entry whose unchanged identity can be verified; preserve unrelated or user-modified files. Never recursively delete an asset directory to synchronize it. If a conflict prevents safe synchronization, report it and ask rather than silently restoring/including a removed selection. Skip copying onto itself when material_dir is already the paper entry, and do not create absent type folders by default. Generate previews/counts from the synchronized current selection and briefly report any material file removal.
8. For each current Method Figure, read and execute `references/method_figure_to_pptx.md` unless `method_pptx=off`. Produce and validate a same-basename PPTX and a per-paper `method_figures_editable.pptx` containing the selected figures. This is an agent-driven reconstruction task, not merely copying an image into a slide. Preserve any user/author-provided PPT and resolve filename collisions safely. Do not label unverified attempts complete.
9. Generate `README.md` following `templates/canonical_paper_readme.md`. Attribute extracted assets to their original figure/table label and PDF page in the asset tables only when provenance still matches the current images. Link each verified PPTX in its `PPT Source` row; add a `Method Figures PPT` metadata row for the verified per-paper deck. Report incomplete/skipped figures explicitly; PPTX files never increase image counts.
10. Test present LaTeX tables according to Table Render Testing below. Repair the README source when a compilation or visual defect is found; the README remains the canonical source.
11. Update the repository's approved Paper Index by default unless `update_index=false`; keep the main README concise when the index lives in `PAPER_INDEX.md`.
12. If `<repo_root>/website/build.py` exists, rebuild the local static gallery with `python website/build.py` from `repo_root` and verify its output. This is a local build, not authorization to publish, commit, push, or change hosting. If the builder is absent, finish README/index generation without inventing a website workflow.
13. Validate local links and report generated paper/site paths, reconstruction scope, test results, and any unverified assets.

## Asset Processing

Process only asset types whose source folders exist and contain supported images. Preserve all three canonical README sections even when one or two types are absent.

### Method Figures

Read `references/method_figure_reconstruction.md` and, by default, `references/method_figure_to_pptx.md`. If a host presentation-authoring skill is available, read and follow it as well; this bundled reference supplies the scientific reconstruction contract, not a replacement for host tool requirements.

For each method figure:

- show centered image preview;
- reconstruct and validate a same-basename editable `.pptx` by default, then link it in the asset table (unless explicitly skipped or unresolved);
- infer a color palette from the actual image;
- use swatch-only icons in the `Swatch` column;
- summarize semantic color roles from the figure content.
- deliver the editable PPTX as the default reconstruction resource; do not add an `Editable Diagram Code` / `Editable Reconstruction` subsection or SVG/TikZ code unless the user explicitly requests it;
- if supplemental code is requested, label it as a reconstruction, not author-provided source, and state whether it reproduces the full diagram or only a schematic subset;
- in the gallery, show one download for the current figure's own PPTX. Do not append the paper's combined deck to every figure; keep any combined-deck link at paper level. Preserve existing README code unless its removal is requested;
- preserve all panels, labels, arrows, equations, and local illustrations in the PPT reconstruction. Photos/screenshots may be separately movable cropped image objects; identify these raster exceptions explicitly. A simplified SVG/TikZ schematic does not fulfill the full PPT deliverable. Preserve preview/palette and report unresolved details rather than disguising them as complete.

### Result Figures

Read `references/result_figure_to_python.md` before reconstructing numerical result plots. Its data-estimation instructions apply to numerical charts, not qualitative screenshots or photo grids; the qualitative exception below takes precedence over any generic code quota.

For each result figure:

- inspect the chart visually;
- infer the result type and title yourself;
- produce faithful, self-contained Python plotting code directly in the README;
- embed data in the code block;
- do not replace this with generic starter code unless the image is truly unreadable.
- distinguish values transcribed from paper annotations/source data from estimated values, with approximation notes both beside the block and in code comments; never present estimated curves as experimental raw data;
- run the generated code in a controlled local QA workspace and visually inspect the output when dependencies are available; report any remaining validation limitation.
- for qualitative image grids/screenshots rather than numerical charts, do not invent measurements or external images to satisfy a code quota. Reconstruct the reusable layout when meaningful, clearly identify missing source imagery, and state the limitation instead of claiming a self-contained faithful chart.

### Tables

Read `references/table_image_to_latex.md` before reconstructing tables.

For each table image:

- inspect the table visually;
- infer the table title yourself;
- produce faithful LaTeX table source directly in the README;
- include only required LaTeX packages;
- prefer `booktabs` and preserve multirow/multicolumn structure when visible.

## Table Render Testing

Read `references/latex_render_testing.md` when testing generated table source.

- `auto`: use an available local or built-in compiler; if it is unavailable or fails operationally, use the online API only when the user has authorized that upload. Otherwise explain the limitation and ask before sending source externally.
- `online`: use the selected online compiler after authorization. The default supported service is LaTeX-on-HTTP (`https://latex.ytotech.com/builds/sync`). A request to use online rendering tests authorizes the scoped table source upload, not unrelated files or other services.
- `local`: compile locally without uploading. Report missing dependencies instead of silently switching to a third party.
- `off`: skip compilation only when explicitly requested and report that validation was skipped.

Use `scripts/latex_render_test.py` to prepare isolated test documents from the README's table and package blocks. Add `--allow-upload` only when authorized. The helper must not upload an entire README, PDF, image, credential, or automatically discovered dependency. Generated PDFs, PNGs, and diagnostic reports belong in a temporary QA directory outside `papers/`, not in the paper gallery by default.

A returned PDF proves compilation, not visual fidelity. Inspect every rendered table against the approved image, including headers, merged cells, highlights, rules, alignment, symbols, and clipping. Fix the README's LaTeX source and rerun affected tests, up to three repair attempts. If the service is unavailable, preserve the source and report the unverified state; do not claim a timeout is a pass or silently omit a failing table.

## Output Rules

- Use relative links from `papers/<paper_id>/README.md`.
- Use natural sort order for figure/table images.
- Keep generated SVG/TikZ, Python code, and LaTeX inside the paper README unless the user explicitly asks for separate files. Static website code-download exports derived from README blocks are allowed build artifacts, not competing canonical sources.
- Do not create `plot.py`, `table.tex`, `palette.json`, CSV files, or per-figure READMEs by default. The default same-basename Method Figure PPTX and per-paper combined PPTX are intentional binary deliverables; authoring scene/source, inventories, renders, and QA receipts remain in an isolated local build directory unless separately requested.
- Use the existing repository style and canonical template.
- Do not tell the user to run a Python command for normal skill usage.
- For Codex usage, do not present this skill as a slash command. Use natural language or `$paper-asset-builder`.
- For Claude Code usage, `/paper-asset-builder ...` is valid after the skill is installed in a Claude skills directory.

## Paper Index Update

Update the approved paper index after creating or updating a paper entry, unless the user explicitly sets `update_index=false`.

Use root-level `PAPER_INDEX.md` when it exists. Only when it is absent, use the marked Paper Index in the root `README.md` for legacy libraries. Do not maintain duplicate indexes or recreate a paper table in the main README after it has been moved out. For a new library, create `PAPER_INDEX.md` and link to it from the main README.

The index is the publication allowlist, not a listing of every folder under `papers/`. Preserve existing valid rows and their order; add only the paper approved by the current task. A present but malformed, empty, or linked index is an error to resolve, not permission to fall back to an older README index or scan unapproved folders. Keep the index as a regular file in the repository root.

Require exactly one ordered marker pair and replace only that marked region. If an existing index has missing, duplicate, or reversed markers, report the problem before modifying it:

```markdown
<!-- PAPER_INDEX_START -->
...
<!-- PAPER_INDEX_END -->
```

Use this table format:

```markdown
| Paper | Venue | Year | Topic | Assets |
|---|---:|---:|---|---|
| [Paper Title](papers/<paper_id>/README.md) | Venue | Year | Topic summary | N method figures, N result figures, N tables |
```

For each paper row:

- read `Title`, `Venue`, `Year`, and `Topic` from that paper's README;
- count image files in `method_figures/`, `result_figures/`, and `tables/`, treating a missing folder as zero;
- preserve all existing valid paper rows;
- add the new paper row if absent;
- replace the row if the paper already exists;
- keep paper links relative to the repository root.

## Validation Checklist

Before finishing, verify:

- when pausing for image review, the directory and asset counts were reported and no paper entry/README/index generation occurred;
- before downstream generation, the user confirmed any pending extraction review and the approved directory was rescanned;
- `templates/canonical_paper_readme.md` was not changed;
- automatically extracted crops were visually reviewed and their source labels/pages were recorded;
- existing supplied images were preserved and the material directory contains at least one supported image;
- the paper README has all canonical sections;
- every present method figure appears in the gallery and Method Figures section;
- every present result figure appears in the gallery and Result Analysis Figures section;
- every present table image appears in the gallery and Paper Tables section;
- present method figures have color palette tables;
- unless explicitly skipped, every selected method figure has a PPTX reconstruction status, with verified individual and combined decks linked; native-object inspection and rendering of the actual final PPTX are both required, and incomplete items are not reported complete;
- final PPTX matches the approved image's complete visual content without a full-image/full-SVG backdrop; any independently editable raster crops, unbound freeform arrows, font substitutions, and application-compatibility limitations are disclosed;
- method figures use PPTX by default; SVG/TikZ code is added only on explicit request, and the gallery has at most one current-figure PPTX download with no combined-deck fallback;
- present numerical result figures have fenced `python` code blocks; qualitative/unrecoverable figures have an explicit reconstruction-scope note rather than invented data;
- present tables have fenced `latex` source and required packages;
- LaTeX test outcomes are reported accurately, with successful compilation and visual inspection distinguished from skipped, unavailable, and failed checks;
- third-party table uploads were authorized and temporary QA outputs were kept out of the paper gallery;
- all local README links resolve;
- the active paper index (`PAPER_INDEX.md`, or the marked root README in legacy libraries) is updated unless `update_index=false`, without duplicating it in the main README;
- an available local website builder was rerun and tested without executing visitor-supplied code or silently publishing;
- default new-paper extraction covers the complete numbered figure/table inventory, including appendices, or reports the exact coverage gap.
