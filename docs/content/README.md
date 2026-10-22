# 个人主页内容更新格式

这套模板用于本仓库的双语个人主页。内容保存在 GitHub 的 Markdown 文件中，不需要数据库。网站已接入内容读取、语言切换和构建时列表更新；本次没有部署或修改远端发布配置。

## 每次更新怎么做

1. 复制对应模板到网站仓库的内容目录，按下面的规则命名。
2. 修改文件顶部两条 `---` 之间的信息，在下面写正文。
3. 检查标题、日期、正文和链接，将 `published: false` 改成 `published: true`。
4. 提交到 GitHub。网站下一次构建时会据此更新列表与文章；推送与部署需按你的发布流程执行。

不要把整个模板包直接放到线上：只复制需要发布的内容文件，模板说明保留作参考。

## 文件放在哪里

以下是重构后的目录约定；`_publications/年份/` 沿用现有仓库的组织方式。

```text
_digest/
  zh/2026-10-10.md             # 中文论文集
  en/2026-10-10.md             # 同一期的英文版
_kitchen/
  zh/2026-10-10-weekend.md      # 中文生活记录
  en/2026-10-10-weekend.md      # 同一篇的英文版
_publications/
  2026/paper-short-name.md     # 一篇论文只录入一次，中英文共用
assets/images/
  digest/2026-10-10/           # 本期论文集配图
  kitchen/2026-10-10-weekend/   # 本篇生活照片
files/
  papers/                     # 论文、幻灯片、BibTeX 等文件
```

文件名使用英文小写、数字和连字符。每日一期直接用日期；同一天有多期时加短名称，例如 `2026-10-10-agentops.md`。

## 每日论文集

复制 [中文模板](templates/digest.zh.md) 或 [英文模板](templates/digest.en.md)。一份文件就是一期，里面可以有多篇论文。

| 字段 | 是否必填 | 怎么填写 |
| --- | --- | --- |
| `title` | 必填 | 本期标题，使用当前文章的语言 |
| `date` | 必填 | 发布日期，格式为 `YYYY-MM-DD`，与文件名中的日期一致 |
| `published` | 必填 | `false` 表示草稿，准备好后改为 `true` |
| `summary` | 可选 | 列表中显示的一句话导读；没有就留空或删除这一行 |

正文用普通 Markdown：一段导读，然后每篇论文一个二级标题。每篇可以放作者、会议、原文链接、你的解读与图片；没有固定篇数，也不要求每篇都填同一组小标题。论文标题、作者和会议名称保留原文。

文章大标题由 `title` 生成，正文从段落或 `##` 开始，无需再写一个 `#` 标题。期号、月份归档和“最新一期”不手填，由网站按日期生成。首页的论文集入口随最新已发布内容更新，不把每期论文集自动变成学术 News。

## 论文成果

复制 [论文模板](templates/publication.md)。一篇论文一个文件，论文信息只维护一次，无须再复制一份英文版。

| 字段 | 是否必填 | 怎么填写 |
| --- | --- | --- |
| `title` | 必填 | 论文完整原始标题 |
| `authors` | 必填 | 按论文顺序逐行填写作者原名，无需手写加粗或 HTML |
| `venue` | 必填 | 原始会议或期刊名称，例如 `FSE`；预印本可写 `arXiv` |
| `year` | 必填 | 发表年份，与所在年份目录一致 |
| `domains` | 必填 | 研究领域，可选一个或两个，见下表 |
| `topics` | 可选 | 对应的研究方向；没有合适方向时保留 `[]` |
| `published` | 必填 | 是否在网站展示，与论文是否正式发表是两个概念 |
| `links` | 可选 | `pdf`、`slides`、`code`、`bib` 四类链接 |

`links` 中有地址才显示按钮。没有地址时保留 `""`，或删除对应行；不要填 `#`、`N/A`、`待补充`。既可以填完整的 `https://` 地址，也可以填仓库文件的站内路径，例如 `/files/papers/paper-short-name.pdf`。`bib` 指向 `.bib` 或包含 BibTeX 的 `.txt` 文件。

论文记录通常不需要正文。排版、作者强调、年份分组和中英文按钮文字由网站统一处理。

