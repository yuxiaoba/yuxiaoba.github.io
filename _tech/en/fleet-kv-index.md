---
date: '2026-10-28'
published: true
layout: article
maintenance: daily-research
authoring_source: assistant
translation_source: assistant
id: fleet-kv-index
title: '2026-10-28 | A fleet-wide KV index: where a prefix lives changes its value'
lang: en
source_type: tech
long_read: true
source_url: https://sference.com/blog/kv-cache-index
tags:
- inference-serving
- observability
summary: An event-driven cache view across replicas, tiers, and attention ranks, with
  explicit limits from staleness and hybrid models.
permalink: /tech/en/fleet-kv-index/
published_at: '2026-10-28T15:24:19.938525+08:00'
updated_at: '2026-10-28T15:24:19.938525+08:00'
---
A prefix in GPU memory is not equivalent to one on host memory, disk, or shared storage. sference describes how its scheduler turns those different reuse costs into routing inputs across a heterogeneous serving fleet.

Original: [Tracking the KV Cache Across a Heterogeneous GPU Fleet](https://sference.com/blog/kv-cache-index) · Peter Us / sference · 2026-10-27.

### Build the view from engine events

A relay beside each engine subscribes to block-store, removal, and clear events. The scheduler maintains a per-model prefix-block tree whose nodes record replicas, tiers, and data-parallel attention ranks. Walking a request down the tree estimates each replica’s reusable prefix and where it must load that state from.

<a class="note-image-link" href="/assets/images/tech/fleet-kv-index/event-flow.png" target="_blank" rel="noopener" aria-label="Engine events flow through relays into the scheduling KV index · View original image ↗"><img src="/assets/images/tech/fleet-kv-index/event-flow.png" alt="Engine events flow through relays into the scheduling KV index" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Events build the global view; the scheduler then routes to a suitable replica or rejects a request early.*

Normalization must preserve semantics: eviction may invalidate descendants in one engine but not another; hashes differ; speculative decoding can use token-pair keys. The relay adapts these differences, and engine upgrades require event-stream checks. This is not a stable standardized protocol.

### Staleness remains observable

A tier move creates a removal and a store. Tracking all locations prevents the index from confusing movement with complete loss. Relay snapshots rebuild the index shallow-prefix-first, with staggered replay to avoid synchronized load.

Eviction can still occur after routing but before execution. The scheduler optimistically credits recently dispatched prompts to reduce event-lag effects, while conservatively dropping states whose reusability cannot be established. These address different uncertainties; the view is neither always conservative nor exact.

Hybrid models also need matching recurrent-state checkpoints. Retained KV alone may not support resumption. Missing state-eviction events make indexed prefix length an upper bound.

### Compare predictions with actual reuse

The system records predicted cached tokens at routing and compares them with engine-reported reuse after completion. For a typical day, the article reports 93.1% of prompt tokens actually reused, 99.6% coverage of reused tokens by the index, and 0.3% erroneous credit. These have different denominators; none should be casually renamed a 99.6% cache-hit rate. No independent routing control experiment establishes a particular latency or cost gain.

The contribution is a decision-oriented cache view with explicit uncertainty. Prefetching, proactive replication, and globally informed eviction remain proposed next steps, rather than measured benefits of the deployed index.
