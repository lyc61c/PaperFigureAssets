# Contributing

Figarium · 图圃 (in the compatible `PaperFigureAssets` repository) is a human-curated, reproducible paper-figure library with a static gallery. Keep contributions simple, reproducible, and license-aware.

## Guidelines

1. Use one directory per paper under `papers/`.
2. Every paper directory must include a `README.md`.
3. Put method figure previews and PPT sources in `method_figures/`.
4. Put result analysis figure previews in `result_figures/`.
5. Put table preview images in `tables/`.
6. Write plotting code, color palettes, LaTeX table source, and feasible editable SVG/TikZ method reconstructions directly in the paper `README.md`; distinguish reconstructed source from author-provided source and label approximations/limitations.
7. Do not upload original paper figures without reuse permission unless the paper license explicitly allows redistribution.

For new papers, the skill defaults to inventorying and extracting all numbered figures/tables (including appendices), then pauses for human selection. Preserve coverage/provenance in the local material manifest. After confirmation, use only the local directory's current images; do not restore deleted selections. Keep the canonical paper README template unchanged and preserve existing valid root index rows.

Run `python website/build.py` after modifying entries to refresh the static export. The builder must not execute paper code blocks; copied/downloaded code is run only in the reader's own controlled environment. Keep full PDFs, private absolute-path manifests, credentials, temporary render-test files, and unrelated hosting identities out of public exports. Online LaTeX tests require scoped upload authorization and compilation plus visual QA, as documented in the skill.

See [Getting Started](docs/GETTING_STARTED.md) for the collection workflow and [Customization](docs/CUSTOMIZATION.md) for branding and deployment. Existing assets have varying reconstruction coverage; do not describe a palette-only method figure as editable-code complete.

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
- `fig2_ablation.png`
- `table1_main_results.png`

