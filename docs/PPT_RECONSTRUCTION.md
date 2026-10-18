# 可编辑 Method Figures · 交付说明

本批覆盖已有 12 篇论文的全部 **26 张 Method Figures**，不包括结果图和表格的 PPT 转换。交付 26 份逐图 PPTX、12 份论文合并版，以及一份 26 页全库合集；保留原始批准图片，不增加论文索引的图片计数。

[下载全库 26 页 PPT 合集](../downloads/Figarium_Method_Figures.pptx)。逐图文件与 PNG 同名，位于各论文的 `method_figures/`；论文合并版名为 `method_figures_editable.pptx`，亦可从图库的方法图详情下载。

## 可编辑范围

这不是作者提供的原始 PPT，也不是像素级一致的源文件恢复。每张批准图片的面板、标签、框架连接、公式和示例均做了完整内容核对。

- 模块标签是可编辑文本；框、线、箭头及图形是原生形状或自由路径。箭头不是自动吸附的绑定连接器。
- 部分公式、特殊字形和细小刻度以原生矢量轮廓保留：可以改颜色、位置和路径，但不是可直接输入的文字或实时公式对象。
- 图表是可编辑矢量几何，不是绑定原始实验数据的 PowerPoint 图表；没有由图像反推并冒充原始数据。
- 照片、截图、3D 插画、品牌标志以及必要的局部渐变/效果是独立图片对象，可以移动、缩放和替换，其内部像素不是可编辑形状。没有使用整页 PNG、整图 SVG、平铺截图或透明文字覆盖来冒充可编辑复现。
- 字体采用本机可用字体替代；部分阴影、渐变、微小图标、线宽与抗锯齿存在近似。REGNav 第一图原本已截断的右侧文字只保留可见部分，不猜补。ODE 省略两层透明度不超过 3/255 的装饰纹理，并将两层大面积阴影改为原生边框效果。

## 逐论文交付

下表统计来自 26 个逐图 PPTX 的实际 OOXML 检查。原生对象包含文本框；图片列为局部图片对象数量，不是图库图片数量，也不代表每个对象都是照片。

| 论文 | 方法图 | 原生对象 | 其中可编辑文本框 | 局部图片对象 | 论文合并版 |
|---|---:|---:|---:|---:|---|
| DDA | 2 | 244 | 67 | 5 | [PPTX](../papers/DDA/method_figures/method_figures_editable.pptx) |
| AdaptiveNN | 3 | 3680 | 537 | 68 | [PPTX](../papers/AdaptiveNN/method_figures/method_figures_editable.pptx) |
| LENS | 2 | 490 | 394 | 46 | [PPTX](../papers/LENS/method_figures/method_figures_editable.pptx) |
| MMDU | 2 | 926 | 669 | 70 | [PPTX](../papers/MMDU/method_figures/method_figures_editable.pptx) |
| Perception Encoder | 2 | 193 | 106 | 10 | [PPTX](../papers/Perception_Encoder/method_figures/method_figures_editable.pptx) |
| REGNav | 2 | 328 | 67 | 10 | [PPTX](../papers/REGNav/method_figures/method_figures_editable.pptx) |
| STAR-Rec | 2 | 740 | 99 | 41 | [PPTX](../papers/STAR-Rec/method_figures/method_figures_editable.pptx) |
| Selective Underfitting | 3 | 8425 | 77 | 38 | [PPTX](../papers/SELECTIVE_UNDERFITTING_IN_DIFFUSION_MODELS/method_figures/method_figures_editable.pptx) |
| WeVisDoc | 2 | 1151 | 384 | 73 | [PPTX](../papers/2026_arxiv_WeVisDoc/method_figures/method_figures_editable.pptx) |
| Qwen-AgentWorld | 3 | 711 | 282 | 14 | [PPTX](../papers/2026_arxiv_Qwen-AgentWorld/method_figures/method_figures_editable.pptx) |
| AutoEnvScaling | 2 | 513 | 103 | 5 | [PPTX](../papers/2026_arxiv_AutoEnvScaling/method_figures/method_figures_editable.pptx) |
| ODE | 1 | 352 | 199 | 117 | [PPTX](../papers/2026_arxiv_ODE/method_figures/method_figures_editable.pptx) |
| 合计 | 26 | 17753 | 2984 | 497 | 12 份论文合并版 |

## 验证边界

交付文件经过原生对象/文字清单检查，以及**实际最终 PPTX 重新导入 Artifact Tool 后的渲染核对**。合并版也单独渲染检查，不以源码预览或 ZIP 能打开代替视觉验收。检查项包括完整内容、公式字形、文字裁剪、透明度、图片对应关系、箭头方向与图表说明；像素差分仅作为诊断，不自动判定通过。

这不是 Microsoft PowerPoint 或 LibreOffice 的桌面应用兼容性测试。不同软件及字体环境仍可能有排版差异；建议下载后用自己的 PowerPoint 检查。完整 authoring scene、源 PDF、对照渲染和 SHA 绑定的检查记录保留在本地隔离任务目录，不默认公开。

后续新论文遵循[使用指南](GETTING_STARTED.md)：提供论文 → 全文清点与提取 → 视觉/复用价值初筛 → 返回本地目录等待人工确认 → 确认后 skill 自动复现 Method Figures、生成 README、更新索引与图库。显式指定 `method_pptx=off` 才跳过 PPT。

原图、截图、标志及重建内容仍受原作者许可约束；本项目代码的 MIT 许可不扩大第三方素材使用权。请同时阅读各论文 README 的来源和许可说明。
