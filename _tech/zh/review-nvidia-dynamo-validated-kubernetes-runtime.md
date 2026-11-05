---
id: review-nvidia-dynamo-validated-kubernetes-runtime
title: 2026-10-31｜Dynamo AICR：固定依赖与运行时验证
date: '2026-10-31'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://developer.nvidia.com/blog/build-a-validated-kubernetes-runtime-for-nvidia-dynamo/
tags:
- agent-reliability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-nvidia-dynamo-validated-kubernetes-runtime/
---

AICR 用固定版本 recipe 把 Dynamo 的驱动、DRA、调度、网络和监控依赖一起验证，再安装应用。文章强调路由应使用 worker 上报的 KV 事件，因为按历史请求预测无法看到淘汰。

只针对 recipe 指定平台组合；离线声明检查会跳过行为验证，不能把 bundle 生成当作运行正确。

来源：[Build a Validated Kubernetes Runtime for NVIDIA Dynamo](https://developer.nvidia.com/blog/build-a-validated-kubernetes-runtime-for-nvidia-dynamo/)

[Build a Validated Kubernetes Runtime for NVIDIA Dynamo](https://developer.nvidia.com/blog/build-a-validated-kubernetes-runtime-for-nvidia-dynamo/)
