---
id: helion-compileiq
title: '2026-10-19 | Helion and CompileIQ: Adding Compiler Controls to Kernel Tuning'
date: '2026-10-19'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
long_read: true
source_url: https://pytorch.org/blog/one-search-two-layers-compiler-controls-inside-pytorch-helion-using-nvidia-compileiq/
tags:
- inference-serving
summary: Joint search, ACF artifacts, and GB200 microbenchmarks explain the benefits,
  compatibility constraints, and system-level limits of compiler tuning.
writing_source: assistant
translation_source: assistant
permalink: /tech/en/helion-compileiq/
published_at: '2026-10-22T08:44:53.471250+08:00'
updated_at: '2026-10-22T08:44:53.471250+08:00'
---
A GPU kernel can retain optimization headroom after its tiles, warp count, and pipeline stages have been tuned. Helion's integration with NVIDIA CompileIQ adds ptxas compiler controls to the search: one layer decides how work is assigned, while another decides how it becomes machine instructions. The important ideas are the coupling between those layers and a way to carry offline search results into later builds.

Original: [One Search, Two Layers: Compiler Controls Inside PyTorch Helion using NVIDIA CompileIQ](https://pytorch.org/blog/one-search-two-layers-compiler-controls-inside-pytorch-helion-using-nvidia-compileiq/)  
Aditya Srikanth (NVIDIA), Rupak Roy (NVIDIA), Abhinav Singh (NVIDIA), Jason Ansel (Meta), Clement Anthonioz-Blanc (Meta), Jongsok Choi (Meta) · First published: 2026-10-19

## Where autotuning stops

Helion lowers PyTorch-like expressions into kernels and searches configurations such as tiles and memory-access choices. Register allocation, instruction scheduling, and code-generation policies can still turn the same intermediate code into different machine behavior. The article packages controls for this layer into an Advanced Control File, or ACF, applied during compilation.

<a class="note-image-link" href="/assets/images/tech/helion-compileiq/lowering-stack.png" target="_blank" rel="noopener" aria-label="Helion lowering through Triton, PTX, ptxas and SASS, with the joint search boundary · View original image ↗"><img src="/assets/images/tech/helion-compileiq/lowering-stack.png" alt="Helion lowering through Triton, PTX, ptxas and SASS, with the joint search boundary" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: the left searches Triton configurations and leaves ptxas at defaults; the right evaluates ACFs alongside kernel configurations before producing GPU machine instructions.*

An engineering consequence is that the best tile depends on how the compiler handles its resource requirements. A larger tile may increase register pressure; allocation policy may change spills or occupancy, which then changes scheduling behavior. Freezing the upper layer before searching the lower one can miss a better combination. Joint search removes that ordering constraint, but a finite search budget does not guarantee a global optimum.

## A manageable artifact after search

Helion can pin an ACF through `advanced_controls_file`, or compare ACF and kernel-configuration combinations through `autotune_search_acf`. Default compiler controls remain a candidate. CompileIQ generates control files by compiling candidates, checking numerical correctness before timing survivors, and continuing the search.

From an engineering perspective, an ACF turns a tuning campaign into a selectable, persistent build input. That also creates a versioning responsibility. The file alone is insufficient: retain the target GPU, toolchain, kernel implementation, input shapes, and validation method. If any of these change, an old filename does not establish that the optimization remains valid.

Keeping a default candidate provides a useful comparison, but does not guarantee that enabling the feature cannot regress production performance. Measurement noise, input-distribution shifts, and contention can change the winner. A sensible workflow searches offline, validates independently, pins a configuration, and observes the actual workload. Putting compilation and measurement on the request path exchanges startup delay for an unconfirmed benefit.

## Microsecond gains need an explicit baseline

The main numerical example is an NVFP4 W4A4 decode GEMV with an existing AOT configuration, rather than a naive implementation. Tests use GB200/sm_100, ptxas 13.3.73, CompileIQ 1.0.3, and Triton 3.8.0. GPU clocks are locked, outputs checked against a PyTorch reference, and gains filtered through independent remeasurement, Welch's test with p<0.05, and Cohen's d>0.2.

For N=8192 and K=28672, compiler-control search with the Helion configuration fixed yields approximately 1.0485× and 1.0478× speedups in two validation runs. The first run reduces mean time from 0.09752 ms to 0.09301 ms. A separate search targeting runtime and L1TEX throughput yields about 1.0689×. These are results for a specific kernel, not equivalent whole-model gains, and not a comprehensive controlled comparison of joint tile-and-ACF search.

**Statistical separation does not imply equal system-level importance.** Deployment value depends on the kernel's share of execution time, invocation count, and maintenance cost. As an idealized calculation, if a kernel consumes 20% of execution time and speeds up by 1.05× while everything else stays unchanged, overall speedup is only about 1.01×. This is a time-share calculation, not an end-to-end result from the article.

## Return from proxy metrics to elapsed time

Occupancy and cache throughput can help identify bottlenecks, but neither is the user objective itself. Higher occupancy can accompany different instruction counts or memory behavior; a higher throughput percentage does not automatically imply shorter completion time. The article demonstrates different objective functions. Their proxy-metric improvements should be distinguished from independently measured runtime.

Multiple deployment shapes add another choice. The fastest configuration for one shape may be unsuitable for another. Sharing a configuration reduces artifact count but may sacrifice performance in particular cases. Evaluation should weight shapes by request frequency or service objectives instead of selecting the largest speedup. Rare shapes that dominate tail latency also need separate inspection.

## Turning search budget into deployment value

Amortization deserves a separate calculation. If offline compilation, timing, and review consume a fixed amount of work while each invocation saves only a few microseconds, sufficient cumulative calls are needed to recover that search expenditure. This is not an argument against small gains: a persistent hot path may amortize them quickly, while an infrequent path may not. Actual invocation volume matters alongside percentage speedup.

Correctness checks also have an input distribution. Passing reference comparisons for one shape, precision, and numerical range does not establish correctness for every value or boundary condition. Engineering validation should retain application-required tolerances and cover shape boundaries that may change execution. Tolerances should not be relaxed beyond application requirements merely to retain the fastest candidate.

Builds also need a fallback baseline. When a toolchain upgrade invalidates an ACF's compatibility, reverting to validated default controls makes diagnosis easier than continuing with a similarly named file under different conditions. Retained correctness and performance records help separate compiler changes, kernel changes, and input changes instead of combining them into unexplained benchmark variation.

Finally, independent remeasurement separates search-time selection from acceptance. Choosing the minimum observed time across many candidates is already more likely to select favorable noise. Increasing candidate count should not weaken acceptance criteria; small benefits make measurement conditions and workload representativeness especially important.

## Compatibility determines whether tuning can ship

ACFs depend on hardware and toolchain compatibility; a mismatch can produce incorrect results or runtime failures. The detailed example uses CUDA 13.3, whereas the described 24-file Helion Booster Pack targets B200 and is validated with CUDA 13.4 ptxas. They should not be treated as interchangeable artifacts. More candidates also add compilation and measurement work.

Licensing is another practical distinction. Helion is open source; the article describes CompileIQ as free to use under a proprietary NVIDIA EULA, while generated ACFs are freely distributable. Tool and artifact distribution conditions therefore need separate consideration.

**This is particularly useful reading for developers who already know their hot kernels.** It makes compiler controls a more accessible optimization space, while leaving profiling, correctness checks, and end-to-end evaluation essential. Read the search interfaces, experimental environment, and caveats before deciding whether a few percent merits the additional build and validation cost.
