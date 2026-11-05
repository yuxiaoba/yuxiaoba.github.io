---
id: review-google-gke-networking-dataplane-agentic-ai
title: 2026-10-29｜GKE：高密度沙箱的网络身份瓶颈
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://cloud.google.com/blog/products/networking/gke-networking-dataplane-for-large-agentic-ai-workloads
tags:
- agent-reliability
- coding-agents
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-google-gke-networking-dataplane-agentic-ai/
---

GKE 文章把高密度 agent 沙箱启动瓶颈定位到网络身份：每个 pod 的动态标签会生成独立身份。把不参与选择器的元数据放入 annotations，或精确排除不相关标签，可减少身份分配与 eBPF map 更新。

过滤前需确认标签不承担网络策略语义；厂商不同沙箱/恢复基准不能合并为统一吞吐保证。

来源：[GKE networking dataplane for large agentic AI workloads](https://cloud.google.com/blog/products/networking/gke-networking-dataplane-for-large-agentic-ai-workloads)

[GKE networking dataplane for large agentic AI workloads](https://cloud.google.com/blog/products/networking/gke-networking-dataplane-for-large-agentic-ai-workloads)
