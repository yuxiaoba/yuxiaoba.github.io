---
id: train-inference-consistency
title: '2026-10-14 | Bitwise Training–Inference Consistency: Keep Low Precision, Fix
  the Computation Path'
date: '2026-10-14'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- self-improvement
summary: Shared inference kernels and aligned quantization and reduction yield zero
  mismatch on two architectures, with explicit training costs and baseline limits.
translation_source: assistant
authorship: assistant
source_url: https://blog.vllm.ai/blog/2026-10-14-train-inference-consistency
permalink: /tech/en/train-inference-consistency/
long_read: true
published_at: "2026-10-20T10:46:23.513966+08:00"
updated_at: "2026-10-20T10:46:23.513966+08:00"
---
In reinforcement learning, an inference engine samples trajectories while a training engine recomputes token probabilities and updates parameters. If identical weights and prefixes produce different probabilities, the optimized policy numerically differs from the sampling policy. Low precision, dynamic batching, and different parallel layouts can compound this mismatch. This vLLM engineering report pursues bitwise agreement on the high-performance deployment path while retaining most rollout throughput.

Original: [Finish RL Training Faster: Bitwise-Consistent, High-Performance, Agent-Driven](https://vllm.ai/blog/2026-10-14-train-inference-consistency)  
Yan Bai (NVIDIA DevTech), Ao Shen (Inferact) · Published: 2026-10-14

## Zero mismatch requires a precise comparison

Before each update, the article compares rollout logprobs with training-side recomputation for valid response tokens under the same weight version and prefix. Maximum, mean, standard deviation, and k3 KL must be exactly zero. This excludes ordinary policy changes caused by updates and does not remove stale-weight sampling in asynchronous training. The recipe uses one update per step to make these boundaries explicit.

Fixing a random seed is insufficient. A request can use different matrix kernels in different batches; prefill and decode can use different attention algorithms; MoE outputs can be merged in different orders. Floating-point accumulation changes can affect the last bit, while discrete Top-K decisions turn small differences into different contexts or expert sets. Alignment must cover computation paths, quantization, tie-breaking, and accumulation order as well as inputs.

## Training forward adopts inference numerics

The authors use inference kernels as the numerical reference. Training forward calls modified vLLM operators and adds backward separately. BF16 master weights remain, with deployment-matched quantization during forward and a straight-through estimator for FP8 quantization. This retains low-precision inference but places intermediate storage, backward implementation, and gradient verification on training. Matching forward values does not prove correct gradients; those require an independent reference.

DeepSeek-V4-Flash dense GEMM uses batch-invariant DeepGEMM, giving up some small-batch kernel switches. Sparse-attention Top-K fixes tie selection and index order so the same selected set also accumulates in the same sequence. MoE aligns quantization rounding, row computation, and expert-output merging rather than relying solely on routing replay.

<a class="note-image-link" href="/assets/images/tech/train-inference-consistency/ds4-fp8-kv.png" target="_blank" rel="noopener" aria-label="A shared FP8-KV read path for prefill, decode and training · View original image ↗"><img src="/assets/images/tech/train-inference-consistency/ds4-fp8-kv.png" alt="A shared FP8-KV read path for prefill, decode and training" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Above, the phases use different read algorithms. Below, storage stays FP8 while all three paths dequantize and gather before the same attention operator.*

FP8 KV illustrates the trade-off. Previously, prefill dequantized its inputs while decode used a separate direct-FP8 path. The consistent implementation makes decode gather and dequantize to BF16 before calling the same sparse-attention operator. Training uses a private cache copy to reproduce the FP8 round trip. Storage remains FP8, but decode pays extra preparation cost. This path currently excludes MTP and speculative decoding.

Cross-GPU consistency has explicit restrictions. The DeepSeek recipe requires TP=1 to avoid tensor-parallel reductions in the compared path. Expert outputs return to the token's owning GPU and merge in FP32 in fixed slot order. CUDA Graph requires agreement with eager execution, stable workspace addresses, in-place weight updates, and checking the first step after restoration. This is not a guarantee for arbitrary parallel configurations.

## Two experiments, with their denominators

The DeepSeek-V4-Flash-Base experiment uses DAPO-format math tasks, GRPO, and an over-length penalty. Each run uses eight machines with 32 GB200 GPUs, 128 prompts with eight responses each per step, and 100 steps. Both runs use one update per step without TIS, MIS, or similar corrections. Baseline train–inference KL rises from about 0.002 to 29.9 as reward falls back; the consistent run maintains zero mismatch at every step and retains its reward.

Mean consistent rollout throughput is 24.22 token/ms versus 26.53 for the baseline, or 91.3%. Baseline throughput falls after step 90; over the first 89 steps, the ratio is 88.6%. Response lengths also change differently across runs, so the ratio reflects workload changes as well as engine speed. Training-side overhead was not measured separately, and full recomputation adds forward execution.

The transfer experiment uses Nemotron-3.5-Lightning-30B-A3B, combining Mamba-2, attention, MoE, and NVFP4. Its SWE-bench Pro training subset contains 375 selected tasks. Each step samples eight trajectories for each of 32 tasks, averaging about 57K tokens per trajectory, with eight GB200 nodes per run. The baseline uses QAT and R3; both runs use one update per step and no TIS/MIS. From the first ten to the last ten steps, consistent training reward moves from 0.56 to 0.59 while the baseline falls from 0.56 to 0.22. Over the first 30 steps, consistent rollout throughput is 87.5% of baseline. These are training rewards on a selected subset, not public test-leaderboard scores.

## Consistency has several layers

The verification order is useful engineering practice: first make inference agree between a request alone and in mixed batches, then compare whole-input prefill with token-by-token decode, and only then connect training. Otherwise, a mismatch between engines may originate from inference's own batch dependence. Finding the first divergent layer narrows diagnosis more than a final KL value, which may already reflect amplification through several discrete decisions.

Updated state is another easy omission. CUDA Graph captures memory addresses; synchronizing weights into newly allocated storage can leave the graph reading old locations. Agreement at the first step does not cover this lifecycle error. The article checks updates, export, reload, and post-checkpoint execution, extending verification from a fixed-input comparison to a real training loop.

Performance interpretation needs comparable care. The authors found that the consistent run used slower Ethernet RDMA while the baseline used faster MNNVL, mixing transport differences into the comparison. Matching conditions was necessary. The lesson is not that one network universally suits every model, but that both versions need equivalent performance maintenance; weakening a baseline cannot establish lower alignment overhead.

Nemotron adds recurrent arithmetic: decode replays prefill's chunked computation order and training reuses the operators, rather than merely approximating the final state. This supports transfer to another architecture but still requires operator-level work. Its reward plot also excludes consistent-run step ten because only a few trajectories returned. Smoothed trends must not be interpreted as if every step had an identical sample count.

## The agent workflow uses checkable engineering goals

The authors package first-divergence localization, minimal reproductions, forward alignment, gradient verification, checkpoint restoration, and incremental optimization into gates C0–C10. A small model retaining all operator classes supports early debugging; full depth, long contexts, and multi-GPU execution follow. Agents handle investigation and regression work, while people review baselines, precision decisions, and recipes. Engineering-time savings are not yet quantified.

**Assessment: a concrete study of numerical contracts and performance co-design.** Each baseline explores only one recipe and is not thoroughly tuned; its collapse does not establish that conventional RL recipes generally fail. The article also lacks an end-to-end wall-clock comparison to reach the same training target, so the title's faster-completion goal still needs long-run evidence. Zero mismatch removes one source of same-weight policy discrepancy. Training quality, gradient correctness, stale-policy data, and total cost remain separate questions.
