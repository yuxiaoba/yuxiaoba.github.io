---
id: lmcache-mp-coordinator
title: '2026-10-16 | LMCache MP Coordinator: Finding Caches Across Servers'
date: '2026-10-16'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: How registration, event gating, and an eventually consistent directory expand
  KV discovery, with clear boundaries around P2P transfer and prior performance results.
authoring_source: assistant
translation_source: assistant-authored paired Chinese/English editorial notes
long_read: true
source_url: https://blog.lmcache.ai/en/2026/10/16/finding-reusable-kv-caches-across-a-fleet-of-servers-lmcaches-mp-multiprocess-coordinator/
permalink: /tech/en/lmcache-mp-coordinator/
published_at: "2026-10-19T20:41:00.047475+08:00"
updated_at: "2026-10-19T20:41:00.047475+08:00"
---
**Siddhant Ray · Official LMCache technical article**  
Original: [Finding Reusable KV Caches Across a Fleet of Servers: LMCache’s MP (MultiProcess) Coordinator](https://blog.lmcache.ai/en/2026/10/16/finding-reusable-kv-caches-across-a-fleet-of-servers-lmcaches-mp-multiprocess-coordinator/)

## A local miss does not mean a fleet-wide absence

A long prompt, retrieved document, or conversation history may already have been computed by one inference process, yet a request assigned elsewhere recomputes it. Visibility matters alongside capacity. LMCache MP mode moves management out of the inference process: several vLLM processes can connect to one independent server and share a cache service. This crosses process boundaries but leaves discovery across nodes unresolved.

The MP Coordinator addresses that next boundary by tracking servers, their reported caches, and placements. It does not store KV tensors or add another storage tier. Metadata and large tensor payloads have different scaling constraints; routing all payloads through a central node could make the control service a bandwidth and latency bottleneck.

## Four steps from registration to directory

Servers register and send heartbeats, currently every five seconds by default in the article. Registration is best effort: an MP server continues serving if the coordinator is temporarily unavailable. This preserves data service, not necessarily equivalent global discovery during the outage.

Cache events come next. With reporting enabled, STORE, ACCESS, and DELETE describe additions, accesses, and removals, delivered through HTTP or Kafka. Registration says who is alive; events say who owns what. A healthy instance listing does not prove the directory receives cache lifecycle updates.

<a class="note-image-link" href="/assets/images/tech/lmcache-mp-coordinator/directory.png" target="_blank" rel="noopener" aria-label="LMCache MP registry, event gate, key directory, and direct server-to-server KV path · View original image ↗"><img src="/assets/images/tech/lmcache-mp-coordinator/directory.png" alt="LMCache MP registry, event gate, key directory, and direct server-to-server KV path" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: servers send events upward through the event gate into the key directory. The orange KV arrow runs directly between servers, bypassing the coordinator. The dashed blend index is optional.*

Third, the Event Gate handles duplicates and obsolete events caused by retries, delays, and restarts. It tracks each server's event sequence and incarnation to reject duplicate messages and messages from stale processes. Otherwise, a late STORE could resurrect a placement invalidated by a restart. This checks ordering and identity at the metadata boundary; it does not replicate every tensor consistently.

Finally, the Key Directory maps cache keys to placements, including instance, tier, backend, and object size, while indexing chunk-token associations. Ordinary lookup derives complete-chunk keys from a token sequence and returns known locations. The owner must still be contacted; a directory entry does not prove that an object exists now.

## Discovering non-prefix content does not establish arbitrary safe reuse

Shared system prompts suit prefix matching, but the same retrieved document may occur at different positions. With Blend lookup enabled, an additional content index can discover cached chunks anywhere in a new sequence and report old and new positions. This expands discovery and connects to CacheBlend's non-prefix reuse mechanism.

Finding a fragment and using it correctly are distinct. In ordinary causal attention, KV depends on preceding context and position; identical text does not justify copying arbitrary intermediate state. The article introduces directory behavior, not a demonstration of accuracy preservation for every model, position change, and mixing method. Adoption still requires validation under the particular reuse mechanism and compatibility conditions. This is an engineering interpretation, not an additional performance promise from the source.

## Why the directory can be temporarily wrong

The directory is eventually consistent soft state: placements are hints, and the owning server validates availability. If a hinted object has been evicted, the system can try another copy or recompute. This accepts lost reuse opportunities and lookup overhead instead of transactional coordination on every cache operation. The correctness requirement is that a failed hint must not introduce incorrect state into generation.

When a server disappears or restarts, a reverse index can fence its L1 placements without scanning the whole directory. L2 data may persist independently and follows its own lifecycle events. A restart therefore does not imply disappearance at every storage tier. Failure handling must respect storage lifetime.

One boundary is particularly easy to overstate: today's P2P path uses the coordinator for membership, then MP servers connect, query peers, and transfer directly. NIXL is the default transfer engine, with RDMA where supported. The coordinator is not the lookup service for every P2P miss. Directory capabilities and current P2P integration are separate; the diagram does not establish that every request uses the global key directory.

## What the performance numbers actually support

The cited MP-mode experiment uses Qwen3-235B-A22B-Instruct-2507-FP8 on eight H100 GPUs. The baseline gives each rank 50 GB of host cache, 400 GB total; the comparison uses a shared MP service of the same capacity. Mean TTFT falls from 3.98 s to 0.29 s, P99 from 13.55 s to 1.30 s, and mean decode speed rises from 9.81 to 37.47 tokens/s. This supports the value of shared capacity and reuse, not a claim that the new coordinator makes lookup 13.7× faster.

An earlier P2P experiment runs two vLLM instances on different GPUs of one host, with the second reusing contexts cached by the first. Query-round mean TTFT is 0.490 s versus 2.028 s, and round duration 7.964 s versus 38.323 s. The authors explicitly describe a contrived full-reuse workload, predating the MP Coordinator. Neither experiment substitutes for coordinator-specific scale, recovery, or metadata-staleness evaluation.

## Validate the actual operating path

When reading the deployment example, ask whether instances registered, whether event reporting is enabled, and which server validates and moves the payload. Enabling Blend indexing and configuring cross-node P2P are additional independent steps. Connecting to the coordinator does not automatically enable every capability. No source commands or cache services were run for this note.

For practical evaluation, supplement mean and tail TTFT with stale-placement failures, heartbeat delays, restart cleanup, transferred bytes, and recomputation fallback. These are evaluation priorities inferred from the soft-state design; the article does not provide a full benchmark for them. The significant change is making cache placement queryable across a fleet while leaving bulk transfer and final availability validation with servers. Whether this saves cost depends on actual reuse, movement cost, and directory maintenance overhead.
