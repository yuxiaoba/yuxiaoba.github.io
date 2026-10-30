---
id: vllm-mistral-large-4
title: 2026-10-30 | How vLLM supports sparse attention and cross-layer KV sharing
date: '2026-10-30'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: 'vLLM''s Mistral Large 4 support shows how model structure and serving infrastructure
  jointly affect long-context performance: sparse indexing reduces attention reads,
  cross-layer sharing avoids cache writes, and the runtime must handle parallelism,
  graph execution and disaggregated transfers.'
long_read: true
source_url: https://vllm.ai/blog/2026-10-29-mistral-large-4
permalink: /tech/en/vllm-mistral-large-4/
translation_source: assistant-authored paired Chinese/English reading notes
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-10-30T10:31:20.339125+08:00'
---
vLLM's Mistral Large 4 support shows how model structure and serving infrastructure jointly affect long-context performance: sparse indexing reduces attention reads, cross-layer sharing avoids cache writes, and the runtime must handle parallelism, graph execution and disaggregated transfers.

**Source:** vLLM, [Day 0 support for Mistral Large 4 on vLLM](https://vllm.ai/blog/2026-10-29-mistral-large-4), October 29, 2026.

The 72-layer MoE combines MLA with a DSA indexer selecting up to 2,048 keys per query. Nine NoPE layers read layer 35's latent KV instead of writing their own. The V2 runner maps these consumers to the target cache, leaving 63 of 72 layers with their own cache. The article says this mechanism is being upstreamed as a general capability.

For long contexts, decode context parallelism shards latent KV across ranks. The authors report about 7.9 times the KV capacity at TP8 and up to a 1.6-fold reduction in time to first token when combined with prefill context parallelism. In their TP8 test, the built-in DSpark drafter accepts about 2.9 tokens per step and roughly doubles output throughput. The implementation also supports NIXL prefill/decode disaggregation and HiSparse host-memory sparse KV offload with cross-layer sharing.

These figures apply to the reported model and configurations, not every workload. The combination of shared KV, sparse indexing and parallelism is the important systems change: it affects cache consumption as well as communication and execution paths across stages.
