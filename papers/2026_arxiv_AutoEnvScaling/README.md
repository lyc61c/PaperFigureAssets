<div align="right">

[← Back to Home](../../README.md)

</div>

<h1 align="center">AutoEnvScaling: Automating the Data Flywheel with Terminal Agents</h1>

---

## Paper Information

| Field | Value |
|---|---|
| Title | AutoEnvScaling: Automating the Data Flywheel with Terminal Agents |
| Venue | arXiv |
| Year | 2026 |
| LaTeX Validation | 2/2 tables compiled with pdfLaTeX via LaTeX-on-HTTP and visually checked against the approved images on 2026-10-14. |
| Authors | Simon Yu, Baolin Peng, Bo Liu, Zhengyan Shi, Zhaoyang Wang, Hao Cheng, Qianhui Wu, Wenlin Yao, Natasha Jaques, Weiyan Shi, Jianfeng Gao |
| Original Asset License | [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) |
| Topic | Terminal agents, automatic environment generation, recursive data-flywheel self-improvement |
| Paper Link | [arXiv paper](https://arxiv.org/abs/2610.14163v1) |
| Code | [Official code](https://aka.ms/autoenvscaling) |
| Project / Blog | [Project page](https://microsoft.github.io/Orchard-Agentic/autoenvscaling/) |
| Assets | 2 method figures, 3 result figures, 2 tables |
| Asset Source | User-reviewed local PNGs extracted from the linked paper PDF; original labels and pages are listed below. |
| Method Figures PPT | [All method figures — editable reconstruction](method_figures/method_figures_editable.pptx) |
| Method PPT Notes | Newly reconstructed, not author-provided source. Native text and vector paths; some equations/tiny glyphs are editable outlines, not typeable text. Arrows are not endpoint-bound; charts are not data-bound. Photos, illustrations, and local effects remain independent raster objects. Fonts/shadows/gradients may differ. Final PPTX roundtrip-rendered and visually checked; PowerPoint desktop not tested. |

---

## Asset Preview Gallery

Original figure/table previews are excerpts from [the paper](https://arxiv.org/abs/2610.14163v1) by Simon Yu, Baolin Peng, Bo Liu, Zhengyan Shi, Zhaoyang Wang, Hao Cheng, Qianhui Wu, Wenlin Yao, Natasha Jaques, Weiyan Shi, Jianfeng Gao, distributed here for noncommercial scholarly reference under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/). The complete selected figure/table regions were rendered from the PDF into PNG; surrounding page text and external captions were excluded, and the artwork itself was not altered. Third-party previews are not covered by this repository's MIT license. Reconstruction code and LaTeX are newly written approximations/transcriptions, not author-provided source; they do not expand the original material's reuse permissions. No endorsement by the original authors is implied.

<table>
  <tr>
    <th>Method Figures</th>
    <th>Result Figures</th>
    <th>Table Figures</th>
  </tr>
  <tr>
    <td align="center">
      <img src="method_figures/fig2_data_flywheel_framework.png" alt="Automated Environment Data Flywheel" width="260"><br>
      <sub>Figure 2: Automated Environment Data Flywheel</sub>
    </td>
    <td align="center">
      <img src="result_figures/fig1_generation_training_self_improvement.png" alt="Generation Quality, Training Gains, and Self-Improvement" width="260"><br>
      <sub>Figure 1: Generation Quality, Training Gains, and Self-Improvement</sub>
    </td>
    <td align="center">
      <img src="tables/table1_environment_generation_methods.png" alt="Environment Generation Method Comparison" width="260"><br>
      <sub>Table 1: Environment Generation Method Comparison</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="method_figures/fig3_environment_design_and_self_play.png" alt="Environment Design and Calibrated Self-Play" width="260"><br>
      <sub>Figure 3: Environment Design and Calibrated Self-Play</sub>
    </td>
    <td align="center">
      <img src="result_figures/fig4_valid_environment_rate_comparison.png" alt="Valid Environment Rates Across Proposer Models" width="260"><br>
      <sub>Figure 4: Valid Environment Rates Across Proposer Models</sub>
    </td>
    <td align="center">
      <img src="tables/table2_validity_and_cost.png" alt="Environment Validity and Generation Cost" width="260"><br>
      <sub>Table 2: Environment Validity and Generation Cost</sub>
    </td>
  </tr>
  <tr>
    <td></td>
    <td align="center">
      <img src="result_figures/fig6_recursive_self_improvement.png" alt="Recursive Self-Improvement of Solvers and Proposers" width="260"><br>
      <sub>Figure 6: Recursive Self-Improvement of Solvers and Proposers</sub>
    </td>
    <td></td>
  </tr>
</table>

---

# 1. Method Figures

## Figure 2: Automated Environment Data Flywheel

<p align="center">
  <img src="method_figures/fig2_data_flywheel_framework.png" alt="Automated Environment Data Flywheel" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig2_data_flywheel_framework.png](method_figures/fig2_data_flywheel_framework.png) |
| PPT Source | [Editable native/hybrid reconstruction](method_figures/fig2_data_flywheel_framework.pptx) |
| Source | Figure 2, PDF page 2 of the [paper](https://arxiv.org/abs/2610.14163v1) |

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Solver training and feedback | ![#237E7B](https://placehold.co/20x20/237E7B/237E7B.svg) | Teal | `#237E7B` |
| Proposer and agent harness | ![#31006E](https://placehold.co/20x20/31006E/31006E.svg) | Purple | `#31006E` |
| Harbor task modules | ![#77AAA3](https://placehold.co/20x20/77AAA3/77AAA3.svg) | Teal | `#77AAA3` |
| Workspace connections | ![#9076B1](https://placehold.co/20x20/9076B1/9076B1.svg) | Purple | `#9076B1` |
| Valid environments | ![#31724F](https://placehold.co/20x20/31724F/31724F.svg) | Green | `#31724F` |
| Ubuntu environment | ![#E8541F](https://placehold.co/20x20/E8541F/E8541F.svg) | Orange | `#E8541F` |

### Editable Diagram Code

Note: Editable schematic reconstruction; not author-provided source. Fine-grained layout and icon artwork are simplified.

Save the code below as an `.svg` file. Edit `<text>` labels, `fill` / `stroke` colors, and `<path d="...">` connections to customize the diagram; all shapes and labels remain vector-editable.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 695" role="img" aria-labelledby="title desc">
<title id="title">AutoEnvScaling — automated environment data flywheel</title>
<desc id="desc">Editable schematic: the solver trains on accepted Harbor tasks; its rollouts guide a proposer inside a coding sandbox, supported by a workspace, web search, and child sandboxes.</desc>
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
<path d="M0 0L10 5L0 10Z" fill="#64748B"/>
</marker>
  <marker id="teal-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">
<path d="M0 0L10 5L0 10Z" fill="#237E7B"/>
</marker>
  <marker id="purple-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">
<path d="M0 0L10 5L0 10Z" fill="#6B3FA0"/>
</marker>
</defs>
<rect width="1440" height="695" fill="#FFFFFF"/>
<g font-family="Arial, Helvetica, sans-serif">
<text x="30" y="44" font-size="29" fill="#253247" font-weight="700" text-anchor="start">AutoEnvScaling · Automated environment data flywheel</text>
<text x="30" y="73" font-size="17" fill="#253247" font-weight="400" text-anchor="start">Solver experience guides environment construction; accepted tasks feed the next training round</text>
<rect x="30" y="112" width="280" height="440" rx="12" fill="#EFF7F5" stroke="#237E7B" stroke-width="2"/>
<text x="50" y="152" font-size="24" fill="#237E7B" font-weight="700" text-anchor="start">Solver training</text>
<rect x="65" y="190" width="215" height="67" rx="9" fill="#FFFFFF" stroke="#77AAA3" stroke-width="2"/>
<text x="172.5" y="231" font-size="22" fill="#237E7B" font-weight="700" text-anchor="middle">Policy</text>
<rect x="65" y="306" width="215" height="76" rx="9" fill="#FFFFFF" stroke="#77AAA3" stroke-width="2"/>
<text x="172.5" y="351" font-size="22" fill="#237E7B" font-weight="700" text-anchor="middle">Terminals</text>
<path d="M173 257V306" fill="none" stroke="#237E7B" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#teal-arrow)"/>
<text x="190" y="286" font-size="15" fill="#237E7B" font-weight="400" text-anchor="start">Rollout</text>
<path d="M65 344H46V224H65" fill="none" stroke="#237E7B" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#teal-arrow)"/>
<text x="50" y="412" font-size="15" fill="#237E7B" font-weight="600" text-anchor="start">Verifier rewards → RL updates</text>
<rect x="50" y="447" width="240" height="76" rx="9" fill="#FFFFFF" stroke="#77AAA3" stroke-width="2"/>
<text x="170" y="478" font-size="20" fill="#237E7B" font-weight="700" text-anchor="middle">Training pool</text>
<text x="170" y="503" font-size="15" fill="#526173" font-weight="400" text-anchor="middle">Accepted environments</text>
<path d="M173 447V431H297V382H280" fill="none" stroke="#237E7B" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#teal-arrow)"/>
<path d="M310 274H390" fill="none" stroke="#237E7B" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#teal-arrow)"/>
<text x="350" y="246" font-size="15" fill="#526173" font-weight="600" text-anchor="middle">Solver</text>
<text x="350" y="265" font-size="15" fill="#526173" font-weight="600" text-anchor="middle">rollouts</text>
<rect x="390" y="112" width="650" height="440" rx="12" fill="#F5F0FA" stroke="#6B3FA0" stroke-width="2"/>
<text x="410" y="152" font-size="24" fill="#31006E" font-weight="700" text-anchor="start">Sandbox + coding harness</text>
<rect x="410" y="181" width="270" height="328" rx="9" fill="#FFFFFF" stroke="#C7B4DD" stroke-width="2"/>
<text x="430" y="215" font-size="21" fill="#31006E" font-weight="700" text-anchor="start">workspace/</text>
<text x="430" y="256" font-size="18" fill="#4D3D61" font-weight="400" text-anchor="start">past_rollouts/</text>
<text x="430" y="296" font-size="18" fill="#4D3D61" font-weight="400" text-anchor="start">  failed/</text>
<text x="430" y="336" font-size="18" fill="#4D3D61" font-weight="400" text-anchor="start">  successful/</text>
<text x="430" y="376" font-size="18" fill="#4D3D61" font-weight="400" text-anchor="start">past_environments/</text>
<text x="430" y="416" font-size="18" fill="#4D3D61" font-weight="400" text-anchor="start">memory/</text>
<text x="430" y="456" font-size="18" fill="#4D3D61" font-weight="400" text-anchor="start">tools/</text>
<rect x="710" y="181" width="310" height="165" rx="9" fill="#3F2A5D" stroke="#3F2A5D" stroke-width="2"/>
<text x="730" y="216" font-size="23" fill="#FFFFFF" font-weight="700" text-anchor="start">Proposer</text>
<text x="730" y="253" font-size="17" fill="#FFFFFF" font-weight="400" text-anchor="start">$ inspect experience</text>
<text x="730" y="285" font-size="17" fill="#FFFFFF" font-weight="400" text-anchor="start">$ build + repair</text>
<text x="730" y="317" font-size="17" fill="#FFFFFF" font-weight="400" text-anchor="start">$ validate environment</text>
<path d="M683 275H707" fill="none" stroke="#9076B1" stroke-width="2.5" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<rect x="710" y="400" width="145" height="109" rx="9" fill="#FFFFFF" stroke="#77AAA3" stroke-width="2"/>
<text x="782.5" y="433" font-size="16" fill="#237E7B" font-weight="700" text-anchor="middle">Child sandboxes</text>
<text x="782.5" y="463" font-size="15" fill="#526173" font-weight="400" text-anchor="middle">Build tasks</text>
<text x="782.5" y="486" font-size="15" fill="#526173" font-weight="400" text-anchor="middle">Execute tests</text>
<rect x="875" y="400" width="145" height="109" rx="9" fill="#FFFFFF" stroke="#C7B4DD" stroke-width="2"/>
<text x="947.5" y="433" font-size="17" fill="#6B3FA0" font-weight="700" text-anchor="middle">Web search</text>
<text x="947.5" y="463" font-size="15" fill="#526173" font-weight="400" text-anchor="middle">Docs / sources</text>
<text x="947.5" y="486" font-size="15" fill="#526173" font-weight="400" text-anchor="middle">Tool resources</text>
<path d="M865 346V373H782V400" fill="none" stroke="#9076B1" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#arrow)"/>
<path d="M865 373H948V400" fill="none" stroke="#9076B1" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#arrow)"/>
<path d="M1040 274H1110" fill="none" stroke="#6B3FA0" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#purple-arrow)"/>
<rect x="1110" y="112" width="300" height="440" rx="12" fill="#F2F8F6" stroke="#77AAA3" stroke-width="2"/>
<text x="1130" y="152" font-size="24" fill="#237E7B" font-weight="700" text-anchor="start">Harbor task</text>
<text x="1135" y="210" font-size="20" fill="#3F2A5D" font-weight="400" text-anchor="start">task.toml</text>
<text x="1135" y="253" font-size="20" fill="#3F2A5D" font-weight="400" text-anchor="start">instruction.md</text>
<text x="1135" y="296" font-size="20" fill="#3F2A5D" font-weight="400" text-anchor="start">environment/</text>
<text x="1135" y="339" font-size="20" fill="#3F2A5D" font-weight="400" text-anchor="start">  Dockerfile</text>
<text x="1135" y="382" font-size="20" fill="#3F2A5D" font-weight="400" text-anchor="start">solution/</text>
<text x="1135" y="425" font-size="20" fill="#3F2A5D" font-weight="400" text-anchor="start">tests/</text>
<rect x="1130" y="478" width="260" height="54" rx="8" fill="#3F2A5D" stroke="#3F2A5D" stroke-width="2"/>
<text x="1260" y="512" font-size="20" fill="#C1E4DB" font-weight="600" text-anchor="middle">$ execute task</text>
<path d="M1260 552V623H170V523" fill="none" stroke="#237E7B" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#teal-arrow)"/>
<rect x="490" y="600" width="510" height="40" rx="0" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="2"/>
<text x="745" y="627" font-size="21" fill="#237E7B" font-weight="700" text-anchor="middle">Accepted new environments → training pool</text>
<text x="30" y="671" font-size="15" fill="#64748B" font-weight="400" text-anchor="start">Schematic reconstruction: file hierarchy and feedback loop retained; icon artwork simplified.</text>
</g>
</svg>
```


---

## Figure 3: Environment Design and Calibrated Self-Play

<p align="center">
  <img src="method_figures/fig3_environment_design_and_self_play.png" alt="Environment Design and Calibrated Self-Play" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig3_environment_design_and_self_play.png](method_figures/fig3_environment_design_and_self_play.png) |
| PPT Source | [Editable native/hybrid reconstruction](method_figures/fig3_environment_design_and_self_play.pptx) |
| Source | Figure 3, PDF page 4 of the [paper](https://arxiv.org/abs/2610.14163v1) |

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Environment generation pipeline | ![#674293](https://placehold.co/20x20/674293/674293.svg) | Purple | `#674293` |
| Terminal workspace | ![#3F2A5D](https://placehold.co/20x20/3F2A5D/3F2A5D.svg) | Purple | `#3F2A5D` |
| Solver calibration | ![#237E7B](https://placehold.co/20x20/237E7B/237E7B.svg) | Teal | `#237E7B` |
| Verifier success | ![#31724F](https://placehold.co/20x20/31724F/31724F.svg) | Green | `#31724F` |
| Failure feedback | ![#BF6959](https://placehold.co/20x20/BF6959/BF6959.svg) | Red | `#BF6959` |
| Failure feedback fill | ![#F2B8AE](https://placehold.co/20x20/F2B8AE/F2B8AE.svg) | Pink | `#F2B8AE` |

---

# 2. Result Analysis Figures

## Figure 1: Generation Quality, Training Gains, and Self-Improvement

<p align="center">
  <img src="result_figures/fig1_generation_training_self_improvement.png" alt="Generation Quality, Training Gains, and Self-Improvement" width="720">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig1_generation_training_self_improvement.png](result_figures/fig1_generation_training_self_improvement.png) |
| Source | Figure 1, PDF page 1 of the [paper](https://arxiv.org/abs/2610.14163v1) |

### Color Palette

Representative colors sampled from the original image; HEX values are approximate.

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Representative color 1 | ![#32006E](https://placehold.co/20x20/32006E/32006E.svg) | Purple | `#32006E` |
| Representative color 2 | ![#208C8D](https://placehold.co/20x20/208C8D/208C8D.svg) | Teal | `#208C8D` |
| Representative color 3 | ![#7A55B5](https://placehold.co/20x20/7A55B5/7A55B5.svg) | Purple | `#7A55B5` |
| Representative color 4 | ![#B9B4C7](https://placehold.co/20x20/B9B4C7/B9B4C7.svg) | Purple | `#B9B4C7` |
| Representative color 5 | ![#3A3145](https://placehold.co/20x20/3A3145/3A3145.svg) | Purple | `#3A3145` |

### Plotting Code

Note: The following code is an approximate visual reconstruction based on the provided figure.

Printed bar labels are transcribed; aggregate error bars and learning-curve samples are approximate.

Requires Python 3 with NumPy and Matplotlib.

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.titlesize": 11, "axes.labelsize": 10,
                     "axes.linewidth": 0.7, "savefig.facecolor": "white"})

def style(ax, axis="y"):
    ax.set_axisbelow(True)
    ax.grid(axis=axis, color="#E4E7EC", linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["bottom", "left"]].set_color("#B8BDC5")
    ax.tick_params(length=3, color="#A0A6AF")

purple, teal, light = "#31006E", "#1C9298", "#C9BAE4"
fig, axes = plt.subplots(1, 3, figsize=(13, 3.3), gridspec_kw={"width_ratios": [1, 1.15, 1.05]})
ax = axes[0]
values = [39, 57, 86]
ax.bar(range(3), values, width=0.64, color=[light, "#8057B0", purple],
       edgecolor="#68517E", yerr=[17, 22, 8], capsize=4)
for x, y in enumerate(values):
    ax.text(x, y + [19, 24, 10][x], f"{y}%", ha="center", fontsize=10, weight="bold", color="#30213E")
ax.set(xticks=range(3), xticklabels=["Prompt", "Prompt +\nEnv Feedback", "AutoEnv-\nScaling"],
       ylabel="Valid-environment rate (%)", ylim=(0, 110), title="Environment generation")
ax.set_yticks([0, 25, 50, 75, 100])
style(ax)
ax = axes[1]
x = np.arange(2)
for shift, values, color, label in [(-0.24, [19.1, 26.7], "#B8B4C5", "Base"),
                                  (0, [27.2, 34.6], teal, "Tmax"),
                                  (0.24, [33.5, 38.9], purple, "AutoEnvScaling")]:
    bars = ax.bar(x + shift, values, width=0.24, color=color, edgecolor="#5E5969", lw=0.5, label=label)
    for bar, y in zip(bars, values):
        ax.text(bar.get_x()+bar.get_width()/2, y+0.7, f"{y:.1f}", ha="center", fontsize=8)
for i, (base, ours, gain) in enumerate([(27.2, 33.5, 6.3), (34.6, 38.9, 4.3)]):
    ax.plot([i, i, i+0.24, i+0.24], [base+3, ours+5, ours+5, ours+3], color=purple, lw=1)
    ax.text(i+0.12, ours+5.5, f"+{gain}", ha="center", color=purple, weight="bold", fontsize=9)
ax.set(xticks=x, xticklabels=["Qwen3.5-9B", "Qwen3.5-35B-A3B"], ylabel="Terminal-Bench 2.1",
       ylim=(0, 55), title="Solver RL on generated environments")
ax.legend(ncol=3, fontsize=7, loc="upper center", frameon=False)
style(ax)
ax = axes[2]
steps = [0, 30, 60, 95, 130, 165, 200, 235, 265, 300]
tmax = [41.1, 41.8, 40.7, 43.9, 44.4, 45.0, 45.4, 46.8, 47.0, 47.2]
ours = [41.1, 41.8, 42.5, 44.3, 45.2, 48.9, 50.0, 50.2, 51.5, 53.3]
ax.plot(steps, tmax, "^-", color=teal, ms=4, lw=1.2, label="Tmax")
ax.plot(steps, ours, "s-", color=purple, ms=4, lw=1.8, label="AutoEnvScaling")
ax.axhline(41.1, color="#9E91BD", ls=":", lw=1)
ax.annotate("", xy=(320, 53.3), xytext=(320, 41.1),
            arrowprops={"arrowstyle": "<->", "color": purple})
ax.text(324, 47.2, "+12.2", color=purple, rotation=90, va="center", weight="bold", fontsize=9)
ax.text(300, 54, "53.3", ha="right", color=purple, weight="bold")
ax.text(300, 46.5, "47.2", ha="right", color=teal)
ax.text(300, 40.3, "Cold-Start 41.1", ha="right", color="#807394", fontsize=8)
ax.set(xlim=(-5, 335), ylim=(39, 56), xticks=[0, 100, 200, 300], yticks=[40, 45, 50, 55],
       xlabel="RL training step", ylabel="Terminal-Bench 2.1", title="Self-improvement")
ax.legend(frameon=False, fontsize=8, loc="upper left")
style(ax)
fig.subplots_adjust(left=0.06, right=0.98, bottom=0.21, top=0.86, wspace=0.42)

fig.savefig("fig1_summary_reconstructed.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

## Figure 4: Valid Environment Rates Across Proposer Models

<p align="center">
  <img src="result_figures/fig4_valid_environment_rate_comparison.png" alt="Valid Environment Rates Across Proposer Models" width="720">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig4_valid_environment_rate_comparison.png](result_figures/fig4_valid_environment_rate_comparison.png) |
| Source | Figure 4, PDF page 6 of the [paper](https://arxiv.org/abs/2610.14163v1) |

### Color Palette

Representative colors sampled from the original image; HEX values are approximate.

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Representative color 1 | ![#32006E](https://placehold.co/20x20/32006E/32006E.svg) | Purple | `#32006E` |
| Representative color 2 | ![#7A55B5](https://placehold.co/20x20/7A55B5/7A55B5.svg) | Purple | `#7A55B5` |
| Representative color 3 | ![#CDBCEA](https://placehold.co/20x20/CDBCEA/CDBCEA.svg) | Purple | `#CDBCEA` |

### Plotting Code

Rates and confidence intervals use the numerical values reported in Table 2; minor rounding can differ from the figure labels.

Requires Python 3 with NumPy and Matplotlib.

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.titlesize": 11, "axes.labelsize": 10,
                     "axes.linewidth": 0.7, "savefig.facecolor": "white"})

def style(ax, axis="y"):
    ax.set_axisbelow(True)
    ax.grid(axis=axis, color="#E4E7EC", linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["bottom", "left"]].set_color("#B8BDC5")
    ax.tick_params(length=3, color="#A0A6AF")

palette = ["#CBBCE6", "#8058B0", "#31006E"]
labels = ["Prompt", "Prompt + Env Feedback", "AutoEnvScaling"]
models = ["Claude\nOpus 5", "GPT-6\nastra", "GPT-5.6\nsol", "Grok\n4.6", "Gemini-3.8\nFlash", "DeepSeek\nV4-Flash"]
rates = np.array([[74.6, 89.5, 94.0], [67.0, 83.0, 94.0], [41.1, 65.5, 86.3],
                  [45.8, 66.6, 86.0], [26.2, 59.6, 64.8], [3.5, 12.1, 89.0]])
lower = np.array([[70.0,86.0,91.2], [61.2,78.0,88.9], [36.4,60.7,82.5],
                  [40.9,61.8,79.7], [22.1,54.5,57.2], [2.1,9.2,83.9]])
upper = np.array([[78.7,92.2,95.9], [72.4,87.1,96.8], [46.0,70.1,89.3],
                  [50.6,71.0,90.6], [30.8,64.4,71.7], [5.8,15.7,92.6]])
fig, axes = plt.subplots(1, 2, figsize=(12.5, 4), gridspec_kw={"width_ratios": [1.7, 1]})
x = np.arange(len(models))
for j, (color, label) in enumerate(zip(palette, labels)):
    axes[0].bar(x+(j-1)*0.24, rates[:,j], width=0.24, color=color, edgecolor="#644778", lw=0.5,
                yerr=np.vstack([rates[:,j]-lower[:,j], upper[:,j]-rates[:,j]]), capsize=2, label=label)
    for xi, value, top in zip(x+(j-1)*0.24, rates[:,j], upper[:,j]):
        axes[0].text(xi, top+1.5, f"{value:.0f}", ha="center", fontsize=8, color="#35253D")
axes[0].set(xticks=x, xticklabels=models, title="Across model families")
family = np.array([[41.1,65.5,86.3], [40.0,53.2,92.5], [17.2,26.5,83.5]])
family_lower = np.array([[36.4,60.7,82.5], [35.3,48.2,88.0], [13.9,22.4,77.7]])
family_upper = np.array([[46.0,70.1,89.3], [44.9,58.1,95.4], [21.3,31.2,88.0]])
for j, color in enumerate(palette):
    axes[1].errorbar(range(3), family[:,j], yerr=np.vstack([family[:,j]-family_lower[:,j], family_upper[:,j]-family[:,j]]),
                     fmt="o-", color=color, lw=1.5, ms=5, capsize=2)
    for xi, yi in enumerate(family[:,j]):
        axes[1].text(xi, yi+(3 if j==2 else -7), f"{yi:.0f}", ha="center", fontsize=9)
axes[1].set(xticks=range(3), xticklabels=["GPT-5.6\nsol", "GPT-5.6\nterra", "GPT-5.6\nluna"],
            xlim=(-0.35,2.35), title="Within the GPT-5.6 family, strongest to weakest")
for ax in axes:
    ax.set(ylim=(0,112), yticks=[0,25,50,75,100], ylabel="Valid-environment rate (%)")
    style(ax)
fig.legend([Patch(facecolor=c) for c in palette], labels, loc="upper center", ncol=3, frameon=False)
fig.subplots_adjust(left=0.07, right=0.99, top=0.80, bottom=0.19, wspace=0.27)

fig.savefig("fig4_validity_reconstructed.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

## Figure 6: Recursive Self-Improvement of Solvers and Proposers

<p align="center">
  <img src="result_figures/fig6_recursive_self_improvement.png" alt="Recursive Self-Improvement of Solvers and Proposers" width="720">
</p>

| Asset | Link |
|---|---|
| Preview Image | [fig6_recursive_self_improvement.png](result_figures/fig6_recursive_self_improvement.png) |
| Source | Figure 6, PDF page 8 of the [paper](https://arxiv.org/abs/2610.14163v1) |

### Color Palette

Representative colors sampled from the original image; HEX values are approximate.

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Representative color 1 | ![#3A3145](https://placehold.co/20x20/3A3145/3A3145.svg) | Purple | `#3A3145` |
| Representative color 2 | ![#32006E](https://placehold.co/20x20/32006E/32006E.svg) | Purple | `#32006E` |
| Representative color 3 | ![#DED8EC](https://placehold.co/20x20/DED8EC/DED8EC.svg) | Purple | `#DED8EC` |
| Representative color 4 | ![#208C8D](https://placehold.co/20x20/208C8D/208C8D.svg) | Teal | `#208C8D` |
| Representative color 5 | ![#D07832](https://placehold.co/20x20/D07832/D07832.svg) | Orange | `#D07832` |
| Representative color 6 | ![#8C8FC2](https://placehold.co/20x20/8C8FC2/8C8FC2.svg) | Blue | `#8C8FC2` |

### Plotting Code

Note: The following code is an approximate visual reconstruction based on the provided figure.

Intermediate samples and the collapsed proposer curve are visually estimated; annotated endpoint values are preserved.

Requires Python 3 with NumPy and Matplotlib.

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.titlesize": 11, "axes.labelsize": 10,
                     "axes.linewidth": 0.7, "savefig.facecolor": "white"})

def style(ax, axis="y"):
    ax.set_axisbelow(True)
    ax.grid(axis=axis, color="#E4E7EC", linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["bottom", "left"]].set_color("#B8BDC5")
    ax.tick_params(length=3, color="#A0A6AF")

steps = np.array([0,30,60,95,130,165,200,235,265,300])
series = [
    ([41.1,41.8,40.7,43.9,44.4,45.0,45.4,46.8,47.0,47.2],
     [1.6,1.2,1.4,1.8,1.8,1.8,1.4,1.8,1.8,1.4]),
    ([41.1,41.8,43.3,44.1,43.5,40.0], [1.6,1.4,1.2,1.0,1.4,1.4]),
    ([41.1,41.8,42.5,44.3,45.2,48.9,50.0,50.2,51.5,53.3],
     [1.6,1.4,1.4,1.8,2.2,1.8,3.2,3.2,3.2,3.2]),
]
colors = ["#1A9399", "#D57C30", "#31006E"]
markers = ["^", "o", "s"]
labels = ["Tmax", "AutoEnvScaling\n(w/o Proposer Training)", "AutoEnvScaling"]
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for j, ax in enumerate(axes):
    for pair, color, marker, label in zip(series, colors, markers, labels):
        values = pair[j]
        ax.plot(steps[:len(values)], values, marker+"-", color=color, lw=1.7, ms=5,
                markeredgecolor="#3A3447", markeredgewidth=0.5, label=label)
    ax.plot(0, [41.1,1.6][j], marker="D", color="#31006E", mfc="white", ms=7, zorder=5)
    ax.axhline([41.1,1.6][j], color="#9E91BD", ls=":", lw=1.3)
    ax.axhline([40,1.4][j], color="#9E91BD", ls=(0,(5,5)), lw=1)
    ax.set(title=["Terminal-Bench 2.1","Terminal-Bench 4.0"][j], xlabel="RL training step",
           ylabel="Score", xlim=(-10,310), xticks=np.arange(0,301,50))
    ax.set_ylim((39.5,54.5) if j==0 else (0.8,3.45))
    ax.set_yticks(np.arange(40,55,2) if j==0 else np.arange(0.8,3.3,0.4))
    style(ax, "both")
fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", ncol=3, frameon=False)
fig.subplots_adjust(left=0.07, right=0.99, top=0.78, bottom=0.16, wspace=0.23)

fig.savefig("fig6_self_improvement_reconstructed.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

# 3. Paper Tables

## Table 1: Environment Generation Method Comparison

<p align="center">
  <img src="tables/table1_environment_generation_methods.png" alt="Environment Generation Method Comparison" width="720">
</p>

| Asset | Link |
|---|---|
| Preview Image | [table1_environment_generation_methods.png](tables/table1_environment_generation_methods.png) |
| Source | Table 1, PDF page 3 of the [paper](https://arxiv.org/abs/2610.14163v1) |

### LaTeX Source

```latex
\begin{table}[t]
\centering
\caption{Comparison of terminal-environment generation methods: proposer strategy, data sources, and optimization.}
\label{tab:autoenvscaling-methods}
\small
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.12}

\resizebox{\textwidth}{!}{%
\begin{tabular}{lllcccc}
\toprule
\rowcolor{black!5}
& & & \multicolumn{2}{c}{\textbf{Proposer Source}} & \multicolumn{2}{c}{\textbf{Proposer Optimization}} \\
\cmidrule(lr){4-5}\cmidrule(lr){6-7}
\rowcolor{black!5}
\multirow{-2}{*}{\textbf{Method}} & \multirow{-2}{*}{\textbf{Strategy}} & \multirow{-2}{*}{\textbf{Data Sources}} & \textbf{External} & \textbf{Self} & \textbf{Harness} & \textbf{Weights} \\
\midrule
Endless Term. [8] & Prompt + feedback & Human-defined & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} \\
TermiGen [67] & Prompt + feedback & Human-defined & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} \\
Terminal-World [5] & Prompt + feedback & Skill-based & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} \\
Tmax [13] & Prompt & Human-defined & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} \\
SETA [35] & Harness & Seed tasks, human-defined & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} \\
RST [20] & Prompt + feedback & Seed tasks & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} \\
Env. Evolution [7] & Prompt + feedback & Seed tasks & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} \\
Terminal-Uni [49] & Prompt + feedback & Solver rollouts & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} \\
T1 [54] & Prompt + feedback & Seed tasks & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} & \textcolor{red!80!black}{$\times$} \\
\midrule
AutoData [17] & Harness & Corpus, solver rollouts & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} \\
SPADE [23] & Prompt & Corpus, memory & \textcolor{red!80!black}{$\times$} & \textcolor{green!50!black}{$\checkmark$} & \textcolor{red!80!black}{$\times$} & \textcolor{green!50!black}{$\checkmark$} \\
\rowcolor{violet!10}
\textbf{\textsc{AutoEnvScaling} (Ours)} & Harness & Corpus, rollouts, memory, web & \textcolor{green!50!black}{$\checkmark$} & \textcolor{green!50!black}{$\checkmark$} & \textcolor{green!50!black}{$\checkmark$} & \textcolor{green!50!black}{$\checkmark$} \\
\bottomrule
\end{tabular}%
}
\end{table}
```

### Required Packages

```latex
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage[table]{xcolor}
\usepackage{multirow}
\usepackage{amssymb}
```

---

## Table 2: Environment Validity and Generation Cost

<p align="center">
  <img src="tables/table2_validity_and_cost.png" alt="Environment Validity and Generation Cost" width="720">
</p>

| Asset | Link |
|---|---|
| Preview Image | [table2_validity_and_cost.png](tables/table2_validity_and_cost.png) |
| Source | Table 2, PDF page 7 of the [paper](https://arxiv.org/abs/2610.14163v1) |

### LaTeX Source

```latex
\begin{table}[t]
\centering
\caption{Valid-environment rates with confidence intervals and cost per valid environment (USD). Cost multipliers reproduce the paper's reported annotations.}
\label{tab:autoenvscaling-validity-cost}
\small
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.12}

\resizebox{\textwidth}{!}{%
\begin{tabular}{lccc|ccc}
\toprule
& \multicolumn{3}{c}{Valid-env. rate (\%)} & \multicolumn{3}{c}{Cost per valid env. (USD)} \\
\cmidrule(lr){2-4}\cmidrule(lr){5-7}
Proposer & Prompt & \shortstack{Prompt +\\Env Feedback} & \textsc{AutoEnvScaling} & Prompt & \shortstack{Prompt +\\Env Feedback} & \textsc{AutoEnvScaling} \\
\midrule
Claude Opus 5 & 74.6 {\scriptsize [70.0, 78.7]} & 89.5 {\scriptsize [86.0, 92.2]} & \textbf{94.0} {\scriptsize [91.2, 95.9]} & 0.72 & 0.70 & 1.18$_{\textcolor{red!80!black}{1.6\times \uparrow}}$ \\
GPT-6-astra & 67.0 {\scriptsize [61.2, 72.4]} & 83.0 {\scriptsize [78.0, 87.1]} & \textbf{94.0} {\scriptsize [88.9, 96.8]} & 1.79 & 1.76 & 2.75$_{\textcolor{red!80!black}{1.5\times \uparrow}}$ \\
GPT-5.6-sol & 41.1 {\scriptsize [36.4, 46.0]} & 65.5 {\scriptsize [60.7, 70.1]} & \textbf{86.3} {\scriptsize [82.5, 89.3]} & 0.90 & 0.80 & 0.59$_{\textcolor{green!50!black}{0.7\times \downarrow}}$ \\
GPT-5.6-terra & 40.0 {\scriptsize [35.3, 44.9]} & 53.2 {\scriptsize [48.2, 58.1]} & \textbf{92.5} {\scriptsize [88.0, 95.4]} & 0.13 & 0.15 & 0.09$_{\textcolor{green!50!black}{0.7\times \downarrow}}$ \\
Gemini-3.8-Flash & 26.2 {\scriptsize [22.1, 30.8]} & 59.6 {\scriptsize [54.5, 64.4]} & \textbf{64.8} {\scriptsize [57.2, 71.7]} & 0.28 & 0.20 & 0.16$_{\textcolor{green!50!black}{0.6\times \downarrow}}$ \\
GPT-5.6-luna & 17.2 {\scriptsize [13.9, 21.3]} & 26.5 {\scriptsize [22.4, 31.2]} & \textbf{83.5} {\scriptsize [77.7, 88.0]} & 0.02 & 0.03 & 0.01$_{\textcolor{green!50!black}{0.4\times \downarrow}}$ \\
DeepSeek-V4-Flash & 3.5 {\scriptsize [2.1, 5.8]} & 12.1 {\scriptsize [9.2, 15.7]} & \textbf{89.0} {\scriptsize [83.9, 92.6]} & 0.08 & 0.06 & 0.02$_{\textcolor{green!50!black}{0.25\times \downarrow}}$ \\
Grok 4.6 & 45.8 {\scriptsize [40.9, 50.6]} & 66.6 {\scriptsize [61.8, 71.0]} & \textbf{86.0} {\scriptsize [79.7, 90.6]} & 0.59 & 0.69 & 0.44$_{\textcolor{green!50!black}{0.7\times \downarrow}}$ \\
\bottomrule
\end{tabular}%
}
\end{table}
```

### Required Packages

```latex
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage[table]{xcolor}
```

---
