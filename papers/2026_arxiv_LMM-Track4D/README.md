<div align="right">

[← Back to Home](../../README.md)

</div>

<h1 align="center">LMM-Track4D: Eliciting 4D Dynamic Reasoning in LMMs via Trajectory-Grounded Dialogue</h1>

---

## Paper Information

| Field | Value |
|---|---|
| Title | LMM-Track4D: Eliciting 4D Dynamic Reasoning in LMMs via Trajectory-Grounded Dialogue |
| Authors | Chaoyue Li, Yongxue Xu, Jie Feng, Jiayu Ding |
| Venue | arXiv |
| Year | 2026 |
| Topic | Geometry-grounded multi-turn dialogue and 4D trajectory reasoning |
| Paper Link | [2605.19390v1](https://arxiv.org/abs/2605.19390v1) |
| PDF | [Paper PDF](https://arxiv.org/pdf/2605.19390v1) |
| Project | [Official project](https://github.com/mikubaka88/LMM-Track4D) |
| Source Version | v1 |
| Method Figures PPT | [Editable method-figure deck](method_figures/method_figures_editable.pptx) |
| Original Asset License | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

---

## Asset Preview Gallery

<table>
  <tr>
    <th>Method Figures</th>
    <th>Result Figures</th>
    <th>Table Figures</th>
  </tr>
  <tr>
    <td align="center">
      <img src="method_figures/fig1_task_and_model_overview.png" alt="Trajectory-grounded Dialogue Task and Model Overview" width="260"><br>
      <sub>Trajectory-grounded Dialogue Task and Model Overview</sub>
    </td>
    <td align="center">—</td>
    <td align="center">—</td>
  </tr>
  <tr>
    <td align="center">
      <img src="method_figures/fig2_track4d_benchmark_construction.png" alt="Track4D-Bench Construction and Diagnostic Scope" width="260"><br>
      <sub>Track4D-Bench Construction and Diagnostic Scope</sub>
    </td>
    <td align="center">—</td>
    <td align="center">—</td>
  </tr>
  <tr>
    <td align="center">
      <img src="method_figures/fig3_lmm_track4d_method_overview.png" alt="LMM-Track4D Geometry and State-memory Architecture" width="260"><br>
      <sub>LMM-Track4D Geometry and State-memory Architecture</sub>
    </td>
    <td align="center">—</td>
    <td align="center">—</td>
  </tr>
</table>

---

# 1. Method Figures

## Figure 1: Trajectory-grounded Dialogue Task and Model Overview

<p align="center">
  <img src="method_figures/fig1_task_and_model_overview.png" alt="Trajectory-grounded Dialogue Task and Model Overview" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig1_task_and_model_overview.png](method_figures/fig1_task_and_model_overview.png) |
| Source | Figure 1, PDF page 2 |
| PPT Source | [fig1_task_and_model_overview.pptx](method_figures/fig1_task_and_model_overview.pptx) — reconstructed, not author source |

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Vision encoder | ![#FFD7BE](https://placehold.co/20x20/FFD7BE/FFD7BE.svg) | Orange | `#FFD7BE` |
| Coordinate / ray-time geometry encoder | ![#C9DEF6](https://placehold.co/20x20/C9DEF6/C9DEF6.svg) | Blue | `#C9DEF6` |
| LLM module | ![#F8EAE8](https://placehold.co/20x20/F8EAE8/F8EAE8.svg) | Pink | `#F8EAE8` |
| Multimodal token strip | ![#D3F4F1](https://placehold.co/20x20/D3F4F1/D3F4F1.svg) | Cyan | `#D3F4F1` |
| Successful stateful reasoning rows | ![#E2F1D9](https://placehold.co/20x20/E2F1D9/E2F1D9.svg) | Green | `#E2F1D9` |
| Baseline-failure rows | ![#F9DBDF](https://placehold.co/20x20/F9DBDF/F9DBDF.svg) | Pink | `#F9DBDF` |
| Ours performance-radar polygon | ![#7CB8E1](https://placehold.co/20x20/7CB8E1/7CB8E1.svg) | Blue | `#7CB8E1` |

> Reconstructed PPTX, not author source. Primary module/task labels, panels, tokens and flow geometry are native editable objects. Photographs, pictograms and local scientific illustrations remain independently movable images with non-editable pixels; Figure 2 also retains the original donut chart and small JSON illustration as images. Some formula/symbol glyphs are editable vector outlines rather than live equations or typeable text. Source fonts are substituted with installed Times New Roman/Arial; antialiasing and spacing differ. Arrows are freeforms, not bound connectors; plot paths are not data-bound charts. Final PPTX roundtrip render visually checked; PowerPoint application compatibility not tested.

---

## Figure 2: Track4D-Bench Construction and Diagnostic Scope

<p align="center">
  <img src="method_figures/fig2_track4d_benchmark_construction.png" alt="Track4D-Bench Construction and Diagnostic Scope" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig2_track4d_benchmark_construction.png](method_figures/fig2_track4d_benchmark_construction.png) |
| Source | Figure 2, PDF page 4 |
| PPT Source | [fig2_track4d_benchmark_construction.pptx](method_figures/fig2_track4d_benchmark_construction.pptx) — reconstructed, not author source |

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| KITTI domain and ring sectors | ![#18B7CA](https://placehold.co/20x20/18B7CA/18B7CA.svg) | Cyan | `#18B7CA` |
| APIDIS domain / state-preparation stage | ![#F7941D](https://placehold.co/20x20/F7941D/F7941D.svg) | Orange | `#F7941D` |
| WildTrack domain / trajectory questions | ![#6F2F9F](https://placehold.co/20x20/6F2F9F/6F2F9F.svg) | Purple | `#6F2F9F` |
| Clip formation / state labels | ![#8FAADC](https://placehold.co/20x20/8FAADC/8FAADC.svg) | Blue | `#8FAADC` |
| Dialogue construction and verification | ![#538235](https://placehold.co/20x20/538235/538235.svg) | Green | `#538235` |
| Diagnostic-scope blocks | ![#FAE9DE](https://placehold.co/20x20/FAE9DE/FAE9DE.svg) | Orange | `#FAE9DE` |
| Motion-trend question group | ![#00B050](https://placehold.co/20x20/00B050/00B050.svg) | Green | `#00B050` |

> Reconstructed PPTX, not author source. Primary module/task labels, panels, tokens and flow geometry are native editable objects. Photographs, pictograms and local scientific illustrations remain independently movable images with non-editable pixels; Figure 2 also retains the original donut chart and small JSON illustration as images. Some formula/symbol glyphs are editable vector outlines rather than live equations or typeable text. Source fonts are substituted with installed Times New Roman/Arial; antialiasing and spacing differ. Arrows are freeforms, not bound connectors; plot paths are not data-bound charts. Final PPTX roundtrip render visually checked; PowerPoint application compatibility not tested.

---

## Figure 3: LMM-Track4D Geometry and State-memory Architecture

<p align="center">
  <img src="method_figures/fig3_lmm_track4d_method_overview.png" alt="LMM-Track4D Geometry and State-memory Architecture" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig3_lmm_track4d_method_overview.png](method_figures/fig3_lmm_track4d_method_overview.png) |
| Source | Figure 3, PDF page 5 |
| PPT Source | [fig3_lmm_track4d_method_overview.pptx](method_figures/fig3_lmm_track4d_method_overview.pptx) — reconstructed, not author source |

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| RTGE geometry branch frames | ![#2E528F](https://placehold.co/20x20/2E528F/2E528F.svg) | Blue | `#2E528F` |
| Visual / position tokens | ![#BCD6ED](https://placehold.co/20x20/BCD6ED/BCD6ED.svg) | Blue | `#BCD6ED` |
| TRK state-memory tokens | ![#B994F1](https://placehold.co/20x20/B994F1/B994F1.svg) | Purple | `#B994F1` |
| TRK semantic group and track identities | ![#6F2F9F](https://placehold.co/20x20/6F2F9F/6F2F9F.svg) | Purple | `#6F2F9F` |
| OSK-RA decoder and motion curve | ![#538235](https://placehold.co/20x20/538235/538235.svg) | Green | `#538235` |
| Time / visual feature tokens | ![#C5DFB4](https://placehold.co/20x20/C5DFB4/C5DFB4.svg) | Green | `#C5DFB4` |
| Encoder / tokenizer outlines | ![#FFC000](https://placehold.co/20x20/FFC000/FFC000.svg) | Yellow | `#FFC000` |
| Word tokens | ![#D0CECE](https://placehold.co/20x20/D0CECE/D0CECE.svg) | Gray | `#D0CECE` |

> Reconstructed PPTX, not author source. Primary module/task labels, panels, tokens and flow geometry are native editable objects. Photographs, pictograms and local scientific illustrations remain independently movable images with non-editable pixels; Figure 2 also retains the original donut chart and small JSON illustration as images. Some formula/symbol glyphs are editable vector outlines rather than live equations or typeable text. Source fonts are substituted with installed Times New Roman/Arial; antialiasing and spacing differ. Arrows are freeforms, not bound connectors; plot paths are not data-bound charts. Final PPTX roundtrip render visually checked; PowerPoint application compatibility not tested.

---

# 2. Result Analysis Figures

# 3. Paper Tables
