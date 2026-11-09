---
id: 2026-11-04-mercor-apex-swe-observability
title: '2026年11月4日｜技术阅读：AI Observability & Debugging Leaderboard: APEX-SWE | Mercor'
date: '2026-11-04'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://www.mercor.com/apex/apex-swe-leaderboard/observability-swe/
source_published_at: '2026-11-03'
tags:
- systems-reliability
authoring_source: assistant
translation_source: assistant
permalink: /tech/zh/2026-11-04-mercor-apex-swe-observability/
long_read: true
summary: "从 APEX-SWE 的费用检查示例理解观测、修复和验证要求，并避免把未通过率当误诊率。"
---

## 榜单测的是带工具的诊断与修复

Mercor 的 APEX-SWE Observability 页面将任务定义为诊断并修复生产式软件故障，使用 Terminus-2 harness。页面说明领域分数是 100 个 held-out prompts 的平均值，示例只用于展示，不能代表整个分项。阅读时不仅要看模型名，还要看 effort；同一页面同模型不同 effort 的成绩不同。

它与只从日志回答根因、或只从源码生成 patch 的评测不同：示例同时提供代码、Loki/Grafana 观测和项目／团队讨论工具，并要求调查过程展示观测工具使用。这让分数包含获取证据、理解任务与实现修复的多种能力，不能把全部失败都叫“根因判断错”。

## 公开示例怎样把症状连到代码约束

示例来自交易池余额检查：旧逻辑未计入 operator fee，余额不足的交易仍入池，执行时才失败。任务要求把基本交易成本、L1 rollup 成本和 operator 成本一起纳入检查，并按 Isthmus 激活时间区分费用规则。

正确修复还需要处理交易替换后的成本更新、费用参数变化后重新检查 pending 交易，以及充值后恢复接受。示例列出 NewTotalRollupCostFunc 和相关参数提取函数，明确接口与测试配置。这个任务说明，定位到一个缺失费用项只是开始，状态变化和升级边界仍可能让局部 patch 不完整。

## 69.8% 不能直接解释成某类误诊率

当前读取快照中，Opus 5.5 Max 为 69.8%。其补数约三成是该分项未通过比例，页面没有提供将其统一归因于证据遗漏、推理错误或修复失败的逐项统计。公开示例的 trajectory 区域还显示该模型无 rubric 数据，不能凭任务说明想象它实际如何调用工具。

我的理解是，这个榜单更适合用来提出分阶段评测问题：必要日志是否被找到、修复是否覆盖状态转换、验证条件是否正确。跨研究比较必须匹配任务与判定器；代码块覆盖率不是这里的任务成功率。要断言模型在哪一步失败，还需访问对应轨迹与评分证据，而不是从总分反推原因。

来源：[原始工程文章](https://www.mercor.com/apex/apex-swe-leaderboard/observability-swe/)
