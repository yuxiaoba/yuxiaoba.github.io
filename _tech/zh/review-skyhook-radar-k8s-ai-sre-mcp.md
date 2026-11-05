---
id: review-skyhook-radar-k8s-ai-sre-mcp
title: 2026-10-31｜Radar：共享集群状态与受限诊断对比
date: '2026-10-31'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://github.com/skyhook-io/radar
tags:
- agent-reliability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-skyhook-radar-k8s-ai-sre-mcp/
---

Radar 让界面与 MCP 读取同一份集群关系、事件和健康状态，并提供只读入口。作者的同 agent 50 故障对比中，平均诊断时间为 64 秒，对照原始 kubectl 为 191 秒。

由产品作者评估，评分含 LLM judge；不同研究的故障、时间和负载不同，不能跨表直接排名或推断真实修复效果。

来源：[Radar: open-source Kubernetes UI with built-in MCP server for AI agents](https://github.com/skyhook-io/radar)

[Radar: open-source Kubernetes UI with built-in MCP server for AI agents](https://github.com/skyhook-io/radar)
