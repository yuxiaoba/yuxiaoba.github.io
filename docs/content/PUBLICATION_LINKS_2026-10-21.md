# Publications 链接核验（2026-10-21）

本轮检查59篇记录，为22篇添加35个链接，其中15个为正式DOI。原有题目、作者、日期、会议／期刊、摘要和正文不改。新链接在同一份共享Markdown维护，中英文同步渲染。

## 处理原则

- 优先出版社登记的正式DOI，ACM及IEEE在页面分别标为 ACM DOI / IEEE DOI，链接仍使用稳定的 doi.org 入口跳转官方站点。
- 用完整题目及作者匹配Crossref元数据；作者主页、论文正文确认PDF与代码归属。
- 保留既有作者PDF、arXiv及项目链接；不复制站外PDF进入仓库。Mint文件和ChangeRCA删除状态保持。
- DOI可定位正式出版物，不表示论文一定开放获取。新增35条HTTP检查26条返回成功，9条ACM返回403；后者已用ACM登记的Crossref题目／作者／官方URL核实，不当作死链删除。

## 更新记录

| 记录 | 新增资源 | 核验来源 |
| --- | --- | --- |
| _publications/2026/tse-ccisolver.md | DOI, pdf | https://api.crossref.org/works/10.1109/tse.2026.3689089 ; https://arxiv.org/abs/2506.20558 |
| _publications/2026/tosem-logging-generation.md | DOI, pdf | https://api.crossref.org/works/10.1145/3773287 ; https://arxiv.org/abs/2505.16590 |
| _publications/2026/kdd-star.md | DOI, code | https://api.crossref.org/works/10.1145/3770855.3817863 ; https://huanghy95.github.io/ |
| _publications/2026/ase-opslens.md | DOI | https://api.crossref.org/works/10.1145/3832783.3834501 |
| _publications/2025/ASE-Alert.md | DOI, Arxiv | https://api.crossref.org/works/10.1109/ase63991.2025.00009 ; https://arxiv.org/abs/2601.14912 |
| _publications/2025/IWQoS-CauseLens.md | DOI | https://api.crossref.org/works/10.1109/iwqos65803.2025.11143407 |
| _publications/2024/Survey-ChaosAI.md | DOI | https://api.crossref.org/works/10.1145/3732777 |
| _publications/2026/tos-efrc.md | DOI | https://api.crossref.org/works/10.1145/3799981 |
| _publications/2026/icse-preserve.md | DOI, pdf, code | https://api.crossref.org/works/10.1145/3744916.3773173 ; https://www.zhihan-jiang.com/files/ICSE26/PreServe.pdf |
| _publications/2026/tosem-autoscope.md | DOI, pdf | https://api.crossref.org/works/10.1145/3830907 ; https://arxiv.org/abs/2509.13852 |
| _publications/2026/tosem-ai-nativebench.md | DOI, pdf, code | https://api.crossref.org/works/10.1145/3821576 ; https://arxiv.org/abs/2601.09393 ; https://arxiv.org/html/2601.09393v1 |
| _publications/2025/Internetware-eRAR.md | DOI | https://api.crossref.org/works/10.1145/3755881.3755887 |
| _publications/2025/ASE-iKnow.md | DOI, Paper, Project | https://research.cuhk.edu.hk/en/publications/iknow-an-intent-guided-chatbot-for-cloud-operations-with-retrieva/ ; https://jun-jie-huang.github.io/ |
| _publications/2026/jsoftware-root-cause-change.md | DOI | https://ebook.xml-journal.net/rjxb/2026/02/files/basic-html/page162.html |
| _publications/2023/jsoftware-java-tracing.md | DOI | https://www.jos.org.cn/josen/article/abstract/6523 |
| _publications/2026/arxiv-cloud-opsbench.md | pdf, code | https://arxiv.org/abs/2603.00468 ; https://arxiv.org/html/2603.00468v2 |
| _publications/2026/arxiv-llm-failures.md | pdf | https://arxiv.org/abs/2601.13655 |
| _publications/2025/arxiv-daifu.md | pdf | https://arxiv.org/abs/2507.01628 |
| _publications/2026/dsn-llmguard.md | pdf | https://www.cse.cuhk.edu.hk/lyu/publications?do=index |
| _publications/2026/fse-ivr-state-snapshot.md | pdf | https://www.cse.cuhk.edu.hk/lyu/publications?do=index |
| _publications/2026/emse-kpiroot-plus.md | pdf, Arxiv | https://arxiv.org/abs/2506.04569 ; https://wenweigu.github.io/publications/emse26/emse26.pdf |
| _publications/2026/jss-logfun.md | code | https://github.com/limin5120/LogFun |

## 保留与待补资源

- ChangeRCA、ServiceMesh、T-Rank 的旧本地PDF缺失；T-Rank旧BibTeX缺失。渲染器继续隐藏这些不存在的资源，正式DOI仍可访问，不恢复用户已删除的ChangeRCA PDF。
- OpsLens某合作者主页的Paper链接实际指向AgentChaos，未采用；使用精确匹配的正式ACM DOI。
- 无可靠公开PDF、代码或幻灯片的条目不补猜测地址。三篇预印本保留arXiv入口，不伪造正式发表DOI。
- 请求结果和完整出版社元数据存于 `.preview/publication-link-audit/`；这轮修改不包含Git推送或正式部署。
