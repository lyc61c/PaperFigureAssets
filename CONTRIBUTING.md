# Contributing

Figarium · 图圃 (in the compatible `PaperFigureAssets` repository) is a human-curated, reproducible paper-figure library with a static gallery. Keep contributions simple, reproducible, and license-aware.

## Guidelines

1. Use one directory per paper under `papers/`.
2. Every paper directory must include a `README.md`.
3. Put approved method figure previews, same-basename editable `.pptx` reconstructions, and the per-paper `method_figures_editable.pptx` merged deck in `method_figures/`; keep author-provided sources distinguishable from reconstructions.
4. Put result analysis figure previews in `result_figures/`.
5. Put table preview images in `tables/`.
6. Write plotting code, color palettes, LaTeX table source, and method reconstruction source/status directly in the paper `README.md`; distinguish reconstructed source from author-provided source and label approximations, local raster regions, and validation limitations.
7. Do not upload original paper figures without reuse permission unless the paper license explicitly allows redistribution.

For new papers, the skill defaults to inventorying and extracting all numbered figures/tables (including appendices), then pauses for human selection. Preserve coverage/provenance in the local material manifest. After confirmation, use only the local directory's current images; do not restore deleted selections. Keep the canonical paper README template unchanged and update the marked table in [PAPER_INDEX.md](PAPER_INDEX.md), preserving existing valid rows and their order. Do not put the paper table back into the main README or include unapproved folders.

After image confirmation, the agent automatically runs the built-in method-PPT subprocess for each retained method figure unless `method_pptx=off` is explicitly requested. The entire workflow ships in the single `paper-asset-builder` directory; contributors must not require another third-party skill or ask users to run reconstruction tools manually.

Target the complete original figure, not a simplified diagram: map its panels, labels, modules, arrows, formulas, examples, and complex visuals to a component inventory. Rebuild readable text, shapes, and lines as native PowerPoint objects; retain necessary complex photos/screenshots/illustrations as independent local raster assets and disclose their non-editable internals. A full-page PNG or SVG image, even with editable text overlays, must not be called a native editable reconstruction.

Validate the final PPTX in two ways: render that actual file and compare its complete visual content to the approved original; inspect editable text/shape/line and image structures. Source previews or successful file creation do not replace these checks. Report each figure's generation, rendering, visual, and editability outcomes; an unverified or partial result must not be marked `complete`. Preserve source scripts, inventories, crop assets, and QA reports in an isolated job workspace. Public entries default to approved images, per-figure/merged PPTX, and README; source may live in README, with separate source exports only when requested.

Run `python website/build.py` after modifying entries to refresh the static export. The builder must not execute paper code blocks; copied/downloaded code is run only in the reader's own controlled environment. Keep full PDFs, private absolute-path manifests, credentials, temporary render-test files, and unrelated hosting identities out of public exports. Online LaTeX tests require scoped upload authorization and compilation plus visual QA, as documented in the skill.

See [Getting Started](docs/GETTING_STARTED.md) for the collection workflow and [Customization](docs/CUSTOMIZATION.md) for branding and deployment. Existing assets have varying reconstruction/validation coverage; do not describe a palette-only, SVG-only, or unverified method figure as native-PPT complete.

## Recommended Paper Folder

```text
papers/year_venue_short_paper_name/
├── README.md
├── method_figures/
├── result_figures/
└── tables/
```

## Asset Naming

Use stable, descriptive names:

- `fig1_overview.png`
- `fig1_overview.pptx`
- `method_figures_editable.pptx`
- `fig2_ablation.png`
- `table1_main_results.png`

