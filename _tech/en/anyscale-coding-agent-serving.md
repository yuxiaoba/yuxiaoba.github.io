---
id: anyscale-coding-agent-serving
title: '2026-10-08 | Anyscale: Caching, Routing, and the Cost of Coding Agents'
date: 2026-10-08
reviewed_on: 2026-10-18
long_read: true
lang: en
source_type: tech
source_url: https://www.anyscale.com/blog/run-coding-agents-on-your-own-gpus
repo: https://github.com/anyscale/llm-serving-for-coding-agents
organization: Anyscale
tags:
- coding-agents
- inference-serving
summary: Design inference serving around long contexts and multi-turn tool use, while separating configuration gains, capacity, and complete-task cost.
published: true
maintenance: manual
approved_on: '2026-10-19'
layout: article
permalink: /tech/en/anyscale-coding-agent-serving/
translated_on: '2026-10-19'
translation_source: /tech/zh/anyscale-coding-agent-serving/
translation_method: assistant translation of the locally approved Chinese article
original_tags:
- LLMOps
- inference
- vLLM
- Ray
- caching
---
**Anyscale · Engineering guide to inference serving**  
Original article: Cut coding agent costs by 90%: Secure LLM serving with Ray + vLLM on Anyscale

## Why coding-agent traffic needs its own optimization strategy

Coding agents repeatedly submit repository context, tool definitions, conversation history, and tool results, often to generate only one tool call. Inputs are long, much of the context repeats across turns, and tool execution or human review introduces pauses. Bottlenecks therefore include context processing, cache reuse, and burst queues, not just token-generation speed.

This guide connects those workload characteristics to the design of a self-hosted inference service. Its useful contribution is how models, caching, routing, and capacity fit together. The headline claim of “90%” savings needs a separate reading of the assumptions.

## Architecture: the engine, replica service, and runtime each own a layer

<a class="note-image-link" href="/assets/images/tech/anyscale-coding-agent-serving/anyscale-stack.png" target="_blank" rel="noopener" aria-label="vLLM and Ray Serve LLM within the Anyscale serving architecture, view original"><img src="/assets/images/tech/anyscale-coding-agent-serving/anyscale-stack.png" alt="vLLM and Ray Serve LLM within the Anyscale serving architecture" loading="lazy"><span class="note-image-action">View original ↗</span></a>

*Reading the diagram: vLLM executes the model; Ray Serve LLM manages replicas, request routing, and unified interfaces; Anyscale manages GPU resources and service operation. A fast engine addresses only one layer.*

When a request arrives, the service must select a replica while considering how much relevant context that replica has already cached. Sending a session back to a familiar replica can avoid repeated work. But maximizing cache hits alone can concentrate traffic on an already busy replica. Routing therefore needs to account for both reusable context and outstanding load.

Routing between models addresses a different question: which tasks should use a self-hosted model, and which should use another model? Session continuity also matters. Switching models in the middle of a tool interaction can introduce incompatible context limits, formats, or tool behavior.

## Separate caching, routing, and scaling

The three mechanisms solve different problems. **Caching** reduces repeated computation on the same context. **Replica routing** selects the engine that receives a request. **Scaling** determines the serving capacity available. They interact, but one concurrency setting cannot solve all three problems.

Consider a developer session. The first turn reads substantial code and requires processing a long input. The next adds a tool result while retaining most of the previous prefix. A replica with the matching cache can potentially skip repeated computation. If that replica has a long queue, however, the waiting cost may outweigh the cache benefit.

Cache-aware routing therefore needs to estimate both the input still to be processed and the work already assigned to an engine. Counting requests alone hides differences between long and short contexts. Maximizing prefix overlap alone can intensify a hotspot. This is a concrete example of workload shape determining the routing policy.

Scaling also needs time to react. The engine's admission limit, the limit on requests sent to a replica, and the target that triggers expansion serve different purposes. Waiting until a hard capacity limit is reached can create queues before new replicas are ready. The article's settings are starting points for its tested configuration, not values to copy unchanged to another model or GPU.

## How caching changes waiting time

<a class="note-image-link" href="/assets/images/tech/anyscale-coding-agent-serving/anyscale-cache.png" target="_blank" rel="noopener" aria-label="KV-cache tiers across GPU memory, CPU memory, and local storage, view original"><img src="/assets/images/tech/anyscale-coding-agent-serving/anyscale-cache.png" alt="KV-cache tiers across GPU memory, CPU memory, and local storage" loading="lazy"><span class="note-image-action">View original ↗</span></a>

