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
| [WeVisDoc: From Coverage to Capability for Robust End-to-End Document Parsing](papers/2026_arxiv_WeVisDoc/README.md) | arXiv | 2026 | Robust end-to-end document parsing, coverage expansion, capability-aware data refinement | 2 method figures, 2 result figures, 2 tables |
| [Qwen-AgentWorld: Language World Models for General Agents](papers/2026_arxiv_Qwen-AgentWorld/README.md) | arXiv | 2026 | Language world models, seven-domain environment simulation, general-agent training | 3 method figures, 3 result figures, 2 tables |
| [AutoEnvScaling: Automating the Data Flywheel with Terminal Agents](papers/2026_arxiv_AutoEnvScaling/README.md) | arXiv | 2026 | Terminal agents, automatic environment generation, recursive data-flywheel self-improvement | 2 method figures, 3 result figures, 2 tables |
| [Towards On-Policy Data Evolution for Visual-Native Multimodal Deep Search Agents](papers/2026_arxiv_ODE/README.md) | arXiv | 2026 | Visual-native multimodal deep search, on-policy data evolution, agent SFT and reinforcement learning | 1 method figures, 4 result figures, 1 tables |
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

This repository includes a local Codex skill for creating a complete paper entry from a paper URL/PDF or a prepared material folder.

With only a paper, the skill first selects attractive, representative method diagrams, result plots, and tables; extracts complete high-resolution PNG regions from the PDF; and organizes them under `../materials/<paper_id>/`. It reports the local material directory and pauses for you to review the images. After you confirm, it rereads the directory's current files, generates the paper README, and updates the root Paper Index. You may delete, replace, rename, or add images during review; the final local selection is used for generation.

Material folder format (include only the asset folders you have):

```text
<material_dir>/
├── method_figures/   # optional
├── result_figures/   # optional
├── tables/           # optional
└── paper.pdf or arxiv.txt or paper_url.txt
```

At least one of the optional asset folders must contain an image after preparation. Missing asset types are recorded with a zero count and retain an empty section in the generated paper README. Existing supplied images are used by default; automatic extraction runs when no images have been supplied, or when `extract_assets=true` is requested. Source pages, captions, crop coordinates, and selection reasons are retained locally in `source_assets.json`.

Codex usage:

```text
使用 paper-asset-builder paper=https://arxiv.org/abs/2501.01234
```

Codex alternative:

```text
$paper-asset-builder material_dir=/path/to/material_dir paper=https://arxiv.org/abs/2501.01234
```

`material_dir` is optional. Provide it to choose the extraction destination or reuse prepared images. `paper_id` optionally sets the entry directory name; otherwise it is inferred from the paper.

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

The skill infers the paper topic, figure titles, plot types, and table titles, then generates the paper README and updates the root Paper Index after any pending image review is confirmed. Reply with `检查好了，继续` to resume from the reviewed directory without repeating the invocation or extraction. In Codex, invoke it by mentioning `paper-asset-builder`; in Claude Code, invoke it with `/paper-asset-builder` after installing it under a Claude skills directory.

### LaTeX Render Tests

Generated table source can be compiled and visually checked before delivery. `latex_test=auto` uses an available local or built-in compiler; online compilation is used only with authorization. Set `latex_test=online` to select the supported [LaTeX-on-HTTP API](https://github.com/YtoTech/latex-on-http#api), `local` to avoid uploads, or `off` to explicitly skip compilation. Only the selected table source, its declared packages, and a minimal test wrapper are sent, never the whole paper or material directory. Public services may be unavailable and do not provide a verified retention guarantee; private material should use a local or self-hosted compiler.

The skill's `scripts/latex_render_test.py` prepares isolated test documents, saves compilation diagnostics, and renders previews when PyMuPDF is available. A PDF response is followed by visual comparison with the approved table image; it is not treated as proof that values and layout are correct. Temporary QA PDFs, previews, and logs remain outside the paper gallery. See [the render-testing reference](paper-asset-builder/references/latex_render_testing.md) for the workflow.

## Copyright Policy

This repository focuses on recreated, reformatted, or reusable academic figure assets. Original paper figures are included only when redistribution is explicitly permitted by the corresponding license. Otherwise, assets are provided as recreated templates or style references.

Third-party figure/table previews retain their original copyrights and licenses, documented in each paper README, and are excluded from the repository's MIT license. An arXiv non-exclusive distribution license does not itself grant third-party reuse rights. Consult the original rightsholders where a public reuse license or separate permission is not documented; reconstruction examples do not imply broader rights to the original artwork.
