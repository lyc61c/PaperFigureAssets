# PaperFigureAssets

A curated academic figure asset repository for reusable paper figures, result plots, and LaTeX tables.

PaperFigureAssets is a static GitHub repository template for organizing reusable academic visual assets at the paper level. Each paper owns a self-contained folder with preview images, editable source placeholders, plotting examples, and LaTeX table snippets.

## What This Repository Contains

- **Method figures:** preview image + color palette + editable PPT source
- **Result analysis figures:** preview image + plotting code
- **Paper tables:** preview image + LaTeX source

## Paper Index

| Paper | Venue | Year | Assets |
|---|---:|---:|---|
| [Example Multimodal Framework](papers/2024_cvpr_example_multimodal_framework/README.md) | CVPR | 2024 | Method figures, result plots, tables |
| [Example GUI Agent](papers/2025_iclr_example_gui_agent/README.md) | ICLR | 2025 | Method figures, result plots, tables |
| [Example Document AI System](papers/2025_neurips_example_document_ai/README.md) | NeurIPS | 2025 | Method figures, result plots, tables |

## Asset Types

| Type | Folder | Description |
|---|---|---|
| Method figures | `method_figures/` | Recreated pipeline diagrams, module illustrations, and editable PPT sources. |
| Result analysis figures | `result_figures/` | Reusable plot previews with complete Python plotting examples in each paper README. |
| Paper tables | `tables/` | Table preview images with LaTeX source snippets and required packages. |

## Repository Structure

```text
PaperFigureAssets/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── .gitignore
└── papers/
    ├── 2024_cvpr_example_multimodal_framework/
    │   ├── README.md
    │   ├── method_figures/
    │   ├── result_figures/
    │   └── tables/
    ├── 2025_iclr_example_gui_agent/
    │   ├── README.md
    │   ├── method_figures/
    │   ├── result_figures/
    │   └── tables/
    └── 2025_neurips_example_document_ai/
        ├── README.md
        ├── method_figures/
        ├── result_figures/
        └── tables/
```

## Copyright Policy

This repository focuses on recreated, reformatted, or reusable academic figure assets. Original paper figures are included only when redistribution is explicitly permitted by the corresponding license. Otherwise, assets are provided as recreated templates or style references.

## Roadmap

- **v0.1:** static gallery and paper-level README pages
- **v0.2:** more paper entries and reusable templates
- **v0.3:** optional figure-to-PPT reconstruction
- **v0.4:** optional plot-to-code and table-to-LaTeX assistance

