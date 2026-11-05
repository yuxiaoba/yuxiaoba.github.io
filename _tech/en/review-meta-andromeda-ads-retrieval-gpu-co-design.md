---
id: review-meta-andromeda-ads-retrieval-gpu-co-design
title: '2026-10-29 | Meta Andromeda: Powering the Next Generation of Ads Retrieval
  Through Model-System Co-Design'
date: '2026-10-29'
lang: en
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
permalink: /tech/en/review-meta-andromeda-ads-retrieval-gpu-co-design/
---

Meta Andromeda fuses embedding gathering, MoE interaction and scoring to keep intermediates off HBM, then colocates index matching, scoring and top-K on a GPU server to reduce candidate transfers. Reported throughput exceeds ten billion ads/s for scoring and one billion for the full pipeline.

These are vendor-specific results with different kernel and end-to-end scopes, not general LLM inference speedups.

[Meta Andromeda: Powering the Next Generation of Ads Retrieval Through Model-System Co-Design](https://engineering.fb.com/2026/10/28/ml-applications/meta-andromeda-next-gen-ads-retrieval-gpu-co-design/)
