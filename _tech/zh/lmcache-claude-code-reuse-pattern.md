---
id: lmcache-claude-code-reuse-pattern
title: 2026年11月13日｜Claude Code 轨迹：92% 前缀复用说明什么
date: '2026-11-13'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- inference-serving
summary: 一个 Django 修复案例展示角色内上下文增长与复用；结构性可复用不等于真实服务缓存命中。
long_read: true
source_url: https://blog.lmcache.ai/en/2025/12/23/context-engineering-reuse-pattern-under-the-hood-of-claude-code/
permalink: /tech/zh/lmcache-claude-code-reuse-pattern/
translation_source: assistant
authorship: assistant
source_published_at: '2025-12-23'
published_at: '2026-11-13T08:46:43.062448+08:00'
updated_at: '2026-11-13T08:46:43.062448+08:00'
---
Kobe, Mengbing · 2025-12-23  
原文：[Context Engineering & Reuse Pattern Under the Hood of Claude Code](https://blog.lmcache.ai/en/2025/12/23/context-engineering-reuse-pattern-under-the-hood-of-claude-code/)

一个很小的代码修复，也可能产生很大的累计输入量。Kobe 与 Mengbing 在 2025 年 12 月的文章追踪一次 Django 只读 JSONField 显示问题，报告 92 次 LLM 调用、约 200 万输入 token、13 分钟与 92% 前缀复用率。这个旧案例的价值，是说明 agent 流量为何不同于互相独立的聊天请求。

## 一次任务包含多条角色上下文

主 agent 先把探索拆给三个 Explore 子 agent，分别查看 JSONField、display_for_field 和只读字段渲染。它们有独立系统提示与工具子集，反复执行工具调用、追加结果。探索总结再交给 Plan，最后主 agent 执行修改和测试。因此，不应把全部调用视为沿同一个共享上下文顺序增长。

作者把早期仅加载工具表或子 agent 提示的调用解释为缓存预热。它们展示稳定前缀可能在实际工作前出现，但轨迹观察本身不能证明产品内部设计动机，也不能直接测出预热节省了多少时延。

<a class="note-image-link" href="/assets/images/tech/lmcache-claude-code-reuse-pattern/figure.png" target="_blank" rel="noopener" aria-label="Claude Code 主 agent、探索与规划角色的调用结构 · 查看原图 ↗"><img src="/assets/images/tech/lmcache-claude-code-reuse-pattern/figure.png" alt="Claude Code 主 agent、探索与规划角色的调用结构" loading="lazy"><span class="note-image-action">查看原图 ↗</span></a>

*先看主 agent 分派探索，再看总结进入规划与执行；不同角色的工具循环各自增长上下文。*

## 复用率的分母很重要

原文按阶段计算输入前缀重叠：Explore 阶段 546,104 token，92.06% 为共享前缀；Plan 阶段 528,286，93.23%；主 agent 后期 827,411，97.83%。随着每轮追加工具结果，旧上下文反复随请求发送，累计 token 远大于一次上下文长度。角色之间只传总结，又会产生不同的前缀分支。

这解释了长程 agent 为什么可能从 prefix cache 获益。它衡量的首先是结构性复用机会，并非 92% 请求在真实 KV 服务层命中，也不是 92% 推理计算已被消除。实际命中仍取决于有效前缀、缓存驻留、路由和服务端策略。

## 一个可观察案例，而非所有 agent 的平均画像

样本只有一个任务、一次运行。文章的总体调用数写为 92，后文又提到辅助调用 #93，统计范围存在细节不一致，不能把这一数字当成完整平台审计。费用例子使用假定读写价格计算，也不等于实际账单。

其最可迁移的观察，是分别追踪角色内的追加历史、跨角色总结与重复文件内容。相同文件出现在不同前缀之后，并不能自动复用标准因果 attention 的同一 KV；原文将非前缀复用作为进一步研究方向。对 AgentOps 而言，这个案例提供了分析请求形状的具体入口，但不足以推出生产流量统一具有 92% 命中率或固定时延收益。
