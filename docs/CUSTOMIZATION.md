# 把 ReFigure 变成你的个人图库

ReFigure 的收藏内容与展示层分开维护：`papers/` 中的论文 README 和图片是源资料；`website/build.py` 读取它们，生成可部署的静态站点。网站不需要论文数据库或 agent 后端，也不会执行访客复制的代码。

## 改自己的名字、介绍和精选论文

编辑仓库中的 `website/figarium.config.json`（保留原配置文件名以兼容已有图库）。例如：

```json
{
  "name": "My ReFigure",
  "chineseName": "我的图库",
  "tagline": "Good figures, reproducible recipes.",
  "description": "我收藏的方法框架、实验图与表格，保留人工筛选和重建说明。",
  "repositoryUrl": "https://github.com/YOUR_NAME/YOUR_REPOSITORY",
  "featuredPaperIds": ["2026_arxiv_ODE", "LENS"]
}
```

| 字段 | 用途 |
|---|---|
| `name` / `chineseName` | 你的英文/中文品牌 |
| `tagline` | 首页一句话定位 |
| `description` | 对自己的收藏方向做简短介绍 |
| `repositoryUrl` | 指向你自己的 GitHub 仓库，供论文 README / 源码入口使用 |
| `featuredPaperIds` | 精选论文，填写 `papers/` 下的实际目录名，而不是论文全名 |

Fork 后先改 `repositoryUrl`，否则网站的源码链接仍会指向原仓库。品牌配置不会改动本地目录名、Git remote 或 skill 的调用名；`paper-asset-builder` 保持兼容。需要定制展示样式时再编辑 `website/` 下的前端源文件，不直接把生成的 `website/dist/` 当作源代码修改。

当前构建器的 GitHub 源条目链接使用 `main` 分支。若把仓库默认分支改成其他名称，也需同步调整 `website/build.py` 中的源链接分支；仅修改部署触发分支不会改变这些链接。

## 增减和更新收藏

新增论文用 [入门指南](GETTING_STARTED.md) 的 skill 流程。默认完整清点、提取后自动初筛，保留方法图、定量图表与特色表格；人工确认后才生成条目。显式 `selection=all` 可跳过初筛，已有收藏不会被自动清理。

仓库根目录的 `PAPER_INDEX.md` 是已批准论文的收录清单，网页只构建其中的条目，不自动扫描公开整个 `papers/`。主 README 保持简洁；索引更新写入独立文件的标记区域。构建器仅在独立索引不存在时兼容旧版主 README 索引，索引有误时会停止，不会退回旧清单。

修改已有论文时，让 agent 使用当前本地材料目录或已有 paper entry，明确说明要更新图片、数据还是 metadata。删除已发布条目中的图需要同步该条目已知的旧文件、README 与索引；不要通过删除整个仓库或整个 `papers/` 来重置。已有用户文件应保留。

源码在论文 README 中：方法图可记录可复现的 PPT 生成代码或辅助 SVG/TikZ，数值实验图有 Python，表格有 LaTeX。网站导出的代码下载内容从这些块生成；想改重建代码，应改 README 后重建，避免源文件和下载内容分叉。方法图默认另有逐图同名 `.pptx` 和每篇 `method_figures/method_figures_editable.pptx` 合并版，供用户在 PowerPoint 中编辑；PPT 可下载与 README 有源码是两个独立能力，不能互相冒充。

方法图的完整视觉复现与可编辑性也分别验收：可读文字、框和连线应为原生 PPT 对象，复杂照片/截图/插画可作为独立局部栅格素材，内部仍不可编辑。整页 PNG 或整页 SVG 嵌入不能冒充原生重建。默认按完整原图清单复现，不以简化示意替代缺失内容；实际最终 PPTX 渲染的视觉核对与对象结构 QA 都完成后，才可标记 `complete`。旧条目或未验证条目应显示实际状态，不把“已有文件”当作“完成验证”。

PPT 子流程已内置于 `paper-asset-builder`，在人工图片确认后由 agent 自动继续执行。只安装一个完整 skill 目录即可，无需再安装第三方 PPT skill 或手动运行转换命令。若明确不做 PPT，可在调用中设置 `method_pptx=off`，并保留跳过状态说明。

PPT 重建的源脚本、对象 inventory、局部素材与 QA 结果留在隔离任务目录，不随公开图库默认上传。公开条目默认包含批准图片、逐图/合并 PPT 和 README；可复现源码可写在 README 中，单独源文件导出按用户请求处理。发布前检查 PPT 文件自身及来源许可，不要把本地任务目录一起推送。

## 图详情与配色

方法图在同一个“PPT 与配色”栏展示单图 PPT 下载和配色；结果图分别展示重建源码、配色和来源；表格只展示源码和来源，不显示配色。

配色与源码一样，以对应论文 README 为源资料。在具体图表的小节里添加 `### Color Palette`，采用 `Role | Swatch | Color | Hex` 四列表，Hex 写成六位色值（例如 `#237ABC`）。方法图可以记录已人工核对的语义角色；自动采样的结果图只标代表色，不猜测其对应模型或曲线。

