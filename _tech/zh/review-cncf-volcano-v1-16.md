---
id: review-cncf-volcano-v1-16
title: 2026-10-29｜Volcano 1.16：事件驱动重试与资源公平
date: '2026-10-29'
lang: zh
published: false
layout: article
maintenance: daily-research
source_type: tech
source_url: https://www.cncf.io/blog/2026/10/28/volcano-v1-16-released-namespacequeue-fairshare-and-a-broader-hypernode-ecosystem/
tags:
- agent-reliability
- coding-agents
- observability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-cncf-volcano-v1-16/
---


Volcano 1.16 引入 NamespaceQueue、历史用量 fairshare 和 HyperNode 反亲和。不可调度 Job 缓存按拒绝原因等待相关事件再重试，减少积压反复检查，并保留 watchdog 定期重试。

缓存默认关闭，仅有安全事件提示的拒绝插件参与；发布说明不等同于本地性能或容灾验证。

来源：[Volcano v1.16 Released: NamespaceQueue, fairshare, and a broader HyperNode ecosystem](https://www.cncf.io/blog/2026/10/28/volcano-v1-16-released-namespacequeue-fairshare-and-a-broader-hypernode-ecosystem/)

[Volcano v1.16 Released: NamespaceQueue, fairshare, and a broader HyperNode ecosystem](https://www.cncf.io/blog/2026/10/28/volcano-v1-16-released-namespacequeue-fairshare-and-a-broader-hypernode-ecosystem/)
