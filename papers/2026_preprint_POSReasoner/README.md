<div align="right">

[← Back to Home](../../README.md)

</div>

<h1 align="center">Learning to Reason with Persistent Object States for Video Instance Segmentation</h1>

---

## Paper Information

| Field | Value |
|---|---|
| Title | Learning to Reason with Persistent Object States for Video Instance Segmentation |
| Authors | Yongxue Xu, Boxue Yang, Ziqian Liu, Shaoqiu Zhang, Haopeng Chen |
| Venue | Preprint |
| Year | 2026 |
| Topic | Persistent object-state reasoning for video instance segmentation |
| Paper Link | [POSReasoner project / preprint](https://github.com/IamJerryXu/POSReasoner) |
| PDF | [Paper PDF](https://raw.githubusercontent.com/IamJerryXu/POSReasoner/06f1dba649ab4142b650e95e4c9a63a1817c4646/assets/posreasoner-preprint.pdf) |
| Source Version | GitHub commit 06f1dba649ab4142b650e95e4c9a63a1817c4646 |
| Original Asset License | Paper / figure redistribution permission has not been established. |

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
      <img src="method_figures/fig2_association_to_persistent_state_reasoning.png" alt="From Association to Persistent-state Reasoning" width="260"><br>
      <sub>From Association to Persistent-state Reasoning</sub>
    </td>
    <td align="center">—</td>
    <td align="center">—</td>
  </tr>
  <tr>
    <td align="center">
      <img src="method_figures/fig3_propose_verify_method_overview.png" alt="Propose–Verify Reasoning and Verified State Transition" width="260"><br>
      <sub>Propose–Verify Reasoning and Verified State Transition</sub>
    </td>
    <td align="center">—</td>
    <td align="center">—</td>
  </tr>
</table>

---

# 1. Method Figures

## Figure 2: From Association to Persistent-state Reasoning

<p align="center">
  <img src="method_figures/fig2_association_to_persistent_state_reasoning.png" alt="From Association to Persistent-state Reasoning" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig2_association_to_persistent_state_reasoning.png](method_figures/fig2_association_to_persistent_state_reasoning.png) |
| Source | Figure 2, PDF page 4 |
| PPT Source | Not available — reconstruction skipped at the user’s request. |

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Object identity A | ![#1196DB](https://placehold.co/20x20/1196DB/1196DB.svg) | Blue | `#1196DB` |
| Object identity B | ![#ACF8B0](https://placehold.co/20x20/ACF8B0/ACF8B0.svg) | Green | `#ACF8B0` |
| Temporal direction arrow | ![#DAE2F5](https://placehold.co/20x20/DAE2F5/DAE2F5.svg) | Blue | `#DAE2F5` |
| Film-frame source surface | ![#685D5B](https://placehold.co/20x20/685D5B/685D5B.svg) | Brown | `#685D5B` |
| Unverified writes and association errors | ![#F14D68](https://placehold.co/20x20/F14D68/F14D68.svg) | Red | `#F14D68` |
| Verified reasoning success | ![#76BD3A](https://placehold.co/20x20/76BD3A/76BD3A.svg) | Green | `#76BD3A` |

---

## Figure 3: Propose–Verify Reasoning and Verified State Transition

<p align="center">
  <img src="method_figures/fig3_propose_verify_method_overview.png" alt="Propose–Verify Reasoning and Verified State Transition" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig3_propose_verify_method_overview.png](method_figures/fig3_propose_verify_method_overview.png) |
| Source | Figure 3, PDF page 5 |
| PPT Source | [fig3_propose_verify_method_overview.pptx](method_figures/fig3_propose_verify_method_overview.pptx) — supplied AstraDraw source, unchanged |

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Frozen host and Propose modules | ![#CDE8FB](https://placehold.co/20x20/CDE8FB/CDE8FB.svg) | Blue | `#CDE8FB` |
| Verify and candidate-state modules | ![#D3E8C6](https://placehold.co/20x20/D3E8C6/D3E8C6.svg) | Green | `#D3E8C6` |
| State-writing and transition gates | ![#FFF4D4](https://placehold.co/20x20/FFF4D4/FFF4D4.svg) | Yellow | `#FFF4D4` |
| Observation / identity A accents | ![#387EAA](https://placehold.co/20x20/387EAA/387EAA.svg) | Blue | `#387EAA` |
| Verification / identity B accents | ![#547548](https://placehold.co/20x20/547548/547548.svg) | Green | `#547548` |
| Rejected probability and refinement routes | ![#C66E79](https://placehold.co/20x20/C66E79/C66E79.svg) | Pink | `#C66E79` |
| Shared-weight / legend boundary | ![#BCA8CD](https://placehold.co/20x20/BCA8CD/BCA8CD.svg) | Purple | `#BCA8CD` |
| Probability and identity-history values | ![#697B89](https://placehold.co/20x20/697B89/697B89.svg) | Gray | `#697B89` |

> User-supplied AstraDraw source, retained byte-identically. Its two slides cover the overview and reasoning detail corresponding to Figure 3. The source uses the name “State reasoner” and is a source-design variant, not a new agent reconstruction or an exact export of this paper crop. Source revision: `cc13467d3b5fe9404267e723327bf383664d96ab`.
>
> Attribution and reuse conditions: [AstraDraw SOURCES.md](https://github.com/IamJerryXu/AstraDraw/blob/cc13467d3b5fe9404267e723327bf383664d96ab/examples/paper-method/SOURCES.md). DAVIS `dogs-scale` frames `00000`, `00020`, `00040` and ground-truth mask overlays are illustrative inputs, not model predictions. Retain the original third-party notices, applicable noncommercial conditions and icon licenses when redistributing; no additional reuse grant is inferred here.

---

# 2. Result Analysis Figures

# 3. Paper Tables