| 字段值 | 中文展示 | 英文展示 |
| --- | --- | --- |
| `domains: [cloud]` | 云系统可靠性与优化 | Cloud Systems Reliability & Optimization |
| `domains: [ai]` | 人工智能系统可靠性与优化 | AI Systems Reliability & Optimization |
| `topics: [aiops]` | 智能运维 | AIOps |
| `topics: [llm4ops]` | 大模型赋能运维 | LLM4Ops |
| `topics: [ops4llm]` | 大模型运维 | Ops4LLM |
| `topics: [agentops]` | 智能体运维 | AgentOps |

跨领域论文可以写 `domains: [cloud, ai]`。多个方向例如 `topics: [llm4ops, agentops]`。只有上层领域适用时，可以不填具体方向。

## 生活记录

复制 [中文模板](templates/kitchen.zh.md) 或 [英文模板](templates/kitchen.en.md)。顶部字段与论文集相同，下面自由写文字、放照片。

可以写一道菜，也可以写一餐饭的故事；材料表、做法步骤都不是必填。图片用 Markdown 插入，说明文字使用该文章的语言：

```markdown
![周末做好的晚餐](/assets/images/kitchen/2026-10-10-weekend/dinner.jpg)
```

先上传真实图片，再填对应路径。不要保留不存在的示例图片地址。中英文可以共用同一张图片。

## 中英文怎么对应

- `zh/` 目录存中文文章，`en/` 目录存英文文章，不需要每篇再填写语言字段。
- 两个目录中**文件名相同**，就表示同一篇文章的两个语言版本；日期也保持一致。
- 中文界面只列出已发布的中文文章，英文界面只列出已发布的英文文章。标题、摘要、正文分别维护，论文标题、作者、会议等专有信息保持原文。
- 可以先发布一种语言，另一种稍后补齐。未发布的译文不会出现在该语言的列表中。
- 阅读文章时切换语言，有已发布的对应译文就跳转到译文；没有则返回目标语言的栏目列表，并用目标语言提示暂无译文，不自动混入另一种语言正文。
- 修改文件名时，两种语言一起改；只改文章标题不影响配对。

## 填写时记住三件事

- 字段名保留英文，修改冒号后面的值。正文随意写，不要改两条 `---`。
- 标题等短文本放在双引号内；需要英文双引号时写成 `\"`。多行摘要可改用 `summary: >-`，后续每行缩进两个空格。使用空格缩进，不用 Tab。
- `published: false` 仅表示网站草稿；公开 GitHub 仓库中的源文件仍然可见。

