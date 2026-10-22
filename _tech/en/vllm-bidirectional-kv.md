---
id: vllm-bidirectional-kv
title: '2026-10-12 | Bidirectional KV Transfer in vLLM: Returning Multi-Turn Context
  to Prefill'
date: '2026-10-12'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: How decode-to-prefill reuse, router metadata, retention, and recomputation
  thresholds reduce TTFT when the local prefill cache misses.
long_read: true
source_url: https://blog.vllm.ai/blog/2026-10-12-bidirectional-kvxfer-multiturn-agentic-workload
permalink: /tech/en/vllm-bidirectional-kv/
translation_source: assistant-authored paired Chinese/English synthesis; English translation
  by assistant
published_at: "2026-10-20T10:16:04.808002+08:00"
updated_at: "2026-10-20T10:16:04.808002+08:00"
---
Multi-turn agents send growing histories with each model request. Separating prefill from decode allows independent compute configurations but also separates cached state: decode may already hold KV for the previous response while the next prefill recomputes it. This vLLM article introduces a reverse path from decode to prefill, alongside the cross-turn lookup, retention, and recomputation decisions needed to use that path.

Original: [Improve TTFT for Multi-Turn Agentic Workloads with Bi-Directional KV Transfer in vLLM](https://blog.vllm.ai/blog/2026-10-12-bidirectional-kvxfer-multiturn-agentic-workload)  
Sunita Nadampalli (AWS) · vLLM Blog · 2026-10-12

## Why one-way transfer still repeats computation

In the conventional P→D flow, prefill computes input KV, then decode retrieves those blocks and generates the response. Decode finishes with state for both the input history and newly generated content. On the next turn, that response becomes part of the prompt, but prefill lacks a reverse read path and must recompute it. If its local prefix has been evicted, or routing selects another prefill node, it may recompute the whole conversation.

Bidirectional transfer addresses previously computed state residing elsewhere. It does not eliminate computation for new tool results or ensure perpetual session-wide hits. Benefit depends on whether reusable blocks survive and whether retrieving them is cheaper than recomputation.

## How one generation leaves an entry point for the next

<a class="note-image-link" href="/assets/images/tech/vllm-bidirectional-kv/kv-connector-enhancement-blocks.png" target="_blank" rel="noopener" aria-label="vLLM bidirectional KV architecture: the router carries metadata and prefill retrieves reusable blocks from decode · View original image ↗"><img src="/assets/images/tech/vllm-bidirectional-kv/kv-connector-enhancement-blocks.png" alt="vLLM bidirectional KV architecture: the router carries metadata and prefill retrieves reusable blocks from decode" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Follow the red numbers: decode retains blocks and reports their location, the router preserves that metadata across turns, and prefill retrieves missing blocks after checking local hits. Blue marks the existing P→D path.*

The extended NIXL connector allows prefill to consume remote KV, with NIXL READ serving both directions. Decode supplies only blocks it already caches; prefill remains responsible for new content and unavailable suffixes. A later request first performs local prefix matching, then checks whether the remaining remotely reusable tokens meet the threshold. If so, it queues an asynchronous receive before computing the suffix.

A stateful router connects the turns. It maps the client-provided `conversation_id` to decode's `kv_transfer_params`, including block-location information. Metadata arrives in the response stream without an extra query. KV tensors move between the compute nodes, bypassing the router. A first-turn miss follows the ordinary flow and saves decode metadata at the end; later turns retrieve that entry and refresh it after generation.

<a class="note-image-link" href="/assets/images/tech/vllm-bidirectional-kv/router-conversation-kv-flow.png" target="_blank" rel="noopener" aria-label="Request sequences among the router, prefill, and decode for first-turn misses and later-turn hits · View original image ↗"><img src="/assets/images/tech/vllm-bidirectional-kv/router-conversation-kv-flow.png" alt="Request sequences among the router, prefill, and decode for first-turn misses and later-turn hits" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*The upper panel establishes first-turn metadata. The lower panel adds a D→P read before the next prefill; purple arrows show that large KV transfers bypass the router.*

The engineering implication is that request forwarding and cache-location management become interdependent responsibilities. Enabling the connector alone is insufficient: without streaming metadata, the router has no entry point for the next turn. The article supplies an example proxy; its sequence diagram does not establish support for arbitrary concurrent branches or proxy failure recovery.

## Reuse depends on valid control information

The conversation ID locates candidate state; actual reuse still depends on local matching and remote availability checks. A shared ID does not mean all prompt computation can be skipped: appended tool output and missing suffixes still need prefill. The ordinary P→D path remains necessary. After retrieving history in reverse, newly computed input state must still reach decode. The two directions handle work from different points in the conversation.

Keeping only metadata in the router avoids moving large tensors through the proxy, but metadata lifetime must remain coordinated with block lifetime. The article's troubleshooting guidance keeps the proxy cache TTL below the decode-block TTL and uses expired-remote-read logs to diagnose failures. Restarting the proxy clears its in-process mapping. This also explains why the experiment restarts the proxy when switching the feature: old mappings are not a reliable cache entry point for the next experimental run.

## Two parameters govern benefit and cost

`decoder_kv_blocks_ttl` defaults to 480 seconds. Decode retains blocks after generation, providing a reuse opportunity if the next turn arrives before expiry; otherwise, normal prefill resumes. This TTL is fixed and not renewed. Longer retention increases reuse opportunities but keeps completed requests in accelerator memory, reducing capacity available for new work. The article identifies a heartbeat-renewed decode lease as future improvement, rather than implemented behavior.

`kv_recompute_threshold` defaults to 64 tokens. Coordination and transfer can cost more than recomputing a short prefix. The relevant quantity is the remotely reusable remainder after local matching. This is a token threshold, not a latency guarantee: per-token computation, KV size, and effective network performance change the break-even point.

An engineering assessment therefore starts with whether inter-turn gaps fit within retention, followed by whether saved computation covers lookup, transfer, and state installation. Higher hit rates can coexist with tighter memory capacity, so both need to be considered together.

## The configuration behind the performance numbers

The benchmark uses a 1P1D deployment: one prefill and one decode EC2 p5en.48xlarge, each with eight H200 GPUs and connected through EFA, plus a node for the proxy and client. Crucially, **prefix caching is disabled on prefill** to emulate eviction or routing to a node without the conversation's KV. Prefix caching remains enabled on decode.

| Model and prompt length | TTFT with bidirectional transfer OFF | TTFT with transfer ON |
| --- | ---: | ---: |
| Qwen3-32B, 2k tokens | 158 ms | 122 ms |
| Qwen3-32B, 24k tokens | 778 ms | 460 ms |
| zai-org/GLM-5-FP8, 2k tokens | 500 ms | 358 ms |
| zai-org/GLM-5-FP8, 20k tokens | 2,334 ms | 702 ms |

The article summarizes the longest-prompt improvements as approximately 1.6× and 3.3×. Across the tested prompt ranges, corresponding KV transfer times are roughly 30–130 ms for Qwen3-32B and 29–110 ms for GLM-5-FP8. Transfer adds network work but removes more prefill computation, reducing time to first token. TTFT still increases with context length when the feature is enabled; it is not constant.

These measurements demonstrate the opportunity when local prefill state is missing. If most production requests hit prefill's local cache, less redundant computation remains to recover. Slower networks, shorter prompts, and longer inter-turn gaps can also change the benefit. Better TTFT alone does not establish equal proportional improvements in sustained decoding speed, total throughput, or tail latency.

Evaluation should also distinguish the first turn from subsequent turns. The first has no previous decode state to retrieve; later turns exercise cross-turn transfer. An engineering extension of these results is to inspect hits, transferred bytes, and latency by prompt length and conversation turn, rather than only an aggregate average. If longer retention increases hits but also increases queueing, user experience may not improve. That capacity trade-off needs assessment on the target workload.

## Check the metadata path when integrating

The article's main text describes support in vLLM v0.21.0 and later. Its reproduction appendix, however, pins vLLM 0.29.0 and NIXL 1.4.1 and requires PR #40186 so streaming responses carry `kv_transfer_params`. The general version-support statement and the specific experimental environment should be interpreted separately. Both P and D must enable `bidirectional_kv_xfer`, and the client must consistently supply a conversation ID. Otherwise, a service can answer requests normally while never reusing state across turns.

Observability should follow the actual path: TTFT comes from client request statistics, total prefill duration from proxy logs, and D→P transfer time and bytes from the prefill node initiating the read. Final latency alone cannot distinguish a cache miss, expired blocks, missing metadata, and slow transfer. **The most useful design lesson is the complete state lifecycle**: retain computed results, discover their location across turns, and compare movement with recomputation. Multi-turn context reuse thereby becomes a serving-orchestration problem as well as a local cache setting.