维护者可用可选取色工具从一张明确指定的本地原图中提取代表色：

```bash
# 仅取色工具需要 Pillow；常规静态构建仍只需要 Python 标准库。
python -m pip install Pillow
python website/extract_palettes.py papers/YourPaper/result_figures/fig1.png --format markdown
```

工具只读取指定图片并向终端输出，不改图像或 README。检查输出后，将配色段放入对应图表的小节，再运行构建。自动取色段保留 `Representative colors sampled from the original image; HEX values are approximate.` 说明；网页据此标为原图采样，点击色值即可复制。采样会尽量避开白底、坐标轴文字和浅网格；照片中的代表色并不等于曲线配色，采样色值也不是作者提供的官方色板。替换原图后应重新取色。

## 本地构建与预览

需要 Python。进入仓库根目录：

```bash
python website/build.py
python -m http.server 8000 --directory website/dist
```

打开 [http://localhost:8000](http://localhost:8000)。停止预览服务可在终端按 `Ctrl+C`。浏览器通过本地 HTTP 读取站点数据，优先使用这种方式而不是直接双击 HTML。

需要指定仓库或输出目录时：

```bash
python website/build.py --repo-root /path/to/my-library --out /path/to/my-static-site
```

不要把输出目录指向源码目录、个人主目录或已有重要文件夹；使用专门的静态导出目录。Python 构建命令是网站维护步骤，不是调用收图 skill 的要求。skill 在确认图片并完成条目后会运行已有 builder；构建本身不会发布到网络。

构建器通过带相对路径与 SHA-256 的生成物清单管理旧图片和指南。后续移除图表时，仅清理前次已登记且内容未变的旧副本；如果旧副本被手工修改，会保留并停止构建，等你处理。第一次没有清单时不会猜测删除，未知输出文件也不会自动移除。发布前检查导出目录；建议使用新的空输出目录或 GitHub Actions 的干净构建，避免把手工放入 `dist/` 的无关文件一同上传。

## 部署到自己的 GitHub Pages

部署前先核对你有权公开的图片/表格。Fork 并不自动授予原论文图的再分发许可，原图通常不属于本项目 MIT 代码许可证。

1. 使用你自己的 Fork，修改 `repositoryUrl`，本地构建并检查结果。
2. 在仓库 **Settings → Pages → Build and deployment** 中，把 Source 设为 **GitHub Actions**。
3. 本仓库已提供 [Pages workflow](../.github/workflows/pages.yml)，不要再创建重复任务；按自己的分支名称调整其中的 `main`。它会运行构建器测试，从批准的论文索引生成静态图库，然后部署到 Pages。
4. 提交/推送源码后检查 Actions 日志和 Pages deployment URL。启用 Pages、提交或推送均是你明确选择的发布动作；本地预览成功不等于已经上线。

工作流使用 GitHub 官方 actions，仅部署 job 拥有 Pages 写入和 OIDC 权限。推送 `main` 上的论文、`PAPER_INDEX.md`、主 README、网站源码或指南更新会自动触发；也可以在 **Actions → Publish ReFigure → Run workflow** 手动部署。`website/dist/` 是干净构建产物，不提交到源码分支；`website/.openai/` 的本机私有预览绑定也不提交。

权限和部署环境的说明见 [GitHub Pages 自定义 workflow 文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)，Python 配置见 [setup-python 文档](https://github.com/actions/setup-python)。

构建产物使用相对资源路径，适合项目子路径部署。发布后检查首页、搜索/筛选、原图、代码复制/下载、论文 README 链接和手机布局。若你的 hosting 配置另有 base path、CSP 或自定义域名限制，以部署环境为准，实际打开验证后再宣布发布成功。

## 其他静态托管

把 `website/dist/` 作为站点根目录上传到你选择的静态托管服务即可；构建命令为 `python website/build.py`。不要把上一级工作区、待审 `materials/`、整篇 PDF 或临时 QA 文件一同上传。

如果使用带项目身份的托管工具，Fork 后应创建/连接自己的 hosting 项目。不要复制原维护者的 `.openai/hosting.json`、deployment ID 或其他身份配置当作自己的部署凭据。本项目不需要你把模型 API Key 放到网页里。

## 可复现，不是无边界执行

- 下载的 Python / LaTeX / SVG 都是供读者查看、修改后在自己的受控环境运行的文本，不在网页内执行任意代码。
- 从图片估读的数据需要保留近似说明，不应在引用时冒充作者原始实验记录。
- 方法图 PPT 必须区分原生文字/形状/连线与局部栅格素材，记录完整视觉内容和最终渲染/结构 QA；辅助 SVG/TikZ 或整图嵌入不等于原生 PPT。重建不是作者源文件，未验证不能标完成。
- 在线 LaTeX 测试仅在得到针对服务和内容的授权后上传最小源码；私有论文优先本地/自托管。
- 发布前查看实际 `website/dist/` 文件清单，确保没有 PDF、绝对私有路径、token、临时日志或未授权第三方素材。

这样你获得的是一个真正属于自己的图库：原始图片用于参照，重建方式可以编辑，收藏选择可以追溯，网站也可以独立迁移。
