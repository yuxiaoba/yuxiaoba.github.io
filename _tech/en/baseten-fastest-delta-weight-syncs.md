---
id: baseten-fastest-delta-weight-syncs
title: 2026-10-31 | Using GPU Weights as the Parent for Delta Sync
date: '2026-10-31'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: Read changed GPU positions, verify incremental updates, shorten policy-switch
  pauses, and free host memory for KV cache.
long_read: true
source_url: https://www.baseten.co/blog/the-fastest-delta-weight-syncs-in-the-world/
permalink: /tech/en/baseten-fastest-delta-weight-syncs/
translation_source: assistant-authored bilingual research notes
published_at: '2026-10-31T08:34:05.438760+08:00'
updated_at: '2026-10-31T08:34:05.438760+08:00'
---
**Baseten · 2026-10-30**  
Original: [The fastest delta weight syncs in the world](https://www.baseten.co/blog/the-fastest-delta-weight-syncs-in-the-world/)

In reinforcement learning, a trainer continually produces policies while inference replicas generate rollouts. When they do not share infrastructure, weights must cross environments; a long update pause can disrupt the training and serving loop. Baseten describes rebuilding delta synchronization around the weights already serving on the GPU, removing a complete CPU parent checkpoint.

## From a full CPU copy to sparse reads

The trainer publishes checkpoints and sparse deltas to object storage. Each delta tensor is the zstd-compressed XOR of parent and new bytes. A rollout replica downloads the update and reconstructs the new policy. The previous design retained the full parent on the host for decoding, then patched that copy after each update so the next delta had the right parent. For GLM-5.3 the article reports a roughly 770 GB copy and approximately 45 seconds to promote it, with host memory competing with the KV cache.

At startup the new design verifies each tensor and stores its Adler-32 checksum, then deletes the local parent checkpoint. The decoder walks zstd commands and keeps only positions and masks for nonzero XOR bytes. Each GPU worker reads old values only at changed positions, computes the absolute new values, and prepares a write plan in the engine’s actual layout. The old policy continues serving during most preparation.

## Verify first, minimize the pause

Rereading every tensor to check it would undermine sparse updates. The article exploits Adler-32’s position-dependent per-byte contributions: starting with the stored parent checksum, it accumulates corrections for changed bytes and compares the result with the trainer’s new checksum. A mismatch rejects the update before GPU writes. For a 30 GB Kimi K3 delta, the authors report that this optimization reduced the whole update from about 230 to 100 seconds; the result is specific to that configuration.

During the switch, the system closes admission and pauses running requests, writes the new values in place, refreshes derived weights, and publishes the policy only after all ranks succeed. For approximately 770 GB GLM-5.3, the reported time from sync request to serving the new policy is about 15 seconds, with a 0.8-second pause, down from 36 and 6 seconds respectively. Total synchronization time and request pause measure different things.

## Preventing update work from starving serving

Updates still share the serving machines. The decoder partitions changes by tensor/expert-parallel ownership and maps them to each GPU’s actual layout. To avoid CPU-heavy work competing with SGLang’s Python scheduling loop for the GIL, planning runs in a separate CUDA-free helper process and exchanges data through shared pinned memory. Download and decode are pipelined by shard; low-priority threads leave CPU cores for serving.

For Kimi K3’s 1.7 TB served layout, the authors use two GB300 nodes with four GPUs each, processing only locally owned tensors. An 8.4 GB delta takes 75 seconds from request to live weights, including a 4.1-second pause. Both nodes must finish writing before service resumes. Subsecond pauses therefore do not generalize to every model and configuration.

## Reusing host memory for KV state

Removing the CPU weights leaves memory for GPU-evicted KV pages. The article reports reloading a shared 150k-token prefix from CPU in 0.48 seconds versus 4.9 seconds for a fresh prefill. In its Kimi K3 AgentX test, concurrency 16 already fits in GPU cache, so offloading makes no difference. At concurrency 48, the new design’s host cache increases the hit rate from 2% to 92% and output throughput per GPU by 3.2 times.

These measurements use a single replica and trainer-shaped fixture deltas. They illustrate trade-offs for particular workloads, not a guarantee for other deployments. The broader engineering lesson is to design **update correctness, pause time, host memory, and cache benefit** together rather than comparing transfer bandwidth alone.
