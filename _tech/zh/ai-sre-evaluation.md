---
date: '2026-11-10'
published: true
layout: article
maintenance: daily-research
translation_source: assistant-authored paired Chinese/English research notes
authoring_source: assistant
editorial_status: source-checked
id: ai-sre-evaluation
title: 2026年11月10日｜AI SRE 评测：把诊断、证据与操作责任拆开
lang: zh
source_type: tech
source_url: https://one2n.io/blog/what-changed-in-how-we-evaluate-ai-sre-agents
long_read: true
tags:
- observability
- agent-reliability
- systems-reliability
summary: 从一次错误 Helm rollback 归因出发，细分 AI SRE 的诊断、共享知识、执行审计与操作边界。
permalink: /tech/zh/ai-sre-evaluation/
published_at: '2026-11-10T09:37:04.860576+08:00'
updated_at: '2026-11-10T09:37:04.860576+08:00'
---
[What changed in how we evaluate AI SRE agents](https://one2n.io/blog/what-changed-in-how-we-evaluate-ai-sre-agents) · One2N · 2026-11-02

通用编码 Agent 接上 MCP 或 CLI 后也能排障，专用 AI SRE 平台需要说明新增价值在哪里。One2N 从一次 OpenSRE PoC 出发，修订了原先过粗的评估维度：不能只问“有没有给出一个合理根因”，还要看调查从何时启动、能看到哪些系统、结论有何依据，以及谁对操作负责。

## 一个错误答案，至少有三种不同缺陷

作者用 kubectl 将副本数设为零，OpenSRE 却说发生了 Helm rollback。旧评分给 RCA 一个负分，但它不能区分是定位错了对象、给正确现象编造了错误机制，还是提到副本数为零却缺少足够证据。这种分解对改进系统很重要：增加工具覆盖、改善解释与补查决定性证据，不是同一项修复。

文章借 SREGym 的诊断评估说明更细的维度：定位、故障特征、影响范围，各包含三个二元问题，九项至少通过七项才能整体通过。这里是 One2N 对该评估方式的转述，并非本篇新增基准实验，也没有据此报告各家产品的可比较分数。

与本期 Cloud-OpsBench 的联系是，两者都反对用一个最终答案掩盖调查缺口；区别在于，One2N 讨论采购和部署所需的能力面，Cloud-OpsBench 则实现固定事故证据与可评分调查轨迹。它们不能互相代替。

## 调查启动方式决定有多少工作可以提前做

文章将启动分为人工触发、告警触发，以及告警前的预防性检查。专用平台可在工程师到场前完成初步查询，或持续看 error budget 和部署变化；但是否真正缩短缓解时间，仍需要实际时间戳与事件数据验证，文章未提供可归因的 MTTR 对照。

工具覆盖也不仅是连接一个日志后端。IaC、代码、CI/CD、feature flag、拓扑与变更记录共同影响可解释性。让 Agent 读全局上下文，不等于赋予它全局写权限。架构、责任归属、共同排障技能和既往事故应成为团队共享知识，同时让人查看、修改与删除 Agent memory，避免过时结论持续影响后续调查。

## 可追查的执行，才便于交接和修正

个人终端里的调查常把上下文和人工引导留在单次会话中，第二位值班者很难知道已经排除哪些假设。文章主张保存每个查询、工具调用、动作和结论，并把支持或否定假设的日志、指标、trace 链接到报告。

独立 Agent 身份还解决归属问题：如果全部借用工程师凭据，审计日志难以区分人手执行与 Agent 操作。缓解计划则应提供可读意图、pre-check、dry run、成功标准和 rollback 步骤，让批准者知道具体要变更什么。摘要化的依据比一大段原始推理更便于审核，但摘要仍须能回到原始执行证据。

这是一份源自工程 PoC 的评估框架，证据强度在具体误诊案例和明确设计要求，而非大规模受控效果。原文没有适合解释机制的架构图，本篇保留文字。**它值得作为 AI SRE 验收问题集阅读**：诊断质量、共同知识、可追查性和动作约束分别验收，再观察这些能力是否改善实际事故处理。
