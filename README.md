# PaperFigureAssets

A curated academic figure asset repository for reusable paper figures, result plots, and LaTeX tables.

Each paper lives in a self-contained directory with method figure previews, editable source links, result-plot reconstruction code, and LaTeX table source.

## Paper Index

<!-- PAPER_INDEX_START -->
| Paper | Venue | Year | Topic | Assets |
|---|---:|---:|---|---|
| [Dual Data Alignment Makes AI-Generated Image Detector Easier Generalizable](papers/DDA/README.md) | NeurIPS | 2025 | AI-generated image detection, dual pixel-frequency data alignment, detector generalization | 2 method figures, 3 result figures, 0 tables |
| [Emulating Human-like Adaptive Vision for Efficient and Flexible Machine Visual Perception](papers/AdaptiveNN/README.md) | Nature Machine Intelligence | 2025 | Adaptive visual perception, sequential fixation policies, efficient and interpretable computer vision | 3 method figures, 3 result figures, 0 tables |
| [LENS: Multi-level Evaluation of Multimodal Reasoning with Large Language Models](papers/LENS/README.md) | ICLR | 2026 | Multimodal reasoning evaluation, perception-understanding-reasoning task hierarchy, MLLM benchmarking | 2 method figures, 2 result figures, 1 table |
| [MMDU: A Multi-Turn Multi-Image Dialog Understanding Benchmark and Instruction-Tuning Dataset for LVLMs](papers/MMDU/README.md) | NeurIPS | 2024 | Multi-turn multi-image dialogue understanding, LVLM evaluation, long-context instruction tuning | 2 method figures, 1 result figure, 1 table |
| [Perception Encoder: The best visual embeddings are not at the output of the network](papers/Perception_Encoder/README.md) | NeurIPS | 2025 | Vision-language contrastive pretraining, intermediate visual embeddings, language and spatial alignment | 2 method figures, 2 result figures, 1 table |
| [REGNav: Room Expert Guided Image-Goal Navigation](papers/REGNav/README.md) | AAAI | 2025 | Image-goal navigation, room-relation reasoning, room-expert guided embodied policy learning | 2 method figures, 0 result figures, 0 tables |
| [STAR-Rec: Making Peace with Length Variance and Pattern Diversity in Sequential Recommendation](papers/STAR-Rec/README.md) | SIGIR | 2025 | Sequential recommendation, state-space modeling, preference-aware attention, mixture-of-experts routing | 2 method figures, 0 result figures, 0 tables |
| [Selective Underfitting in Diffusion Models](papers/SELECTIVE_UNDERFITTING_IN_DIFFUSION_MODELS/README.md) | arXiv | 2025 | Diffusion model generalization, empirical score approximation, supervision and extrapolation regions | 3 method figures, 3 result figures, 1 table |
<!-- PAPER_INDEX_END -->

## Asset Types

| Type | Folder | Included in Paper README |
|---|---|---|
| Method figures | `method_figures/` | Preview image, color palette, PPT source link when available |
| Result analysis figures | `result_figures/` | Preview image and self-contained Python plotting code |
| Paper tables | `tables/` | Preview image, LaTeX source, required packages |

## Paper Directory Pattern

```text
papers/<paper_id>/
├── README.md
├── method_figures/
├── result_figures/
└── tables/
```

## Paper Asset Builder Skill

This repository includes a local Codex skill for creating a complete paper entry from a material folder.

Material folder format:

```text
<material_dir>/
├── method_figures/
├── result_figures/
├── tables/
└── paper.pdf or arxiv.txt or paper_url.txt
```

Codex usage:

```text
使用 paper-asset-builder material_dir=/path/to/material_dir paper=https://arxiv.org/abs/2501.01234
```

Codex alternative:

```text
$paper-asset-builder material_dir=/path/to/material_dir paper=https://arxiv.org/abs/2501.01234
```

Claude Code project-local install:

```bash
mkdir -p .claude/skills
cp -R paper-asset-builder .claude/skills/paper-asset-builder
```

Claude Code personal install:

```bash
mkdir -p ~/.claude/skills
cp -R paper-asset-builder ~/.claude/skills/paper-asset-builder
```

Claude Code usage:

```text
/paper-asset-builder material_dir=/path/to/material_dir paper=https://arxiv.org/abs/2501.01234
```

The skill infers the paper topic, figure titles, plot types, and table titles, then generates the paper README and updates the root Paper Index. In Codex, invoke it by mentioning `paper-asset-builder`; in Claude Code, invoke it with `/paper-asset-builder` after installing it under a Claude skills directory.

## Copyright Policy

This repository focuses on recreated, reformatted, or reusable academic figure assets. Original paper figures are included only when redistribution is explicitly permitted by the corresponding license. Otherwise, assets are provided as recreated templates or style references.
