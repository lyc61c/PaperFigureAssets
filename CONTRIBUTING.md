# Contributing

PaperFigureAssets is organized as a static, paper-level asset gallery. Keep contributions simple, reproducible, and license-aware.

## Guidelines

1. Use one directory per paper under `papers/`.
2. Every paper directory must include a `README.md`.
3. Put method figure previews and PPT sources in `method_figures/`.
4. Put result analysis figure previews in `result_figures/`.
5. Put table preview images in `tables/`.
6. Write plotting code, color palettes, and LaTeX table source directly in the paper `README.md`.
7. Do not upload original paper figures without reuse permission unless the paper license explicitly allows redistribution.

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

