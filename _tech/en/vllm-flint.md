---
id: vllm-flint
title: '2026-10-22 | Flint on vLLM: lowering single-GPU long-context decode latency'
date: '2026-10-22'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Recursive Flint’s local/global attention, NVFP4 loading and small-batch kernels,
  separating model-forward latency from end-to-end speed.
long_read: true
source_url: https://blog.vllm.ai/blog/2026-10-21-flint
permalink: /tech/en/vllm-flint/
authoring_source: assistant
translation_source: assistant-authored bilingual editorial and translation
published_at: '2026-10-22T09:38:48.907626+08:00'
updated_at: '2026-10-22T09:38:48.907626+08:00'
---
How fast can a 40B-parameter MoE with roughly 2.5B active parameters per token run on one GPU? Active experts are only part of the answer. Full-history KV layers, low-bit loading and the number of small decode kernels also matter. vLLM's day-0 Flint article traces a concrete optimization path through these costs. Recursive's generative Flint model is separate from the similarly named FLINT multi-vector retrieval paper.

**Source: Inferact and Recursive / vLLM · First published 2026-10-21**  
Original: [Day-0 Support for Flint on vLLM](https://vllm.ai/blog/2026-10-21-flint). Figures below come from the official single-GB200 measurements.

## Only 14 of 49 layers retain full-history KV

Flint has 49 pre-norm layers, hidden size 2048 and a 262K-token context. Thirty-five layers use a 513-token sliding window with RoPE; the other 14 use full-context attention without positional encoding. Most layers therefore read local history while selected layers support long-range interaction.

The article reports full-history cache growth of 28 KiB per token. Long context still consumes memory: only part of the stack grows with the entire sequence, but window layers retain local state and weights, workspaces and runtime allocation require additional capacity. A 262K context capability alone does not establish concurrency capacity on an arbitrary GPU.

<a class="note-image-link" href="/assets/images/tech/vllm-flint/architecture.png" target="_blank" rel="noopener" aria-label="The top marks full and windowed attention layers; the lower panels show attention and MoE sublayers, including the shared expert alongside routed experts. · View original image ↗"><img src="/assets/images/tech/vllm-flint/architecture.png" alt="The top marks full and windowed attention layers; the lower panels show attention and MoE sublayers, including the shared expert alongside routed experts." loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*The top marks full and windowed attention layers; the lower panels show attention and MoE sublayers, including the shared expert alongside routed experts.*

Attention uses GQA with 32 query heads and 4 KV heads, per-head Q/K RMSNorm and learned attention sinks. The first two layers use dense MLPs. Other layers have 256 routed experts, sigmoid top-6 selection and a shared expert. Sparse activation reduces per-token computation, but weights must remain accessible; expert reads, routing and launch costs can dominate small batches.

## Separate the NVFP4 file format from runtime types

Flint ships separate NVFP4 and BF16 checkpoints. The NVFP4 checkpoint uses GGUF blocks corresponding to NVIDIA NVFP4 in a different byte order. vLLM losslessly repacks them at load time and runs W4A16, retaining BF16 activations and KV. This does not make all computation and cache storage 4-bit, nor does weight compression determine total request memory.

The authors state that Flint kernels follow the reference implementation's rounding points and match accuracy on GSM8K, GPQA-Diamond, long-context MRCR and a tool-calling suite. Numerical behavior is part of optimization. The article does not provide all benchmark scores or error distributions, so this supports a reported reference match, not token identity for every prompt or equivalent quality under arbitrary quantization settings.

## Reduce 1,096 kernel launches to 346

The first implementation used standard vLLM layers and ran 1,096 kernels per small-batch decode step, many tuned for larger batches. Flint-specific replacements fuse Q/K norm, RoPE and KV writes; specialize routing and expert GEMVs to read selected experts; and optimize small-batch dense GEMV, norm, SiLU and attention.

Fusion reduces launch and intermediate-processing overhead, while specialized GEMVs better match a few requests and active experts. Lower-precision parameters alone do not remove these costs. The optimized forward still uses 346 kernels, a multi-stage pipeline rather than one giant kernel.

For up to eight requests, the low-latency path uses seven kernels per MoE layer. Q/K norm, RoPE, routing and expert combination are fused into neighboring GEMVs. Programmatic dependent launch lets a later kernel begin weight loading while the preceding one is still running. This overlaps preparation under architectural and dependency constraints; it does not eliminate data dependencies.

## A 1.78 ms forward is not a complete output token

The reported decode setting is one GB200, batch 1 and 100K context; prefill uses a separate 8,192-token input:

| Measurement | Initial implementation | Optimized | Speedup |
|---|---:|---:|---:|
| NVFP4 decode model forward | 4.81 ms | 1.78 ms | About 2.7× |
| BF16 decode model forward | 3.53 ms | 2.34 ms | About 1.5× |
| 8K-token prefill | 207 ms | 145 ms | About 1.4× |

These are cumulative outcomes of successive changes; stage percentages should not simply be added. End-to-end served decode at batch 1 and 100K context is approximately 2.06 ms/token, or 485 tokens/s, including the LM head and sampling. The opening “about 500 tokens/s” summarizes that scale rather than supplying an independent model-forward measurement.

Interactive latency also separates TTFT from later-token latency. An 8K prefill time of 145 ms does not establish TTFT for a 100K prompt, and 485 tokens/s for one request does not establish aggregate high-concurrency throughput. The evidence locates and removes overhead at one declared hardware/shape combination, rather than establishing universal deployment speed.

## Compatibility extends beyond loading weights

Flint emits GLM-4.7-style tool calls and thinking blocks. The official integration uses `glm47` tool and reasoning parsers, and removes tool definitions when `tool_choice` is `none` to match reference prompt construction. Without compatible parsing, fast token generation may still fail to produce the structured tool responses an application expects.

Default sampling is temperature 1.0, top-p 0.95 and top-k 20. Reasoning counts toward `max_tokens`; the article recommends at least 32K for difficult tasks. This is part of the output budget, not additional free space. Equal final-answer lengths can therefore hide different reasoning costs, and latency comparisons need these conditions.

The specialized kernels target a single Blackwell GPU, TP=1 and BF16 KV. Other configurations fall back to standard vLLM layers. Running successfully and using the optimized path are distinct. The day-0 article also describes mainline support as being merged, so its specified image or code version matters; existing installations cannot be assumed equivalent.

The advance is translating hybrid attention, sparse experts and low-bit weights into a small-batch execution path while distinguishing forward and served latency. Read the architecture and stepwise optimizations first to identify gains from model design, layout and launch overhead, and the unanswered questions for other hardware, concurrency levels and context lengths.

## A cache calculation clarifies long-context cost

Using only the reported full-history growth term, 100,000 tokens times 28 KiB is approximately 2.67 GiB. This arithmetic example uses a decimal token count and is not measured total memory: window layers, weights and temporary storage are excluded. It illustrates how hybrid attention changes the growth slope and why context capacity and concurrency need separate accounting. Without cache sharing, this state demand also increases with the number of requests.

Low-latency optimization is shape-dependent too. Small batches can be limited by weight reads and launches; larger batches change matrix reuse, expert distribution and queuing. Savings for one request need not improve aggregate throughput proportionally. The article’s separate path for up to eight requests is an important boundary.

Day-0 support also combines operators, sampling, tool parsing and prompt templates. Numerical tests answer only part of that integration problem. For tool-using applications, correctly parsed responses and termination affect task latency and success. The article does not report those end-to-end task metrics, so its evidence concerns serving speed rather than complete agent-task quality.
