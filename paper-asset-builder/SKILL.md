---
name: paper-asset-builder
description: Build or update a PaperFigureAssets entry from a paper URL/PDF or an existing material directory. Select attractive paper figures and tables, extract and organize them into method_figures, result_figures, and tables, pause for user image review, then generate a paper README and update the root Paper Index after confirmation.
---

# Paper Asset Builder

Accept either a paper alone or a paper with a prepared material directory. When only a paper is supplied, select and extract suitable assets first, report the local directory, and pause for the user's image review. Resume README and index generation only after the user confirms; a natural-language confirmation is sufficient and does not require repeating the skill invocation.

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

Also accept a paper URL or attached/local PDF in natural language when the user asks for automatic figure selection, extraction, and repository entry creation.

Accepted parameters:

```text
material_dir=...      Optional. Use existing images here; otherwise prepare this directory from the paper.
paper=...             Required unless discoverable. arXiv URL, paper URL, or local PDF path.
repo_root=...         Optional. Target PaperFigureAssets repository root; discover it from the workspace when omitted.
paper_id=...          Optional. Output folder name under papers/.
extract_assets=...    Optional. auto (default), true (select/extract from the paper), or false (use supplied images only).
latex_test=...        Optional. auto (default), online, local, or off. Online testing requires authorization to send table source to the selected service.
update_index=false    Optional. Skip root README paper index update only when explicitly false.
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

When `material_dir` is omitted, use `<repo_root>/../materials/<paper_id>/`; in this workspace that is `D:\CodeSpace\PaperFigure\materials\<paper_id>\`. Derive a stable paper ID from the paper metadata before creating this directory. Do not use the literal example name `NewPaper` for every paper.

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
- Inspect rendered pages and captions, then prefer visually clear, attractive, representative diagrams, plots, and tables over extracting every embedded PDF image.
- Render complete selected regions from the PDF at sufficient resolution, preserving vector labels, legends, and table text. Use `scripts/pdf_asset_tools.py` for repeatable inspection and region cropping when PyMuPDF is available.
- Save selected PNGs in the appropriate asset folders and record their original labels, pages, captions, crop coordinates, and selection reasons in `source_assets.json` in the material directory.
- Inspect the final crops, then follow User Review Checkpoint. Do not continue directly into README or root index generation after extraction.

## User Review Checkpoint

After collecting or revising extracted assets:

1. Mark the extraction's `source_assets.json` review status as `pending`.
2. Report the actual absolute material directory as a clickable local link, with the counts of method figures, result figures, and tables. Tell the user they may delete, replace, rename, or add images before confirming.
3. End the turn and wait for the user to explicitly confirm the images, for example `检查好了，继续` or `用这个目录里的图片生成 README`. Do not create/update the paper entry or either README during this checkpoint. Elapsed time, existing images, or an earlier request to run the whole workflow is not review confirmation.
4. If the user requests extraction/crop changes, make those changes and return to this checkpoint before downstream generation.

On explicit confirmation, rescan the approved local directory and use its current files as the source of truth. Bypass automatic extraction on this resume, including when `extract_assets=true` appeared in the original invocation. Do not restore deleted images or overwrite user replacements. Use recorded SHA-256 hashes to identify unchanged extracted images, including renamed/moved copies; re-inspect changed/new images and do not attach stale provenance to replacements. Ignore metadata for removed files. If no supported images remain, report that condition instead of silently extracting again.

Record the confirmation and the current relative image filenames under `review` in `source_assets.json` when that file exists, then continue with asset processing and README/index generation. A pending review remains pending even if a later invocation supplies `material_dir` and would normally reuse existing images. User-prepared directories that have no pending extraction review can follow the existing direct-generation workflow.

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

1. Parse the invocation and locate the target repository root. Use `repo_root=` when provided; otherwise discover a workspace directory containing `papers/`, the root `README.md`, and the `<!-- PAPER_INDEX_START -->` marker. Do not write `papers/` beside the repository merely because the workspace opened one level above it.
2. Locate the paper source from `paper=...`, an attachment, the supplied paper link, or an existing material directory.
3. Read the paper to infer title, topic, venue, year, and a stable paper ID; locate or derive `material_dir`.
4. Inspect existing asset folders and apply Automatic Paper Asset Preparation according to `extract_assets`. Verify that at least one supported image exists after preparation.
5. If assets were extracted/revised or their extraction review is pending, follow User Review Checkpoint and stop. On user confirmation, rescan that directory and resume at the next step without repeating extraction.
6. Create or update `<repo_root>/papers/<paper_id>/`; reuse an existing entry for the same paper.
7. Copy only the approved directory's current images and method `.pptx` files into the paper asset folders. Skip copying a file onto itself when the material directory is already the paper entry. Preserve unrelated files and do not create absent asset folders by default. Generate previews and counts from this current selection, not the pre-review crop list.
8. Generate `README.md` following `templates/canonical_paper_readme.md`. Attribute extracted assets to their original figure/table label and PDF page in the asset tables only when provenance still matches the current images.
9. Test present LaTeX tables according to Table Render Testing below. Repair the README source when a compilation or visual defect is found; the README remains the canonical source.
10. Update the root `README.md` Paper Index by default unless `update_index=false`.
11. Validate local links and report the generated paper path, test results, and any unverified tables.

## Asset Processing

Process only asset types whose source folders exist and contain supported images. Preserve all three canonical README sections even when one or two types are absent.

### Method Figures

Read `references/method_figure_reconstruction.md`.

For each method figure:

- show centered image preview;
- add asset table with image and same-basename `.pptx` if available;
- infer a color palette from the actual image;
- use swatch-only icons in the `Swatch` column;
- summarize semantic color roles from the figure content.

### Result Figures

Read `references/result_figure_to_python.md` before reconstructing result plots.

For each result figure:

- inspect the chart visually;
- infer the result type and title yourself;
- produce faithful, self-contained Python plotting code directly in the README;
- embed data in the code block;
- do not replace this with generic starter code unless the image is truly unreadable.

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
- Keep generated code and LaTeX inside the paper README unless the user explicitly asks for separate files.
- Do not create `plot.py`, `table.tex`, `palette.json`, CSV files, or per-figure READMEs by default.
- Use the existing repository style and canonical template.
- Do not tell the user to run a Python command for normal skill usage.
- For Codex usage, do not present this skill as a slash command. Use natural language or `$paper-asset-builder`.
- For Claude Code usage, `/paper-asset-builder ...` is valid after the skill is installed in a Claude skills directory.

## Root README Update

Always update the root `README.md` after creating or updating a paper entry, unless the user explicitly sets `update_index=false`.

Update the `## Paper Index` table, not `## Asset Types`. `Asset Types` describes the repository schema and should not list papers.

If these markers exist, replace only the marked region:

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
- present result figures have fenced `python` code blocks;
- present tables have fenced `latex` source and required packages;
- LaTeX test outcomes are reported accurately, with successful compilation and visual inspection distinguished from skipped, unavailable, and failed checks;
- third-party table uploads were authorized and temporary QA outputs were kept out of the paper gallery;
- all local README links resolve;
- root `README.md` Paper Index is updated unless `update_index=false`.
