---
id: revolut-self-hosted-coding
title: 2026年11月4日｜Revolut 如何在固定 GPU 规模下调优编码模型服务
date: '2026-11-04'
lang: zh
published: false
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- coding-agents
summary: Revolut 分享自托管编码模型的服务调优、成本和运行控制，重点是按实际工作负载配置上下文、缓存及并行度。
source_url: https://ai.engineer/nyc/2026/talks/revolut
permalink: /tech/zh/revolut-self-hosted-coding/
translation_source: assistant-authored paired Chinese and English
---

编码 Agent 的成本与体验，不只取决于模型能力，也取决于真实请求的上下文长度、缓存命中率以及服务并行方式。在 [AI Engineer NYC 2026 的演讲](https://ai.engineer/nyc/2026/talks/revolut)中，Revolut 的 David Abitbol 分享了该公司自托管编码模型的部署经验；以下依据会议页面和演讲文字记录。

## 固定硬件，围绕工作负载调优

演讲者表示，Revolut 使用约 56 张 B200 为约 2,000 名工程师提供 GLM 5.3 服务。在其展示的迁移至稳定运行阶段，GPU 数量保持不变，请求量增加约 76%，首 token 时间从 14.26 秒降至 1.68 秒。两段时间的需求和系统配置均有变化，这是一项内部运营观察，不是单一优化项的受控实验。

调优首先考虑实际上下文长度：预留过大的上下文会与并发请求竞争 KV Cache 空间。演讲者还提到针对 Blackwell 使用低精度量化、检查编码任务的缓存命中率，以及在模型能以四路张量并行装载时，比较八路并行能否为 KV 留出更适合负载的空间。他同时列出推测解码与 prefill/decode 分离作为可研究方向，但并未对每项的独立收益给出消融结果。

## 体验、成本与控制一起看

该部署的经验目标是首 token 时间低于三秒；演讲者称超过五秒时用户反馈明显。他报告综合成本约为每百万 token 0.30 美元，并称自托管账单约为此前外部模型账单的十分之一。这些是特定硬件、利用率与工作负载下的自述，不能直接当作其他团队的部署报价。

自托管也把运行责任带回团队：演讲提及限制 Agent 可执行操作的沙箱和审批规则，以及用于事故排查的遥测。演讲中的监管与数据驻留判断是该组织的经验表述，不能推广为其他部署自动满足合规要求。
