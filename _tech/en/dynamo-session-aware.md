---
id: dynamo-session-aware
title: '2026-10-08 | Dynamo: Scheduling Agent Inference and KV Cache by Session'
date: '2026-10-08'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- observability
summary: 'Session identity, admission at tool boundaries, and shared-cache indexing:
  mechanisms, throughput evidence, and interface maturity in Dynamo.'
authoring_source: assistant
translation_source: assistant
permalink: /tech/en/dynamo-session-aware/
long_read: true
source_url: https://pytorch.org/blog/session-aware-agentic-inference-with-nvidia-dynamo/
published_at: "2026-10-20T09:38:54.997728+08:00"
updated_at: "2026-10-20T09:38:54.997728+08:00"
---
The pressure in agent inference often arises between model calls. A coding task starts with a long context, appends tool results, and sends its history again; subagents may share prefixes while running concurrently. A GPU that has stopped generating tokens can still hold a session's KV cache. The interesting development in Dynamo is a session identity that connects routing, admission, observability, and cache policy, extending the optimization unit to an entire execution chain.

Original: [Session-Aware Agentic Inference with NVIDIA Dynamo](https://pytorch.org/blog/session-aware-agentic-inference-with-nvidia-dynamo/)  
Ishan Dhanani, Jamie Li, Karen Chung · PyTorch Blog / NVIDIA Dynamo · Published: 2026-10-08

## Connect individual requests through session identity

A request router can identify the worker with the greatest cached-prefix overlap. It has less information about whether the agent is still active, when it will return from a tool call, which subtasks share its context, or how much resident state additional sessions will leave behind. The article introduces a stable `session_id` for one execution chain and an optional `parent_session_id` for parent–child relationships. Optimizations opt in to consuming this information.

Dynamo maps identity headers already emitted by Claude Code, Codex, and OpenCode. Custom harnesses can supply `X-Dynamo-Session-ID` and a parent-session header. These fields establish associations, not cache hits. Actual reuse still depends on specific prefixes and cache state; parent–child identity helps the system estimate which state may be needed again.

## Include tool waits in performance evidence

With request tracing enabled, Dynamo emits a record when a response stream ends, including session fields, output-token count, finish reason, KV metrics, tool names, and replay information. Prompt, response, and tool-call content are excluded by default. Input lengths and block-sequence hashes preserve prefix-sharing relationships. This connects a tool wait to later eviction and repeated prefill, instead of showing only a slower model call.

The same trace can drive GPU-free configuration comparisons in AISimulate or live endpoint replay through AIPerf. Simulation explores worker counts, routing, and capacity; live replay measures actual latency and throughput. An engineering distinction matters: serving the same request graph is different from rerunning an agent's decisions. Replay preserves the captured traffic structure and does not establish that changed policies leave tool choices and task outcomes unchanged. Excluding content by default also does not make all metadata nonsensitive.

## Apply admission control at tool boundaries

Cache thrashing occurs when working sets exceed capacity: evicting a live session's prefix can force its next turn to recompute it. Dynamo integrates the ThunderAgent scheduling approach into a native Rust plugin that directly owns KvRouter and tracks working sets from actual prompt and completion token counts in responses. It maintains two state dimensions: reasoning versus acting, and active versus paused.

Under memory pressure, the scheduler logically pauses sessions at tool boundaries, allowing their KV blocks to become eviction candidates. It does not preempt ongoing decode. If no acting session is available to pause, it marks a smaller reasoning session for pausing at its next tool boundary. The published defaults pause at utilization 0.95, target 0.80, apply an early priority reduction between 0.80 and 0.95, and allow resumption only once utilization falls to 0.85 or below.

Resumption packs smaller-token sessions first, including a per-session buffer. Resumed requests receive a one-second priority boost, and a 30-minute forced-resume cap provides a further starvation guard. Hysteresis prevents repeated switching near the threshold, but these parameters are not universal service constants. Pausing shifts some waiting to the session layer, while smaller-first admission makes long-session completion time relevant. The engineering trade-off is fewer simultaneously active working sets in exchange for less repeated prefill; physical cache capacity does not increase.

## Read results with hardware and baselines attached

For SWE-bench on one node with eight H100 GPUs and two TP4 MiniMax-M2 replicas, the authors report approximately 12%–16% higher throughput than KV routing alone. A separate Uni-Agent SWE-Bench rollout experiment uses eight H20-3e GPUs and Qwen3-Coder-30B-A3B-Instruct against VERL's default Global LB. Performance is roughly even at low concurrency, CC32–128. At CC384–512, Global LB degrades sharply while session scheduling maintains higher throughput. Prefix-cache hit rate stays above 94.5% across the full concurrency sweep.

The article's textual medium-concurrency percentages do not fully match the plotted values. The more defensible conclusion is that the high-concurrency degradation is mitigated, rather than a single speedup applying across configurations. These measurements concern serving throughput, not task correctness. Different hardware, models, and baselines cannot be combined into one scaling curve. Session completion latency, pause duration, and fairness remain complementary measurements for assessing interactive experience.

## Credit external caches only for complete reusable pages

Once state moves into CPU memory or shared storage, GPU-only visibility misses retrievable cache contents. The experimental shared-pool indexer consumes Mooncake Store and Remove events. It expands logical pages into physical objects according to TP/PP layout, K/V tensors, and related configuration, counting a page as reusable only when all required objects exist. Routing consults contiguous hit ranges in its local index rather than probing remote storage object by object on the hot path.

FlashIndexer separately computes overlap across a worker's native tiers. Shared-pool credit applies only beyond the device-resident prefix, preventing GPU-local hits from being counted twice. Placement also incorporates tier weights and current load. As an engineering interpretation, the existence of reusable pages and the benefit of retrieving them are different questions: movement costs, parallel layouts, and cache freshness affect the result, so credits must reflect actual service costs.

As an engineering consideration, indexing adds maintenance work: block storage, removal, and session branching must feed a usable association view. Evaluation should account for index-update overhead alongside saved computation, and distinguish knowing that remote state exists from having moved it into an executable location. Crediting shared cache is therefore a first step; the engine must still carry out movement and resource checks.

## Let the router express intent and the engine control execution

<a class="note-image-link" href="/assets/images/tech/dynamo-session-aware/session-prefix.png" target="_blank" rel="noopener" aria-label="KV events and hints between the Dynamo Session-Prefix Indexer, routing policy, and inference engine · View original image ↗"><img src="/assets/images/tech/dynamo-session-aware/session-prefix.png" alt="KV events and hints between the Dynamo Session-Prefix Indexer, routing policy, and inference engine" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: the tree on the left records shared prefixes, session branches, and block locations; workers on the right report KV events. Routing policies use these associations to send optional hints with requests.*

The Session-Prefix Indexer uses a radix tree to associate session lineage with KV blocks, continuously updated by engine Stored/Removed events and FlashIndexer hits. These associations enable policies such as demoting state during a tool wait or prefetching before a subtask completes, without embedding the entire session scheduler into each inference engine.

The proposed KvHint surface includes Share, Prefetch, Demote, Pin, and Retain, expressing sharing, prefetching, movement to a colder tier, bounded pinning, and retention preferences. Hints are soft: an engine may clip, defer, or ignore them, while workloads without hints retain existing behavior. The article describes a working Share implementation based on HiCache, with Prefetch and Demote intended to build on it. This does not establish that every listed policy is fully available.

**Read the work at three maturity levels: session identity and admission scheduling, experimental external shared-pool awareness, and an evolving cache-hint interface.** The engineering advance combines where state resides with which session may return to use it. It is most relevant to long contexts, repeated tool calls, and substantial session concurrency. Workloads with little prefix reuse or no capacity pressure should not be expected to see the same gains.
