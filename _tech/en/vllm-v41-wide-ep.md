---
id: vllm-v41-wide-ep
title: '2026-10-25 | vLLM at Rack Scale: CPU Costs After Wide Expert Parallelism'
date: '2026-10-25'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: Disaggregated serving, expert balancing, and host overhead for V4.1-Flash,
  with distinct throughput and comparison conditions.
translation_source: assistant
authorship: assistant
long_read: true
source_url: https://vllm.ai/blog/2026-10-23-deepseek-v41-flash-pd-wide-ep
permalink: /tech/en/vllm-v41-wide-ep/
published_at: '2026-10-25T08:48:16.922011+08:00'
updated_at: '2026-10-25T08:48:16.922011+08:00'
---
The most useful part of vLLM's DeepSeek-V4.1-Flash report is how bottlenecks move from one node to a rack. Small KV state makes MoE weight reads a dominant decode cost; wider expert parallelism then exposes CPU scheduling, admission, and transfer overhead. The decomposition is more transferable than a single throughput headline.

Original: [Serving DeepSeek-V4.1-Flash at Scale: vLLM Matches DeepInfer and Scales to GB300 NVL72](https://vllm.ai/blog/2026-10-23-deepseek-v41-flash-pd-wide-ep)  
Inferact and the vLLM Team · 2026-10-23

## What the throughput counts

On GB300 NVL72 with prefill/decode disaggregation and Wide-EP, the authors report 954K tokens/s/GPU on AgentX at P90 196 tokens/s/user. That total includes cached inputs, uncached inputs, and outputs. It measures served workload tokens, not 954K newly generated tokens per GPU each second.

The 7.9× comparison is against the team's previous aggregated single-node deployment, not against DeepInfer. The separate 826 tokens/s result uses four B300 GPUs at concurrency one with a specialized low-latency path, reported as user P90. It cannot be combined with rack throughput into one operating point. The results address capacity and low-concurrency experience separately.

<a class="note-image-link" href="/assets/images/tech/vllm-v41-wide-ep/overview.png" target="_blank" rel="noopener" aria-label="Official vLLM overview of throughput and single-user speed · View original image ↗"><img src="/assets/images/tech/vllm-v41-wide-ep/overview.png" alt="Official vLLM overview of throughput and single-user speed" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Total-token throughput, single-user speed, and DeepInfer comparisons are separate measurements; the lower-left label explicitly includes cached inputs.*

The decode comparison against DeepInfer uses GB200, 131K context, nextn=3, and batch sizes 8–256, staying within 6% of its published curve. Prefill is less directly comparable: DeepInfer's chart does not specify hardware and uses EP4DP4, 32 redundant experts, and 140-token replay; vLLM uses GB300 DEP2, no redundant experts, 128-token replay, and different prompts. The article treats the curves as tracking each other, not as a controlled engine speedup.

## Small prefill instances and wide decode

DEP combines data-parallel attention and expert parallelism. Cross-layer sharing and FP4 compression reduce global KV to about 890 bytes/token. Bounded replay limits later-layer work, and context growth has a modest effect on target forward time. On GB300 DEP32 with 16 requests/rank and six tokens/request, increasing context from 128K to 855K raises target forward from 8.93 to 9.53 ms. This excludes the rest of serving.

Prefill therefore need not widen merely to fit KV. At concurrency 256 in an AgentX prefill-only run, DEP2 reaches 64.4K tokens/s/GPU against DEP4's 53.3K. Mirrored and staggered replays expose greater DP imbalance with DEP4. More resources also create more coordination and waiting.

Decode benefits from distributing expert weights. At 128K context and 64 requests/GPU, scaling DEP4 to DEP32 reduces target MegaMoE time from 13.4 to 6.0 ms, while other work remains near 10 ms. Gains diminish and draft communication begins to offset further expansion. Prefill and decode consequently benefit from different parallelism choices.

## GPU optimization meets expert balancing

Three prefill changes address unnecessary work, address translation, and ranking: restrict layer-20 work other than KV writes to the last 128 tokens; allocate Engram host tables using 2 MB GPU pages to reduce TLB misses; and use DeepSelect top-k in the indexer. With a 128K cached prefix and 32K new tokens, their combined new-token throughput gain is 42.5%. Sequential incremental percentages should not be added directly.

Wide-EP also needs EPLB because the busiest rank constrains the step. Rebalancing every 3,000 steps from the previous 1,000 steps raises target balancedness from 0.35 to 0.94 and draft balancedness from 0.21 to 0.89. Balancedness is mean rank load divided by maximum load. Target and DSpark draft have different expert counts and routing, requiring separate load and placement tracking.

The draft is not automatically negligible. Balancing only the target can leave the draft on the critical path. Shorter GPU work also leaves less time to hide CPU work. Optimization must follow the complete execution loop.

## Why rack scale exposes the CPU

An unoptimized DEP32 step took 17.57 ms against DEP16's 13.84 ms, despite GPU execution being 1.1 ms faster. More synchronized ranks increase the chance that one slow CPU stalls everyone. Fixes address synchronous KV reads, Gloo all-reduce, bursts of request admission, and prompt-length-dependent host work.

They change transfer direction, the CPU collective algorithm, the number of new KV loads admitted per step, and prompt representation. Rows in the effects table use different setups and cannot be multiplied into one total gain. A representative microbenchmark reduces CPU admission time for an 855K prompt from 38.8 to 6.0 ms, showing that even cached long prompts retain host-side costs.

The report demonstrates the potential of a general serving stack incorporating specialized kernels. Its transferable method is to separate GPU forward, engine decode, expert imbalance, and admission before interpreting the final AgentX curve. Architecture, interconnect, cache ratio, and concurrency can move those bottlenecks. The 954K and 826 results retain their own conditions rather than defining a universal capacity promise.

## Controlled replay explains scaling loss

Mirror replay sends identical requests to every DP rank simultaneously. Lag replay sends the same work with ranks staggered by five seconds. Total work remains fixed while alignment changes. With prefix caching disabled, DEP2 instance throughput falls from 138.7K to 130.5K, a 5.9% loss; DEP4 falls from 267.6K to 231.1K, a 13.6% loss. This isolates imbalance more clearly than unrelated random agent traces.

Expert routing uses another control: compare real routing with uniformly random routing for the same decode batch. Uniform routing retains sampling noise. At DEP32 and 72 requests/GPU, target balancedness is about 0.96 and draft balancedness 0.94. EPLB's 0.94 and 0.89 are therefore near that reference; perfect balance of one is not a realistic expectation for every random workload. Nor can expert rearrangement necessarily eliminate the remaining time.

Low latency has a different optimum. On four B300 GPUs at concurrency one, the specialized path improves P90 speed from 575 to 826 tokens/s, approximately 44%. Small batches emphasize fixed per-step costs, while high concurrency emphasizes amortization and aggregate throughput. Multiple execution paths acknowledge these different objectives.

The transferable reasoning sequence establishes GPU stage costs, isolates imbalance, and then locates host and transfer overhead. When a wider deployment slows down, further kernel optimization may miss the cause. Queueing, admission, and synchronization belong in service-level measurement to explain the user's actual benefit.

The measurement path also matters: the authors use the actual execute_model path for GPU forward and DecodeBenchConnector for engine-level decode. Their difference can include request organization, rank coordination, and necessary state management. Reducing that difference is valuable only if the workload and required work remain comparable.

Admission bursts expose another trade-off. Capping new KV loads per step can smooth progress for existing requests while changing queueing for new ones. Decode speed alone cannot establish improvement for every user; first-token and waiting time also matter. This is scheduling interpretation, not a claim that the article quantifies every queueing effect.
