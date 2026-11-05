---
id: review-meta-andromeda-ads-retrieval-gpu-co-design
title: 2026-10-29｜Meta Andromeda：融合执行与 GPU 共置的边界
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://engineering.fb.com/2026/10/28/ml-applications/meta-andromeda-next-gen-ads-retrieval-gpu-co-design/
tags:
- agent-reliability
- coding-agents
- observability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-meta-andromeda-ads-retrieval-gpu-co-design/
---

Meta Andromeda 把 embedding gather、MoE 交互和评分融合，避免中间张量落 HBM；再将索引匹配、评分和 top-K 放到同一 GPU 服务器，减少跨机候选传输。文章分别报告评分 kernel 超百亿广告/秒、完整流水线超十亿。

均为厂商特定系统报告，kernel 与端到端口径不同；广告评分吞吐不能推广成通用 LLM 推理收益。

来源：[Meta Andromeda: Powering the Next Generation of Ads Retrieval Through Model-System Co-Design](https://engineering.fb.com/2026/10/28/ml-applications/meta-andromeda-next-gen-ads-retrieval-gpu-co-design/)

[Meta Andromeda: Powering the Next Generation of Ads Retrieval Through Model-System Co-Design](https://engineering.fb.com/2026/10/28/ml-applications/meta-andromeda-next-gen-ads-retrieval-gpu-co-design/)
