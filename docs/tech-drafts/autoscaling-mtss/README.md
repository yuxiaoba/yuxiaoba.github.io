# MTSS 技术阅读（用户指定链接）

- 原文：David Morrison / drmorr，Applied Computing Research Labs，2026-10-05。
- 阅读日期：2026-10-21。正式配对稿 `_tech/zh/autoscaling-mtss.md` 与英文同名文件，手动维护，不消耗日任务调用次数。
- 简要概述原文观点，随后给出明确标为工程推导的事件定义、稳定窗口、积压模型、事件关联与对照实验方法。不是原文全文翻译，不虚构基准结果。
- Kubernetes HPA／探针、Karpenter指标、KEDA控制循环和OpenTelemetry资料另行核验。区分0→1与1→N，不把KEDA轮询间隔说成整个伸缩链路的控制周期。
- 一张原文定性阶段图，1183×201，原字节复制；保留来源及SHA-256于provenance.json。公式为本笔记解释用推导，正文明确恒定速率、μ>λ等假设。
- 原文HTML、构建和浏览器验证保存在 `.preview/manual-tech-autoscaling-mtss/`，不进入网站或Git；来源URL被现有published_sources自动识别，后续日任务可据此去重。
