---
id: nvidia-mlip-tensor-core
title: 2026-10-30 | Tensor Core acceleration for interatomic potentials with stability
  checks
date: '2026-10-30'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
summary: NVIDIA approximates FP32 with lower-precision products and checks errors
  in trajectories and structural relaxation.
long_read: true
source_url: https://developer.nvidia.com/blog/unlocking-tensor-core-performance-for-machine-learning-interatomic-potentials/
permalink: /tech/en/nvidia-mlip-tensor-core/
translation_source: assistant-authored paired Chinese/English reading notes
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-10-30T10:31:20.339125+08:00'
---
NVIDIA explores Tensor Core acceleration for the Point Edge Transformer interatomic potential, measuring not only matrix multiplication speed but also force error, energy conservation and structural relaxation.

**Source:** Anoushka Bhutani, Atul Thakur, Erica Tsai, Kristopher Keipert and Michele Ceriotti, [Unlocking Tensor Core Performance for Machine Learning Interatomic Potentials](https://developer.nvidia.com/blog/unlocking-tensor-core-performance-for-machine-learning-interatomic-potentials/), October 29, 2026.

BF16x9 splits each FP32 operand into three scaled BF16 components and accumulates nine products in FP32. TF32x3 splits operands into leading and residual components, evaluates the leading product and two cross-products, and omits the residual product. On a 17,280-atom workload, BF16x9 on Blackwell accelerated large GEMMs by 2.2–2.5 times. TF32x3 on A100 accelerated major GEMMs by 1.7–1.9 times and the complete molecular dynamics step by 1.5 times for the larger system. Smaller systems benefit less because launch overhead and non-GEMM work account for more runtime.

Single-point error alone does not establish long-term numerical behavior. In a 30 ps NVE trajectory of a 192-atom water box, the authors observed comparable bounded energy fluctuations for TF32x3 and FP32, while one-pass TF32 drifted more. In a 539-atom alloy relaxation, three TF32x3 runs reached the force tolerance in 218–222 steps; one-pass TF32 failed even after 1,000 steps. These findings are limited to the tested model and tasks, but illustrate a transferable evaluation principle: check both end-to-end performance and the numerical invariants the application needs.
