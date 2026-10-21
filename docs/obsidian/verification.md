# Obsidian 同步实现与验收

整理日期：2026-10-18。实现、隔离测试和预览已完成；真实内容自动发布没有启用。

## 实现

- 服务器使用独立 `/home/Obsidian-sync` 快进拉取。原 `/home/Obsidian` 不写入、不拉取、不 stash/reset/clean。
- 严格 `publish: true`、稳定 id、中英文配对、Paper Digest / Tech Notes 分栏、日期兼容和公开元数据白名单。
- 图片、Obsidian/Markdown 链接、标题锚点、私有注释、callout、代码保护和 Liquid 字面量转换；本地 KaTeX 0.19.0 完成公式渲染。
- Pagefind 1.5.2 Extended 全文检索，支持中文分词、英文标题、语言隔离、类型和标签筛选、命中片段、无结果、清空及键盘操作。
- 导出清单只管理自己的文章／资产；手工修改冲突时停止，手写内容复用的图片不误删。撤销发布／删除后清理网页、无引用配图和索引。
- 完整候选构建通过后原子切换 `.preview/current`。Git 分叉、源错误或构建失败保留上次正常版本；网站源码监听和同步事务共用锁。
- 每日 03:00 Asia/Shanghai 的 systemd 模板、本机范围限定的 commit/push 脚本及配置说明已准备，均未自动启用。

## 验证证据

| 项目 | 结果 |
| --- | --- |
| 导出器与事务单元测试 | 27 项通过，含发布类型、日期、重复 id、断图、重名、路径越界、私有注释、标题/代码、同输入零变化、手工文件保护、共享图片和 Git 分叉 |
| 本地真实 Git 提交管线 | 7 项通过；本机 bare 仓库内提交/推送/快进拉取，完整运行 Jekyll、15 个数学表达式、2 种语言和 4 篇文章的索引 |
| 撤下和恢复 | 取消 MASS publish 后页面、5 张无引用图片和搜索片段撤下；删除另一篇也正确移除；手写草稿保留 |
| 实际构建失败 | 无效 KaTeX 命令令真实构建失败，旧页面、索引和管理文件不变；修复提交后成功恢复 |
| 新功能浏览器 | 54 组页面/宽度检查通过，MASS 5 张图、13 个正文公式、Tech 2 个公式、原图链接、中文锚点、双语配对与缺译提示正确 |
| 搜索 | MASS、recursive、工作流、RSI 均命中；技术关键词、类型/标签筛选、清空、键盘及英文隔离通过 |
| 隐私 | HTML 和搜索产物中无私有测试标记，独立草稿不生成页面；公网未包含演示样例 |
| 原网站回归 | 1274 项内容/资源/草稿检查、553 项简历一致性检查、19 项运行中预览检查通过 |
| 运行中新增入口 | 公网及本机共 12 个 Digest/Tech/Search 路由可访问；公网索引 total=0，私有演示 index=4 |
| 定时任务 | systemd 日历语法通过，timer 查询为 `not-found`，未安装/启用 |
| Git/PDF | `git diff --check` 通过；Mint 哈希保持，ChangeRCA 保持删除 |

浏览器：Chromium，宽度 320、390、768、821、1280、1440px。已查看桌面和手机截图。未测试其他浏览器、真实手机或 GitHub Pages 实际部署。未重做 MASS 全文科学事实核查；五张图目视检查仅确认图像边界、图例、坐标及子图标签，未修改数值。

本地测试提交：`21415404783aab8f9ffcbbc62d1a9460ae0fb9ec`；恢复后的提交：`d3a99ac82b7b8bf615229725b58ae8f9a51bca40`。这些提交只存在于 `.preview/` 内测试仓库，没有向 GitHub 推送。

## 真实源当前结果与剩余事项

真实 GitHub 拉取成功，专用副本仍为 `175e32c1a982b1fd19088b84ba03dd736491cddc`。扫描 140 篇，解析 139 篇，没有可确认的 `publish: true`；`Paper/Company/Guance.md` 的 company 字段包含未加引号的冒号，因此事务停止，`applied=false`。

原源库未被修复或改写。建议补丁仅保存在 `.preview/obsidian-patches/guance-yaml-fix.patch`；在本机确认并修正后提交推送，再给准备公开的笔记填写稳定 id、日期和 publish。MASS 原稿和图片未替换，修正稿只在私有演示中。

校验原目录时，Paper/Tech Report 全部 486 个文件一致，Git HEAD 和工作区文件清单一致。`Todo.md` 在会话期间出现外部内容变更；本次未写入该文件，也没有按旧哈希回滚，保留其更新后的内容。其他文件没有新增、删除或内容差异。

Pages 仍为 legacy / master 根目录，配置未改。未来正式部署需要显式授权，并使用包含数学后处理和 Pagefind 的完整产物；当前不能把直接推送给旧 Pages 构建等同于已接通搜索。

## 预览

- 常规公网：`http://111.119.236.134:4001/zh/tech/`、`/zh/digest/`、`/zh/search/`；对应英文入口不带 `/zh`。真实内容未公开，所以显示空状态。
- 私有 MASS：`http://127.0.0.1:4002/digest/zh/obsidian/mass-2026/`。
- 私有搜索：`http://127.0.0.1:4002/zh/search/`；Tech：`http://127.0.0.1:4002/zh/tech/`。

```bash
ssh -N -L 4002:127.0.0.1:4002 <你的 AgentBench SSH 地址>
```

tmux `homepage-preview` 中四个窗口：`jekyll`（4000 静态服务）、`public`（4001）、`build`（完整构建监听，仅网站源码，不拉取笔记）、`obsidian-test`（4002 私有样例）。日志位于 `.preview/`；脱离窗口用 Ctrl-b 再 d。

操作说明见 [README.md](README.md)。测试报告位于 `.preview/obsidian-*-checks.json`、`.preview/real-vault-final-run.json`。依赖在 `node_modules/`，npm 缓存在 `.preview/npm-cache/`；当前安装审计为 0 个漏洞。所有已有网站开发改动和 PDF 改动保留，未推送网站、正式部署或启用自动任务。

## 2026-10-18：按天聚合增量验收

已将 Paper 按阅读日期和语言聚合，Tech Notes 保持单篇。31 项单元/事务测试包含当天部分撤下、最后一篇删除、日期迁移、旧导出迁移、重复标题锚点及私有元数据排除；6 项本地 Git 管线检查通过。28 组真实单日浏览器检查和 54 组双语样例回归通过，原站 1274 项内容检查与 19 项预览检查通过。

真实示例为 2026-10-11 的 6 篇笔记隔离副本，24 图、60 个公式、1 个中文搜索文档。报告为 `.preview/daily-browser-checks.json`、`.preview/obsidian-browser-checks.json`、`.preview/obsidian-pipeline-checks.json`；来源哈希见 `.preview/daily-source-report.json`。图片能够显示不代表截图完整：6 张存在原始裁边或错截，详见 `daily-image-review.json`，新图片未加入批准哈希。原库 486 文件哈希与 PDF 改动保全。

预览更新为 `127.0.0.1:4002/digest/zh/daily/2026-10-11/`，tmux `homepage-preview:obsidian-test`。MASS 原路径跳转到当天章节。未公开至 4001、未 push、未部署、未开启定时任务；未重新检查全部外链和其他浏览器。
