---
id: humming-quantized-kernels
title: '2026-10-21 | Humming: Unifying Quantized Kernels Without Erasing Their Differences'
date: '2026-10-21'
lang: en
published: true
layout: article
maintenance: manual-research
source_type: tech
tags:
- inference-serving
summary: Quantization contracts, JIT choices, and the conditions behind end-to-end serving comparisons.
long_read: true
source_url: https://vllm.ai/blog/2026-10-21-humming
source_date: '2026-10-21'
permalink: /tech/en/humming-quantized-kernels/
authorship: assistant
translation_source: assistant
published_at: '2026-10-22T08:54:49.993592+08:00'
updated_at: '2026-10-22T08:54:49.993592+08:00'
input_urls:
- https://blog.vllm.ai/blog/2026-10-21-humming
---
Ant Group / vLLM Community · 2026-10-21 · [Original article](https://vllm.ai/blog/2026-10-21-humming)

Humming separates quantization representation, hardware selection, and CUDA execution components, then specializes kernels for workloads through JIT compilation. Its significance is not only a speedup plot: it is whether optimizations can be reused across formats and devices while preserving clear numerical and execution contracts.

<a class="note-image-link" href="/assets/images/tech/humming-quantized-kernels/jit-flow.svg" target="_blank" rel="noopener" aria-label="Original flow from quantization representation through configuration selection to JIT execution. · Open image"><img src="/assets/images/tech/humming-quantized-kernels/jit-flow.svg" alt="Original flow from quantization representation through configuration selection to JIT execution." loading="lazy"><span class="note-image-action">Open image ↗</span></a>

*Original flow from quantization representation through configuration selection to JIT execution.*

## A common interface must preserve numerical meaning

The [project repository](https://github.com/vllm-project/humming) exposes HummingLayer and quantized GEMM interfaces. Equal bit width does not imply equal numerical semantics. Scaling granularity, zero points, formats, and tensor layouts all affect execution and results. A common representation must express those distinctions rather than treating every low-bit tensor identically.

Treat import as a contract check: do weights, scales, and zero points have compatible shapes? Does repacking preserve element correspondence? Does padding affect valid outputs? Is an appropriate instruction path available on the target device? Successful loading alone moves many failures into real requests.

## Evaluate compilation against the serving distribution

A fast configuration for one matrix shape does not establish coverage of a serving workload. Batch-size variation, prefill/decode transitions, and skewed expert loads change the balance of computation and memory traffic.

Measure first compilation, cached execution, and the cost of encountering new shapes separately. Warm microbenchmarks help explain steady-state performance; startup latency and compilation-cache footprint matter for elasticity and multi-tenant deployment. Preserve both instead of optimizing only a fully warmed experimental point.

<a class="note-image-link" href="/assets/images/tech/humming-quantized-kernels/kernel-components.svg" target="_blank" rel="noopener" aria-label="Original CUDA component structure: compatible components are reused across execution pipelines. · Open image"><img src="/assets/images/tech/humming-quantized-kernels/kernel-components.svg" alt="Original CUDA component structure: compatible components are reused across execution pipelines." loading="lazy"><span class="note-image-action">Open image ↗</span></a>

*Original CUDA component structure: compatible components are reused across execution pipelines.*

## What changes in the end-to-end comparison?

The article reports roughly 14%–43% higher throughput for DeepSeek-V4.1-Flash on eight H20 GPUs with TP=8 when moving from Marlin W4A16 to Humming W4A8. Activations also change from BF16 to tokenwise FP8. This is therefore not a kernel-only substitution with all numerical settings held fixed. Keep model, format, concurrency, and hardware conditions attached to the result.

A stricter validation plan would first hold quantization semantics fixed while comparing backends, then evaluate the joint quality/performance effect of changing precision. Include numerical error, task quality, throughput, and tail latency so that faster output does not conceal a quality regression.

For MoE, record work per expert as well. Equal average load with a different distribution can substantially change the behavior of grouping and scheduling strategies.

## Test conversions and combinations

Start with small-tensor reference implementations and differential tests over scaling granularities, boundary values, irregular dimensions, and extreme activations. Then introduce changing batches, multiple experts, and complete models. This separates format-conversion defects from kernel arithmetic and model-integration problems.

Performance regression records also need configuration signatures: exported model format, device architecture, compiler, kernel options, and input shapes. An apparent backend regression can instead arise from changed dispatch or stale compilation artifacts.

The longer-term question is whether composition reduces maintenance effort, not merely whether another combination appears in a support matrix. A unified entry point is attractive for serving platforms and creates useful reliability questions across formats, hardware, and workload distributions.
