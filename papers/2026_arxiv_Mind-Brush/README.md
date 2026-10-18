<div align="right">

[← Back to Home](../../README.md)

</div>

<h1 align="center">Mind-Brush: Integrating Agentic Cognitive Search and Reasoning into Image Generation</h1>

---

## Paper Information

| Field | Value |
|---|---|
| Title | Mind-Brush: Integrating Agentic Cognitive Search and Reasoning into Image Generation |
| Authors | Jun He, Junyan Ye, Zilong Huang, Dongzhi Jiang, Chenjue Zhang, Leqi Zhu, Renrui Zhang, Xiang Zhang, Weijia Li |
| Venue | arXiv |
| Year | 2026 |
| Topic | Agentic cognitive search and explicit reasoning for knowledge-grounded image generation |
| Paper Link | [arXiv:2602.01756v1](https://arxiv.org/abs/2602.01756v1) |
| Project | [Mind-Brush](https://github.com/PicoTrex/Mind-Brush) |
| Dataset | [Mind-Brush on Hugging Face](https://huggingface.co/datasets/PicoTrex/Mind-Brush) |
| Original Asset License | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), as linked from the arXiv record; third-party reference imagery may carry separate terms. |
| Asset Type | 3 method figures, 0 result figures, 0 tables |
| Method Figures PPT | [Download all 3 editable figures](method_figures/method_figures_editable.pptx) |

Figures are attributed to the authors above. The previews reproduce the approved paper artwork; the PPT files are ReFigure reconstructions, not author-provided source. Figure 1 is a concept/capability overview, not an implementation architecture or a quantitative chart. Ordinary qualitative comparisons and tables were not selected.

Text, containers, arrows, numbered steps, checklist marks and flag geometry are native PowerPoint objects. Photos, generated examples, maps, retrieved-image strips, logos and complex icons are independently movable images; their internal pixels and embedded example labels are not editable. Comic Sans MS and Arial approximate the source lettering, with platform fallback for Chinese text. Gradients, shadows, dotted fill texture, mixed-weight details and dash spacing have minor approximations. Pale oversized step numbers are editable vector outlines rather than typeable text. Arrows are editable freeform paths, not endpoint-bound connectors. The actual final PPTX files were rendered and visually checked through Artifact Tool; PowerPoint application compatibility was not tested.

Appendix B.3 identifies third-party sources including Wikipedia CC BY-SA 3.0 material, weather and recipe websites, and MathVerse. The paper license does not override those sources' separate conditions.

---

## Asset Preview Gallery

<table>
  <tr><th>Method Figures</th><th>Result Figures</th><th>Table Figures</th></tr>
  <tr>
    <td align="center"><img src="method_figures/fig1_cognitive_generation_capability_overview.png" alt="Cognitive Generation Capability Overview" width="260"><br><sub>Cognitive Generation Capability Overview</sub></td>
    <td align="center"><sub>No result figures selected</sub></td>
    <td align="center"><sub>No table figures selected</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="method_figures/fig2_mind_brush_framework.png" alt="Search and Reasoning Framework" width="260"><br><sub>Search and Reasoning Framework</sub></td><td></td><td></td>
  </tr>
  <tr>
    <td align="center"><img src="method_figures/fig3_checklist_based_strict_accuracy_evaluation.png" alt="Checklist-based Strict Accuracy Evaluation" width="260"><br><sub>Checklist-based Strict Accuracy Evaluation</sub></td><td></td><td></td>
  </tr>
</table>

---

# 1. Method Figures

## Figure 1: Cognitive Generation Capability Overview

<p align="center">
  <img src="method_figures/fig1_cognitive_generation_capability_overview.png" alt="Cognitive Generation Capability Overview" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig1_cognitive_generation_capability_overview.png](method_figures/fig1_cognitive_generation_capability_overview.png) |
| Source | Figure 1, PDF page 1; complete ten-task capability overview from arXiv v1. |
| PPT Source | [fig1_cognitive_generation_capability_overview.pptx](method_figures/fig1_cognitive_generation_capability_overview.pptx) |

The ten task cards retain their prompts, evidence descriptions, task labels and search/reasoning-to-generation organization. Card geometry and narrative labels are editable; example imagery and the central illustrated MindBrush logo remain local image objects. The overview contains no quantitative measurements, so no numerical plotting code is invented.

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Object tasks | ![#A6ECAE](https://placehold.co/20x20/A6ECAE/A6ECAE.svg) | Green | `#A6ECAE` |
| Special events | ![#98F5E2](https://placehold.co/20x20/98F5E2/98F5E2.svg) | Teal | `#98F5E2` |
| Weather | ![#8EECF4](https://placehold.co/20x20/8EECF4/8EECF4.svg) | Cyan | `#8EECF4` |
| Character knowledge | ![#8FDBF3](https://placehold.co/20x20/8FDBF3/8FDBF3.svg) | Blue | `#8FDBF3` |
| World knowledge | ![#F6F092](https://placehold.co/20x20/F6F092/F6F092.svg) | Yellow | `#F6F092` |
| Mathematics | ![#A3C3F2](https://placehold.co/20x20/A3C3F2/A3C3F2.svg) | Blue | `#A3C3F2` |
| Life reasoning | ![#FBC394](https://placehold.co/20x20/FBC394/FBC394.svg) | Orange | `#FBC394` |
| Geographic reasoning | ![#FFA7AD](https://placehold.co/20x20/FFA7AD/FFA7AD.svg) | Pink | `#FFA7AD` |
| Poetry | ![#F0C0E8](https://placehold.co/20x20/F0C0E8/F0C0E8.svg) | Pink | `#F0C0E8` |
| Science and logic | ![#CEBAEF](https://placehold.co/20x20/CEBAEF/CEBAEF.svg) | Purple | `#CEBAEF` |

---

## Figure 2: Search and Reasoning Framework

<p align="center">
  <img src="method_figures/fig2_mind_brush_framework.png" alt="Search and Reasoning Framework" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig2_mind_brush_framework.png](method_figures/fig2_mind_brush_framework.png) |
| Source | Figure 2, PDF page 4; complete framework including both routes and the shared toolbox, arXiv v1. |
| PPT Source | [fig2_mind_brush_framework.pptx](method_figures/fig2_mind_brush_framework.pptx) |

Both intent-to-generation routes, action bars and toolbox groups are reconstructed as native text and geometry. Retrieved portraits, generated examples and tool pictograms remain independent images. Geometry and labels inside the original generated geometry examples remain raster evidence; the separate reasoning equations are editable text.

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Intent analysis | ![#FFA99C](https://placehold.co/20x20/FFA99C/FFA99C.svg) | Red | `#FFA99C` |
| Query construction and search | ![#F8BD8B](https://placehold.co/20x20/F8BD8B/F8BD8B.svg) | Orange | `#F8BD8B` |
| Knowledge reasoning | ![#EEB6E3](https://placehold.co/20x20/EEB6E3/EEB6E3.svg) | Pink | `#EEB6E3` |
| Concept review | ![#CEB9F1](https://placehold.co/20x20/CEB9F1/CEB9F1.svg) | Purple | `#CEB9F1` |
| Image generation | ![#AEC8EF](https://placehold.co/20x20/AEC8EF/AEC8EF.svg) | Blue | `#AEC8EF` |
| Shared toolbox | ![#9AE3DA](https://placehold.co/20x20/9AE3DA/9AE3DA.svg) | Teal | `#9AE3DA` |

---

## Figure 3: Checklist-based Strict Accuracy Evaluation

<p align="center">
  <img src="method_figures/fig3_checklist_based_strict_accuracy_evaluation.png" alt="Checklist-based Strict Accuracy Evaluation" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig3_checklist_based_strict_accuracy_evaluation.png](method_figures/fig3_checklist_based_strict_accuracy_evaluation.png) |
| Source | Figure 3, PDF page 5; complete CSA evaluation schematic from arXiv v1. |
| PPT Source | [fig3_checklist_based_strict_accuracy_evaluation.pptx](method_figures/fig3_checklist_based_strict_accuracy_evaluation.pptx) |

The prompt, reference flag geometry, four criteria, numbered diamonds, underlines and pass/fail indicators are native editable objects. The generated scoreboard example with its internal annotations, the Spanish coat of arms and circular pictograms remain independent original image crops. The displayed 3/4 verdict is preserved as an example of the evaluation rule, not introduced as a new experimental measurement.

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Prompt | ![#3399E2](https://placehold.co/20x20/3399E2/3399E2.svg) | Blue | `#3399E2` |
| Visual references | ![#F48B8B](https://placehold.co/20x20/F48B8B/F48B8B.svg) | Pink | `#F48B8B` |
| Evaluation grouping | ![#FBDA65](https://placehold.co/20x20/FBDA65/FBDA65.svg) | Yellow | `#FBDA65` |
| Satisfied checks | ![#10915D](https://placehold.co/20x20/10915D/10915D.svg) | Green | `#10915D` |
| Failed check | ![#F25B5F](https://placehold.co/20x20/F25B5F/F25B5F.svg) | Red | `#F25B5F` |

---

# 2. Result Analysis Figures

No result figures selected.

---

# 3. Paper Tables

No table figures selected.
