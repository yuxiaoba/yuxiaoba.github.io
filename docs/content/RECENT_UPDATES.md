# 首页最近更新

首页在个人介绍卡片之后、完整个人经历之前显示“最近更新 / Recent updates”：最新一期 Paper Digest 和最近两篇 Tech Notes。学术 News 紧接最近更新，位于完整个人经历之前。Life 从首页正文移除，只保留顶部导航入口与独立栏目页；旧的底部论文入口已移到这里，避免同一篇日报在首页重复出现。

入口由 `_includes/homepage-updates.html` 和 `recent-note.html` 渲染，无须维护首页文章列表。

- 只读取当前语言中 `published: true` 的 `_digest`、`_tech` 内容。
- 按 Markdown 的 `date` 倒序选择；不以文件修改时间、构建时间或任务运行时间替代阅读日期。
- 展示日期、标题、已有 `summary`。日报有 `daily_digest` 和 `paper_count` 时额外显示论文数量。
- 为避免日期重复，首页只移除与 date 精确匹配的标准标题前缀（中文 `YYYY年M月D日｜`、英文 `YYYY-MM-DD | `）。原 Markdown 和文章页标题不改；不符合格式的标题完整显示。
- 不展示运行状态、失败日志、RSS 或未生成的每周总结。只有一种语言时，另一个语言首页继续显示自身已有文章或真实空状态。
- 桌面两栏，700px 以下依次显示日报和技术笔记；原图、论文正文与资料内容不受影响。

每日任务通过校验后写入完整双语 Markdown，后续完整构建会自动更新首页。不能把 Grok 原始收件文件直接当作最近更新。

验证：`python3 scripts/verify_site.py` 覆盖日期排序、数量上限、草稿与缺译隔离、日期标题展示及临时新内容自动进入首页。浏览器截图与响应式检查在 `.preview/home-updates/`。
