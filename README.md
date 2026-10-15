<div align="center">

<h1>🖼️ ReFigure · 图续</h1>

<p><strong>收藏好图，也留下复现的方法。</strong></p>
<p>Curate the figure. Keep the recipe.</p>

<p>
  <a href="https://lyc61c.github.io/PaperFigureAssets/"><strong>🌐 浏览在线图库</strong></a>
  &nbsp; · &nbsp;
  <a href="docs/GETTING_STARTED.md">📖 使用指南</a>
  &nbsp; · &nbsp;
  <a href="paper-asset-builder/SKILL.md">🧩 收图 Skill</a>
</p>

</div>

ReFigure 是一个**由你筛选、可以定制的论文图收藏库**。提供论文名、链接或 PDF，让 skill 提取和整理图表；你决定留下哪些，再将它们变成可编辑资源与个人网页。

## ✨ 好图，不止收藏

从论文里的灵感，到下一次创作的素材：

> 📄 提供论文 → 🔎 自动提取 → 🙋 人工筛选 → 🛠️ 可编辑重建 → 🌐 更新图库

| 🧩 方法框架图 | 📊 实验结果图 | 📋 论文表格 |
|:---|:---|:---|
| 可编辑 PPTX · 配色 | 配色 · 数值图 Python 代码 | LaTeX 表格源码 |

**你负责审美和取舍，skill 负责提取、整理与重建。** 每篇论文的原图、来源和可编辑资源放在一起，收什么、怎么用，都由你决定。

## 🚀 从一篇论文开始

Fork 并 clone 本仓库，按[安装指南](docs/GETTING_STARTED.md#2-安装完整-skill)安装完整的 `paper-asset-builder`。

**1. 把论文交给 agent**

在仓库中输入：

```text
$paper-asset-builder paper="论文名、链接或本地 PDF 路径"
```

**2. 留下喜欢的图，再继续**

Skill 会提取全文图表并返回本地目录，**停下来等你筛选**。删除不需要的图片，或调整裁剪和分类，检查后回复：

```text
检查好了，继续。请使用目录里现在保留的图片。
```

随后 skill 会使用目录中**当前保留的图片**，重建图表、生成论文 README，并更新索引与本地图库。

已经有图片？也可以[直接从本地目录开始](docs/GETTING_STARTED.md#常见问题)。

## 🪴 让图库长成你的样子

在[站点配置](website/figarium.config.json)中换上自己的名称、简介和仓库链接，再按[定制与部署指南](docs/CUSTOMIZATION.md)发布到自己的 GitHub Pages。

网页负责浏览、筛选、复制与下载；skill 在本地 agent 中运行。你的图片、条目和网站都保存在自己的仓库里。

[🗂️ 论文目录](PAPER_INDEX.md) · [🤝 参与贡献](CONTRIBUTING.md) · [💻 网页源码](website/)

---

项目代码采用 [MIT 许可](LICENSE)。论文原图与第三方素材遵循各自许可；来源、重建范围与验证记录保留在对应论文条目中。
