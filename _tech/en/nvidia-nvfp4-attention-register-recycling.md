---
date: '2026-11-26'
published: true
layout: article
maintenance: daily-research
translation_source: assistant
id: nvidia-nvfp4-attention-register-recycling
title: 2026-11-26 | How SM120 NVFP4 attention frees half a score tile
lang: en
source_type: tech
long_read: true
source_url: https://developer.nvidia.com/blog/how-to-optimize-nvfp4-attention-on-nvidia-rtx-blackwell-through-register-recycling/
tags:
- inference-serving
permalink: /tech/en/nvidia-nvfp4-attention-register-recycling/
summary: Packing probabilities releases register slots for the next tile’s matrix
  product.
published_at: '2026-11-26T08:45:51.058767+08:00'
updated_at: '2026-11-26T08:45:51.058767+08:00'
---
On RTX PRO 6000 Blackwell, lower-precision matrix multiplication can be fast yet have nowhere to put the next score tile. NVIDIA exploits a short interval when half of the current scores have already become packed probabilities and the other half still needs softmax work.

## Idle compute with almost no spare registers

SageAttention3 computes the query–key product QK and the probability–value product PV in NVFP4 on SM120. Rescaling probabilities before quantization makes better use of a narrow range of values. The original schedule completes QK, softmax, scaling, quantization and PV in order for each 128-column tile. Consumer warps remain busy during exponentiation and packing, but Tensor Core activity has gaps.

Four producer warps load data and eight consumer warps handle the arithmetic. Together they use 62,464 registers, about 95.3% of an SM's capacity. There is little room for a full second score tile. Transfers also need full tiles to use bandwidth efficiently, so halving every operation would introduce a different cost.

## Update normalization across the tile and reuse scores by halves

The optimized schedule still fetches all 128 columns of K and V. It holds scores in two 64-column register slots. First it updates the online-softmax state across the entire current tile and rescales the output accumulator. Only then can either half be consumed. Once the first half has been exponentiated and packed into NVFP4 probabilities, PV reads the packed representation. The original score registers can be overwritten.

Those registers receive the first half of the next tile's QK while work continues on the current tile's PV and remaining quantization. The other half follows the same pattern. By the start of the next iteration, its two score halves are ready. The prologue fills the first tile and the final iteration only drains it. Interleaving neighboring tiles in steady state removes idle intervals without double-buffering the full scores.

## Kernel speedup and video latency have different baselines

Reactor compared two NVFP4 kernels on a 96 GB RTX PRO 6000 Blackwell Server Edition, holding Q/K/V, packed inputs and log-sum-exp settings fixed. Batch size was one, with 24 heads of width 128. Synthetic causal attention at 8,192 tokens fell from 0.76466 to 0.46659 milliseconds, a 1.64-fold speedup. A captured 7,040-token noncausal LongLive input gained 1.18-fold. Core timing excludes input quantization and output-stride restoration.

The full-model comparison replaces selected BF16 attention calls with optimized NVFP4, retaining BF16 weights and other attention operations. In a moving OmniDreams scene with 2,045 frames and 256 chunks, warmed generation fell from 155.92 to 132.00 seconds, a 15.34% reduction. Helios gained 1.70% on a 33-frame output when only its largest self-attention calls changed. The former used one process per arm, the latter medians of three independent processes. Precision and kernel implementation both change in this comparison. The latency tables alone cannot determine output quality or isolate the contribution of register scheduling.


Atharva Joshi · 2026-11-25 · [How to Optimize NVFP4 Attention on NVIDIA RTX Blackwell Through Register Recycling](https://developer.nvidia.com/blog/how-to-optimize-nvfp4-attention-on-nvidia-rtx-blackwell-through-register-recycling/)
