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
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-meta-andromeda-ads-retrieval-gpu-co-design/
long_read: true
summary: "How Andromeda removes intermediate and cross-host candidate traffic, with distinct kernel and pipeline measurements."
---

## Retrieval becomes a data-movement problem

Andromeda narrows a huge advertising candidate pool within a millisecond budget before expensive ranking. Meta's architecture uses specialized user experts, context-aware ad representations and an MoE gating interaction layer. The reported roughly 300-fold FLOP reduction relative to the 2024 retrieval model creates room for system fusion.

At billions of candidates per second, even small intermediate tensors generate terabytes per second of traffic. Separately launching embedding gather, user–ad interaction and scoring repeatedly materializes results in HBM. Once arithmetic becomes cheaper, movement becomes the limiting resource.

## Fusion and co-location remove different transfers

A fused kernel performs each user–ad gather, interaction and score while keeping intermediates in registers and shared memory. A separate architectural change addresses networking: previously CPU-side index matching and top-K exchanged large candidate lists with a remote GPU scoring service.

The new pipeline co-locates index matching, scoring and top-K on one GPU server. Requests send user features and a targeting query and receive final candidates; Meta reports about 100 times less network traffic. This also requires a GPU index that preserves complex targeting semantics and real-time updates, not simply relocating a process. Subsequent work aligns matching and scoring layouts to remove indirection between components.

## Component and production rates differ

The article reports over ten billion ads per second for the scoring kernel on a GH200, but over one billion for the complete co-located production pipeline. Index matching has a different, higher peak. INT8's further gain over optimized FP16 is another comparison. Cumulative conversion improvements since 2025 cannot be attributed wholly to one new kernel.

My interpretation is that the transferable method is joint analysis of model structure, memory hierarchy and deployment boundaries. It depends on compact scoring, preserved indexing semantics and GPU-compatible layouts. Ads per second is neither LLM token throughput nor a promised benefit for arbitrary MoE models.

Source: [Original engineering article](https://engineering.fb.com/2026/10/28/ml-applications/meta-andromeda-next-gen-ads-retrieval-gpu-co-design/)
