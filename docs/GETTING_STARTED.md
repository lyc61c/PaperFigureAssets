# 从一篇论文开始，让好图延续

ReFigure · 图续不是一份固定图单，而是一套可以 Fork、定制和复现的个人论文图收藏工作流。为选中的论文图保存来源、配色和可编辑的重建资源，让它们在你的下一次创作中继续发挥作用。

你负责审美和取舍，skill 负责繁琐整理；网页负责让收藏容易浏览和使用。

```text
论文名 / 链接 / PDF
  → 全文图表清点与分类提取
  → 返回本地目录，等待人工筛选
  → 你确认后，重读目录中的当前图片
  → 方法图可编辑 PPT、重建代码、论文 README、主索引
  → 构建你的静态图库
```

## 1. 拥有一个自己的仓库

想维护自己的公开/私有图库，先在 GitHub Fork 本项目，再 clone 你的 Fork。下面的 `YOUR_NAME` 需要替换为你的 GitHub 用户名；如果 Fork 时改了仓库名，也一起替换。

```bash
git clone https://github.com/YOUR_NAME/PaperFigureAssets.git
cd PaperFigureAssets
```

只想本地体验，也可以直接 clone [原项目](https://github.com/lyc61c/PaperFigureAssets)。ReFigure 是产品名称，现有 GitHub 仓库名和 `paper-asset-builder` 调用名保持兼容，不需要为了使用它重命名本地目录。

将这个仓库根目录在 Codex 或 Claude Code 中打开。这里的根目录应同时包含 `papers/`、`README.md`、`paper-asset-builder/` 和 `website/`，不是它们的上一级。

## 2. 安装完整 skill

需要支持本地文件和终端工具的 coding agent；单独打开图库网页不能运行 skill。安装时复制整个 `paper-asset-builder/`，它还包含提取辅助脚本、方法图 PPT 子流程规范、重建规范和模板。只需安装这一个完整目录，不必另外安装第三方 PPT skill；调用名仍是 `paper-asset-builder`。

### Codex

推荐二选一，不要同名重复安装。

| 范围 | 目标目录 | 适合谁 |
|---|---|---|
| 当前仓库 | `.agents/skills/paper-asset-builder/` | 只在这个图库里使用 |
| 当前用户 | `~/.agents/skills/paper-asset-builder/` | 在多个项目里复用 |

以上路径依据 [OpenAI 官方 skills 文档](https://developers.openai.com/codex/skills)（核对于 2026-10-14）。Codex 会检测本地 skill 变化；未显示时重启。已有可用的旧版/宿主专用安装目录可原位更新，不必另外复制出第二个同名 skill。

macOS / Linux，仓库内执行：

```bash
mkdir -p .agents/skills
cp -R paper-asset-builder .agents/skills/paper-asset-builder
```

Windows PowerShell，仓库内执行：

```powershell
New-Item -ItemType Directory -Path .agents\skills -Force
Copy-Item -LiteralPath .\paper-asset-builder -Destination .\.agents\skills\paper-asset-builder -Recurse
```

个人安装则把目标换成当前用户目录下的 `.agents/skills/paper-asset-builder`；Windows 通常为 `%USERPROFILE%\.agents\skills\paper-asset-builder`，不要照抄他人的管理员用户名。更新已有安装前确认目标目录，覆盖 skill 自身文件即可，不要误删个人图库。

也可以告诉内置 `$skill-installer`：“从 `https://github.com/lyc61c/PaperFigureAssets/tree/main/paper-asset-builder` 安装这个 skill”。若你维护了 Fork 的 skill，应使用自己的 Fork 链接。安装后的根文件应是 `<目标目录>/paper-asset-builder/SKILL.md`，而不是多套一层同名文件夹。

### Claude Code

复制到仓库的 `.claude/skills/paper-asset-builder/` 或用户的 `~/.claude/skills/paper-asset-builder/`，二选一。例如：

```bash
mkdir -p .claude/skills
cp -R paper-asset-builder .claude/skills/paper-asset-builder
```

安装后使用 `/paper-asset-builder`。在 Codex 中使用 `$paper-asset-builder` 或自然语言，不把它写成 Claude 的 slash command。

### 运行环境

普通收图用自然语言即可，不需要手动调用提取脚本或 PPT 工具。agent 会检查所需环境：PDF 区域提取使用 PyMuPDF；多数实验图重建使用 NumPy/Matplotlib；方法图 PPT 使用可用的 PPTX 生成库和最终 PPTX 渲染器；本地 LaTeX 编译可选。依赖不足时，让 agent 在项目虚拟环境中安装所需包，避免盲目改动全局 Python。缺少可用的 PowerPoint/LibreOffice 等实际 PPTX 渲染器时，应报告未验证，不能用源码预览代替最终验证；系统软件安装仍需遵循你的授权。网站构建独立于这些重建工具。

## 3. 提供论文，先收齐再选

Codex 示例：

```text
$paper-asset-builder paper="WeVisDoc: From Coverage to Capability for Robust End-to-End Document Parsing"
```

或直接提供链接/PDF：

```text
请用 paper-asset-builder 整理论文 https://arxiv.org/abs/2605.10832，提取后先给我本地目录检查。
```

```text
$paper-asset-builder paper="D:\Papers\my-paper.pdf" paper_id=2026_my_paper
```

如果工作区中有多个仓库，可以指定 `repo_root="D:\MyLibrary"`。论文名会被解析为可靠来源；遇到同名论文时，agent 应让你确认，不凭空猜测 PDF 链接。

新论文默认 `selection=all`：清点并提取全文所有编号 figure/table，包括 PDF 内的 appendix/supplementary 图表。它不是“每篇挑两张”的固定精选模式，也不是只导出 PDF 嵌入的位图——矢量图和文字表格同样需要完整截图。遇到无法识别、跨页、裁剪不完整的项目，应在清单中报告覆盖缺口，不能宣称已经全部提取。

如果你明确希望 agent 先精选，可指定：

```text
$paper-asset-builder paper="论文链接" selection=curated
```

精选模式仍保留全文编号清单和跳过原因，方便后续补图。

## 4. 到本地目录做人工筛选

默认待审目录位于仓库旁边的 `materials/<paper_id>/`，agent 会返回你机器上真实、可点击的绝对路径，而不是让你猜目录。目录最多有三类图片文件夹；没有某类资产时不必创建空文件夹。

```text
materials/<paper_id>/
├── method_figures/   方法图、框架图、模块示意
├── result_figures/   实验曲线、统计图、定性结果
├── tables/           表格截图
├── paper.pdf         原始论文，仅供本地处理
└── source_assets.json  来源、页码、裁剪区域、哈希、覆盖与审核记录
```

此时 skill 必须暂停，不生成论文 README、不更新主索引，也不提前为未经确认的图片制作 PPT。你可以直接：

- 删除不想收藏的图片。
- 替换裁剪不满意的图片，或者要求 agent 重新裁剪。
- 重命名、移动到正确分类、补充自己上传的图片。
- 留下自己喜欢的配色、布局、实验图类型，不必与其他人的图库一致。

检查完回复：

```text
检查好了，继续。请使用这个目录里现在保留的图片。
```

确认后 agent 会重新扫描当前目录。已删除的图不能再次提取回来；被替换的图片不能沿用旧图片的错误页码/来源。若一张都没留下，流程应停下说明情况，而不是擅自补回原图。

## 5. 生成可复现条目

审核后的图片会进入 `papers/<paper_id>/`，对应 README 保留三类栏目和图库预览，独立的论文目录 `PAPER_INDEX.md` 同步更新。主 README 只作项目介绍，不再展开论文索引。

| 资产 | 重建输出 | 需要理解的边界 |
|---|---|---|
| 方法图 | 默认生成逐图同名可编辑 PPTX、每篇合并 PPTX，保留预览与配色；不默认额外生成图表代码 | 目标是完整视觉内容，原生文字/形状/连线与独立局部图片混合；照片等栅格素材内部仍不可编辑，不是作者原始工程 |
| 数值实验图 | 数据内嵌、可独立运行的 Python 代码 | 从图估读的曲线必须标注 approximate，不等于实验原始数据 |
| 定性结果图 / 截图 | 可复用的布局重建或明确的限制说明 | 不虚构数值或原始图像来满足代码数量；保留原图参考 |
| 表格 | LaTeX 源码及必要 packages | 编译成功不等于数值正确，还需与原图逐项核对 |

实验图与表格的代码默认保存在论文 README 中，网页可提供复制/下载。方法图默认交付下述 PPT 文件，不额外生成 Editable Diagram Code / SVG / TikZ；需要这些补充代码时请明确提出。网页每张方法图只显示对应单图 PPT 的一个下载按钮，合并版保留在论文级 README 链接中。历史 README 中已有的代码不自动删除。既有条目的完成范围以逐图状态为准，启用新流程不等于已经补完所有旧图。

### 方法图：自动继续到可编辑 PPT

图片确认后，agent 会自动调用 skill 内置的 PPT 子流程，无需你再次安装/调用另一个 skill，也无需你手动运行转换命令。未显式设置 `method_pptx=off` 时，为当前目录保留的每张方法图制作一页 PPT，并按论文组织：

```text
papers/<paper_id>/method_figures/
├── fig1_framework.png
├── fig1_framework.pptx             # 与原图同名，单图单页
├── fig2_pipeline.png
├── fig2_pipeline.pptx
└── method_figures_editable.pptx    # 本篇全部方法图合并版
```

重建目标是保留完整原图内容，而非只画一个简化流程代替：面板、文字、模块、连线、箭头、公式、示例和复杂素材都需要对应清单。可读文字重建为原生文本框，框/形状/连线重建为 PowerPoint 对象；照片、截图、复杂插画等保留为来源明确的独立局部 raster 图片，可以移动和缩放，但其内部像素不能像文字或形状那样编辑。不能把整页 PNG 或完整 SVG 作为一个图片对象，再加几个可编辑文本框，就称为原生可编辑 PPT。

交付前需要两类独立检查：实际渲染**最终 PPTX**，与批准的原图逐项视觉核对；检查 PPTX 的文字、形状、连线和图片结构，确认不是整图伪装。源码/SVG 预览、ZIP 可打开或文件已生成，均不等于最终 PPT 通过检查。必须报告每张方法图的生成、渲染、视觉核对和可编辑性状态，区分 `complete`、部分完成、未验证、失败或明确跳过；未验证不能标为 `complete`。无法完成的元素要列明，不能静默删掉或以简化示意冒充完整复现。

若这次不需要 PPT，显式指定：

```text
$paper-asset-builder paper="论文链接" method_pptx=off
```

跳过只影响 PPT 子流程，人工图片审核、其他重建和索引流程保持不变，并应在报告中注明。生成脚本、对象清单、局部素材和 QA 图片/日志保存在独立任务目录；公开条目默认仅新增 PPT、批准图片和 README，源码可放在 README 中，另行导出文件需你提出要求。重建 PPT 不会扩大原论文图像的使用许可。

### LaTeX 渲染测试与隐私

`latex_test=auto` 优先本地/内置编译器；`local` 禁止上传；`online` 可使用支持的 LaTeX-on-HTTP 服务；`off` 明确跳过测试。在线编译需要你对上传目的地和内容授权，只发送所选表格源码、必要 packages 和最小测试包装，不上传整篇论文、图片、README 或私有目录。

```text
允许将这篇论文的表格 LaTeX 源码发送到 https://latex.ytotech.com/builds/sync 做渲染测试，其他文件不要上传。
```

公共服务没有已验证的保留时长或可用性保证。未公开材料请使用本地或你指定的自托管服务。每次报告应区分“编译通过”“视觉检查通过”和“未验证”；超时不算通过。本仓库此前四篇新增论文的 7 张表格曾完成编译与视觉检查，这不代表以后的表格自动通过。

## 6. 浏览你的网页

如果仓库带有 `website/build.py`，skill 完成条目后会重建本地网站；不会擅自发布。你也可以手动重建和本地预览，在仓库根目录执行：

```bash
python website/build.py
python -m http.server 8000 --directory website/dist
```

打开 [本地预览](http://localhost:8000)。Python 服务只用于预览静态文件；不是 agent 后端，也不会在访客浏览器执行 Python、TikZ 或任意代码。

接着阅读 [定制与部署](CUSTOMIZATION.md)，换成自己的品牌、精选论文和 GitHub 链接，再决定是否发布到 GitHub Pages 或其他静态托管。

## 常见问题

**我已经有三类图片文件夹。** 提供 `material_dir` 和论文信息即可。没有待确认的自动提取审核时，可直接生成；有 pending 审核时仍需你确认。

```text
$paper-asset-builder material_dir="D:\MyMaterials\NewPaper" paper="论文链接" extract_assets=false
```

**只有一种图片，可以吗？** 可以，至少有一张支持的图片即可。缺失类别计为 0，README 对应栏目保留为空。

**我只想更新索引、不改图。** 明确说出要更新的内容；不要用重新提取来代替已有资料的维护。

**为什么我的删除在网页上没体现？** 确认 agent 重新扫描了待审目录、同步了该条目中已知的旧生成文件，并运行网站构建。检查当前站点是否仍在显示旧部署/缓存；不要直接删除整个 `papers/` 来排障。

**Fork 后原有论文的图能直接公开吗？** 不能仅凭 Fork 就假定有再分发权。原图/表格遵循原作者许可，重建代码也不自动授予第三方作品的使用权。发布前核对每篇来源和许可；许可不明时保留私有收藏、链接引用，或取得授权。
