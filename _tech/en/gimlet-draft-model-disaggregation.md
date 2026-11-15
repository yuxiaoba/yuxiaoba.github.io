---
id: gimlet-draft-model-disaggregation
title: 2026-11-13 | Disaggregating the drafter preserves fast decode
date: '2026-11-13'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Gimlet separates interactivity, TTFT and energy efficiency when placing draft-model
  phases, with explicit modeling assumptions.
long_read: true
source_url: https://gimletlabs.ai/blog/draft-model-disaggregation
permalink: /tech/en/gimlet-draft-model-disaggregation/
translation_source: assistant
authorship: assistant
source_published_at: '2026-11-10'
published_at: '2026-11-13T08:46:43.062448+08:00'
updated_at: '2026-11-13T08:46:43.062448+08:00'
---
Phillip Kuznetsov, Omid Azizi · 2026-11-10  
Original: [Disaggregating the Disaggregated Model](https://gimletlabs.ai/blog/draft-model-disaggregation)

Speculative-decoding optimization often focuses on the target model: verifying more candidates or improving acceptance. Gimlet asks a different placement question. If an accelerator drafts quickly but handles prefill poorly, why keep both draft phases on it? Its proposed split retains draft prefill on GPUs and places draft decode on a fast accelerator, while GPUs continue target verification.

## Faster drafting changes the best speculation depth

The draft proposes tokens sequentially and the target verifies them in parallel. Longer proposals can yield more accepted tokens but also more discarded work. The best length depends on draft latency, verification cost and acceptance, rather than increasing indefinitely.

An introductory model changes drafting from five milliseconds per token to five times faster, moving the optimum from nine to fifteen. The later system model uses eight milliseconds on GPU and 1.5 on the accelerator: the optimum moves from eight to fifteen, with peak interactivity rising from about 61 to 137 output tokens/s/request. These are different parameter examples, not one hardware measurement.

Faster drafting makes waiting for additional candidates less expensive, allowing a target forward to validate more useful tokens. That improves the generation experience; aggregate throughput also depends on stage capacities and resource ratios.

## Fast decode does not imply efficient prefill

GPU prefill processes many tokens in parallel, while small-batch decode is often limited by weight bandwidth. SRAM-centric devices can address the latter, but smaller capacity can require more chips. Speed and energy efficiency need not improve together.

The baseline model fixes input/output lengths at 4,096/512, disables prefix caching and allows fractional device ratios to match stage capacity. Draft decode costs are assumed to be 30 mJ/token on GPU and 150 on the accelerator. At draft length ten, draft decode's share of forward energy rises from roughly 5.8% to 22.4%. These are consequences of model parameters, not an energy ranking of Cerebras or any particular product.

## Moving draft prefill back to GPU

<a class="note-image-link" href="/assets/images/tech/gimlet-draft-model-disaggregation/figure.png" target="_blank" rel="noopener" aria-label="Draft prefill on GPU and draft decode on an accelerator · View original image ↗"><img src="/assets/images/tech/gimlet-draft-model-disaggregation/figure.png" alt="Draft prefill on GPU and draft decode on an accelerator" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Blue stages run on GPUs; the purple stage drafts tokens. Draft KV crosses devices, and target verification feeds accepted tokens back.*

Gimlet describes two deployment observations: one accelerator had slow draft prefill, another expensive draft prefill. The split sends the prompt to GPU target and draft prefill, then transfers draft KV to the accelerator for the draft–verify loop. It changes phase placement, not the assumed draft model or acceptance behavior.

The numerical evidence remains scenario modeling. In the slow-prefill case, accelerator draft prefill rises from ten to 150 milliseconds. At speculation length fifteen, moving it to GPU reduces system TTFT from 212.5 to 190 milliseconds while retaining fast-draft interactivity. In the energy case, accelerator draft prefill rises from 40,000 to 100,000 mJ/prompt, versus 20,000 on GPU. Splitting improves peak throughput/kW by approximately 17%. These scenarios change separate parameters; they are not simultaneous measured gains from one deployment.

## System costs outside the model

The analysis assumes fixed batching, omits prefill–decode interference, and charges no latency or energy for KV transfer. Even mostly overlapped transfer can leave residual TTFT cost. Fractional resource ratios also avoid deployment rounding, which can create substantial idle capacity in small systems.

Accepted length follows a saturating exponential. Cache hits, task-dependent acceptance and dynamic batches can all move the optimum. The article is strongest as an explanation of phase placement, not a universally transferable procurement speedup. DSpark additionally transfers hidden state between target and draft; the authors identify it as future investigation rather than a direct application of this linear-speculation model.

For heterogeneous serving, keep three objectives distinct: decode speed determines interactivity, prefill's critical path affects TTFT, and stage energy plus resource ratios determine efficiency. Disaggregating the drafter creates more room to adjust them, provided transfer, queueing and integer device allocation do not consume the gains.
