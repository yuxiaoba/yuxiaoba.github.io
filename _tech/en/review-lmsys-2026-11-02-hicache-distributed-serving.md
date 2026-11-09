---
id: review-lmsys-2026-11-02-hicache-distributed-serving
title: 2026-11-03 | HiCache Across Multi-Parallelism and Distributed Serving
date: '2026-11-03'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://lmsys.org/blog/2026-11-02-hicache-distributed-serving
tags:
- agent-reliability
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-lmsys-2026-11-02-hicache-distributed-serving/
long_read: true
summary: "How page ownership, ACK order and draft state make parallel prefix reuse safe."
---

## A prefix hit is not yet usable state

HiCache extends SGLang prefix reuse from GPU memory to host memory and external storage. Repeated agent histories make this valuable, but parallel execution adds ownership and ordering requirements. CP ranks share a logical radix tree while logical page IDs distribute physical KV pages across owners. Backup and restore must preserve ownership so the next gather receives the correct data.

The article illustrates requests sharing A/B and branching to C or E. Restored pages may move physically without changing their owner. Each layer restores local pages, gathers the distributed prefix, then runs attention, with completion events ordering the streams. Two alternating scratch buffers hold adjacent layers and count against admission capacity. Reuse avoids recomputation but still pays for gathering shards.

## Why pipeline stages cannot consume completions independently

PP stages hold different layers and finish asynchronous copies at different times. If PP0 observes only A complete while PP1 observes both A and B, independently releasing locks changes eviction eligibility and eventually prefix decisions. With pp_sync, PP0 chooses an ACK count and passes it down the pipeline. Faster stages retain extra ACKs; slower stages wait for selected local transfers before changing bookkeeping.

External storage additionally takes cross-rank minima of hit and completed lengths and publishes agreed progress through ordered ACKs. If PP0 selects four pages, later stages use four even when six are locally available. The protocol aligns logical operations without a simultaneous pipeline-wide barrier. The article's rank_consensus_checker compares corresponding calls and returns to locate divergence before a later shape mismatch or collective hang.

## Draft state, topology and decode-side reuse

Speculative decoding must restore the draft model's KV, indexer and recurrent state as needed, not just target KV. Compatible layouts use packed host mappings; sidecar pools handle separately laid-out state. Unified storage partitions by global layers and heads, with namespace fields including model, dtype and page size. The documented integration supports a file backend and a single MHA or MLA pool within stated topology limits, not arbitrary combinations.

For P/D serving, the decode worker matches and restores its prefix and receives only the missing suffix. The CP traffic comparison uses GLM-5.2-NVFP4, TP4/CP4, matched host-cache targets and two four-GB300 prefill engines per deployment. Combined hit rate remains near 93% over roughly three hours; much of the benefit is shifting hits from host to GPU. My interpretation is that layout, readiness and event agreement form one reuse contract. Hit rate alone establishes neither correctness nor TTFT.

Source: [Original engineering article](https://lmsys.org/blog/2026-11-02-hicache-distributed-serving)
