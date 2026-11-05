---
id: review-nvidia-3-ways-boost-moe-inference-dgx-spark
title: 2026-10-29｜DGX Spark MoE 优化：实测收益与组合故障
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://developer.nvidia.com/blog/3-ways-to-boost-moe-inference-on-nvidia-dgx-spark/
tags:
- agent-reliability
- coding-agents
- observability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-nvidia-3-ways-boost-moe-inference-dgx-spark/
---

该 DGX Spark 实践组合 Humming、FP8 LM head 和 MTP；全 GSM8K 测试吞吐提高 42.5%、平均延迟降低 24.5%，远低于合成场景 185.1% 的吞吐增益。只共享权重而不共享完整 LM-head 模块会让组合优化反而退化。

厂商报告限于 Ling 模型、单 batch 和给定采样；准确率无显著差异不是所有输出逐位等价。

来源：[3 Ways to Boost MoE Inference on NVIDIA DGX Spark](https://developer.nvidia.com/blog/3-ways-to-boost-moe-inference-on-nvidia-dgx-spark/)

[3 Ways to Boost MoE Inference on NVIDIA DGX Spark](https://developer.nvidia.com/blog/3-ways-to-boost-moe-inference-on-nvidia-dgx-spark/)
