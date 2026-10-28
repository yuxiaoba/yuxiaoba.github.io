---
date: '2026-10-28'
published: true
layout: article
maintenance: daily-research
authoring_source: assistant
translation_source: assistant
id: minite-nvfp4
title: '2026-10-28 | miniTE: align numerics, learning, and complete RL cost'
lang: en
source_type: tech
long_read: true
source_url: https://www.lmsys.org/blog/2026-10-25-minite/
tags:
- inference-serving
- systems-reliability
summary: Separating TRIAGE’s update control from miniTE’s execution optimizations
  and their remaining system costs.
permalink: /tech/en/minite-nvfp4/
published_at: '2026-10-28T15:24:19.938525+08:00'
updated_at: '2026-10-28T15:24:19.938525+08:00'
---
miniTE’s useful result is broader than faster NVFP4 learner updates: it also documents a case where conversion and synchronization erase system gains. RL connects sampling, probability recomputation, backpropagation, and weight transfer. Giving both sides the same precision label does not guarantee matching token probabilities.

Original: [miniTE Technical Report: Stable and Efficient Reinforcement Learning with Native NVFP4](https://www.lmsys.org/blog/2026-10-25-minite/) · LMSYS / InfiX.ai · 2026-10-25.

### Follow the numerical execution path

The report distinguishes quantization error against high precision, additional checkpoint-conversion error, and differences between actual learner and sampler execution. Scaling granularity matters because sampling advances token by token while training processes whole responses. Tensor-wide activation maxima can give the same token different scales depending on its neighbors. Per-token scaling removes that dependency, but not every rounding, KV precision, reduction-order, or routing difference.

Diagnostics align token and expert identities before comparing codes and scales, expert outputs, and token log probabilities. Otherwise, routing permutations can look like numerical errors. A strict alignment configuration reaches roughly 10⁻⁸ gap over the measured interval, but changes multiple implementation choices together.

### Two complementary interventions

TRIAGE adjusts updates according to advantage and mismatch direction. Its gate attenuates negative-gap tokens in risky negative-advantage segments; bounded repair addresses negative segment offsets in positive-advantage responses. Risk uses 64-token segments, while repair uses 128-token segments. A small average gap can hide concentrated tail risk.

<a class="note-image-link" href="/assets/images/tech/minite-nvfp4/triage-risk.png" target="_blank" rel="noopener" aria-label="Update-direction shares and negative-tail depth in TRIAGE diagnostics · View original image ↗"><img src="/assets/images/tech/minite-nvfp4/triage-risk.png" alt="Update-direction shares and negative-tail depth in TRIAGE diagnostics" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*The top panel tracks directional risk; the bottom tracks negative-gap tails. Each model contributes one diagnostic trajectory, not a confidence interval across training runs.*

miniTE instead separates module wrappers, quantization policies, and GEMM backends. Contiguous buffers and device-side metadata reduce expert-tensor splitting and repacking. Computing amax during permutation or weighted SwiGLU avoids another full scan. Fusing scale-layout conversion with quantization removes extra traffic and launches. Forward and backward precision remain independent choices; lower-bit backward computation is not automatically faster.

These tracks use separate experimental configurations. TRIAGE quality results, strict-alignment gaps, and maximum miniTE throughput must not be combined into one supposedly measured system.

### Respect the timing boundaries

Main learner tests use Qwen3-30B-A3B on 8×B300, sequence length 4096, micro-batch one, and global batch 128. Across ten independent runs, the two miniTE paths with BF16 backward achieve paired speedups of 1.334× and 1.369×. Timing includes forward/backward work, communication, optimizer, and data loading, but excludes rollout and weight synchronization.

A separate eight-engine serving test forces 1,024 output tokens per request and reaches approximately 1.64× BF16 throughput. This is sampling-stack throughput. In an online RL recording, miniTE reduces the training stage from 47.04 to 42.56 seconds but increases conversion/synchronization from 9.94 to 55.26 seconds. Those two stages add 40.84 seconds overall and still do not constitute a complete iteration. The report says rollout gains did not offset synchronization cost in that run.

Learning quality is another comparison: step-999 checkpoints score 56.35% for miniTE+TIS, 54.57% for native NVFP4, and 58.84% for BF16 on an equally weighted five-task average. Repeated checkpoint evaluations do not provide independent training seeds.

**The contribution worth transferring is layered validation.** Operator agreement, long-run learning, complete learner timing, and conversion/synchronization answer separate questions. Local speed is useful only insofar as it improves learning under the intended resource and quality constraints.
