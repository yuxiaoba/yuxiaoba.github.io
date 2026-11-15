---
date: '2026-11-14'
published: true
layout: article
maintenance: daily-research
translation_source: assistant
authorship: assistant
id: rounding-ml-formulas
lang: en
title: '2026-11-14 | Floating-point formulas: why real-number proofs miss zero gradients'
source_type: tech
long_read: true
source_url: https://www.robertj1.com/ai4science/rounding-bugs-in-ml-formulas/
tags:
- systems-reliability
summary: A concrete softmax failure explains rounding, formula rewrites and the limits
  of proofs.
permalink: /tech/en/rounding-ml-formulas/
published_at: '2026-11-15T15:56:49.257918+08:00'
updated_at: '2026-11-15T15:56:49.257918+08:00'
---
A formula proved correct over real numbers can still erase a small, representable gradient. Robert Joseph George and Sasha Rush begin with a softmax failure in TorchLean itself and make precision, operation order, and intermediate rounding part of the verification target. The infrastructure lesson is why mathematically equivalent rewrites can behave differently numerically, and what evidence can support a repair beyond a few random tests.

Original: [When Rounding Breaks Machine Learning](https://www.robertj1.com/ai4science/rounding-bugs-in-ml-formulas/) · Robert Joseph George, Sasha Rush · 2026-11

## Representable values can disappear in intermediate arithmetic

Immediately above 1, adjacent float32 values are separated by 2 to the power −23. Let q be the exactly representable value 2 to the power −25. Over the reals, (1+q)-1 equals q. Rounding the addition to float32 first produces 1, however, so the subtraction returns zero. The result was representable; adding it to a much larger value lost it.

Softmax turns this into a missing training signal. For logits [9,-9,-9] with target class 0, subtracting the maximum leaves a denominator of 1 plus two exp(-18) terms. Each is approximately 1.52×10⁻⁸ and disappears when added to 1. The computed target probability becomes exactly 1, making both loss and target gradient zero. Their true magnitudes are approximately 3.046×10⁻⁸, which float32 can represent. Subtracting the maximum prevents overflow but does not solve this cancellation.

## Repair the intermediate values, not just the output dtype

The article retains the sum T of the non-target terms separately and computes:

$$L=\operatorname{log1p}(T),\qquad g_0=\operatorname{expm1}(-L).$$

log1p computes log(1+T) without first rounding away T in the addition. expm1 computes exp(x)-1 without first rounding the exponential to 1. The expression equals p₀-1 over the reals but preserves small intermediate quantities. For the worked input, the authors obtain a nonzero gradient near −3.046×10⁻⁸.

The pattern extends to other formulas. Computing variance as E[x²]-E[x]² subtracts nearby large values. In the JAX example, [10001,10002,10003,10004] yields zero variance instead of 1.25; the documentation already offers a stable algorithm option. The tanh approximation to GELU can similarly lose 1+tanh(z) for negative inputs. Rewriting it as x·sigmoid(2z) preserves the same approximation while changing its rounding path. Documented numerical trade-offs must be distinguished from newly discovered defects rather than labeling every discrepancy an unreported bug.

## What FloatLib proves and what the experiments establish

FloatLib explicitly models formats and arithmetic in Lean. Its roundoff tactic combines operation-level rounding theorems into conditional forward-error bounds:

$$|\widehat y-y|\le r|y|+a.$$

The relative component scales with the result; the absolute allowance accommodates effects such as underflow. Finiteness and range premises still need justification, and Lean’s kernel checks completed proofs. Real-number correctness, error bounds for a particular floating-point program, and cross-library measurements concern different objects and coverage.

The current article lists 154 TorchLean operators, 162 entries including variants, and executable Lean rules for 159 entries. The main library comparison spans approximately 780 million outputs. A footnote reports generated forward-error bounds for at least one computation in 137 operators, with 96 computations yielding no bound. This does not support the intake summary’s claim of certificates for 152 operators. CPU and GPU results are separate: a float32 output does not establish intermediate multiplication precision, as illustrated by tested paths that use TF32 by default.

## Local repairs do not establish training-wide benefits

A small transformer-block example traces accumulated errors. Repairing the loss does not undo rounding earlier in the network. Some very low-precision results correctly round to zero, which algebraic rearrangement cannot prevent. Certain transcendental approximations also lack accuracy theorems, and modeled arithmetic still needs alignment with hardware.

The work provides local counterexamples, alternative formulas, and conditional proofs. It does not estimate their frequency in real training or establish improved final model quality. The source primarily uses interactive numerical visualizations rather than a reusable standalone architecture image; this note retains the equations and counterexamples to make the information-losing step explicit.
