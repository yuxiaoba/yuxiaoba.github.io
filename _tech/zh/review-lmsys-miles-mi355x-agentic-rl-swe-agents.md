---
id: review-lmsys-miles-mi355x-agentic-rl-swe-agents
title: 2026-10-29｜Miles：agent RL 的长尾、沙箱与资源上限
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://lmsys.org/blog/2026-10-22-miles-mi355x-agentic-rl
tags:
- agent-reliability
- coding-agents
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-lmsys-miles-mi355x-agentic-rl-swe-agents/
long_read: true
summary: "区分长尾限制、沙箱瓶颈、扩容吞吐与基础设施失败造成的奖励污染。"
---

## 一个样本为何拖住整轮训练

Miles 在 MI355X 上训练 SWE agent，样本是完整的代码修改轨迹：读 issue、执行工具、改代码，再用仓库测试给奖励。相同任务的尝试长度差异很大，而 GRPO 组要等齐才能计分。原文观测到 90% 轨迹完成后仍消耗 32% rollout 时间，尾段批量接近一，GPU 利用率下降。

系统把训练和推理放在不同节点，以 Harbor 管理每条轨迹的沙箱，Miles 汇集完成轨迹交给 Megatron-LM，再把权重推回 SGLang。异步训练减少等待，长度上限抑制失败 agent 持续循环。单个八卡推理节点上的步时由 850 秒降至 284 秒，是这一组限制带来的比较，不能与扩容后的吞吐收益混算。

## KV 容量与 CPU 沙箱形成不同瓶颈

没有引擎上下文上限的一次运行中，少数请求增长至 113K–186K tokens，约十条就占满 1.5M-token KV 容量，其他请求排队直到超时。将引擎上下文限制为 64K 解决了这次失控；每轮输出上限不能替代累计上下文上限，因为工具结果也在增长。

迁到云端 E2B microVM 后，沙箱启动中位数降为 1.9 秒，但两核环境的 agent 安装和测试更慢，还增加隧道调用成本。384 条并发轨迹时 GPU KV 使用最多只有 23%，限制已转为沙箱并发。团队还移除了 HTTP 连接池、代理单核、Docker 网络及下载限额等固定上限。把这些失败计为零奖励，会惩罚模型没有犯下的错误，因此基础设施错误需要独立记录和过滤。

## 结果必须带着资源与样本范围阅读

约四倍 rollout 吞吐由每小时 860 增至 3,480 条，同时把推理从一个八卡节点扩到三个，并改变沙箱和并发限制。这不是同硬件软件优化四倍。质量实验使用 Qwen3-30B-A3B-Instruct，先以约四千轨迹 SFT，再在约 1,350 个 SWE-smith 任务上 RL；SWE-bench Verified 的 100 题分层子集、每题四次尝试上，pass@1 从 7.3% 经 12.8% 到 27.5%。

我的理解是，这篇实践最适合用来排查 agent RL 的跨层等待，而非据此选择某种 GPU。需要分别看训练步时、完成轨迹吞吐、沙箱故障和策略质量；把扩容、长度限制与基础设施修复压成一个“加速比”，会掩盖真正的资源预算和奖励污染。

来源：[原始工程文章](https://lmsys.org/blog/2026-10-22-miles-mi355x-agentic-rl)
