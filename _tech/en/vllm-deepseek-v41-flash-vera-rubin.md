---
id: vllm-deepseek-v41-flash-vera-rubin
title: '2026-11-13 | vLLM on Rubin: memory locality and rack-wide sharing'
date: '2026-11-13'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Separate total throughput including cached input, per-user decode and kernel
  profiling to understand three layers of Rubin optimization.
long_read: true
source_url: https://vllm.ai/blog/2026-11-12-deepseek-v41-flash-vera-rubin
permalink: /tech/en/vllm-deepseek-v41-flash-vera-rubin/
translation_source: assistant
authorship: assistant
source_published_at: '2026-11-12'
published_at: '2026-11-13T08:46:43.062448+08:00'
updated_at: '2026-11-13T08:46:43.062448+08:00'
---
Inferact and the vLLM Team · 2026-11-12  
Original: [DeepSeek-V4.1-Flash on Vera Rubin NVL72: 58x Throughput vs. GB300 NVL72 at 387 tokens/s](https://vllm.ai/blog/2026-11-12-deepseek-v41-flash-vera-rubin)

vLLM's Rubin report extends optimization from kernels to rack-wide state: keep bandwidth-bound reads local within a GPU, share KV and Engram tables across the rack, and remove session affinity from routing. Its throughput claims require the AgentX workload and cache-counting convention to remain visible.

## Three different performance quantities

The reported 1.7 million tokens/s/GPU and 58× comparison with GB300 NVL72 count **cached input, uncached input and output together**, at 387 tokens/s per user. They do not mean 1.7 million newly generated tokens per GPU-second. Peak total throughput of 2.52 million and maximum single-user speed of 1,810 also describe different operating points, not simultaneous service properties.

The low-latency path uses TP8 across two compute trays; 1,810 tokens/s at batch one is labeled P90. The text separately reports single-session AgentX P50 rising from 1,117 to 1,844 with fixed DSpark acceptance of 3.51. Percentiles, acceptance, parallelism and concurrency all matter. The mechanisms below are more transferable than a combined headline number.

## Place data near the SMs that read it

Each Rubin GPU has two memory domains. Domain-local reads are faster than interleaved or remote-domain reads. For bandwidth-limited decode expert GEMMs, vLLM splits weights by output columns and assigns local tiles to each domain's SMs. Prefill mHC residual work similarly uses per-domain task counters, draining local work before helping the other side.

Another change handles DP imbalance. An idle rank must not choose tiny MegaMoE tiles solely from its local token count because its experts may serve the busy rank. Using the larger of local and DP-average counts cuts MegaMoE time by 55% in a forty-step replay. Local batch size can misrepresent actual local expert work.

SM107's K64 FP8×FP4 MMA does more work per instruction, while packed FP4 permits more weight-loading stages in the low-latency path. Attention prefetches indices and KV earlier to keep tensor cores issuing. Together, changes reduce a 32K-token/rank DEP2 prefill step by about 28%. Individual kernel improvements cannot be added into a rack-level multiplier.

## Shorten dependencies instead of waiting globally

Wide-EP dispatch issues remote loads early to reduce NVLink round trips per token. Combine buffers use a sentinel that valid outputs cannot take, letting CTAs wait for their own GEMM results rather than a global barrier. mHC keeps the Post, route collapse and RMSNorm needed by the next layer on the critical path, moving later mixes onto a side stream.

The roughly 25% DEP32 decode target-forward reduction is measured against an earlier Rubin build using a four-GPU-node simulation, twenty requests times six tokens per rank and DSpark k=5. It is not a 25% end-to-end latency reduction for every rack request. The TP8 low-latency path uses different optimizations, including fused post-all-reduce processing and reserving SMs for side work; its evidence is not interchangeable with Wide-EP profiling.

## Shared state removes a routing constraint

Per-rank CPU caches and session pinning can leave one rank queued while another is idle, and fail to retain enough live prefixes at higher concurrency. Mooncake pools rack DRAM and experimentally adds spare HBM, letting any prefill rank load prefixes over RDMA. Two 94.4 GiB Engram tables are instead sharded in GPU HBM and read over NVLink. **KV-pool RDMA and Engram NVLink are distinct paths.**

Once cache location no longer pins sessions, Dynamo routes by uncached work. On three DEP2 instances at concurrency 4,800, pools plus routing increase requests/s by 68%, reduce TTFT P50 from 29.8 to 4.2 seconds and raise hit rate from 91.8% to 96.1%. The larger 12 × DEP2 result is simulation: time spent idle while another rank queues falls from 10.3% to 1.3%. These are different scales and evidence types.

The source's core diagrams are interactive pages; this note retains a textual explanation rather than substituting a cover image. The transferable observation is that faster compute changes cache-capacity and queueing bottlenecks. Locality, asynchronous loading and routing must evolve together to translate hardware speed into user experience. Results concern DeepSeek-V4.1-Flash, AgentX and a particular rack; the HBM pool remains experimental, and equal gains are not established for arbitrary models or low-hit workloads.
