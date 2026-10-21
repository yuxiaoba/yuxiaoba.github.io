# Obsidian → Paper Digest / Tech Notes

本轮实现服务器拉取、选择性导出、完整静态构建与搜索。当前仅手动运行与预览；没有启用客户端自动推送、服务器 timer、GitHub Actions 或 GitHub Pages 部署。

## 目录与最少字段

- 受保护的原笔记工作区：`/home/Obsidian`，不由脚本 pull、stash、reset 或写回。
- 自动任务专用副本：`/home/Obsidian-sync`，读取 `origin/main` 的已提交快照，拒绝脏工作区、分叉及非快进。
- `Paper/` → 按阅读日期、语言合并为 `_digest/<lang>/obsidian/daily-YYYY-MM-DD.md`；网址 `/digest/<lang>/daily/YYYY-MM-DD/`。
- `Tech Report/` → `_tech/<lang>/obsidian/<id>.md`。
- 手写合集、Kitchen、Publications 不归同步器管理。

论文已有 YAML 可直接补字段，不要添加第二个 YAML 块：

```yaml
---
title: "Original paper title"
id: stable-note-id
publish: true
created_date: 2026-10-11
paper_url: "https://example.org/paper"
lang: zh
tags: [RSI, multi-agent]
summary: "可选导读。"
---
```

技术笔记把 `paper_url` 换成 `source_url`。`lang` 默认 `zh`，英文为 `en`。`id` 用小写字母、数字、连字符，在同一栏目、语言中唯一；中英译文共享 id。改文件名、位置或标题不改变稳定链接。Paper 的稳定链接 `/digest/<lang>/obsidian/<id>/` 会跳转到当天页面的 `#paper-<id>`；修改日期会移动章节并更新跳转。

`date` 优先于 `created_date`，必须是完整有效日期。冲突会提示，不使用文件修改时间或论文年份代替。`summary` 可省略，导出器仅尝试抽取“核心直觉／一句话”的首段，不生成新内容。

仅字面布尔 `publish: true` 会公开。缺失、false 不导出；字符串 `"true"`、yes、on、数字等会报错。导出时生成 `published: true`，源笔记不用维护第二个开关。

## 按天维护 Paper Digest

继续逐篇维护 Markdown 即可，导出器按 `date`（优先）或 `created_date` 的阅读日期聚合，同一天不同语言分别成页。每一天包含当日目录、原论文标题、来源／代码链接、每篇标签和完整正文；不生成研究结论或人工翻译。章节按稳定 id 排序，内部标题带论文 id 前缀，避免相同章节名冲突。Tech Notes 保持逐篇。

只有各自 `publish: true` 的笔记进入合集。取消一篇的 publish 或删除该笔记会重建当天合集，删除它的章节、旧链接和独占图片；当天最后一篇撤下后，整天及其搜索条目删除。旧单篇导出文件会按清单迁移，手写文件不覆盖。全文搜索返回当日合集，标签取当天公开论文的并集。

从当日页切换语言按日期配对；从指定论文锚点切换时还要求该论文 id 存在，否则提示缺少译文。没有英文内容时不复制中文冒充英文。

## 日常衔接

1. 在本机编辑笔记和附件，准备公开时填写字段。
2. 本机 commit/push 到 Obsidian Git 仓库。
3. 服务器任务从独立副本快进拉取，固定一个提交快照后处理。
4. 在隔离目录导出 → Jekyll → KaTeX → Pagefind → 校验。
5. 全部通过后才更新受管理的 Markdown／资源及预览指针。

服务器无法获取尚未 push 的本机内容；Mac 休眠、断网或 Obsidian 未运行时不会自动出现新提交。当前跟踪配置中自动提交／推送间隔为 0，这不证明 Mac 此刻设置已变更。本轮没有修改客户端插件。

本机可使用 `scripts/obsidian_client_sync.py`（先复制到本机合适位置）：

```bash
python3 obsidian_client_sync.py --vault /你的/vault
# 确认范围后才提交及推送：
python3 obsidian_client_sync.py --vault /你的/vault --apply --push
```

默认仅处理 `Paper/`、`Tech Report/`；共享附件目录可用 `--asset-dir` 显式添加。已有暂存内容会阻止执行，无关文件不自动加入提交。远端分叉时保留本地提交并停止，不自动 merge/rebase/force-push。后续可按用户授权接入客户端每 5 分钟运行的机制；未在本轮配置。

