---
id: minimax-m31-serving
title: '2026-10-24 | MiniMax-M3.1-Flash: Low-Precision Cache Across the Serving Stack'
date: '2026-10-24'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: From NVFP4 and sparse indexing to cross-node KV layout, unpacking the systems
  work behind vLLM’s day-zero support.
long_read: true
source_url: https://blog.vllm.ai/blog/2026-10-23-minimax-m31-flash
permalink: /tech/en/minimax-m31-serving/
authoring_source: assistant
translation_source: assistant
published_at: '2026-10-26T11:44:51.392682+08:00'
updated_at: "2026-10-27T13:54:34.510124+08:00"
---
Adding a model to a support list can require coordinated changes to cache formats, dequantization, expert execution, speculative decoding, and communication layouts. vLLM’s MiniMax-M3.1-Flash article illustrates this integration. Native NVFP4 KV training establishes low-precision usability; turning saved bytes into concurrency and speed still requires changes throughout the serving path. [Original: vLLM Delivers Day-0 Support for MiniMax-M3.1-Flash](https://blog.vllm.ai/blog/2026-10-23-minimax-m31-flash).

[MiniMax’s October 19 release announcement](https://www.minimax.io/blog/minimax-m31f) emphasizes long-running agent performance and cost, and describes more aggressive sparsity. It does not disclose the full serving configuration or architecture; the vLLM mechanisms and test conditions below provide the more concrete systems context.

**Inferact and the vLLM Team · 2026-10-23**

## Sparse attention still scans an index

MiniMax Sparse Attention organizes KV into 128-token blocks. A lightweight indexer scores context, selects 16 blocks, and retains the most recent block. Main attention then works over roughly 2,048 keys per query. The indexer still scans history: long-context work shifts from large K/V reads toward smaller index reads rather than disappearing.

For FP8 with four KV heads of dimension 128, the article compares 128 index bytes per token per layer with 1,024 dense K/V bytes. This favors bandwidth-bound decode and makes indexer parallelism independently valuable. Exact attention over selected blocks is not equivalent to full dense attention.

## Capacity savings must pay for conversion

NVFP4 routed experts shrink the checkpoint from M3-MXFP8’s 451.5 GB to 250.1 GB, or 44.6%. KV storage falls from 61,440 FP8 bytes per token to 34,560 bytes, saving 43.75%. On four B300s with DEP4 and 256K sequences, estimated capacity increases from 28 to 76 concurrent sequences, about 2.7×. This configuration-specific capacity result is not a universal throughput multiplier.

Blackwell queries remain FP8, so kernels convert NVFP4 KV to FP8 before matrix multiplication. Specialized instructions combine scaled conversions and avoid an FP16 round trip. The authors report up to 1.7× indexer QK decode and 1.3× sparse-attention decode kernel speedups. Storage savings become serving gains only after conversion and scheduling overhead.

## Reduce both data movement and resource waits

NVFP4 MegaMoE releases a Tensor Memory stage early once the FC1 epilogue has moved accumulators into registers. The article reports 20% lower prefill kernel latency and 7% higher overall prefill throughput. These are different measurement levels, not interchangeable end-to-end gains.

A fused QKV projection, normalization, RoPE, and cache insertion path also avoids writing and rereading the full intermediate tensor from HBM. On GB300 at TP4, the reported median TTFT falls by about 19%. Faster arithmetic can make intermediate storage and resource lifetimes the next bottlenecks.

## Parallelize index work across context

At TP4, independently scanning the full index cache creates four copies of the read traffic. Indexer DCP instead assigns a quarter of the context to each GPU, computes the relevant heads, exchanges local candidates, and merges final top-16 selections. This redistributes selection work while preserving exact selection in the described implementation.

On four GB300s at 512K context, the indexer reaches up to 3.3× per-sparse-layer speedup. AMD similarly shards context and uses multiple heads and speculative queries to better fill matrix-unit shapes. The gain depends on request count, context length, and hardware execution shape; repeated bandwidth and underutilization need separate diagnosis.

## AMD uses different conversion and communication mechanisms

Without the same NVFP4 conversion instruction, CDNA4 uses a small lookup table of scaled values and sign handling. Shared prefixes reduce repeated dequantization across requests. Sequence parallelism reduces prefill communication, while dual-batch overlap hides remaining communication behind another microbatch.

Cross-node layout matters too. The previous layout splits a KV block across 125 pages and multiple NIXL RDMA reads. A block-outer layout stores it as one contiguous approximately 1.82 MB row for a single read. Combined engine and transfer changes accelerate 16K-plus prefill batches by 1.8–2.1× on four MI355Xs. Low concurrency has a separate mono-kernel strategy for reducing launches; one kernel arrangement need not suit every regime.

## Preserve speculative conditions on AgentX results

The GB300 frontier includes a low-latency point at 418.9 tokens/s/user and a high-throughput point at 153.8K total tokens/s/GPU with roughly 127 tokens/s/user. These are different operating points and cannot be combined into one configuration. The figure uses seven speculative tokens and synthetic acceptance lengths of 3.16–3.26, not naturally observed DSpark acceptance rates.

The AMD chart measures total tokens per dollar of TCO rather than NVIDIA’s per-GPU throughput, and points use different acceptance lengths and speculative settings. Comparisons should match latency objectives and account for actual traffic, acceptance, cache reuse, and hardware cost rather than selecting maxima across incompatible axes.

A separate RL experiment uses a low-precision base with rank-32 LoRA. On 16 GB300s, DAPO-Math-17K, and 200 GRPO steps, AIME-2024 accuracy rises from 36.3% to 67.5%. This is training evidence, not quality improvement from faster serving kernels. The mechanism figures are interactive; the static hero does not explain data flow and is therefore omitted.

## The same format can use different execution paths

Cross-hardware comparisons need care: one low-precision format can require different conversion and matrix-multiply paths. Blackwell uses specialized conversion instructions, AMD uses lookup tables, and Rubin uses different precision and resource arrangements. Model and storage representation are shared, while kernels are rebalanced for hardware. Portability must preserve numerical behavior, selection logic, and state layout rather than copying an instruction schedule.

Speculation also changes query batches and kernel shapes. Faster drafting can reduce part of latency, but acceptance and verification work determine net benefit. Synthetic acceptance makes systems comparisons more controlled while holding real prediction quality fixed. Assessing application benefit requires restoring that variable and observing how it changes with task, context, and sampling behavior.

## Keep capacity, layer, and system results separate

Capacity describes how much state fits; kernel results describe a particular operation; serving frontiers describe the exchange between user speed and system throughput under load. These are not multipliers that can simply be multiplied. Added concurrency consumes saved capacity and can shift the bottleneck to indexing, communication, or scheduling. Reducing launches at low concurrency need not retain its advantage at high concurrency.

Read the article in data-flow order: cache representation, kernel inputs, intra-node and cross-node reconstruction, then benchmark curves. This helps match changes to actual bottlenecks rather than choosing deployment configurations from a precision label or peak number. The engineering is compositional, not evidence of one optimal configuration across all hardware and workloads.
