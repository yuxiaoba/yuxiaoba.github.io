# 2026-10-01 阅读批次

来源为用户提供的十篇论文、两篇技术报告和一则 X 消息。论文统一核对 arXiv v1；博客与项目说明核对时间为 2026-10-19。`provenance.json` 记录链接、图片出处、PDF 哈希及既有内容基线。

- 一期 Paper Digest，日期为 2026-10-01：ActiveSaddler 与 Leto 重点阅读，另八篇研究动态；Qingwei Lin 作为用户关注作者标记，不标为通讯作者。
- 两篇独立 Tech Notes：TLX Jagged Flash Attention、KV Cache / LMCache，启用既有长文阅读模式。
- 中英文同批准备，共六份 Markdown。`zh/`、`en/` 是写作底稿；其中 `{{FIG:...}}` 仅为内部插图标记，正式 Markdown 已替换为完整图链。
- 十篇论文中九篇放原文方法／流程图；Compound AI 没有合适的原图，不虚构架构。技术长文使用五张官方图；图片共享，alt、图注与正文分别翻译。
- X 消息给定时间是上海时间 10 月 2 日 01:05，作为次日补充收入 10 月 1 日批次；未独立核验分钟。数据规模与 metadata-only 性质依据 Azure 官方仓库，不用社交转述代替数据说明。
- 结果全部归于作者的实验／模拟。LMCache 的 24 层配置与传输延迟是显式假设算例，不是产品测量。没有执行论文系统或 GPU 基准。

## 内容维护

正式文件为 `_digest/{zh,en}/obsidian/daily-2026-10-01.md` 和 `_tech/{zh,en}/{tlx-jagged-attention,lmcache-kv-cache-intro}.md`，属于人工维护，不加入 Obsidian 导出清单。原 `/home/Obsidian` 未改动；未来导出同 ID 应保持现有冲突保护，不覆盖本批稿件。

后续修改同时更新中英文，继续使用固定八类标签。正文保持日期、原始论文题名、来源入口与适用条件；图号、页码等核对细节放在此目录，不作为密集前台标注。

本轮仅更新 AgentBench 上的已有 tmux 预览服务，未推送网站或启用自动发布。Life 临时布局示例继续保留在预览 release 中。

## 验证

`.preview/digest-2026-10-01/` 保存构建日志、浏览器脚本、截图和检查报告。完整站点验证包含临时发布、草稿排除、缺译回退；正文 hash 对照保证旧文章未被重写。

验收还发现 Pagefind 构建词典与浏览器 Intl.Segmenter 对“残差”的切分不一致。`assets/js/search.js` 增加仅针对无结果中文查询的字面正文回退，数据仍来自同语言、同筛选条件下的公开 Pagefind 文档；不读 vault、不生成私有索引，也不改变标签数量。
