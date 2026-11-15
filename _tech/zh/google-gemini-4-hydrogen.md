---
id: google-gemini-4-hydrogen
title: 2026年11月13日｜Hydrogen 与 Orchestrator：在轨迹中切换模型
date: '2026-11-13'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- agent-reliability
summary: Google 把快速执行模型与双向重规划交接组合；官方收益数字存在基准版本冲突。
long_read: true
source_url: https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen/
permalink: /tech/zh/google-gemini-4-hydrogen/
translation_source: assistant
authorship: assistant
source_published_at: '2026-11-12'
published_at: '2026-11-13T08:46:43.062448+08:00'
updated_at: '2026-11-13T08:46:43.062448+08:00'
---
Koray Kavukcuoglu; The Antigravity Team · 2026-11-12  
原文：[Introducing Gemini 4 Hydrogen](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen/)

Gemini 4 Hydrogen 的发布值得关注之处，不只是模型分数，而是配套 Orchestrator 把模型选择从“开始时选一次”变成“任务执行中可以交还”。这与长程 agent 的实际困难相符：初始提示很简单，也可能在依赖、测试或代码状态中暴露复杂问题。

## 静态路由缺少中途升级机会

[Antigravity 官方说明](https://antigravity.google/blog/gemini-4-hydrogen-in-google-antigravity/)给出的流程是：Carbon 先以只读方式探索依赖、消除歧义并建立包含重规划触发条件的计划；Hydrogen 接手编辑、更新包与运行测试；遇到阻力，再交还 Carbon 检查状态、修正计划并恢复执行。

这里的增量是同一条轨迹内的双向交接，而不只是把简单任务整体交给便宜模型。它也区别于并行多 agent：不同角色可并发工作，但 Orchestrator 的例子强调一个持续演化的任务怎样在不同推理能力之间切换。公告未公开触发器阈值、状态传递格式或完整回退策略，不能将示例看作已充分规定的调度算法。

## 模型能力与成本属于不同维度

Google 报告 Hydrogen 默认 high 档在 Artificial Analysis Intelligence Index 为 51，xhigh 为 54；Terminal-Bench 4.1 为 57%，对照 3.8 Flash 为 18.2%。这些是发布方报告，不等于每项本地编码任务都会同幅改善。四档 thinking level 提供质量与等待时间的选择，但更深推理不能只凭名字判断是否划算。

发布时标价为每百万输入 token 1.50 美元、输出 7.50 美元，整个 1M 上下文窗口采用相同单价。单价、一次任务总 token、执行时间和成功率仍是不同指标。把模型换便宜，不代表在更多重试或更长输出下任务总成本必然下降。

## 当前证据能支持的判断

两篇官方文章对 Orchestrator 同一组配额与时间收益使用不同 Terminal-Bench 版本：主发布页写 4.0，Antigravity 页写 4.1。因此这里不采用该组收益作为定量结论。配额也不是美元成本，不能直接拿来与 API 单价相乘。

这是一项有明确流程变化的产品发布，尚不足以推导最优交接策略。对 AgentOps 的启发是把升级、重新规划和状态交接视为运行时行为，而不是把首轮模型选择当成最终决定。公告中的图以基准和演示为主，没有足够明确的 Orchestrator 架构图可用于解释交接内部实现，本页保留文字分析。
