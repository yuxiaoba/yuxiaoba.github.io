---
id: flydsl
title: '2026-10-23 | FlyDSL in PyTorch: Hardware-Specific Kernels Join Backend Selection'
date: '2026-10-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: The eager, Inductor, and AOTriton entry points, with MI355X operator gains
  separated from request-level results and numerical constraints.
long_read: true
source_url: https://pytorch.org/blog/accelerating-pytorch-on-amd-gpus-with-flydsl/
permalink: /tech/en/flydsl/
translation_source: assistant
authorship: assistant
published_at: '2026-10-23T08:58:47.180720+08:00'
updated_at: '2026-10-23T08:58:47.180720+08:00'
---
GPU DSL improvements reach most model users only after entering common operator paths. FlyDSL's PyTorch integration places AMD-specific kernels behind existing APIs and backend selection. Applications need not replace every operation with custom calls, but different operators enter through different routes, with distinct support boundaries and evidence.

Original: [Accelerating PyTorch on AMD GPUs with FlyDSL](https://pytorch.org/blog/accelerating-pytorch-on-amd-gpus-with-flydsl/) · Joint AMD and Meta authors, Xiaobing Zhang et al. · 2026-10-21

## Explicit layouts bring optimization close to hardware

FlyDSL expresses mappings between threads, waves, tiles, and instructions in Python, lowering through MLIR. Layout algebra, LDS buffers, MFMA instructions, and synchronization boundaries control data movement. This suits architecture-specific templates where placement is part of the algorithm, at the cost of hardware-specific maintenance and tuning.

For example, GEMM's half-tile-interleaved path staggers computation and loading across wave groups, reusing already-consumed halves of LDS for later data. Attention's dual-wave pipeline overlaps one KV tile's softmax with another tile's matrix work. The gain comes from dependency and resource scheduling, not a syntax change alone.

## Three distinct entry paths

In eager execution, supported RMSNorm and TopK calls dispatch to FlyDSL when the optional runtime is available and enabled; other inputs retain existing implementations. Compiled GEMMs instead go through TorchInductor candidate filtering, benchmarking against ATen and Triton, and caching of the winner. Enabling FlyDSL adds a candidate rather than forcing its selection.

<a class="note-image-link" href="/assets/images/tech/flydsl/overview.png" target="_blank" rel="noopener" aria-label="FlyDSL eager, SDPA, and compiled execution paths · View original image ↗"><img src="/assets/images/tech/flydsl/overview.png" alt="FlyDSL eager, SDPA, and compiled execution paths" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: eager dispatch on the left follows input support, SDPA in the middle uses AOTriton's tuning database, and compiled GEMMs on the right benchmark candidates. All three paths ultimately execute on AMD GPUs.*

SDPA uses AOTriton's bundled precompiled attention kernels and tuning database to choose among FlyDSL, Triton, and AITER ASM. The article says an appropriate PyTorch build linked to AOTriton 0.14.2b or later provides this path without a separate FlyDSL package. FlexAttention uses a different API and compilation route and is outside the current integration described here.

## Performance numbers need their baselines

Operator measurements use MI355X steady-state execution, excluding compilation and initial tuning. Across 15 BF16 NT GEMM shapes, geometric-mean speedup is 1.10 times the faster ATen/Triton result at each shape. For 17 shapes each, MXFP8 and MXFP4 achieve 1.58 and 1.68 times ATen. The latter measurements start from quantized inputs and exclude quantization cost.

Across 24 grouped-GEMM cases, the geometric mean is 1.20 times Triton, covering uniform groups, projection-dimension changes, and uneven expert loads. RMSNorm ranges from 1.17 to 3.66 times ATen, with the peak arising in a particular unaligned dimension and more modest gains for typical aligned shapes. A peak for one shape is not an expected gain for every model layer.

For ten small-K TopK cases, geometric-mean speedup over ATen is 4.82 with deterministic algorithms disabled and 4.02 with them enabled. Comparisons need matching settings. Equal-valued index ordering and NaN selection can also differ from ATen, which matters for routing or evaluation that depends on stable indices.

## Whole-request experiments are closer to serving, with narrow conditions

The authors test Llama-3.1-8B-Instruct, Qwen3-32B, and Llama-3.3-70B-Instruct on one MI355X with TP=1, 256 input tokens, fixed 512-token outputs, and concurrency from 8 to 256. Baseline and treatment share serving settings and per-model KV cache, changing only the Inductor GEMM candidate list.

BF16 whole-request speedup peaks at 1.13 for the 8B model and 1.06 for the 32B model; the 70B results mostly remain within a measured 1.79% noise floor. BF16 reports medians from at least two ABBA-interleaved repetitions. MXFP8 and MXFP4 peak at 2.04 and 3.01, respectively, but each model–concurrency cell has one measured run. MXFP4 also leaves lm_head unquantized. Small differences therefore lack a variance-qualified interpretation.

The AOTriton attention release comparison is separate: forward ratios range from 0.92 to 2.34 and backward from 0.93 to 2.47, including regressions. Other kernels and tuning databases changed too, so the entire difference cannot be attributed to FlyDSL.

## API compatibility is not universal input coverage

Current primary support targets MI350-series gfx950. MXFP scaled GEMM requires specific row/column layouts, an E8M0 scale per 32 values along K, and K divisible by 128; incompatible layouts may introduce copies. Attention currently excludes FP32, and RMSNorm acceleration covers forward while backward retains the existing implementation. These conditions determine actual dispatch coverage and overhead.

Engineering evaluation should first identify dominant operators and shapes, then establish dispatch and numerical requirements. Communication, scheduling, or KV movement may hide a local GEMM improvement. Initial compilation and tuning also matter for short-lived services; steady-state operator charts do not answer cold-start economics.

## Dispatch is still several steps away from user latency

Consider a request spending only part of its time in the GEMMs that benefit, with the rest in attention, communication, scheduling, and output handling. Faster GEMMs do not automatically shorten those other components. Layout copies can consume some gains as well. An operator geometric mean describes the sampled test suite, not an online service weighted by time spent in each operation.

Autotuning also requires observing actual dispatch. One shape selecting FlyDSL and another selecting ATen is normal candidate selection, not installation failure. Conversely, enabling a candidate without confirming its use does not attribute later performance changes to it. Dynamic-length services should examine recurring shapes, reuse of tuning results, and compilation overhead for rare shapes.

Low precision introduces another quality question. The serving tests change kernel candidates within a precision configuration. They do not establish that replacing a BF16 application with MXFP4 preserves task quality. Quantization policy, scales, and unquantized layers all matter, so numerical and task-quality checks remain separate from speed evaluation. Separating precision changes from kernel changes makes the cause of improvements interpretable.

A useful reading order is to identify ordinary matmul, scaled GEMM, or SDPA first, then inspect layout and dtype requirements, and finally choose the matching baseline figure. Supporting an operator name does not imply one implementation across all input combinations. Nightly integration also makes pinned software builds important because configuration interfaces and available kernels can change.

For service maintainers, upgrade checks should record both correctness and dispatch changes. Even without application edits, a changed candidate set or tuning database can select a different implementation; performance changes need to be traced through that path.

**The useful mechanism is admitting specialized optimization into measured selection.** Multiple backends, shape-level benchmarking, and fallback for unsupported inputs make hardware-specific kernels comparable options. MI450 coverage, broader low precision, FlexAttention, fusion, and training extensions remain future work rather than capabilities established by these results.
