<div align="center">

<h1>ReFigure · 图续</h1>

<p><strong>收藏好图，也留下复现的方法。</strong></p>
<p>Curate the figure. Keep the recipe.</p>

<p>
  <a href="https://lyc61c.github.io/PaperFigureAssets/"><strong>浏览在线图库 ↗</strong></a>
  &nbsp; · &nbsp;
  <a href="docs/GETTING_STARTED.md">使用指南</a>
  &nbsp; · &nbsp;
  <a href="paper-asset-builder/SKILL.md">Paper Asset Builder</a>
</p>

</div>

ReFigure 是一个**由你筛选、可以定制的论文图收藏库**。提供论文名、链接或 PDF，让 skill 提取和整理图表；你决定留下哪些，再将它们变成可编辑资源与个人网页。

## 从论文，到你的创作

**提供论文 → 自动提取 → 人工筛选 → 可编辑重建 → 更新图库**

| 方法框架图 | 实验结果图 | 论文表格 |
|:---|:---|:---|
| 可编辑 PPTX · 配色 | 配色 · 数值图 Python 代码 | LaTeX 表格源码 |

每篇论文独立整理，原图、来源与重建资源放在一起。收什么、怎么用、如何展示，都由你决定。

## 开始收藏

Fork 并 clone 本仓库，按[使用指南](docs/GETTING_STARTED.md#2-安装完整-skill)安装完整的 `paper-asset-builder`，然后在仓库中告诉 agent：

```text
$paper-asset-builder paper="论文名、链接或本地 PDF 路径"
```

Skill 会提取全文图表并返回本地目录，**停下来等你筛选**。检查后回复：

```text
检查好了，继续。请使用目录里现在保留的图片。
```

随后自动重建保留的图表、生成论文 README，并更新索引与本地网页。也支持直接使用已有图片目录，详见[使用指南](docs/GETTING_STARTED.md#常见问题)。

## 建立自己的图库

在[站点配置](website/figarium.config.json)中设置名称、简介和仓库链接，按[定制与部署指南](docs/CUSTOMIZATION.md)发布到自己的 GitHub Pages。

网页负责浏览、筛选、复制与下载；skill 在本地 agent 中运行。你的图片、条目和网站都保存在自己的仓库里。

[论文目录](PAPER_INDEX.md) · [贡献指南](CONTRIBUTING.md) · [网页源码](website/)

---

项目代码采用 [MIT 许可](LICENSE)。论文原图与第三方素材遵循各自许可；来源、重建范围与验证记录保留在对应论文条目中。
