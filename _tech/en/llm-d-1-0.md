---
id: llm-d-1-0
title: '2026-10-20 | llm-d 1.0: coordinating cache locality, request priority, and
  upgrades'
date: '2026-10-20'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: 'Distributed inference increasingly depends on coordination between engines:
  prefix-aware routing, tiered KV caches, and flow control jointly shape multi-turn
  agent latency and cost.'
long_read: true
source_url: https://cloud.google.com/blog/topics/ai-infrastructure/llm-d-1-0-an-open-source-stack-for-distributed-inference/
permalink: /tech/en/llm-d-1-0/
authorship: assistant
translation_source: assistant-authored bilingual analysis and translation
published_at: '2026-10-23T12:22:02.560508+08:00'
updated_at: '2026-10-23T12:22:02.560508+08:00'
---
Multi-turn agents turn inference from independent requests into workflows with history: the next step repeats a long prefix, returns suddenly after a tool call, and may compete with background jobs for the same accelerators. The interesting aspect of llm-d 1.0 is its integration of caching, routing, flow control, and model-server orchestration into a Kubernetes serving system. It addresses coordination among engines; token generation speed inside one engine is only part of that problem.

Original: [Announcing llm-d 1.0: Open distributed inference for agents on Google Cloud TPUs and GPUs](https://cloud.google.com/blog/topics/ai-infrastructure/llm-d-1-0-an-open-source-stack-for-distributed-inference/)  
Mark Lohmeyer, Sean Horgan · Google Cloud · 2026-10-20

## One request requires at least three decisions

Three engineering questions help explain the stack: whether to admit the request now, which replica should receive it, and which resources should process the input and generate output. The article combines prefix- and load-aware routing, tiered caches, phase disaggregation, and priority control. It also reports a demonstration with 1,000 sandboxed agents accessing one endpoint. That demonstration size does not establish equivalent service quality for every model, accelerator, and traffic combination.

<a class="note-image-link" href="/assets/images/tech/llm-d-1-0/serving.png" target="_blank" rel="noopener" aria-label="Progression from round-robin distribution to cache-aware routing, tiered KV caches, and multi-tenant flow control · View original image ↗"><img src="/assets/images/tech/llm-d-1-0/serving.png" alt="Progression from round-robin distribution to cache-aware routing, tiered KV caches, and multi-tenant flow control" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*The left panel distributes requests across ordinary replicas; the middle adds phase separation and cache tiers; the right distinguishes priorities at admission. These are stages of capability, not a controlled performance curve.*

These decisions cannot each optimize an isolated metric. The replica with the warmest cache may have the longest queue. The emptiest replica may need to recompute extensive context. Maximizing utilization can also make interactive users wait behind background work. Scheduling quality should therefore be judged through completion times and service objectives, not only hit rate or utilization.

## Larger caches still need a location-aware router

The [tiered prefix-cache guide](https://llm-d.ai/docs/well-lit-paths/foundations/tiered-prefix-cache) describes offloading evicted KV blocks from accelerator memory to host memory, optionally extending into a shared filesystem, then reloading them when later requests reuse the prefix. Routing also considers CPU-tier cache locations. Expanding cache capacity and finding existing state are thus related problems.

A useful engineering comparison remains whether lookup, queueing, and transfer together cost less than recomputing the prefix. Long prefixes and repeated turns increase the opportunity, while storage congestion, poor reuse, or an overloaded warm replica can offset it. This relationship explains the design; it is not a latency guarantee for arbitrary requests.

The guide also notes that vLLM host-cache allocations count toward the pod memory limit. Moving pressure out of HBM does not remove capacity constraints. Cache sizing, container memory limits, and router index capacity must agree. A successfully served request alone also does not establish that offloading and reuse are functioning.

## Disaggregation makes upgrades a cross-role problem

Prefill constructs input KV state; decode generates subsequent tokens incrementally. Their computation and memory-access characteristics differ. Separate pools permit independent capacity choices while adding state transfer and lifecycle coordination. The [DisaggregatedSet design documentation](https://llm-d.ai/docs/dev/architecture/model-server-orchestration/disaggregatedset) describes a higher-level resource managing the LeaderWorkerSets associated with different roles, allowing rolling updates to account for relationships among them.

Operationally, one ready pod does not imply an available end-to-end serving path. If old prefill capacity disappears before compatible new decode capacity is ready, locally healthy components can still yield an interruption. Rollout capacity, version compatibility, and routing transitions need to be validated together. This is dev-version documentation; availability budgets must be checked against the deployed version. A smooth-upgrade claim in a release article is not a zero-interruption guarantee for every configuration.

## Background throughput needs explicit admission boundaries

The [Async Processor documentation](https://github.com/llm-d/llm-d-async) describes pulling tasks from message queues and dispatching them to an inference gateway after admission and capacity checks. Queue-level gates can refuse requests for redelivery; pool-level gates can wait for capacity. Requests carry deadlines, which bound retries after failures. Latency-tolerant work can consequently use spare capacity without reserving all execution resources at submission.

Such waiting belongs in end-to-end task latency, rather than disappearing from a report that measures only generation. Delayed, rejected, and failed work should also be distinguished. Protecting interactive traffic does not establish that background jobs finish soon enough. A multi-tenant evaluation should measure both high-priority latency and low-priority completions and maximum waiting time.

## Measure cache benefits over complete sessions

Consider a hypothetical evaluation with identical requests, submitted either consecutively or after tens of seconds spent executing tools. In the latter case, state may already have been evicted and replica load may have changed. Identical prefixes need not produce identical benefits. Multi-turn benchmarks should preserve inter-turn delays instead of flattening sessions into uninterrupted calls.

Cold starts deserve separate observation. New replicas have no existing context. Routing that continues to prefer old replicas can delay the benefit of expansion; immediately distributing traffic evenly can increase recomputation. This is a natural tension between locality and capacity growth. It calls for joint consideration of load and cache state, rather than treating fixed session affinity as a universal answer.

Model or configuration upgrades also change state compatibility. Matching prefix text alone does not establish that old KV state remains reusable. Cache hits, state validity, and version transitions need distinct treatment, so a performance optimization does not cross a correctness boundary.

## What the public numbers establish

Google Cloud reports that, on an agentic coding workload using Ironwood TPU (TPU 7x), prefix-aware routing plus host-memory offload reduced median time to first token by more than 85% and increased total throughput 2.4× relative to a plain Kubernetes Service. This compares combined optimizations with a basic routing baseline. It cannot separately attribute gains to routing and caching, or establish gains on requests without repeated prefixes.

The article does not fully specify the model version, concurrency, and prompt distribution next to that result, so the number alone cannot establish a portable performance expectation. The reading remains useful: first determine whether local traffic has repeated context and uneven cache warmth, then assess whether routing and caching address the dominant bottleneck. Evaluate separate phase pools and their transfer costs when phase contention actually matters.

For inference infrastructure, the release broadens optimization to state location, traffic fairness, and upgrades. A useful adoption sequence adds capabilities incrementally and observes first-token latency, subsequent-token latency, completion rates, and cost under the same workload. That distinguishes avoided recomputation from waiting merely moved into a different queue.
