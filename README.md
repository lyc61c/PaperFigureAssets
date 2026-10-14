# Figarium · 图圃

**Curate the figure. Keep the recipe.**

一座由你策展、可以复现的论文图圃。Figarium 来自 **Figure + Herbarium**：收藏好图，也保存它们的来源、配色与可编辑的重建方式。

提供论文名、链接或 PDF，`paper-asset-builder` 会清点并分类提取全文图表，返回本地目录让你筛选；确认之后，再为留下的图片生成代码与论文条目。收藏属于你的研究兴趣和审美，而不是一份只能照单全收的图单。

[在线图库](https://lyc61c.github.io/PaperFigureAssets/) · [开始建立你的图库](docs/GETTING_STARTED.md) · [定制与发布](docs/CUSTOMIZATION.md) · [Skill 规范](paper-asset-builder/SKILL.md) · [网页源码](website/)

## 不止展示，也能带走

| 你想做什么 | Figarium 提供什么 |
|---|---|
| 挑选真正喜欢的图 | 全文提取后暂停，直接在本地删、换、增图，人工决定最终收藏 |
| 搭建自己的图形语言 | 按论文与资产类型组织；保留配色、原编号、页码和重建范围 |
| 拿去改成自己的图 | 结果图 Python、表格 LaTeX；可行的方法图提供 SVG / TikZ 可编辑重建 |
| 维护个人图库 | Fork 仓库、安装 skill、定制品牌与精选论文、构建静态网页 |

“可复现”不代表每张图都能恢复成作者的原始工程。估读数据会明确标注，照片/截图和复杂插画会说明重建限制；旧条目的源码覆盖也不完全相同。网页只提供浏览、复制和下载，不在访客浏览器执行任意代码。

## 从论文到你的收藏

```text
论文名 / 链接 / PDF
  → 全文编号图表清点与分类提取（包括附录）
  → 本地 materials/<paper_id>/，等待你筛选
  → 你确认后，重读当前目录中的图片
  → 可编辑重建 + 论文 README + 主索引
  → 构建个人静态图库
```

新论文默认 `selection=all`，不提前替你丢掉不够“漂亮”的编号图表。想让 agent 先精选，可显式指定 `selection=curated`。提取覆盖和无法完成的项目会记录下来，完整截图不等于只导出 PDF 内的嵌入位图。

## 快速开始

先 clone/Fork 本仓库，把完整的 `paper-asset-builder/` 安装到 Codex 的项目 `.agents/skills/` 或个人 `~/.agents/skills/`；已有安装可以原位更新。Claude Code 使用 `.claude/skills/`。分平台步骤见[入门指南](docs/GETTING_STARTED.md#2-安装完整-skill)，Codex 路径以 [OpenAI 官方文档](https://developers.openai.com/codex/skills)为准。

在 Codex 中：

```text
$paper-asset-builder paper="论文名、论文链接或本地 PDF 路径"
```

Skill 会返回你机器上的**实际绝对路径**并暂停。检查本地图片后回复：

```text
检查好了，继续。请使用目录里现在保留的图片。
```

最终以当前目录为准，删除的图不会被自动提取回来。也支持直接提供已有图片：

```text
$paper-asset-builder material_dir="/path/to/materials" paper="论文链接" extract_assets=false
```

Claude Code 安装后用 `/paper-asset-builder` 调用。正常收图不需要用户手动运行提取脚本。

## 本地浏览与个性化

在仓库根目录执行：

```bash
python website/build.py
python -m http.server 8000 --directory website/dist
```

打开 [localhost:8000](http://localhost:8000)。站点从论文 README 和实际图片构建，源文件仍可独立阅读；更换 `website/figarium.config.json` 即可设置自己的品牌和精选论文。完成条目后 skill 会重建可用的本地站点，但不会擅自提交、推送或发布。

网页是静态图库，不是在线 skill 服务。把它发布到自己的 GitHub Pages 或其他托管平台，见[定制与部署](docs/CUSTOMIZATION.md)。

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
| Method figures | `method_figures/` | Preview, semantic palette, supplied PPT link; SVG/TikZ reconstruction where feasible, with scope note |
| Result analysis figures | `result_figures/` | Preview, self-contained Python plotting code for numerical charts, explicit approximation/limitation notes |
| Paper tables | `tables/` | Preview, LaTeX source, required packages and render-test outcome |

## Repository Layout

```text
PaperFigureAssets/
├── papers/<paper_id>/
│   ├── README.md             # canonical metadata and reconstruction code
│   ├── method_figures/       # optional
│   ├── result_figures/       # optional
│   └── tables/               # optional
├── paper-asset-builder/      # portable skill, helpers and reconstruction references
├── website/                 # static viewer, config and builder
└── docs/                    # own-your-library setup and customization
```

待审材料默认位于仓库旁边的 `../materials/<paper_id>/`，保留 `paper.pdf` 与 `source_assets.json` 来源/覆盖记录，不作为网页公开内容。缺失资产类别计为 0，不必创建空文件夹。论文 README 的规范模板保持不变。

## LaTeX Render Tests

表格可先编译再与原图做视觉核对。`latex_test=auto` 优先本地/内置编译器；`local` 不上传；`online` 使用已支持的 [LaTeX-on-HTTP API](https://github.com/YtoTech/latex-on-http#api)；`off` 显式跳过。第三方编译必须获得 scoped authorization，只发送所选表格 LaTeX、必要 packages 和最小包装，不上传整篇论文、图片、README 或其他文件。

公共服务没有已验证的保留时长或可用性保证，私有材料请使用本地或明确指定的自托管服务。PDF 返回只证明编译成功，不证明科学数值或布局正确；超时/失败必须如实报告。此前四篇新增论文的 7 张表格已完成编译和视觉检查，其他/新表格仍需单独验证。[测试规范](paper-asset-builder/references/latex_render_testing.md)说明了授权边界、辅助脚本和检查流程。

## Copyright & Reuse

图库中的论文原图、表格与第三方素材保留原作者版权和许可，不包含在本项目 MIT 代码许可中。每篇论文的来源/许可说明应随条目保留；部分原图没有已确认的再分发许可，不能因为 PDF 可公开下载或仓库可 Fork 就假定拥有再利用权。arXiv 的非独占传播许可也不是第三方复用授权。

本地提取用于整理并不自动授权公开再分发。维护自己的公开图库前，请逐篇核对许可或取得授权；许可不明时考虑私有收藏或链接引用。重建源码明确区分作者原始源文件、复现示例和估读数据，也不会扩大对第三方作品的使用权。

想贡献条目或改进重建方式，请阅读 [Contributing](CONTRIBUTING.md)。
