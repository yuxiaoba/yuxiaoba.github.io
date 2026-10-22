---
id: elastic-ep-downtime
title: '2026-10-19 | Elastic EP: Restricting Scaling Pauses to Topology Handover'
date: '2026-10-19'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
long_read: true
source_url: https://blog.vllm.ai/blog/2026-10-19-elastic-ep-near-zero-downtime
tags:
- inference-serving
- systems-reliability
summary: How NIXL EP preserves communication and CUDA graph state, and why a subsecond
  interruption differs from capacity preparation time.
writing_source: assistant
translation_source: assistant
permalink: /tech/en/elastic-ep-downtime/
published_at: '2026-10-22T08:44:53.471250+08:00'
updated_at: '2026-10-22T08:44:53.471250+08:00'
---
The difficult part of scaling an MoE service is preparing new GPUs while the existing ones continue serving. vLLM tackles communication membership and CUDA graph validity together: expensive preparation runs in the background, leaving a short service pause for handover. The interesting contribution is the set of conditions that makes state reuse possible and changes what users experience during scaling.

Original: [Achieving near-zero-downtime scaling in Elastic Expert Parallelism](https://vllm.ai/blog/2026-10-19-elastic-ep-near-zero-downtime)  
Itay Alroy (NVIDIA) · First published: 2026-10-19

## Avoiding a restart can still leave a long pause

With data-parallel attention and expert-parallel MoE, changing the GPU count also changes communication among experts. Earlier Elastic EP could resize a running deployment, but initializing workers, transferring weights, and preparing communication and execution graphs still blocked serving. Moving process startup into the background removes only part of the wait. If switching communicators invalidates captured CUDA graphs, retained GPUs still need warmup and recapture.

This explains why a machine joining a cluster does not immediately add usable throughput. Resource allocation, state preparation, and service activation are different milestones. For capacity planning, they should be observed separately; otherwise an autoscaler may count unavailable capacity and stop scaling too early.

## Separate preparation from activation

During background preparation, retained workers serve through their current communication groups while preparing connections, transferring weights, and arranging execution state for the target topology. Joining workers initialize independently. The short commit pauses schedulers, activates the prepared topology, and resumes serving. Asynchronous expert load balancing subsequently redistributes experts; new workers can initially handle attention.

<a class="note-image-link" href="/assets/images/tech/elastic-ep-downtime/communicator.png" target="_blank" rel="noopener" aria-label="Three stages of NIXL EP membership: existing peers, background connections, and activation · View original image ↗"><img src="/assets/images/tech/elastic-ep-downtime/communicator.png" alt="Three stages of NIXL EP membership: existing peers, background connections, and activation" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: existing peers keep serving on the left; new peers are connected but masked in the middle; commit activates them on the right while retaining the communicator and buffers.*

The central interface change is in-place membership adjustment in NIXL EP. New peers can be connected while masked, then activated at commit; existing communication buffers, connections, and the agent survive. An engineering interpretation is that knowing about a peer and including it in current computation become separate operations. Coupling them would make it easier for preparation to pull live requests into a collective synchronization.

## Graph reuse is a set of constraints

A captured execution graph retains kernel launch arguments and tensor addresses. Keeping the communicator's identity alone is insufficient: addresses, layouts, and launch configurations visible to communication and surrounding compute kernels must remain valid. The implementation retains fused-MoE execution objects, workspaces, dispatch outputs, and the backing storage of routing mappings, updating mappings in place.

The mechanism implies that runtime elasticity and memory-layout design cannot be treated independently. A local optimization that reallocates tensors for the current membership could force graph recapture across the service. Implementers need to distinguish mutable contents, replaceable objects, and addresses that must remain stable. This is a deeper requirement than placing a resize function on a background thread.

Joining workers face a different problem: they have no reusable graphs. During preparation, NIXL EP lets each mask all remote peers and use only its local rank for warmup and capture. These preparation passes also avoid waiting for other workers' DP batch information. New machines therefore prepare without requiring live workers to participate. Preparation still happens; its dependency on coordinated live execution is removed.

## Read downtime alongside total duration

The authors test DeepSeek V4 Pro on GB200 GPUs with TP=1, resizing DP/EP from 16 to 20 and back to 16. Weights were pre-downloaded to shared Lustre storage, and kernel compilation caches were warm. The table compares blocking preparation with asynchronous preparation plus graph reuse.

| Operation and metric | Blocking preparation | Async preparation + graph reuse |
| --- | --- | --- |
| 16→20 GPUs, serving interruption | 99.62 s | 0.82 s |
| 16→20 GPUs, total duration | 99.72 s | 92.34 s |
| 20→16 GPUs, serving interruption | 56.25 s | 1.96 s |
| 20→16 GPUs, total duration | 56.21 s | 9.32 s |

**The 0.82 seconds measures the handover interruption; new capacity did not become ready in 0.82 seconds.** Total duration and interruption are measured separately. The small inversion in the blocking scale-down measurements should not be used to infer stage durations. In a separate rising-load scenario with 11,391 requests and approximately 8→16 requests per second, Elastic EP completes every request and keeps rolling p95 time to first token below 5 seconds. Curves use 30-second windows and assign failed requests a 30-second penalty.

The evidence supports a substantial reduction in scaling interruptions under this hardware, software, and traffic configuration. It does not cover cold compilation, arbitrary network contention, every model combination, or recovery from failures midway through scaling. Numerical correctness checks also do not establish correctness across all production failure paths.

## Implications for the service controller

The following are engineering deductions from the mechanism. Scaling still needs lead time: if preparation takes more than a minute and begins only after capacity becomes tight, queues may grow before new capacity arrives. Background work also consumes links and device resources. Latency during preparation should be observed separately from ordinary serving; the existence of a background thread does not establish zero interference.

Scale-down additionally requires the controller to know when hardware can be released. A committed topology, a worker no longer performing work, and a device safe to reclaim are related but different states. A vague success flag makes subsequent resource operations difficult to coordinate.

A shorter normal handover window does not automatically define exceptional handover semantics. If a joining worker fails during preparation, how does the system recognize that it is unready? If a peer disappears after commit, which requests need rescheduling? Those questions require implementation details and fault tests. Normal resizing measurements do not answer them, and near-zero downtime should not be interpreted as uninterrupted service under every condition.

Further evaluation can divide resizing into before preparation, preparation, commit, and the stable period afterward, comparing throughput and latency distributions in each. This distinguishes an eliminated pause from queueing moved elsewhere and from capacity actually becoming usable. With variable request lengths, short-request averages may hide long requests stalling at handover.

In-place reuse also introduces lifecycle trade-offs. Avoiding address changes may require reserving resources or restricting adjustable layouts. The article gives no generalizable additional-memory-cost figure, so graph preservation should not be treated as free. Deployment needs to balance stable state, memory headroom, and the supported resizing range.

**Read the in-place communication and graph-preservation sections before the performance table.** The useful advance is translating elasticity into explicit execution-state invariants. Snapshot-based preparation and integration with Dynamo and llm-d autoscalers remain future directions in the article, rather than capabilities demonstrated by these results.
