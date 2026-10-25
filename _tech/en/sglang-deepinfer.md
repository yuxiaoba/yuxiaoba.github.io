---
id: sglang-deepinfer
title: '2026-10-25 | SGLang and DeepInfer: Bounded Replay and a Complete Serving Stack'
date: '2026-10-25'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Kernel fusion, Engram placement, and cache restoration, with conditions behind
  up to 1.04× prefill and 7.4% shorter decode steps.
translation_source: assistant
authorship: assistant
long_read: true
source_url: https://www.lmsys.org/blog/2026-10-24-dsv41-deepinfer
permalink: /tech/en/sglang-deepinfer/
published_at: '2026-10-25T08:48:16.922011+08:00'
updated_at: '2026-10-25T08:48:16.922011+08:00'
---
SGLang's follow-up to DeepInfer connects fast model execution with a complete serving system. It compares core execution on the same hardware, then explains how caching, prefill/decode disaggregation, routing, and output parsing support a service. The link between these layers is useful, provided microbenchmarks remain distinct from production workloads.

Original: [More Than DeepInfer: What SGLang Delivers](https://www.lmsys.org/blog/2026-10-24-dsv41-deepinfer)  
The SGLang Team · 2026-10-24

## Kernels still need state management and scheduling

The integration includes FlashMLA, DeepGEMM, DeepEP, DeepSelect, TileLang, and the Mega series. MegaMoE fuses dispatch, expert GEMMs, and combine; MegaAttention becomes the default attention path on B300 and GB300. Other changes feed Mega-mHC output directly to MegaMoE and produce MXFP8 attention output for projection.

They reduce intermediate traffic and launch gaps, with benefits dependent on model shapes and hardware. DSpark reduces target forward passes by proposing a block for joint verification; real gains still depend on acceptance.

The scheduler overlaps CPU preparation of the next step with GPU execution of the current step. This hides work that fits within the overlap window. If host work exceeds that window, waiting can remain. “Zero-overhead” is best understood as the scheduling design rather than a guarantee for every workload.

## Two kinds of replay

Decoder replay lets early source layers process the full prompt while later layers process only its final 128 tokens. Encoder replay addresses a different condition: a prefix-cache hit with missing sliding-window KV. It reconstructs that window from the final 128 cached tokens.

<a class="note-image-link" href="/assets/images/tech/sglang-deepinfer/bounded-replay.png" target="_blank" rel="noopener" aria-label="SGLang decoder and encoder bounded replay · View original image ↗"><img src="/assets/images/tech/sglang-deepinfer/bounded-replay.png" alt="SGLang decoder and encoder bounded replay" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Top: late layers process only the final 128 tokens. Bottom: a prefix hit is followed by reconstruction of missing sliding-window state.*

One reduces late-layer work during long prefill; the other restores state omitted from the cache. A hybrid-model cache hit does not simply skip everything. The retained states and those recoverable from a short suffix determine the remaining computation.

CUDA graphs follow the same boundary. Breakable graphs cover prefill up to 8K tokens/GPU, while late replay uses separate bounded graphs. The late layers can retain graph execution even when the rest of a large prefill runs eagerly. Model structure therefore shapes execution scheduling directly.

## Engram placement trades capacity for access

Host placement keeps one Engram table copy per node, preserving more HBM for KV. Device placement shards tables across GPUs and reads needed rows directly through NVLink, avoiding all-gather or reduce-scatter around lookup.

Device access benefits must be weighed against HBM use, and host capacity benefits against access costs. The article does not establish one universally optimal choice. Placement also matters when interpreting the comparison because some tests use different locations in the two engines.

## Results and remaining configuration differences

Prefill uses the same four-GPU node, weights, DP4/EP4, balanced expert routing, EPLB disabled, and 32 redundant experts. Requests have 128K context and 4K new tokens; each GPU processes 4K–64K new tokens per step. SGLang reaches up to 1.04× measured DeepInfer throughput on both GB300 and B300, with other points approximately equal.

DeepInfer's fastest tested Engram configuration is selected at each point. Measurement still differs: DeepInfer times about nine batches on GPU 0; SGLang averages complete batches on every GPU between 20% and 90% request completion. DeepInfer repeats a prompt, while SGLang uses different new tokens per request. These conditions should accompany a gain of a few percent.

Decode uses 64 GB300 GPUs across 16 nodes, DP64/EP64, 128K shared-prefix contexts, three draft tokens per step, static full-block verification, and balanced expert routing. Steps are 1.1%–7.4% shorter at 16–256 requests/GPU and approximately equal at eight. The chart converts time to throughput using 3.25 accepted tokens/step; that is not a separate measured online acceptance rate.

SGLang keeps Engram on device while DeepInfer uses host memory. DeepInfer's draft has 64 redundant experts; SGLang's draft has none. Published commits and launch commands improve traceability, but these comparison settings are not production recommendations.

## Completing the service

A unified radix cache reuses state across requests and turns. The illustrated Linker path connects GPU L1 directly to shared L3 storage; HiCache also supports an optional host-memory L2. P/D disaggregation offers Mooncake, NIXL, or MORI transfer, while the model gateway distributes requests across replicas with cache-aware routing. DeepSeek's format package handles prompt rendering and reasoning/tool-call parsing, alongside structured-output constraints.

These components explain why an offline execution curve cannot describe the full value of an API service. They also introduce configuration and failure surfaces. Cold and warm caches, request distributions, and tail latency remain relevant. Read the replay and Engram mechanisms, then the benchmark appendix, before the headline. The report supports near-specialized execution performance inside a general serving stack, while leaving target-workload end-to-end evaluation necessary.

## Distinguish the lines in the results figure

Solid curves represent measurements; dashed curves are read from DeepInfer's earlier published charts. The textual prefill ratios use measured DeepInfer on the same hardware, not a selectively chosen older curve. Published charts provide context, while same-machine measurements better support differences of a few percent.

Static verification makes every request verify a complete draft block, removing variation from actual rejection positions. Balanced routing reduces expert hotspots. Both stabilize execution-cost comparisons while excluding some production difficulties. Real traffic changes draft quality, context lengths, and expert skew together, potentially changing service-level rankings.

There are two evidence layers: measured forward/step performance with commits and configurations, and the presence of caching, gateway, and disaggregation capabilities. The latter establishes functionality but is not separately quantified by the same benchmark plot. Keeping the layers distinct avoids turning a feature list into an end-to-end result.

A subsequent engineering evaluation could hold arrivals fixed while varying cache hits and input/output lengths, observing first-token and subsequent-token latency along with rejection or retry behavior. That is a proposed follow-up, not an additional result reported by the authors.

Cache-tier names do not define every request's read path. Direct shared-storage access is one configuration, while an optional host tier is another deployment choice. Reuse distance, transfer costs, and available memory determine suitability.