*Reading the diagram: active blocks remain on the GPU; idle blocks can move to larger CPU or storage tiers. When a session returns, the system tries to restore them instead of recomputing the full prefix.*

Long contexts consume substantial KV-cache memory. While a developer pauses to read code, other requests may evict their blocks from the GPU. Tiering tries to extend the useful lifetime of that context, although restoring it has a transfer cost of its own.

Anyscale reports a controlled test using GLM-5.2 on one node with eight RTX PRO 6000 GPUs and an additional 512 GiB CPU-cache tier:

| Metric | GPU cache only | With CPU tier |
| --- | --- | --- |
| Requests completed in the nominal 900-second window | 58 | 215 |
| Median time to first token | 48.4 seconds | 9.2 seconds |

The latency comparison uses the 58 requests completed under both configurations. These results show that the tested workload benefited from retaining cached context. They do not establish the same improvement for arbitrary models, concurrency levels, or session distributions.

## Routing between models changes task allocation

Replica routing typically distributes work among equivalent services. Multi-model routing changes which model performs it. The guide discusses serving routine work with a self-hosted model, using another model for difficult tasks or capacity shortages, and retaining explicit user choice.

Estimating difficulty is only part of the problem. A later request in a coding session may contain tool results without a new user instruction. Reclassifying every turn can move one tool interaction between models. Differences in formats, context capacity, and tool behavior can disrupt continuity, which is why the article emphasizes session stickiness.

Routing benefits therefore need to be measured over complete tasks. A cheaper request may increase repair iterations, retries, or human intervention. Throughput and token prices should be considered alongside task success and total completion time.

## How to interpret the “90% savings” claim

The article's planning model assumes roughly $4 per GPU-node hour and 50 registered developers sharing one GPU. It estimates per-developer GPU expenditure from operating hours. **Registered users are not a validated concurrency limit, and GPU expenditure is not total cost of ownership.** Model quality, peak queues, idle capacity, platform costs, and operations all affect the outcome.

A further distinction is essential: the cache-performance experiment above uses eight GPUs, while the cost projection assumes one. They cannot be combined into a performance-and-price promise for one deployment. Required capacity must first be measured against real session traffic and latency objectives, then evaluated together with task success.

## Performance tuning must preserve correct tool use

The article discusses weight and KV quantization, CUDA graphs, speculative decoding, and cold-start caches. These target different bottlenecks. Quantization affects memory and computation. CUDA graphs reduce repeated execution overhead. Speculative decoding attempts to advance multiple tokens at once. Compilation caches primarily affect startup.

Their gains cannot simply be multiplied. Under one concurrency setting, increasing speculation depth from three tokens to four reduced output throughput. The article also warns of tool-call compatibility problems in some model, parser, and runtime combinations. More aggressive configurations need validation on complete multi-turn sessions.

Cold starts should also be decomposed into model download, weight loading, engine compilation, and service readiness. A proportional reduction in compilation time does not imply the same reduction in total startup time, or a corresponding increase in steady-state throughput.

## A useful order of implementation

Start with a baseline that performs the required tool interactions correctly, then change one part at a time. The article emphasizes replaying real sessions while preserving input growth, delays between turns, and bursts. Uniform synthetic prompts cannot represent those properties well.

| Measure first | Question to answer |
| --- | --- |
| Complete-task success and tool errors | Does the configuration harm task completion? |
| Time to first token, output intervals, and total duration | Where does the user experience the wait? |
| Queues, cache hits, and GPU utilization | Is the bottleneck capacity, repeated work, or imbalance? |
| Work completed within latency objectives | Does higher throughput still provide an acceptable interactive experience? |

These measurements make it possible to assess whether quantization, caching, or expansion helps. Changes in models, hardware, or software versions require renewed compatibility and quality checks; old measurements are not a promise for a new deployment.

**Engineering assessment: a useful guide for teams evaluating self-hosted inference for coding agents.** Its main value is the organization and measurement of a service from one replica to many. Whether it is cheaper than a hosted API still depends on the team's tasks and traffic. The repository provides staged examples. This article does not report installing or running them, and does not treat the blog's cost model as a current procurement quote.
