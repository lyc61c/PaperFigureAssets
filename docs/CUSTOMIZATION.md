# 把 Figarium 变成你的个人图库

Figarium 的收藏内容与展示层分开维护：`papers/` 中的论文 README 和图片是源资料；`website/build.py` 读取它们，生成可部署的静态站点。网站不需要论文数据库或 agent 后端，也不会执行访客复制的代码。

## 改自己的名字、介绍和精选论文

编辑仓库中的 `website/figarium.config.json`。例如：

```json
{
  "name": "My Figure Garden",
  "chineseName": "我的图圃",
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

新增论文用 [入门指南](GETTING_STARTED.md) 的 skill 流程。默认全文提取，人工筛选后才生成条目。你决定收藏哪些图；这个选择比网站的配色更重要。

修改已有论文时，让 agent 使用当前本地材料目录或已有 paper entry，明确说明要更新图片、数据还是 metadata。删除已发布条目中的图需要同步该条目已知的旧文件、README 与索引；不要通过删除整个仓库或整个 `papers/` 来重置。已有用户文件应保留。

源码在论文 README 中：方法图可行时有 SVG/TikZ，数值实验图有 Python，表格有 LaTeX。网站导出的下载文件从这些块生成；想改重建代码，应改 README 后重建，避免源文件和下载内容分叉。旧方法图可能只有配色/PPT，网页应如实显示“暂无可编辑重建”，不伪装已有代码。

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

工作流使用 GitHub 官方 actions，仅部署 job 拥有 Pages 写入和 OIDC 权限。推送 `main` 上的论文、主 README、网站源码或指南更新会自动触发；也可以在 **Actions → Publish Figarium → Run workflow** 手动部署。`website/dist/` 是干净构建产物，不提交到源码分支；`website/.openai/` 的本机私有预览绑定也不提交。

权限和部署环境的说明见 [GitHub Pages 自定义 workflow 文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)，Python 配置见 [setup-python 文档](https://github.com/actions/setup-python)。

构建产物使用相对资源路径，适合项目子路径部署。发布后检查首页、搜索/筛选、原图、代码复制/下载、论文 README 链接和手机布局。若你的 hosting 配置另有 base path、CSP 或自定义域名限制，以部署环境为准，实际打开验证后再宣布发布成功。

## 其他静态托管

把 `website/dist/` 作为站点根目录上传到你选择的静态托管服务即可；构建命令为 `python website/build.py`。不要把上一级工作区、待审 `materials/`、整篇 PDF 或临时 QA 文件一同上传。

如果使用带项目身份的托管工具，Fork 后应创建/连接自己的 hosting 项目。不要复制原维护者的 `.openai/hosting.json`、deployment ID 或其他身份配置当作自己的部署凭据。本项目不需要你把模型 API Key 放到网页里。

## 可复现，不是无边界执行

- 下载的 Python / LaTeX / SVG 都是供读者查看、修改后在自己的受控环境运行的文本，不在网页内执行任意代码。
- 从图片估读的数据需要保留近似说明，不应在引用时冒充作者原始实验记录。
- SVG/TikZ 重建应说明结构、插画或照片的保真边界，不能把重建称为作者源文件。
- 在线 LaTeX 测试仅在得到针对服务和内容的授权后上传最小源码；私有论文优先本地/自托管。
- 发布前查看实际 `website/dist/` 文件清单，确保没有 PDF、绝对私有路径、token、临时日志或未授权第三方素材。

这样你获得的是一座真正属于自己的图圃：原始图片用于参照，重建方式可以编辑，收藏选择可以追溯，网站也可以独立迁移。
