---
id: eagle-4
title: '2026-10-22 | EAGLE-4: adapt the drafting budget to hardware and load'
date: '2026-10-22'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: How adaptive trees and a low-rank candidate head work, with separate treatment
  of paper results, release measurements and high-load limits.
long_read: true
source_url: https://github.com/eagle-hq/EAGLE-4
permalink: /tech/en/eagle-4/
authoring_source: assistant
translation_source: assistant-authored bilingual editorial and translation
published_at: '2026-10-22T09:38:48.907626+08:00'
updated_at: '2026-10-22T09:38:48.907626+08:00'
---
Speculative decoding depends on more than draft accuracy. Proposing more tokens may increase accepted length per verification, but also adds drafting, verification and state-management cost. A tree that helps a small batch can slow a busy service. EAGLE-4 brings these costs into per-round decisions and reduces draft vocabulary-head computation. One drafter can change its workload across environments, within explicit release and engine limits.

**Source: EAGLE-4 Team / Eagle AI**  
Original: [EAGLE-4: One Flexible Drafter for All Batch Sizes and Hardware](https://github.com/eagle-hq/EAGLE-4) · [Paper](https://github.com/eagle-hq/EAGLE-4/blob/main/EAGLE4_Paper.pdf) · [Release support matrix](https://github.com/eagle-hq/EAGLE-4/blob/main/docs/support-matrix.md). The project announcement is dated 2026-10-20; release figures below use the current 0.1.1 documentation.

## Why a draft tree needs a cost model

Confidence-driven trees identify promising branches but do not establish whether another level is worth computing. EAGLE-Harness prices additional drafting and verification using latency tables indexed by hardware, batch, context length and verification width. Products of draft probabilities approximate the benefit in accepted tokens. Each round decides whether to deepen the tree, how many candidates to verify and how wide branches should be at the current load.

The paper summarizes local selection as:

$$\Delta A/\Delta C\geq\tau.$$

A is estimated accepted-token benefit, C is latency cost, and the threshold depends on the decision. Light loads permit deeper, wider trees; heavier loads favor shorter chains. Deeper-branch estimates are also less reliable. Autoregressive drafting can stop before computing the next step, avoiding work already spent on a parallel block's discarded suffix. The objective is benefit per time rather than accepted length alone.

## Retrieve vocabulary candidates cheaply, then score them exactly

Even a small drafter can spend much of its time in the output head. EAGLE-4 uses a low-rank head over the full vocabulary to retrieve candidates, then evaluates their exact logits with the original full-rank head. The low-rank stage selects candidates rather than supplying final probability estimates. Unlike a permanently truncated vocabulary, candidates can change with context, although retrieval quality still affects draft efficiency.

<a class="note-image-link" href="/assets/images/tech/eagle-4/draft-head.png" target="_blank" rel="noopener" aria-label="Blue is the LM head and gray the rest of drafting. Low-rank candidate retrieval reduces head cost; these bars do not measure complete serving latency. · View original image ↗"><img src="/assets/images/tech/eagle-4/draft-head.png" alt="Blue is the LM head and gray the rest of drafting. Low-rank candidate retrieval reduces head cost; these bars do not measure complete serving latency." loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Blue is the LM head and gray the rest of drafting. Low-rank candidate retrieval reduces head cost; these bars do not measure complete serving latency.*

In the paper's profiled draft forward, the full head accounts for 65.4% of 574 microseconds. Rank-512 and rank-128 variants reduce total latency to 326 and 255 microseconds. This locates the improvement but is not an end-to-end serving speedup: target verification, scheduling and sampling remain. Cheaper proposals and adaptive budgets complement each other by reducing cost per proposal and choosing how many proposals to make.

## Release measurements need engine and concurrency conditions

The research paper and released software are separate measurement sets. The 0.1.1 README summarizes Qwen3.8-27B on four NVIDIA B300 GPUs, temperature 0 and the SPEED-Bench client, relative to the same engine without speculation:

| Engine | 1 request | Client concurrency 8 | Client concurrency 64 |
|---|---:|---:|---:|
| SGLang | 3.42× | 2.09× | 1.39× |
| vLLM | 2.83× | 1.72× | 1.14× |
| TokenSpeed | 3.09× | 2.02× | 1.41× |

Each uses an engine-specific recipe, so the ratios do not rank the engines directly. Client concurrency can include queued requests rather than the batch running on the GPU; read it alongside each row's running cap. The 961.6 tokens/s figure in the [official announcement](https://x.com/EagleCorp/status/2112660683670323531) cannot substitute for these versioned rows. AMD results are separate: SGLang on one MI355X reaches 2.07× and 1.56× at concurrency 8 and 32. Those are not general ROCm performance guarantees.

## Distribution preservation has algorithmic and implementation conditions

Correct speculative sampling uses target verification and rejection correction to retain the target distribution; greedy decoding follows target choices. The paper handles a subtle selection problem: choosing when to stop based on tokens sampled in the current round could bias output. At positive temperature, it fixes each round's depth before that round starts, using information from the previous round.

The software still has numerical and execution-path limits. Current documentation reports a greedy comparison discrepancy at vLLM TP4 and concurrency 64 that exceeds its fp32 checking rule and remains under investigation. Temperature-1 distribution checks cover specified sampling settings only. Finite tests and theoretical distribution preservation provide different evidence. Verification method, numerical tolerance, sampling configuration and engine version therefore matter; “same output” does not establish token-for-token identity on every GPU and batch.

## Adaptation has not eliminated high-load regressions

The project's known limits are especially informative. With SGLang, TP4, running cap 512 and the default tree, ratios against no speculation are 1.03×/0.74×/0.61× at client concurrency 64/256/512. Automatic high-load policy remains under qualification and disabled by default; current guidance recommends no speculation above concurrency 64. This is a different setting from the paper's high-concurrency comparisons. Method potential does not establish a release-wide guarantee.

Calibration is also configuration-specific. Changing target, draft, precision, TP, attention backend or engine can invalidate costs. Online timing tracks some changes, but initial sampling, uncovered context intervals and compilation affect estimates. Representative acceptance behavior says more than a few startup prompts. Native no-speculation and a zero-proposal round that still retains draft state need not have equal overhead.

The advance is an adjustable speculative execution policy with integration into SGLang, vLLM and TokenSpeed. Prioritize the cost decision, candidate head and cell-by-cell support matrix: they explain benefits, overhead and qualification boundaries respectively. Low-latency services are a promising setting; for congested throughput and tail latency, the regression conditions deserve as much attention as the highest single-request ratio.

## Reading correctness marks alongside speed

The matrix distinguishes exact token agreement, near-tie numerical choices and fp32 arbitration. Floating-point operation order can swap nearly tied logits, but that explanation needs an explicit tolerance; it cannot excuse every divergence. The vLLM concurrency-64 row therefore carries a qualification even though its speed ratio exceeds one. Read correctness and performance together to understand the evidence in a cell.

Multiple backends also expose different capabilities. Matching engine hooks are required. TokenSpeed does not yet provide all live-cost measurement, native no-speculation and sampling paths; a static-mode startup check does not establish serve-mode qualification. A common entry point does not make backend behavior identical.

A longer draft helps only when additional accepted tokens repay its time. If verification becomes expensive with batch size, the best choice may be no speculation. Published regression regions make this trade-off inspectable. The next useful evidence is sustained benefit across independent starts, ongoing traffic and context lengths, accompanied by expanded correctness checks.
