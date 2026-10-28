---
id: attention-co-design
title: 2026-08-01 | Co-Designing Attention for Long Context
date: '2026-08-01'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: NVIDIA examines how head grouping, dimensions, sequence length and parallelism
  affect long-context inference.
long_read: true
source_url: https://developer.nvidia.com/blog/co-designing-ai-model-attention-for-fast-interactive-long-context-inference/
translation_source: assistant-authored paired Chinese/English notes
permalink: /tech/en/attention-co-design/
published_at: '2026-10-28T15:30:52.583960+08:00'
updated_at: '2026-10-28T15:30:52.583960+08:00'
---
**Nidhi Bhatia, Samkit Jain, Sai Kishan Pampana, Ritika Borkar, Bita Darvish Rouhani · NVIDIA · 2026-07-31**  
Original: [Co-Designing AI Model Attention for Fast, Interactive Long-Context Inference](https://developer.nvidia.com/blog/co-designing-ai-model-attention-for-fast-interactive-long-context-inference/)

Long contexts make attention an increasingly visible inference cost. NVIDIA relates matrix shapes, memory traffic and parallelism on GPUs to model design choices for prefill and decode. The analysis concerns dense attention and the kernels measured in the article; it is not a universal speed formula for every model or all serving overhead.

## One attention operation, two bottlenecks

Prefill processes input tokens together and creates large matrices, which the article treats as compute-bound. Ordinary decode generates one token per step and repeatedly reads historical KV cache, often making memory bandwidth the constraint. Prefix caching creates an important exception: a short new input attending to a long cached prefix can make prefill behave more like decode. Speculative decoding increases effective query length per step and can move decode toward the compute-bound regime.

Let G be the number of query heads sharing a KV head. Under the article's FP8 attention and KV-cache assumptions, larger G lets queries reuse a KV read and increases decode arithmetic intensity; prefill is primarily governed by input length.

<a class="note-image-link" href="/assets/images/tech/attention-co-design/group-size.webp" target="_blank" rel="noopener" aria-label="Group size and prefill and decode runtime, view original image"><img src="/assets/images/tech/attention-co-design/group-size.webp" alt="Prefill runtime remains nearly flat while decode runtime falls as group size grows" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the chart: measured prefill is nearly flat; decode falls with larger groups, though the shorter KV sequence flattens at large group sizes.*

The figure uses 64 query heads, head dimension 128, prefill batch 1 and decode batch 8, with 32K or 128K sequences. The authors report less than 1% prefill runtime change as G goes from 1 to 64. Decode approximately halves for some doublings of G, but the 32K curve flattens above G=16 as fixed overhead and parallel reduction become more prominent. These are kernel measurements, not equivalent end-to-end serving speedups.

## Head dimension and sequence length

Increasing head dimension increases both compute and KV data but leaves arithmetic intensity unchanged in the simplified model. Based on GPU tiles, 128-byte memory transfers and tensor-memory capacity, the authors suggest head dimensions of 128 or 256. A dimension of 64 may still pay for a wider tile, while 512 approaches capacity limits. These recommendations depend on hardware and kernels and do not replace model-quality evaluation.

With dense attention, prefill work grows approximately quadratically with input length; per-step decode KV reads grow approximately linearly with cache length. Fixed costs cause measured ratios to depart from ideal scaling at short lengths. KV compression, sparse or sliding-window attention, and hybrid architectures can reduce effective state, but alter model or attention behavior and require separate quality assessment.

## KV heads also constrain parallelism

Tensor parallelism shards heads; beyond the number of KV heads, shared KV state must be replicated, potentially increasing memory and bandwidth costs. Larger G helps decode but means fewer KV heads, so this parallelism boundary can arrive sooner. The article discusses combining attention data parallelism or KV parallelism with expert parallelism; the practical gain depends on communication, workload and implementation.

The useful contribution is to place single-device kernel efficiency and multi-device sharding in one design discussion: grouping, sequence length, model quality and deployment topology must be evaluated together.
