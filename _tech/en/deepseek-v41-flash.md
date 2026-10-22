---
id: deepseek-v41-flash
title: '2026-10-07 | DeepSeek-V4.1-Flash: Replay and Kernel Optimizations Behind Fivefold
  Throughput'
date: '2026-10-07'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: How bounded SWA replay, CUDA graphs, fused kernels, and parallelism contribute
  to AgentX improvements, and under what conditions.
long_read: true
source_url: https://blog.vllm.ai/blog/2026-10-07-deepseek-v41-flash
permalink: /tech/en/deepseek-v41-flash/
authorship: assistant
translation_source: assistant
published_at: "2026-10-20T09:29:16.460712+08:00"
updated_at: "2026-10-20T09:29:16.460712+08:00"
---
The interesting development in vLLM’s DeepSeek-V4.1-Flash support is the joint optimization of model structure and serving implementation. The official article reports roughly 1.9× better low-concurrency interactivity and 5.3× higher throughput than the day-zero implementation. The changes span reduced prefill work, cache representation, CUDA graphs, kernel fusion, and parallelism. Understanding the multipliers requires following the execution path.

Original: [DeepSeek-V4.1-Flash on vLLM: 5x Agentic Throughput Since Day 0](https://blog.vllm.ai/blog/2026-10-07-deepseek-v41-flash)  
Inferact and the vLLM Team · 2026-10-07

## Two caches, two different costs

V4.1’s causal encoder-decoder architecture activates 16B parameters per token during decode and 8B during prefill. Global KV uses compression, FP4 storage, and sharing across layers, requiring about 890 bytes per token. Sliding-window attention (SWA) instead retains uncompressed FP8 KV for the last 128 positions in each of 40 layers. A small global cache does not make the entire prefix cache inexpensive.

Saving SWA state at every possible prefix-hit boundary costs more than ten times the storage of global KV. Meanwhile, the previous prefill path runs layers 21–39 on every prompt token, although decode reads only those layers’ last 128 positions. Much of that long-prompt work does not directly survive in the usable window. Excess cache storage and excess computation are related but distinct problems.

## Bounded replay trades exactness for space and compute

Recomputing SWA can save storage, but an exact rebuild has dependencies across layers. Each upper-layer window depends on earlier positions below it, requiring roughly L×128 replay tokens across L layers. Bounded replay processes only the last 128 tokens and clips each layer’s window at the replay start. The result is not bit-exact. This is an approximation with a quality trade-off, not merely a change in storage placement.

On the encoder side, a prefix hit of length H retrieves only cached global KV and replays [H−128, H) to rebuild SWA. One window of computation replaces retained cache state. On the decoder side, layer 20 produces global KV that layers 21–39 share. Layer 20 still processes every token, but the later layers process only the last window. Long prompts therefore skip nearly half the model’s prefill work.

The two sides have different benefits. Replaying after a hit adds computation; direct time savings mainly come from decoder trimming. The default-enabled path is controlled by `--[no-]swa-bounded-replay`. On benchmarks including GSM8K and GPQA, the article reports accuracy gaps within about 1.5 standard errors. This supports small differences on those evaluations, not equivalence for every long-horizon agent task.

## Less computation can expose launch overhead

After trimming, layers 21–39 perform little GPU work. Launching their kernels individually can cost more than the computation saved. Their input shapes also differ from the first part of the model, preventing a straightforward single CUDA-graph capture. vLLM uses its breakable PIECEWISE graph to capture the full batch for layers 0–20 separately from the trimmed batch for later layers, with independent capture sizes.

The single-request prefill experiment uses NVIDIA GB200, disables prefix caching, and reports medians of three runs. Replay with CUDA graphs reduces prefill computation time by about 30–40%. Without decoder graph capture, the DEP2 configuration at a 1K prompt can be up to about 12% slower than replay disabled. Less arithmetic does not guarantee proportionally less waiting; short prompts especially depend on controlling launch overhead.

## Fuse kernels and shorten the actual critical path

Another set of changes removes intermediate writes and repeated launches. Mega-mHC combines post, delayed-pre, and RMSNorm operations, running 1.14–1.51× faster than the previous TileLang path on GB200. Mega-Gate combines router matrix multiplication, scoring, bias, and top-k, delivering 1.18–1.31× kernel speedups at medium batch sizes. These are local measurements and cannot be multiplied into a whole-system speedup.

The sparse indexer scores only a fixed set of 16K candidate positions instead of scaling with the full context. On GB300, the per-layer speedup at 512K context reaches 14–23×, while end-to-end decode on four GB300 GPUs improves 3–6%. The gap is informative: the optimized operation occupies only part of the execution chain, and other stages still take time.

MegaAttention fuses RoPE, sparse attention, inverse RoPE, and FP8 casting, writing directly into the buffer consumed by the following projection. Its new NVFP4 compressed KV format is 45% smaller than the previous FP8 format. For small batches, mHC coefficient computation also moves to a side CUDA stream, overlapping attention/FFN work and reducing latency by about 4% in the TP4 low-latency scenario. These changes target data movement, cache capacity, and the critical path separately; their value changes with load.

Engram exposes another bottleneck. It looks up a few rows in two large FP8 tables using hashed token n-grams, making lookup latency and table placement more important than bulk arithmetic. vLLM asynchronously prefetches CPU-offloaded entries while decode proceeds; colocated data-parallel replicas share tables to avoid duplication. Transparent huge pages reduce related memory-management overhead, with the article reporting up to tenfold acceleration of prefill lookup kernels. That result again concerns the lookup path, not an entire agent turn.

These details show why fusion is not an unconditional instruction to combine every operator. Some work benefits from retaining intermediates within one kernel, some can run independently on a side stream, and some needs advance retrieval from host memory. Choosing a path requires knowing when dependencies are satisfied, whether compute or memory access dominates, and whether overlap remains possible at the target batch size.

## Low latency and high throughput favor different configurations

<a class="note-image-link" href="/assets/images/tech/deepseek-v41-flash/agentx-results.png" target="_blank" rel="noopener" aria-label="Day-zero and optimized throughput versus P90 interactivity on GB300 NVL72 · View original image ↗"><img src="/assets/images/tech/deepseek-v41-flash/agentx-results.png" alt="Day-zero and optimized throughput versus P90 interactivity on GB300 NVL72" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Compare vertically at a fixed user generation rate for per-chip throughput; compare the rightmost endpoints for peak interactivity. The figure’s 5.3× annotation is at about 155 token/s/user, while the prose summarizes a 150 TPS constraint.*

The official AgentX plot compares optimal configurations on September 11 and October 2 on GB300 NVL72. At about 155 token/s/user P90 interactivity, per-chip throughput rises from approximately 27K to 144K token/s. Peak interactivity rises from 311 to 599 token/s/user. The two arrows compare different objectives, not simultaneous gains at one operating point.

The low-latency configuration uses TP4 and FlashInfer attention, spreading weights across four GPUs for memory-bandwidth-bound small-batch decode. The high-throughput configuration switches to DEP2, using data-parallel attention with experts split across GPUs. Each GPU stores KV only for its own requests, avoiding duplication under tensor parallelism. Session affinity preserves prefix locality across turns, and MegaAttention’s NVFP4 representation increases concurrency capacity further.

<a class="note-image-link" href="/assets/images/tech/deepseek-v41-flash/ttft-vs-throughput.png" target="_blank" rel="noopener" aria-label="Per-chip throughput versus P90 time to first token on GB300 NVL72 · View original image ↗"><img src="/assets/images/tech/deepseek-v41-flash/ttft-vs-throughput.png" alt="Per-chip throughput versus P90 time to first token on GB300 NVL72" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*At fixed throughput, moving left means less waiting. The annotation near 94K token/s/chip shows 1.86→0.32 seconds, about an 83% reduction. The prose describes nearly 70% around 100K throughput; the comparison points should remain distinct.*

## Interpreting the serving-level gains

P90 interactivity is measured in tokens per second per user, time to first token in seconds, and throughput separately normalized per chip. They answer different questions: how fluid generation is, how long the initial wait lasts, and how much work the hardware handles overall. A high-throughput point can mean longer waits per user. Comparisons should therefore hold an interactivity or latency objective fixed before evaluating supported load.

The single-request experiment with prefix caching disabled primarily shows the computational effect of trimming and graph capture. Multi-turn AgentX also involves prefix locality, capacity, and scheduling. These evidence types complement each other, but a median over three single-request runs cannot stand in for tail experience in the serving workload. Nor can local kernel multipliers measured on different hardware be assembled into one prediction. The useful question is how these paths change across short prompts, long contexts, and concurrency ranges.

These results combine configuration changes and multiple optimizations, rather than isolating one switch. The article also says no KV offloading is needed throughout this benchmark. Benefits from offloading at higher concurrency with prefill/decode disaggregation remain an expectation for future work. Replay dependencies, graph boundaries, and configuration choices are the best reading priorities: they explain why model-level opportunities to save compute need compatible cache management and execution scheduling before they become serving throughput.