这些文件采用 [Jekyll Front Matter](https://jekyllrb.com/docs/front-matter/) 的标准格式。本仓库已在网站中注册 [Collections](https://jekyllrb.com/docs/collections/)，首页、归档、文章链接和双语切换均过滤草稿。请使用正常构建，不要为发布添加 `--unpublished`。


## 本仓库的兼容规则

- 英文首页为 `/`，中文首页为 `/zh/`；论文旧入口 `/publications.html` 保留。
- 文章语言由 `_config.yml` 对目录的 defaults 推导，不在每篇文章中重复填 `lang`。文件放在正确的 `zh/` 或 `en/` 目录中。
- 历史论文字段继续读取：`date`、`pub`、`pub_pre`、`pub_post`、`pub_last` 和原资源键；缺少 `published` 的历史论文仍显示。新论文使用模板的 `year` 与 `venue`。
- 原始论文标题、作者、来源保留原文；不要为界面翻译修改它们。
- 本站绝对资源地址会转为本地链接，确保预览使用本地 PDF。不存在的本地资源不显示下载入口。ChangeRCA 已删除的 PDF 不恢复，DOI 等其他资源仍显示。
- 英文 News 继续维护 `_news/*.md`，可在同一记录添加 `title_zh`。`_data/news_zh.yml` 保存确认稿中已有的两条译文；中文缺译项不混入英文，英文历史记录不删除。
- 英文个人资料维护 `_data/profile.yml`，已确认中文简介、教育和获奖维护 `_data/profile_zh.yml`，界面文字维护 `_data/locales.yml`。
- 生活列表会使用正文第一张标准 Markdown 图片；没有图片时显示文字条目。图片链接采用 `/assets/images/...`，不必额外填写封面字段。

## 预览与检查

```bash
bundle3.2 install
bundle3.2 exec jekyll build --strict_front_matter
bundle3.2 exec jekyll serve --host 127.0.0.1 --port 4000
```

依赖安装在 `vendor/bundle`，不进入网站或 Git。修改 `_config.yml` 后需重启自己的预览进程。`.handoff/`、`docs/`、`scripts/`、`.preview/` 均被排除出网站输出。

构建输出为 `.preview/site/`，避免覆盖仓库历史上已跟踪的 `_site/` 文件。浏览器检查依赖 Python 的 `playwright`、`beautifulsoup4`、`PyYAML`；运行 `python3 scripts/verify_site.py` 后再运行 `python3 scripts/check_browser.py`，测试记录和截图保存在 `.preview/`。

浏览器首次安装（缓存保存在项目内）：

```bash
PLAYWRIGHT_BROWSERS_PATH="$PWD/.preview/browsers" python3 -m playwright install chromium
```

持续预览：`python3 scripts/start_preview.py`。它创建独立的 tmux 会话及 `jekyll` 窗口，从 4000 开始选空闲端口，不停止已有服务；会话名和端口记录在 `.preview/preview.json`，日志在 `.preview/jekyll.log`。在服务器上用 `tmux attach -t 会话名` 查看，按 `Ctrl-b` 再按 `d` 脱离而保持运行。若已在 tmux 内，可用 `tmux switch-client -t 会话名`。

## 阅读笔记的署名

Paper Digest 和 Tech Notes 的文章标题下只显示日期，不自动署站主姓名。两个栏目的说明统一注明内容由 AI 辅助整理；正文仍保留原论文／技术文章的真实作者与来源链接。内部作者及翻译来源字段照常保留，不用于冒充原文作者。

## 论文页年份、作者与话题

- 年份导航在桌面右侧随滚动停留；平板和手机使用顶部换行导航。年份由已展示论文自动生成。
- 通讯作者在源记录中可继续使用 `†`、`#`，也可使用 `✉️`，页面仅对 Guangba Yu 本人显示 `✉️`，其他作者的通讯标记隐藏；`*` 的共同第一作者标记保留，姓名和作者顺序不改变。
- 新论文继续通过 `domains` / `topics` 字段展示研究领域及话题；已填写 `topics` 时优先采用该记录。
- 确认稿中四篇历史论文的具体话题及中英译文保存在 `_data/publication_topics.yml`，按论文路径匹配。没有依据的历史话题不自动猜填。

## 从简历同步后的论文元数据

- `venue` 保存简历里的会议／期刊简称，左栏统一显示 `venue` 与 `year`；`ccf` 为可选等级 `A` / `B` / `C`，只填有来源的值，单独一行展示。没有等级时留空或省略。
- `preprint: true` 在数据中记录预印本状态，不计作正式论文；页面只保留 `arXiv` 来源，不额外显示 Preprint 标签。`award` 可填写已确认的 `distinguished_paper` 或 `esi_highly_cited`，两种语言统一渲染。
- 旧论文路径保留以避免破坏引用；其目录年份和 `date` 可能是早期记录日期，页面发表年份优先读取最新 `year`。
- 本次来源和逐条变更记录在 `docs/resume-sync-data.json`。没有新增论文录用 News，因为简历没有提供精确录用日期。
- 学术服务条目可设 `hidden: true` 暂时隐藏；Sub-reviewer 已按用户要求隐藏。

- `pub` 保存作者下方展示的完整发表来源，新旧论文都使用这一行；`venue` 仍用于左侧简称，`year` 用于年份，不要只填简称而遗漏完整来源。


## Life / 生活栏目

栏目已更名为 Life / 生活，入口为 `/life/` 与 `/zh/life/`。原 `/kitchen/` 与 `/zh/kitchen/` 自动跳转，已有文章 URL 不变。为保留兼容性，内容仍放在 `_kitchen/zh/`、`_kitchen/en/`，并沿用 kitchen 模板文件名与图片目录；无需迁移旧文件。内容可包含旅行、照片、饮食与日常记录，只发布真实素材；没有内容时保留空状态。
