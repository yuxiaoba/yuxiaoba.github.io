---
date: '2026-10-01'
lang: en
published: true
layout: article
maintenance: manual
reviewed_on: '2026-10-19'
editorial_status: source-checked
translation_source: assistant-authored paired Chinese/English reading notes
id: lmcache-kv-cache-intro
title: '2026-10-01 | KV Cache and LMCache: From Generation to Reusable Multi-Turn
  State'
source_type: tech
source_url: https://blog.lmcache.ai/en/2026/10/01/intro-to-kv-cache-and-lmcache-part-one/
repo: https://github.com/LMCache/LMCache
organization: LMCache
long_read: true
summary: What KV caches retain, why they grow, and the trade-offs between memory,
  transfer and recomputation.
tags:
- inference-serving
permalink: /tech/en/lmcache-kv-cache-intro/
---
**LMCache · Inference foundations and engineering interpretation · 2026-10-01**  
Original: [Intro to KV Cache and LMCache (Part One)](https://blog.lmcache.ai/en/2026/10/01/intro-to-kv-cache-and-lmcache-part-one/) · [Project](https://github.com/LMCache/LMCache)

## What kind of article this is

This is a conceptual introduction, not a performance report for a new caching algorithm. It explains why attention creates KV state, then motivates LMCache’s state-management problem. The central idea is that retaining already computed intermediate state avoids repeated computation, while consuming memory and incurring matching and movement costs.

Multi-turn agents make the trade-off concrete. System instructions, repository context, and earlier conversation may recur in later calls. Reprocessing an identical prefix wastes GPU work. Keeping every state indefinitely in the fastest memory, however, leaves less room for new requests.

This note combines the article’s explanation with engineering interpretation. Numerical examples below are illustrative calculations, not LMCache measurements.

## The cache contains neither weights nor final answers

In an attention layer, fixed projection weights transform input representations into Queries, Keys, and Values. A new position’s Query is compared with accessible historical Keys, then used to weight their Values. Model weights stay fixed during inference; K/V state depends on request content, token position, and layer.

For standard causal self-attention under matching execution conditions, appending future tokens does not change historical K/V. The next step can reuse that state and append K/V for the new position. The current Query is usually consumed immediately rather than retained like historical K/V.

Matching conditions matter. The same sentence after different preceding text need not produce identical intermediate state. Prefix reuse must also match the model and relevant execution configuration. Semantic similarity is not token-prefix identity. KV caching differs from response caching, which returns an earlier answer to a matching question.

## Prefill and decode share the state

<a class="note-image-link" href="/assets/images/tech/lmcache-kv-cache-intro/prefill-decode.png" target="_blank" rel="noopener" aria-label="Building and extending KV state during prefill and decode · View original image ↗"><img src="/assets/images/tech/lmcache-kv-cache-intro/prefill-decode.png" alt="Building and extending KV state during prefill and decode" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: prefill on the left processes the input and creates per-layer K/V; decode on the right processes a new position, reads existing state, and appends its K/V. The cache below connects both phases.*

Prefill can process known input positions in parallel to establish context state. Decode follows the autoregressive dependency to generate subsequent tokens. Caching avoids rerunning old positions through the model to reconstruct their state; it does not remove the new token’s attention over history.

Consequently, caching does not make every later token equally fast. Under full attention, a growing context still means reading more historical K/V. Batching, scheduling, and memory pressure also affect multi-turn latency; a binary cache-enabled indicator cannot explain all of it.

Observe time to first token, subsequent-token latency, and throughput separately. Avoiding repeated prefill primarily changes the first; cache movement, concurrency, and scheduling may also change the others.

## Where the memory goes

For a standard full-attention model with identical layer configurations, ignoring sharding, quantization metadata, and allocation overhead, one sequence’s KV storage is approximately:

$$M_{KV} \approx 2 L T H_{KV} d_h b$$

Here, 2 accounts for both K and V; L is the layer count, T the cached-token count, H_KV the number of KV heads, d_h the head dimension, and b bytes per stored value. With GQA, use the KV-head count, not the Query-head count.

**Consider a hypothetical configuration:** 24 layers, four KV heads, dimension 128, and BF16 storage. That is approximately 48 KiB per token and 384 MiB for 8,192 tokens. Sixteen independent sequences without sharing would occupy about 6 GiB. These are formula-based estimates excluding weights, activations, communication, and allocator overhead; they do not cover every compressed or specialized attention architecture.

This explains why long context and concurrency jointly consume capacity. Fitting model parameters does not guarantee room for KV state at the desired concurrency. Fewer KV heads, lower cache precision, and shared blocks address different parts of that resource problem.

## From request-local caching to a reusable storage layer

<a class="note-image-link" href="/assets/images/tech/lmcache-kv-cache-intro/storage-tiers.png" target="_blank" rel="noopener" aria-label="GPU, host memory, local storage and remote cache tiers · View original image ↗"><img src="/assets/images/tech/lmcache-kv-cache-intro/storage-tiers.png" alt="GPU, host memory, local storage and remote cache tiers" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: GPU memory is fast and scarce; lower tiers include host memory, local storage, and remote backends. Retaining data in larger tiers means paying movement costs when it is retrieved.*

The article presents LMCache as a way to preserve KV state beyond an immediate GPU allocation, request, or engine process. A storage hierarchy can retain and transfer state so that a later matching request retrieves context instead of rebuilding all of it through prefill.

That does not mean every cache should move to the largest, slowest tier. Hot state may belong nearby; rarely reused state may not justify retention and indexing. Part One mainly establishes this motivation. It does not fully specify coordination, transfer, and storage implementations, so its conceptual diagram should not be read as a complete deployment plan.

## When retrieval is worthwhile

A useful engineering comparison is: **lookup, transfer, and installation should together cost less than the recomputation avoided.** This is reasoning about the design, not a measured performance promise from the article.

For arithmetic illustration, transferring 384 MiB at an effective 8 GiB/s takes about 47 ms before queueing, lookup, and installation. If recomputation took only 20 ms, even a hit would not necessarily help. If it replaced substantially more expensive prefill, the trade-off could reverse. Actual values require measurement on the target hardware, concurrency, and storage tier.

Hit rate also needs a denominator: requests hit, tokens reused, and computation saved measure different things. Frequent hits on short prefixes may save less than fewer hits on long contexts. Hit rate without user-visible latency provides incomplete evidence of an improvement.

## Implications for agent workloads

Agents may repeatedly carry stable instructions and task context, but tool results, history truncation, and prompt reordering can change prefixes. Reuse potential follows actual token structure; belonging to one user session does not make all previous state reusable.

This connects to RETIRE in the same issue. After instructions change, some prefix state may remain valid while obsolete work must lose its authority. A cache hit identifies a performance opportunity; validity determines whether it is safe to use. Both conditions matter. This is a connection between readings, not a claim that LMCache integrates RETIRE.

**Suggested reading order:** understand K/V, prefill/decode, and the memory estimate before consulting integration documentation for a pinned version. Evaluation should cover correctness, cold and warm caches, TTFT, subsequent-token latency, concurrency, throughput, and transferred bytes. No serving benchmark was run for this note, and it does not claim a universal speedup.
