---
id: specforge-v03
title: 2026年8月4日｜SpecForge 将目标模型推理与草稿模型训练拆开
date: '2026-08-04'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://lmsys.org/blog/2026-08-04-specforge-v0-3/
long_read: true
tags:
- inference-serving
summary: SpecForge 将目标模型推理与草稿模型训练拆开
translation_source: assistant-authored paired Chinese and English
permalink: /tech/zh/specforge-v03/
published_at: '2026-10-28T15:48:27.004821+08:00'
updated_at: '2026-10-28T15:48:27.004821+08:00'
---
[SpecForge v0.3.0: a Unified Disaggregated and Colocated Speculative Decoding Stack, and New Open SpecBundle Draft Models](https://lmsys.org/blog/2026-08-04-specforge-v0-3/) · LMSYS / SGLang · 2026-08-04

SpecForge v0.3 将投机解码训练中被冻结的 target 模型和待优化的 draft 模型拆成可独立扩缩的生产者与消费者。此前两者共用生命周期和固定资源布局，即使只有一侧成为瓶颈，也难以单独调整。

在线拆分模式中，打补丁的 SGLang 服务捕获目标模型特征，Mooncake 承载大张量；控制面只传递轻量 SampleRef，训练 worker 按需解析引用并组批。捕获、交付和生命周期契约共同处理数据归属与释放，避免仅靠进程边界掩盖缓冲和失败问题。统一入口也支持在线、离线与共置流程，以及 EAGLE3、DFlash 等多种草稿方法。

团队报告在 8×H20 测试环境中，3 个 SGLang 服务和 5 个训练 worker 的端到端训练吞吐比此前共置实现高约 10%；这是特定拓扑和环境的结果，并不等于所有负载均可获益。版本还提供训练与服务一致性检查，用受控样例核对特征捕获、训练、导出与 SGLang 服务，帮助在长训练前发现接口不一致。
