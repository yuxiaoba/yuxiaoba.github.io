---
id: review-nvidia-workload-map
title: 2026-11-03｜Workload Map：共享 Kubernetes 工作负载描述
date: '2026-11-03'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://developer.nvidia.com/blog/support-new-ai-frameworks-faster-using-nvidia-workload-map/
tags:
- agent-reliability
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-nvidia-workload-map/
---

Workload Map 用公共声明描述分布式工作负载的角色、pod 模板、副本和状态，让检查工具、gang scheduler 与管理平台复用同一 CRD 解释，减少每种框架分别写 adapter。

定义仍需维护并适配 CRD 语义；文章没有量化开发时间或调度性能收益，统一结构不证明统一运行语义。

来源：[Support New AI Frameworks Faster Using NVIDIA Workload Map](https://developer.nvidia.com/blog/support-new-ai-frameworks-faster-using-nvidia-workload-map/)

[Support New AI Frameworks Faster Using NVIDIA Workload Map](https://developer.nvidia.com/blog/support-new-ai-frameworks-faster-using-nvidia-workload-map/)
