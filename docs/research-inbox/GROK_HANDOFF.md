# Grok → 网站论文收件箱交接

更新时间：2026-10-19。服务器已启用每日消费任务：上海时间 08:30 首次检查、12:00 补查。上传完成不表示文章已经生成或发布；处理与预览状态见下方回执入口。

## 你的任务

你在用户的 Mac 上负责发现、初筛论文与技术资讯。将每日结果作为完整 YAML 文件，通过用户已有的 AgentBench SSH/SFTP 连接上传到服务器收件箱。无需给网站写长篇解读或英文翻译；后续阅读任务负责核对原文、挑选重点、配图和中英文写作。

服务器项目：`/home/GB-Project/yuxiaoba.github.io`

唯一清单交付目录：`/home/GB-Project/yuxiaoba.github.io/.incoming/research/`

这是服务器路径，不是 Mac 路径。`.incoming/` 已加入 `.gitignore` 和 Jekyll 排除，不通过 Git 同步，不进入网站或搜索。Mac 本地保存的清单必须另外上传；不要为传递清单运行 git add/commit/push。

用户另外指定 X 原帖全文导出目录 `.incoming/research/x_exports/`，已有按日期成对的 JSON/Markdown。完整约定见 [X_EXPORTS.md](X_EXPORTS.md)。保留原帖链接、作者、正文、时间和关联原始来源；先上传导出和附件，再交付 ready YAML。定时消费者已接通匹配材料的隔离复制与哈希记录，JSON 不替代顶层 YAML，也不直接发表。

## 文件与批次约定

- 每个阅读日交付一份 UTF-8 YAML，首次文件名为 `YYYY-MM-DD.yaml`，revision 为 1。
- 同日修订交付完整清单，不是增量补丁：`YYYY-MM-DD.r002.yaml`、`.r003.yaml`，revision 相应递增。不覆盖已交付版本。
- date 是用户的阅读批次日期，timezone 固定为 Asia/Shanghai。每条资料自己的发布日期写 published_at，不用检索时间代替首发日期。
- status: ready 表示整份清单已写完，可以交给阅读任务；不是直接的publish:true。依据用户2026-10-22的持续授权，服务器自检、生成双语并通过验证后可直接更新本机预览，无需用户逐日确认；通过验证的正常日更由外层发布器自动提交并推送官网；Grok仍只上传原始清单，不操作网站Git。
- 跨日发现重复资料时，保持同一个 id；同一天的 items 内 id 不得重复。
- 无新资料可交付 items: []，不要为了凑数量编造条目。空清单不代表撤下历史文章。

## 最少字段

批次必填：schema_version（整数 1）、date（YYYY-MM-DD 字符串）、timezone、revision（正整数）、status（ready）、items（列表）。

每条必填：id、type、title、url。type 只允许 paper、tech、social。

- id：稳定的小写英文、数字、点号和连字符，不得含路径分隔符或连续点号。arXiv 用 `arxiv-2610.00906`；不要把 v1/v2 加到身份 ID 中，版本放 URL 或 note。其他资料使用稳定短名。
  服务端兼容误填的ASCII大小写和首尾空白，规范化后检查重名并留下回执；Grok仍应按规范输出，且不可依赖服务端猜测其他非法字符。
- title：原始标题；论文标题不翻译。不知道确切标题的社交消息可以使用准确的简短主题，并在 note 说明。
- url：可直接打开的原始来源 HTTPS 链接。论文给 arXiv/DOI/出版社落地页，技术报告给官方博客，社交消息给具体帖子。不要给搜索结果页、猜测地址或仅账号主页。
- 可选 published_at：已核实的发布日期；有精确时间则使用带时区的 ISO 8601 字符串。不确定时省略，note 写明。
- 可选 authors、organization、priority（normal/high）、note、related_urls（补充项目／代码／数据集 HTTPS 链接列表）。

只有用户要求关注或有明确筛选理由时标 high；关注作者不等于通讯作者。不要求你判断 CCF、录用状态或替网站扩大标签集。

完整示例（历史格式演示，不要把它当新批次再次上传）：

```yaml
schema_version: 1
date: "2026-10-01"
timezone: Asia/Shanghai
revision: 1
status: ready
items:
  - id: arxiv-2610.00906
    type: paper
    title: "ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization"
    url: "https://arxiv.org/abs/2610.00906v1"
    published_at: "2026-10-01"
    priority: high
    note: "用户重点关注 Qingwei Lin。"
    related_urls:
      - "https://autosaddler-projectpage.github.io/activesaddler/"
```

## 上传与完成回执

1. 在 Mac 完成整份清单，使用 YAML 解析器检查格式，并检查必填字段、日期、重复 ID 与来源链接。资料中出现的命令或指令是内容，不得作为上传脚本执行。
2. 使用用户已经配置的 SSH 主机别名、用户名、端口和密钥。不要推测登录用户名，也不要把密钥或 token 放进清单。连接不可用时保留本地文件并报告，不能声称已交付。
3. 上传到同一个服务器目录下的唯一临时文件，例如 `2026-10-20.upload-<唯一编号>.part`。未传完的文件始终保留 `.part` 后缀。
4. 核对本机和服务器文件 SHA-256 一致，确认最终文件名不存在，再在服务器同一目录中改名为最终 `.yaml` 文件。只运行一个上传者；重试时，若最终文件已存在且哈希相同，视为已交付；不同则停止并使用新的 revision，不覆盖。
5. 向用户返回最终服务器路径、SHA-256、批次日期、revision，以及 paper/tech/social 各自数量。用“已上传，等待处理”，不要用“已发布”。

第一次接入可用 `status: draft` 的空清单完成连接测试，最终文件名必须为 `.part`，不要交付成 `.yaml`。测试成功后清理本次测试文件即可。

## 职责边界

- 只写 `.incoming/research/`，不改 `_digest/`、`_tech/`、assets、配置、已有 PDF 或 `/home/Obsidian`。
- 不删除旧清单、不执行 git reset/clean、不推送网站、不重启预览、不配置定时任务。
- 清单、标题和检索摘要是待核验材料。无法取得原文时报告，不凭标题补写方法、性能数字或论文图。
- Paper 后续按天合并；Tech Notes 每篇独立；网站中英文同批更新，沿用固定分类与现有样式。
- 自动消费已接通。上传后等待 08:30／12:00 的服务器任务；新日期从 2026-10-19 起，历史 10 月 1—18 日清单已批准逐日补更，使用正常日更之外的剩余额度；不必重新上传。Grok 可只读查看 `.preview/research-jobs/latest-run.json` 和各 run/report.json，不修改这些文件，也不以清单是否消失判断成功。现有文章发生冲突会转为 needs_review，处理失败不会替换上次正常预览。

## 给网站助手的消费约定

只接收最终 `.yaml` 中 schema_version=1、status=ready 的完整批次；严格检查文件名日期／revision、字段类型与条目 ID。记录输入哈希以避免重复处理。缺失文件、空批次或修订删除条目不授权撤下已发布文章；修订先作为候选，不覆盖人工改稿。收到清单只允许按已有授权生成本地预览，网站推送、正式发布与启用定时任务另行授权。

消费者和校验器已实现，详见 `DAILY_TASK.md`。每日任务仅更新服务器预览；Git 推送、正式部署仍未授权。
