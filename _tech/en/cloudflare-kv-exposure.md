---
date: '2026-10-28'
published: true
layout: article
maintenance: daily-research
authoring_source: assistant
translation_source: assistant
id: cloudflare-kv-exposure
title: '2026-10-28 | Cloudflare’s KV exposure: why HTTP 200 missed a request-isolation
  failure'
lang: en
source_type: tech
long_read: true
source_url: https://blog.cloudflare.com/kv-cache-exposure-remediation/
tags:
- inference-serving
- systems-reliability
- observability
summary: How a context-capacity mismatch crossed rejection and handoff boundaries
  to expose stale KV pages.
permalink: /tech/en/cloudflare-kv-exposure/
published_at: '2026-10-28T15:24:19.938525+08:00'
updated_at: '2026-10-28T15:24:19.938525+08:00'
---
Cloudflare’s postmortem describes a testing gap: status codes and throughput looked healthy while responses could attend to another request’s KV pages. The failure concerned state ownership and request isolation, which a normal streaming response could not establish.

Original: [Cross-request KV cache exposure in the GLM-5.3 Workers AI model, and our remediation with SGLang](https://blog.cloudflare.com/kv-cache-exposure-remediation/) · Cloudflare · 2026-10-26.

### Separate impact, recovery, and disclosure

Cloudflare identifies 155 affected responses on Workers AI’s `@cf/zai-org/glm-5.3` between August 27 and September 9, 2026, all for prompts exceeding 681,280 tokens. It reports no other Workers AI model affected. Excluding company and researcher tests, observed traffic was consistent with ordinary long-context use; the investigation found no evidence of deliberate exploitation. That is an investigative finding, not proof exploitation was impossible.

The researcher reported the issue on September 8. Cloudflare reproduced it, disabled the model, and restored service after remediation on September 9. October 26 is the disclosure date.

### A rejected request still reached decode

The configured context window allowed 1,048,576 tokens, but the prefill KV pool held 681,280. Pool capacity depends on memory remaining after model loading; it is not automatically tied to the advertised context limit. Cloudflare knew about the mismatch but interpreted successful long-request responses as evidence the engine handled it.

SGLang marked oversized requests rejected and substituted a one-token placeholder to drain through internal batching. The single-node path eventually returned an error. In disaggregated mode, admission checked whether a request was finished rather than correctly handling its pending rejection. The placeholder proceeded through prefill and signaled transfer completion.

<a class="note-image-link" href="/assets/images/tech/cloudflare-kv-exposure/rejection-handoff.png" target="_blank" rel="noopener" aria-label="Normal handoff versus a rejected request reading stale KV pages · View original image ↗"><img src="/assets/images/tech/cloudflare-kv-exposure/rejection-handoff.png" alt="Normal handoff versus a rejected request reading stale KV pages" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*The healthy example writes all eight reserved pages. The rejected path writes one, yet decode reads the full reservation.*

Decode had reserved pages for the original prompt but received only the placeholder’s small KV transfer. It interpreted completion as readiness of the full request and attended over remaining stale pages. Reused pages were not zeroed, so those pages could contain another customer’s state. The diagram’s eight pages illustrate the mechanism, not the size of every affected request.

### Fix capacity and rejection independently

Cloudflare enlarged the pool to approximately 2.04 million tokens and patched admission to return the rejection before bootstrap, allocation, or transfer. The capacity change prevents valid long prompts from reaching that boundary; the engine fix protects other rejection cases and future configuration changes. Weights, quantization, parallelism, and memory allocation can all change the available pool.

Validation used the researcher’s reproducer and canary markers. Deployment checks now compare the running engine’s pool capacity with its context limit. The transferable improvement is to test whether rejection actually stops handoff and whether consumed pages belong to the current request, rather than infer correctness from HTTP success.

### Related memory hazards need different controls

The report also covers late RDMA writes and local offload/release races. They violate the same ownership principle through different mechanisms. Deferred release, bounded transfer batches, and integrity checks address those related risks. Per-page tags and formal verification remain ongoing work, not a completed proof of production safety.

For agent infrastructure, long-context testing should include isolation. “Stop computing,” “stop writing,” “stop reading,” and “safe to reallocate” are separate conditions even when the implementation calls all of them request termination.
