---
date: '2026-10-28'
published: true
layout: article
maintenance: daily-research
authoring_source: assistant
translation_source: assistant
id: sglang-request-isolation
title: '2026-10-28 | SGLang: when is a terminated request’s KV memory reusable?'
lang: en
source_type: tech
long_read: true
source_url: https://www.lmsys.org/blog/2026-10-26-cf-security
tags:
- inference-serving
- systems-reliability
summary: How asynchronous RDMA writes motivate deferred release, drain acknowledgements,
  and carefully bounded timeouts.
permalink: /tech/en/sglang-request-isolation/
published_at: '2026-10-28T15:24:19.938525+08:00'
updated_at: '2026-10-28T15:24:19.938525+08:00'
---
The central issue in SGLang’s report is a hidden lifetime: a request has terminated, yet a remote engine can still write its KV pages. Marking the request aborted cannot recall work already submitted to a transfer engine or NIC. In disaggregated serving, memory ownership must outlast every asynchronous operation that may touch it.

Original: [SGLang security update: improving request isolation](https://www.lmsys.org/blog/2026-10-26-cf-security) · LMSYS / SGLang · 2026-10-26.

### Separate admission failure from a lifetime race

The Cloudflare incident involved a rejected request continuing through handoff, allowing decode to read pages not populated by that request. Admission must stop that transition.

The related race is different: request A aborts during transfer, decode frees its slots, B acquires them, and A’s outstanding writes arrive afterward. Long contexts extend the transfer window; memory pressure accelerates reuse. Together they make a lifecycle mistake easier to trigger.

### Cancellation and completion answer different questions

The router should cancel prefill and decode together. That stops abandoned work from continuing indefinitely, but cannot recall posted writes. The engine must retain memory until the relevant senders establish completion.

<a class="note-image-link" href="/assets/images/tech/sglang-request-isolation/deferred-release.png" target="_blank" rel="noopener" aria-label="KV slots remain held while prefill ranks drain outstanding writes · View original image ↗"><img src="/assets/images/tech/sglang-request-isolation/deferred-release.png" alt="KV slots remain held while prefill ranks drain outstanding writes" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Decode’s hold spans the outstanding writes below it. Normal release follows all required acknowledgements; timeout release still assumes writes have stopped.*

Decode sends ABORT and holds KV slots, request-pool state, and metadata. Prefill drops unsent chunks and tracks launched work. Each relevant rank acknowledges only after draining; decode releases on the complete acknowledgement set. Generation tags prevent reused request identifiers from consuming stale acknowledgements.

A failed transfer call is not completion evidence. A timed-out Mooncake call may leave writes retrying underneath. The fix therefore withholds a drain acknowledgement after failed sends. The required invariant concerns writer lifetime, not whether an upper-layer exception has been handled.

### Timeouts need an external bound

Missing acknowledgements trigger a timeout fallback. Expiry alone does not prove that remote writes stopped. Safe release requires the hold to cover abort propagation, remaining chunks, and the outstanding-call tail. Bounded transfer batches help constrain that tail. Longer holds also consume more KV capacity during abort storms.

Optional PD checksums validate the received cache at handoff commit, adding a GPU read and synchronization. They can catch some corruption before that point, but cannot replace protection against later writes or establish ownership at every decode step.

### What the evidence supports

The report distinguishes a controlled single-pair overlap experiment, whose wrong-output demonstration emulates a late write, from a real RDMA late-arrival experiment with two prefill engines sharing decode. With the fix, the latter records hold, drain acknowledgement, and release, followed by baseline output.

A normal-path performance comparison uses 21 runs on 2×H100 with 1P1D Mooncake, 1,024 requests, concurrency 256, and seven repetitions per arm. Throughput deltas stay within ±2%, with confidence intervals spanning zero. That does not establish zero cost under cancellation storms or memory pressure.

For operators, the informative signal is whether holds resolve through `drained` or `timeout`. A timeout-heavy distribution warrants investigation of acknowledgement delivery and transfer tails. Router pairing, backend support, and compatible prefill/decode versions belong in the same deployment review. The official patch table distinguishes those responsibilities; a single feature flag does not cover every failure path.
