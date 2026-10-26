---
id: glm53-context-parallel
title: '2026-10-24 | GLM-5.3 Long Context: Splitting Query Work and KV Capacity'
date: '2026-10-24'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: Understanding PCP, DCP, and Hybrid HiSparse on 16 H200s, including communication
  costs and benchmark conditions.
long_read: true
source_url: https://blog.vllm.ai/blog/2026-10-23-glm53-part2-pcp-dcp-hisparse
permalink: /tech/en/glm53-context-parallel/
authoring_source: assistant
translation_source: assistant
published_at: '2026-10-26T11:44:51.392682+08:00'
updated_at: '2026-10-26T11:44:51.392682+08:00'
---
Long agent contexts pressure both prefill computation and KV capacity. Adding GPUs does not automatically solve both. vLLM’s second GLM-5.3 optimization article separates query work, persistent KV placement, and decode storage across two eight-H200 nodes. The central distinction is that PCP splits queries, DCP splits KV, and Hybrid HiSparse changes decode-side storage. [Original: GLM-5.3 Optimizations, Part 2: PCP, DCP, and Hybrid HiSparse on 16 H200s](https://blog.vllm.ai/blog/2026-10-23-glm53-part2-pcp-dcp-hisparse).

**vLLM Team · 2026-10-23**

## What DP and TP leave unresolved

DP8 assigns a prompt to one GPU, leaving its attention work and KV capacity constrained by that device. TP8 splits attention heads, but MLA shares latent KV across heads, so each GPU retains the full cache. Each serves fewer heads while repeating the indexer’s historical-token scan.

Sparse MLA attends to 2,048 selected tokens per query, while the indexer still scans history to select them. Over a full prefill, the former grows approximately linearly and the latter quadratically with context length. Head parallelism does not automatically remove indexing work or turn replicated KV into pooled capacity.

## PCP distributes queries

PCP8 assigns one eighth of a prompt’s queries to each GPU, with all 64 heads. Causal attention makes later tokens more expensive, so the implementation divides the prompt into 16 chunks and pairs early and late chunks to balance work.

Each GPU indexes only its queries, and each fetched KV row serves more heads. The article estimates sparse-MLA arithmetic intensity increasing from about 26 to 191 FLOPs/byte. But each layer all-gathers new KV, leaving every GPU with the full persistent cache. Computation distribution therefore still needs a capacity solution.

## DCP saves persistent capacity at a communication cost

A 1M-token request requires roughly 53.4 GiB of FP8 KV, versus about 15 GiB available per GPU. DCP8 distributes tokens round-robin, reducing persistent storage to about 6.7 GiB per device. Despite its historical Decode name, DCP runs alongside PCP in this prefill engine.

<a class="note-image-link" href="/assets/images/tech/glm53-context-parallel/mechanism.png" target="_blank" rel="noopener" aria-label="Tokens are sharded round-robin above; bars compare per-GPU persistent KV under DP, TP, and PCP×DCP against the available capacity."><img src="/assets/images/tech/glm53-context-parallel/mechanism.png" alt="Tokens are sharded round-robin above; bars compare per-GPU persistent KV under DP, TP, and PCP×DCP against the available capacity." loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Tokens are sharded round-robin above; bars compare per-GPU persistent KV under DP, TP, and PCP×DCP against the available capacity.*

Persistent sharding does not mean attention reads only a local eighth of the context. Each prefill layer all-gathers shards into a temporary full-context copy, computes its queries, and frees that copy. For the same 2K-token prefill chunk, DCP8 adds about 6% per-step overhead through 64K cached tokens and about 15% at 248K. The larger persistent pool is not free.

## Decode needs its own storage strategy

The 16-H200 deployment uses PCP8×DCP8×EP8 prefill with 512 GiB of CPU KV offload. Decode has eight DP ranks with EP8, each using a 48 GiB HiSparse host pool plus 16 GiB offload, also totaling 512 GiB. Prefix-aware routing feeds prefill; NIXL transfers and reassembles KV.

Comparisons hold GPU count, host memory, and vLLM build fixed while changing prefill parallelism and decode caching. Integration must transform token-sharded prefill KV into a decode rank’s complete paged layout, including MTP state, while retaining correct prefix reuse.

## Understand the token denominator

AgentX replays Claude Code traces with prefix reuse, fresh servers for each concurrency, and one-hour runs. All configurations use MTP3 with synthetic acceptance length fixed at 2.99. Throughput counts logical input plus output tokens, including cached input, across all 16 GPUs. Interactivity is P90 end-to-end-normalized output tokens per second per user. Total throughput is therefore not newly generated output throughput, nor evidence of real drafter acceptance at that level.

In the mostly prefill-bound range, with HiSparse decode held fixed, PCP8×DCP8 delivers 1.7–3.2× DP8’s interactivity at matched throughput. Median TTFT falls from 1.5–5.2 seconds to 0.8–0.9 seconds. Decoder differences are small at low concurrency, and offload-only is slightly faster at c8; benefits are not uniform at every operating point.

## Million-token support requires the combination

Decode pressure rises from c32. At c64, the combined system reaches 8,340 logical tokens/s/GPU and 29.6 tokens/s/user, while other configurations fall to 1–2 tokens/s/user. At 1M context, both ends need sufficient capacity: neither DP8 prefill nor an offload-only decode rank can hold one such request.

The result supports composing mechanisms around measured bottlenecks rather than choosing one universal parallelism flag. Capacity planning must include persistent KV, temporary gathers, interconnect traffic, and decode host pools. Communication overlap remains future work. Read layout transformations and benchmark definitions first to judge suitability for a target context and concurrency regime.

## Layout correctness precedes combined speedups

Each optimization changes ownership of state. Query chunks and KV-token shards do not align, so a local block table alone cannot establish that a GPU has all required context. Layer communication, temporary-copy release, and cross-node reconstruction must each respect data dependencies. Composability adds state-management contracts alongside performance gains.

A useful analysis starts with one request’s state lifetime and the maximum simultaneously live copies. Eightfold lower persistent storage describes only residency; temporary full-context copies, transfer buffers, and other runtime state still need space. Equal host-offload capacity likewise does not imply equal latency, because reuse, movement, and queueing differ.

## Choose the operating point that matters

Mostly short-context, low-concurrency traffic may not benefit first from trading communication for capacity. When one request exceeds a device’s capacity, however, memory mechanisms determine feasibility before speed. Small decoder differences at low concurrency and larger HiSparse gains at high concurrency illustrate this shift.

Evaluate fixed traces and hardware while retaining TTFT, user-visible generation rate, and logical system throughput. An optimization can move the bottleneck from prefill to decode, preventing continued linear gains. A frontier across concurrency levels is more useful than one maximum-throughput point.

These are engineering deductions from the reported resource relationships, not additional measurements. They help distinguish capacity, interconnect, and execution bottlenecks instead of attributing every long-context problem to insufficient HBM.

The measured commit differs from the commit pinned by the reproduction script. Implementation version is another experimental condition; feature availability alone does not establish the reported performance.