## 手动命令

在网站目录执行：

```bash
# 只检查，不拉取、不改变网站输出
python3 scripts/run_obsidian_sync.py --dry-run

# 手动拉取并尝试完整事务（当前真实库会被 Guance YAML 错误阻止）
python3 scripts/run_obsidian_sync.py --pull

# 只做源转换预检
python3 scripts/obsidian_sync.py --vault /home/Obsidian-sync --dry-run

# 导出到一个尚不存在的隔离候选目录
python3 scripts/obsidian_sync.py --vault /你的/测试副本 \
  --output .preview/新的候选目录 \
  --image-reviews docs/obsidian/image-reviews.json

# 完整构建，不会自动发布或切换服务
python3 scripts/build_site.py --source .preview/新的候选目录 \
  --destination .preview/新的构建目录

# 构建当前网站并切换到通过验证的预览版本
python3 scripts/watch_site.py --once
```

同一构建锁阻止并发。`run_obsidian_sync.py` 只对专用 source checkout 工作，不接受 `/home/Obsidian` 作为自动同步目标。

## 图片、链接、公式与隐私

- 支持 Obsidian 图片 `![[figure/name.png]]`、`|宽度`、`|宽度x高度`，以及普通 Markdown 相对图片。高度不强制，保留纵横比，不裁剪图表。
- 支持本地 PNG/JPEG/WebP/GIF。先解析笔记相对路径，再解析 vault 路径；裸文件名重名报错。合法的 `../` 可以引用 vault 内附件，越界或符号链接逃逸会阻止导出。
- 图片复制为带内容哈希的路径；文章中可点击查看原尺寸。首次或变更图片需目视复核，记录在 `image-reviews.json`。无已批准哈希的图片可以生成隔离预览，但正式应用事务会停止，等待复核。记录绑定字节哈希，不把自动解码检查当成科学内容检查。
- `[[笔记|别名]]`、公开笔记的标题锚点及相对 `.md` 链接转换为站内 URL；未公开目标只保留可见文字并报告。不会连带公开其他笔记。
- 代码块、行内代码的演示语法保留；`%% ... %%` 私有注释在导出前删除，未闭合则报错。允许导出的文本元数据也处理私有注释。
- 字段采用公开白名单；NotebookLM 标识、存档路径和其他内部字段不导出。
- Liquid 定界符转为字面文本，代码示例在 Jekyll 之后恢复；不会执行笔记中的模板语句。
- 常见 `$…$`、`$$…$$`、`\(…\)`、`\[…\]` 公式经 kramdown 后由本地 KaTeX 渲染。错误公式会让候选构建失败；不是仅在页面上保留未处理的公式文本。
- PDF/Canvas/笔记嵌入、Dataview、块引用、远程图片、HTML 图片和引用式 Markdown 图片会明确报错，需要先人工转换。脚本不会自动改写正文或科学数值。

MASS 的五张修正图已逐张检查，哈希、尺寸和来源见本目录 `image-reviews.json` 及交接包的 `figure-provenance.json`。它们仅用于隔离演示，没有替换原 vault 的笔记和图片；正文也没有被宣称经过逐句事实核查。

## 全文检索

搜索覆盖已发布的 Paper Digest、Tech Notes（包括手写已发布文章），不包括主页、Publications、Kitchen、草稿、私有注释和导航。标题加权，支持正文命中片段、类型和标签筛选、清空、无结果提示、键盘操作。

Pagefind **1.5.2 Extended** 由项目锁文件固定，中文和英文分别索引。中文页可查询中文解释及英文论文名；英文页不回退到中文索引。没有公开文章的语言显示空搜索状态，不生成或使用其他栏目索引。Pagefind 总在实际构建目录运行，不固定假设 `_site`。

## 修改、撤下与失败回退

清单位于 `.sync-state/manifest.json`，记录管理文件、源笔记哈希和输出哈希；此目录不进入 Git 或网站，服务器备份应保留它。取消 publish 或已提交删除后，只清理清单中的对应文章和不再使用的图片。手写文章若复用导出图片，该图会保留，直到不再被引用。

