---
id: "adaptive-verification"
title: "2026-10-14 | Online Verification Budgets Without a Confidence Head"
date: "2026-10-14"
lang: "en"
published: true
layout: "article"
maintenance: "daily-research"
source_type: "tech"
tags: ["inference-serving"]
summary: "An online acceptance estimator extends adaptive verification to more draft models; calibration, sampling correctness and throughput remain distinct."
translation_source: "assistant"
authorship: "assistant"
source_url: "https://blog.vllm.ai/blog/2026-10-14-adaptive-verification-online-estimator"
permalink: "/tech/en/adaptive-verification/"
long_read: true
---

Speculative decoding lets a cheaper draft model propose several tokens before the target verifies them. A longer draft can advance further in one step, but verification after a rejection can be wasted. vLLM's Adaptive Verification (AV) trims less promising draft tails using acceptance estimates. This update extends that budget control to existing draft checkpoints without a dedicated confidence head.

Original: [Adaptive Verification Without a Confidence Head](https://vllm.ai/blog/2026-10-14-adaptive-verification-online-estimator)  
Giancarlo Delfin (Inferact) · Published: 2026-10-14

## Draft confidence needs calibration to target acceptance

Earlier AV used a DSpark confidence head, a classifier predicting acceptance from hidden states. EAGLE, MTP, DFlash, and some DSpark checkpoints lack this head; adding one generally requires training. The new approach extracts a feature from the draft distribution and fits a tiny logistic regression online using acceptance labels already produced by normal verification.

A drafter assigning high probability to its own answer does not ensure that the target agrees. Model pairing, sampling settings, and workload all affect that relationship. AV must do more than rank candidates: it compares expected accepted-token counts with measured drafting and verification costs to choose an efficient budget. A ranking that is consistently overconfident can still allocate too much verification work.

## One shared slope and a bias for each position

The feature is the log-odds of the maximum probability in the draft distribution, not the probability of the token actually sampled. For position i:

$$\hat a_i=\sigma\left(\omega\,\mathrm{logit}(q_{\max})+\beta_i\right)$$

The estimate represents acceptance probability. Positions share a slope but have separate intercepts, requiring only K+1 parameters for K draft positions. Deeper positions are generally less likely to be accepted, which the intercepts can capture. AV then computes survival along a draft prefix; later tokens cannot independently survive a preceding rejection.

Sampling correctness is the crucial feature-selection constraint. If verification depends on the probability of the sampled token, surviving candidates no longer follow the original draft distribution, invalidating an assumption of standard rejection sampling. Such features achieved higher AUC in the authors' tests but were rejected because they bias output. Using the distribution's maximum probability avoids this particular selection bias; throughput optimization must still respect the speculative sampling protocol.

## Online fitting does not retain the entire sample history

Only tokens through the first rejection have usable verification labels. Drafts after that rejection must not simply be labeled negative. Over a fixed round, the implementation accumulates the gradient and Hessian for an IRLS update instead of keeping every raw record. Accumulated storage scales approximately with K squared rather than growing with round length and batch size.

Deep positions receive fewer labels and can become noisy. Sharing the slope reduces the degrees of freedom, and updates are scaled by supporting sample count so sparse evidence produces smaller changes. The fit can adapt to traffic without magnifying every rare observation. Online fitting does not mean training a new model for every request.

<a class="note-image-link" href="/assets/images/tech/adaptive-verification/auc-by-draft-position.png" target="_blank" rel="noopener" aria-label="Acceptance-prediction AUC by draft position · View original image ↗"><img src="/assets/images/tech/adaptive-verification/auc-by-draft-position.png" alt="Acceptance-prediction AUC by draft position" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Across seven zero-indexed draft positions, the orange estimator leads the blue confidence head from position one; higher AUC does not establish universal calibration or throughput superiority.*

## Prediction quality and serving speed are separate results

Using DeepSeek-V4-Flash + DSpark at temperature 1, top-p 0.95, concurrency 64, and with AV disabled, the author collected about 4.5 million labeled drafts from SPEED-Bench low/high-entropy workloads, GSM8K, HumanEval, and MT-Bench. The fitted feature has AUC 0.8336, log-loss 0.4284, and ECE 0.0100. Using the maximum draft probability directly gives ECE 0.0736; its mean prediction is 0.784 against observed acceptance of 0.723, illustrating why calibration matters.

The trained confidence head has lower AUC, 0.8191, but better ECE, 0.0052. The result supports an alternative for checkpoints without a head, not universal replacement. Position-level analysis favors the head at the first position and the estimator from the second onward. Both decline beyond the fifth position, which the author relates to this DSpark's training block size of five.

Serving experiments cover MiMo-V2.5-Pro-FP4 + DFlash, Inkling-NVFP4 + MTP, Muse-Glimmer-30B + DFlash2, and both DSpark scoring methods. At the same speculative length, online AV improves throughput across the tested datasets. Allowing fixed-length verification to choose a shorter length creates a stronger comparison. On MiMo's throughput/interactivity curve, AV lies on the frontier at five of seven concurrency settings. It reduces the burden of choosing a length, without winning at every concurrency.

## A counterexample: better prediction can still break sampling

The article illustrates bias with two tokens. Suppose the target assigns a and b probability one-half each, while the draft assigns 0.2 and 0.8. If verification is canceled whenever the sampled token has probability below one-half, drawing a causes fresh target sampling, while drawing b follows the usual acceptance/rejection procedure. The resulting output probabilities become 0.4 and 0.6 instead of the target distribution. Discarding low-confidence samples changes the sampling process itself.

Two questions must remain separate: whether a predictor distinguishes accepted from rejected drafts, and whether decisions based on that predictor preserve the correct distribution. Higher AUC answers only the first. A distribution-level feature restricts usable information so it does not depend on the current sampled outcome, then optimizes prediction within that constraint.

Serving has a related distinction: a budget controller needs expected output and expected cost. Even perfect acceptance estimates do not fix batch-dependent verification cost or recover drafting work already spent. Measured cost tables connect prediction to resource allocation. For engineers, the useful question is whether calibration and cost estimates track a changing workload together, rather than which predictor obtains the best static score. The article's slope/intercept analysis across datasets suggests different roles, but does not prove immediate convergence under arbitrary traffic bursts.

## Engineering boundaries

The target attention backend must support variable-length verification. Autoregressive drafters such as MTP and EAGLE have already spent substantial work producing tokens that may be trimmed, so their gains are generally smaller than those of DFlash and DSpark. Large batches, where the GPU is more compute-bound, provide a stronger opportunity to save verification work.

The feature is enabled through `enable_adaptive_verification`; the estimator is selected automatically when the checkpoint lacks a confidence head and backend requirements hold. Assess calibration, throughput, and interactive latency together, against several fixed speculative lengths. The most useful parts of this article explain why the feature cannot depend on the sampled outcome and how normal feedback can train a budget controller. The decision advances from how long a draft should be to which verification work is worthwhile under current conditions, subject to explicit sampling constraints.
