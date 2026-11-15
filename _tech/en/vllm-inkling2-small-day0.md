---
id: vllm-inkling2-small-day0
title: 2026-11-13 | Inkling 2 Small needs more than mixed precision
date: '2026-11-13'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Fused boundaries, six-head GQA packing and prefill sequence parallelism explain
  the conditions behind vLLM serving results.
long_read: true
source_url: https://vllm.ai/blog/2026-11-12-inkling2-small
permalink: /tech/en/vllm-inkling2-small-day0/
translation_source: assistant
authorship: assistant
source_published_at: '2026-11-12'
published_at: '2026-11-13T08:46:43.062448+08:00'
updated_at: '2026-11-13T08:46:43.062448+08:00'
---
Inferact and Thinking Machines; work led by Aurick Qiao and Woosuk Kwon · 2026-11-12  
Original: [Inkling 2 Small on vLLM: Day-0 Support](https://vllm.ai/blog/2026-11-12-inkling2-small)

Inkling 2 Small's day-zero vLLM support contains concrete engineering beyond model loading: mixed precision reduces expert storage, boundary fusion avoids repeated hidden-state movement, and a dedicated attention kernel repairs a shape-triggered slow path. Like the Rubin work, it emphasizes data movement, but here the central problem is mapping a new architecture onto existing execution paths.

## Architectural changes that affect execution

The model has 594B total and 17B active parameters, with 48 layers in a five-to-one sliding-window/full-attention pattern. All MoE layers select eight of 384 experts, without shared experts. The first forty layers use NVFP4 experts and the last eight MXFP8. A new 23-layer ViT handles image input; output is text. A 1M context capability does not imply that capacity at every concurrency.

Block attention residuals mix previous six-layer block outputs using a learned query. Short convolutions remain, and attention adds a gate and sink, creating more operations over the same hidden states between sublayers. Four Over Six quantization tries scales mapping each sixteen-element block maximum to either six or four, selecting lower mean absolute reconstruction error. Execution must preserve these layer-specific numerical choices rather than applying one low-precision format everywhere.

A five-layer DSpark draft with an RNN head proposes seven tokens per step. Proposal length is not acceptance length, which remains workload- and sampling-dependent.

## Fuse decode boundaries and distribute prefill work

A sublayer boundary can require all-reduce, short convolution, residual update, block mixing and RMSNorm. vLLM combines them in allreduce_conv_mix, using NVLink multicast for reduction and retaining subsequent work in registers where possible. PDL overlaps a dependent kernel's preparation with its predecessor's tail, benefiting chains of short kernels at small batches.

Routing and SwiGLU kernels also perform activation quantization as they produce data, eliminating a separate pass. Prefill addresses a different redundancy: plain TP repeats convolution, mixing and normalization for all tokens on every GPU after all-reduce. Sequence parallelism instead reduce-scatters, processes only each GPU's token slice, and all-gathers for the next GEMM. The authors report 22%/26% lower 8K-token prefill step time at TP4/TP8 and 1.3–1.9 GiB more memory per GPU for KV.

## Six query heads expose an attention slow path

With 48 query heads and eight KV heads, GQA is 6:1. The previous FlashAttention-4 decode path did not enable GQA packing at that ratio, reducing reuse of the same KV.

A new Gluon kernel packs the six query heads into a 64-row tile and reads KV once. A TMA warp streams KV, a tcgen05 warp handles MMA, and four softmax warps apply relative bias. At batch one and 100K context, the reported decode step falls from 15.1 to 4.8 milliseconds. This is a specific long-context path, not an arbitrary-length whole-model speedup.

The source's architecture and fusion figures are interactive embeds. This note uses a textual explanation because no directly usable static mechanism figure was obtained.

## Long-context serving results depend on reuse

Serving tests use TP8 across two four-GPU nodes, probabilistic DSpark drafting and prefix caching. Each turn appends the previous answer and approximately 2K tool-output tokens, adding about 3K new tokens, then generates 1,024 with reasoning enabled and temperature 1.0. At roughly 100 tokens/s/user, 32K contexts deliver about 1,070 output tokens/s/GPU with 84 sessions and 91% cache hits. At 256K, these become about 450, 37 and 99%.

These are **output-throughput** numbers and cannot be compared directly with Rubin's total-token metric including cached input. The TP4 single-user result of about 630 tokens/s with acceptance length 3.5 is another operating point; seven proposed tokens are not seven accepted tokens.

The authors retain reference dtypes, with differences including reduction order and BF16 all-reduce partials. They report matching scores with and without DSpark on NIAH up to 1M, MMMU-Pro and HLE, but do not provide the complete score breakdown here. This does not establish token-for-token equivalence for every prompt. The engineering lesson is that GQA ratios, residual structure and quantization expose assumptions inside old kernels; high-quality day-zero support must address those execution paths.