管理文件被手工改动、源不可读／目录缺失、无效 YAML、缺失图片或构建错误，都中止本轮。不会把读取失败当成“全部删除”。源解析错误是阻止应用，不只是从列表隐藏。

候选构建位于 `.preview/jobs/`，有效版本位于 `.preview/releases/`；`.preview/current` 原子切换到通过验证的版本。更新源文件失败会恢复同步器管理的文件，已有预览指针不变。错误日志和预检报告在 `.preview/`，不进入网页。

手动回退预览（不会修改原笔记或 Git）：

```bash
python3 scripts/rollback_preview.py <已存在的版本目录名>
```

## 定时模板：未安装、未启用

`systemd/` 中提供 service/timer 模板，计划时间为每天 **03:00 Asia/Shanghai**，已通过日历语法检查。模板使用本服务器现有 Node 路径；迁移机器时需调整 PATH、运行用户及目录。

启用前必须：修复真实源的 YAML、准备要公开的笔记、提交推送并检查图片、手动运行成功，再明确授权安装／启用 timer。此处不提供会在复制 README 时自动启用的命令。

真实源当前没有可确认的 `publish: true`，并且 `Paper/Company/Guance.md` 的 company 字段包含未引用的冒号。仅生成了建议补丁 `.preview/obsidian-patches/guance-yaml-fix.patch`。建议在本机修正后提交推送，不要直接修改自动拉取副本造成脏工作区。

## 依赖、测试与部署边界

```bash
npm ci --cache .preview/npm-cache --ignore-scripts
bundle3.2 install
# Python 包版本见 requirements-sync.txt；新机器建议装入项目 .venv。
python3 scripts/prepare_obsidian_demo.py  # 已有演示时会保留并退出
python3 -m unittest discover -s tests/obsidian -v
python3 scripts/check_obsidian_pipeline.py
python3 scripts/check_obsidian_browser.py
```

管线和浏览器检查使用 `.preview/obsidian-demo-vault` 隔离样例（本次已准备），不使用原 vault 作写入测试。管线测试的 Git 推送只发生在本机临时 bare 仓库，不连接 GitHub。当前环境的 Python 依赖原已存在，版本已记录；新装的 Node 依赖与缓存均在项目内。

GitHub Pages 当前只读核实为 **legacy / master / 根目录**。这种方式不会自动执行 Pagefind 和本地数学后处理；以后正式部署需另行授权，将完整构建产物交给 Pages。服务器拉取笔记不依赖 Actions；本轮未更改发布源、未推送网站、未创建/启用发布工作流。

## 当前预览（2026-10-18 验收）

- 常规公网入口：`http://111.119.236.134:4001/zh/tech/`、`/zh/digest/`、`/zh/search/`。已接入用户要求生成的 2026-10-11 单日合集；中文论文阅读与搜索可见。英文和技术笔记没有对应内容，仍显示空状态。
- 4002 隔离预览仍监听 `127.0.0.1:4002`；同一日更内容现也已接入公网 4001。当前为 2026-10-11 的 6 篇真实笔记隔离副本：`/digest/zh/daily/2026-10-11/`；MASS 旧路径会跳到合集中的对应章节；搜索：`/zh/search/`。这一天没有 Tech Notes 或英文源笔记，两栏显示空状态。
- 在电脑执行 `ssh -N -L 4002:127.0.0.1:4002 <你的 AgentBench SSH 地址>` 后访问本机 4002。
- tmux：`homepage-preview:jekyll`（4000 静态服务）、`:public`（4001）、`:build`（网站文件变化后的完整构建，不拉取笔记）、`:obsidian-test`（4002 私有样例）。
- 日志：`.preview/build.log`、`.preview/public-preview.log`、`.preview/obsidian-private-preview.log`。
- 仅预览源码监听在运行，没有每日 Git 拉取任务；timer 模板仍未安装。

### 单日预览证据

仅 `.preview/daily-vault-2026-10-11` 的 6 篇副本设置 `publish: true`，原 `/home/Obsidian` 不写入；MASS 使用交接包修正版，其余正文来自原始笔记。通信故障笔记的副本将已有 `arxiv`／`code` 字段映射为 `paper_url`／`repo`。来源哈希见 `.preview/daily-source-report.json`。

