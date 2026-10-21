---
id: "nixl-push"
title: "2026-10-14 | NIXL Push: Move KV-Transfer Setup Off the First-Token Path"
date: "2026-10-14"
lang: "en"
published: true
layout: "article"
maintenance: "daily-research"
source_type: "tech"
tags: ["inference-serving"]
summary: "Early decode allocation and registration enable background KV pushes from prefill, trading routing flexibility for less exposed setup latency."
translation_source: "assistant"
authorship: "assistant"
source_url: "https://blog.vllm.ai/blog/2026-10-14-nixl-push-connector"
permalink: "/tech/en/nixl-push/"
long_read: true
---

Disaggregating prefill and decode lets each phase scale independently, but a request must move its context state between them before generation can continue. vLLM's NIXL Push connector changes the timing of that handoff: the destination prepares early, and the producer writes once data is ready, overlapping work that previously happened in sequence.

Original: [Push-Based KV Transfer to Improve TTFT and TPOT for Disaggregated Inference in vLLM](https://vllm.ai/blog/2026-10-14-nixl-push-connector)  
Sunita Nadampalli (AWS), Nicolò Lucchesi (Mistral) · Published: 2026-10-14

## Fast transfers do not necessarily mean a fast first token

NIXL moves KV blocks between instances over interconnects that can support RDMA. The article discusses direct device-memory transfers over AWS EFA, avoiding host-memory staging. Link speed is only one requirement: discovering source addresses, allocating destination blocks, preparing descriptors, and submitting the transfer can also sit on the critical path.

In the default pull flow, prefill finishes before the router relays source metadata to decode. Decode then allocates space, prepares the transfer, and initiates NIXL READ. The next phase waits for those serial control operations as well as the network copy. When descriptor preparation runs synchronously in the decode loop, other active requests can also be affected.

Push retains the underlying network path. It overlaps destination setup with prefill computation and assigns transfer submission to a background thread on the prefill side. It can therefore reduce time to first token (TTFT) and relieve the decode loop, improving time per output token (TPOT).

<a class="note-image-link" href="/assets/images/tech/nixl-push/push-architecture.png" target="_blank" rel="noopener" aria-label="Concurrent setup and direct writes in NIXL Push · View original image ↗"><img src="/assets/images/tech/nixl-push/push-architecture.png" alt="Concurrent setup and direct writes in NIXL Push" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*The router starts both sides: prefill computes KV while decode registers destination blocks. Only their rendezvous triggers WRITE; decode begins after completion.*

## Two readiness conditions must meet

First, decode allocates local KV blocks for a request requiring remote prefill and registers its identity and destination locations with the producer. Prefill can still be computing; the two sides proceed concurrently instead of waiting for source completion before discovering destination addresses.

Second, the producer matches destination registration with local KV readiness by request identity. Either event may arrive first: an early registration waits for computation, while early computation retains its blocks until registration arrives. The second event triggers transfer. Matching must also handle requests reissued after preemption or retry, rather than pairing stale addresses with a new execution.

Finally, the producer establishes or reuses connections and issues NIXL WRITE operations to destination tensor-parallel ranks. The sides can use different block sizes and layouts, mapping locations to their respective physical layouts during transfer. Decode does not begin on an arbitrary completion message. It waits for all expected notifications from producer ranks writing to it before marking KV ready.

Reliability depends on this handoff protocol. Knowing an address does not make its data readable, and partial completion does not make every shard available. The diagram's completion arrow represents the transition from reserved memory to state usable by decode.

## Background work changes who pays setup costs

When both conditions hold, the prefill loop hands work to a background thread and returns to model execution. The thread manages connections, maps block addresses to descriptors, merges contiguous regions, and submits WRITE. Per-request setup previously burdening decode moves to another endpoint and execution path.

Copies still cost resources, and background work can contend for CPU, network, or memory. The mechanism explains why the same transport can produce different user latency: overlapping preparation with computation and removing synchronous interruptions from decode reduces exposed waiting. The relevant comparison is the complete timeline, not NIC bandwidth alone.

## The conditions behind the threefold result

The authors benchmark Qwen3-32B in a 1P1D deployment on Amazon EC2 P5en with EFA. The appendix uses two p5en.48xlarge instances, each with eight H200 GPUs; the model runs in BF16 with TP=8. Output length is 128 tokens. Inputs range from 1k to 16k tokens and arrival rates from 1 to 8 QPS. Decode prefix caching is disabled to force full P→D KV transfer for every request.

The modes perform similarly for light load and short inputs. At 8 QPS and 16k input tokens, pull TTFT is approximately 1,744 ms versus 540 ms for push, a roughly threefold difference. In the long-input, high-load region, pull TPOT reaches about 10.4 ms versus roughly 7 ms for push. At light load, both are around 5.6–5.8 ms. The benefit is tied to control overhead under pressure, not a fixed multiplier.

Disabling prefix caching isolates transfer performance but limits the interpretation. Frequent local decode-cache hits can bypass full KV movement, changing the aggregate benefit. The authors built and validated the feature on Trainium clusters, but the performance plots here come from P5en GPUs. Their numbers do not directly describe Trainium or another network.

## Interpret the result through a timeline

The protocol suggests separating destination registration, source computation, handoff preparation, actual transfer, and generation start. This is an analytical decomposition: push primarily overlaps the first two and moves preparation away from the decode loop. If the link is already saturated, changing handoff order does not eliminate bytes. If short-request model computation dominates, the exposed control-time saving can also be small.

Environment details further explain why an isolated multiplier is insufficient. Each test instance has sixteen EFA interfaces with 3.2 Tb/s aggregate advertised bandwidth. NIXL's LIBFABRIC backend opens all interfaces as rails but registers each GPU's KV only on the two rails sharing its PCIe switch, preserving transfer locality. Hardware topology and registration affect effective movement; aggregate advertised bandwidth is not per-request effective bandwidth.

For an existing service, first establish whether descriptor preparation actually blocks decode, then weigh early reservation costs. Changing network, cache behavior, routing, and threading together can improve the whole system without revealing which change matters. The article's paired comparisons keep model, input lengths, arrival rates, and output lengths aligned to make the mechanism more interpretable. The evidence remains tied to this topology and disabled decode prefix caching.

## What early destination commitment buys

Pull can choose decode after prefill, allowing routing based on current load and quality-of-service needs. Push chooses earlier and reserves blocks to obtain overlap. This is a meaningful trade-off: destination load may change during a long prefill, and reserved resources have a lifetime. The article therefore retains pull for workloads requiring late destination selection or bidirectional KV transfer.

Both endpoints need `NixlPushConnector`, and the proxy must follow its protocol. Read registration, rendezvous, completion handling, and thread responsibilities before the performance plots. The authors also propose bringing background NIXL preparation to pull, showing that some gains arise from asynchronous implementation rather than an inherent advantage of push in every design. The transferable lesson is to identify which control steps are exposed on the token-generation path and decide how much early resource commitment their overlap justifies.
