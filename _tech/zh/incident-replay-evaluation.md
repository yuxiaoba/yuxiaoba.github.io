---
id: incident-replay-evaluation
title: 2026年10月1日｜历史故障回放：先确认Agent能看到足够证据
date: '2026-10-01'
lang: zh
published: true
layout: article
maintenance: manual-research
source_type: tech
tags:
- observability
- agent-reliability
summary: 固定遥测和调查接口，区分模型能力、证据缺失与事后信息泄漏。
long_read: true
source_url: https://zenn.dev/genax_corp/articles/5214d9e0228928
source_date: '2026-09-29'
permalink: /tech/zh/incident-replay-evaluation/
authorship: assistant
translation_source: assistant
published_at: '2026-10-22T08:54:49.993592+08:00'
updated_at: '2026-10-22T08:54:49.993592+08:00'
---
Sho Okada · Gen-AX · 2026-09-29 · [原文](https://zenn.dev/genax_corp/articles/5214d9e0228928)

Gen-AX 把真实故障附近的遥测复制到独立 ClickHouse，让 Incident Agent 对固定数据反复调查。一个 Collector 负载偏斜案例揭示了评测边界：保存的遥测能表现异常，却没有完整保留解释网络路径所需的历史 Kubernetes 配置。事后知道根因，不代表当时交给 Agent 的数据足以证明它。

<a class="note-image-link" href="/assets/images/tech/incident-replay-evaluation/replay-zh.svg" target="_blank" rel="noopener" aria-label="阅读整理：把调查证据与评分答案分开，流程图不表示实验结果。 · 查看大图"><img src="/assets/images/tech/incident-replay-evaluation/replay-zh.svg" alt="阅读整理：把调查证据与评分答案分开，流程图不表示实验结果。" loading="lazy"><span class="note-image-action">查看大图 ↗</span></a>

*阅读整理：把调查证据与评分答案分开，流程图不表示实验结果。*

## 回放首先解决的是比较条件

同一查询在不同时间运行，可能因保留期、迟到数据或配置变化而得到不同结果。固定输入后，才能把模型、提示词或工具变化与环境变化分开。它也允许离线重复查询，减少评测对生产数据库的干扰。

进一步的工程要求是把“固定数据”扩展为“固定调查接口”。不仅要保存表中的行，还应记录表结构、查询权限、时区、工具版本与返回上限。否则，两次实验即使读取同一数据库，仍可能通过不同接口看到不同的信息。

## 历史状态不能用当前状态代替

[OpenTelemetry Kubernetes Objects Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/k8sobjectsreceiver)支持定期拉取和 watch。前者取得离散状态，后者追踪更新；使用时还要处理初始状态、资源版本和权限。选择哪些对象及采样频率，应由需要验证的故障机制决定。

例如，若研究请求路由，需要能恢复相关时刻的服务选择关系和接收端集合；若研究资源限制，需要区分工作负载模板和实际运行对象。只存最终配置会把故障发生后的修复结果带进“事发现场”，而只存事件又可能缺少解释变化所需的基线。

一个可行的数据包可以包含三层：不可变的原始观察、按时间整理的对象状态、独立保存的参考解释。前两层供调查端读取，第三层只用于评分。敏感字段的处理应保留跨信号实体对应关系，否则匿名化本身会破坏因果分析。

## 用证据消融检验评测是否公平

基于这个思路，可以做一个受控实验：从完整案例中移除一种信号，保持其余工具、预算和问题不变。分别检查异常对象定位、机制解释和不确定性表达是否变化。这样测到的才更接近该信号的增量价值。

关键是不要要求删减版仍给出完整答案。若移除的信息确实不可替代，合理结果应是更谨慎的判断。反之，如果删除关键证据后答案仍然完全准确，就需要检查剩余字段是否泄露了标签，或者案例是否存在另一条可行证据路径。

评分器也要接受同样的检查。可以让人工审阅一组“结论正确但证据错误”“定位正确但机制错误”“证据不足并明确保留意见”的输出，观察自动评分是否把这些情况区分开。仅报告一个F1值，无法覆盖这些差异。

## 静态回放与真实修复是两个实验

静态数据库适合调查评测，却不会因为 Agent 提议回滚而改变状态。若研究修复，需要有可执行环境、动作权限、状态转移和成功判定；把建议文本写得像操作步骤，不等于已经完成恢复。

这类回放最有价值的产物因此不只是模型排行榜，还包括一份可检验的证据需求：哪些数据必须保留、哪些信息足以区分候选原因、哪些结论只能依赖事后知识。对故障诊断研究而言，它把“模型不够聪明”和“根本没有足够观察”变成了可以分别验证的问题。