运行 `python3 scripts/check_daily_digest_browser.py --site .preview/daily-preview-2026-10-11` 检查本次单日示例；此专用验收固定 6 篇、24 图、60 个公式，普通维护无需保持这些数量。`daily-image-review.json` 记录原截图的缺陷；所有新图继续不进入已批准图片哈希表，避免误认为可正式同步。

2026-10-18 入口修正：日更生成的 Markdown、24 张图片及稳定跳转已纳入本地网站受管理输出，常规预览重建不会恢复为空。源 vault 仍未设置 publish，后续正式同步前须在本机准备同一批源笔记；自动同步仍关闭。

## 已确认日更的人工维护（2026-10-18）

用户已确认 2026-10-11 资讯稿，网站现以 `_digest/zh/obsidian/daily-2026-10-11.md` 为正式内容源；原日更 URL 不变，首页、中文列表及搜索均已更新。六张核对后的图位于 `assets/images/digest/2026-10-11/`。

这篇已从 `.sync-state/manifest.json` 的输出所有权中移出，六个旧单篇跳转也转为人工维护。后续直接编辑此 Markdown 即可，正文和图片不会因源笔记撤下而被同步器清理。若再次导出同日期同语言内容，现有“不得覆盖未管理文件”保护会中止整批导出并提示冲突，而不会覆盖确认稿；接通自动同步前需明确处理该日期的内容归属。其他日期的正常导出规则未改变。

原审阅 URL `/review/digest-2026-10-11/` 现在跳转正式日更，支持旧审阅章节锚点映射。旧日更正文与原清单备份在 `.preview/approved-digest-2026-10-11/`；审阅底稿与确认记录保留在 `docs/digest-drafts/2026-10-11/`。不再运行旧的临时审阅构建脚本覆盖当前预览。

本次仅更新本地网站与已有 4000/4001 预览服务，没有推送、GitHub Pages 部署或定时任务启用。

## 三篇 Tech Notes 的本地启用（2026-10-19）

三篇已确认技术长文已接入 `_tech/zh/`，独立维护，不按天聚合；URL 为 `/tech/zh/aqua-production-quality/`、`/tech/zh/anyscale-coding-agent-serving/`、`/tech/zh/pai-agent-observability/`。正文与图不是原 vault 自动导出文件，不由当前同步清单管理。接通真实 Tech Report 原笔记同步前须处理与这批人工稿的重复来源。

本地索引为 4 篇中文（1 篇日更＋3 篇技术解读），并已启用类型/标签筛选。原审阅路径跳转到正式本地页面。仅本机 4000/4001 预览更新，未向 GitHub 推送或发布。

## 网站内容的双语交付要求（2026-10-19）

用户要求以后 Paper Digest 与 Tech Notes 出现或修改时，中英文同批更新，不再接受实际内容只上中文、稍后补英文。源导出器仍只读取已有且明确公开的笔记，不自动伪造译文；人工编辑流程须准备同路径 zh/en 成对内容，核对数据、图注、语言切换、各语言列表与搜索，再一次切换构建完成的预览。缺译回退机制作为保护保留，不能代表内容任务完成。

## 固定标签与日期筛选（2026-10-19）

Paper Digest / Tech Notes 共用 `_data/note_tags.yml` 的 8 个固定分类，构建器限制最多 10 类，每类必须有中英文名称。Markdown 的 tags 使用稳定 ID，例如 `tags: [agent-reliability, observability]`。现有文章原始标签保留在 original_tags 字段，正文与日期不变。

分类：智能体可靠性、编码智能体、多智能体协作、自改进与学习、可观测性与诊断、异常检测、推理服务、系统可靠性。页面显示本地化名称，搜索索引保存稳定 ID。导出器把已知历史别名归到固定分类；未识别标签会报告并略过，不扩张搜索下拉框。无需修改原 Obsidian 标签文件。

搜索页、论文阅读列表、技术笔记列表支持关键词＋类型＋标签＋年份＋月份的交集筛选。年份和月份根据已公开文章的 date 生成；月份内部值为 YYYY-MM，选定年份后只展示该年的月份，失效月份选择自动清除。清空筛选恢复该页面默认类型，并清除关键词、标签和年月。草稿日期不进入可选项，双语索引保持隔离。
