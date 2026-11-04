---
id: llamacpp-kv-fallback
title: 2026-11-04 | When Quantized KV Cache Quietly Sends Attention Back to the CPU
date: '2026-11-04'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: A llama.cpp issue reports that some quantized KV Cache and FlashAttention combinations silently fall back to CPU, making displayed configuration differ from actual execution.
source_url: https://github.com/ggml-org/llama.cpp/issues/28455
permalink: /tech/en/llamacpp-kv-fallback/
translation_source: assistant-authored paired Chinese and English
---
An inference server may appear to use GPU FlashAttention while a particular KV Cache type combination causes its attention operator to run on the CPU. A [llama.cpp issue report](https://github.com/ggml-org/llama.cpp/issues/28455) describes a performance regression that is difficult to identify from the displayed configuration alone.

## What triggers the fallback?

The report says that, when the default build leaves `GGML_CUDA_FA_ALL_QUANTS` disabled, some quantized K/V types or mixed combinations lack a matching FlashAttention CUDA kernel. After the GPU backend rejects the operator, the scheduler assigns attention to the CPU. The reporter describes this as silent: the benchmark still displays FlashAttention as enabled.

On the reporter's RTX 4080, with a 27B model and the specified test setup, `llama-server` prompt processing was about 38.4 tokens/s with q5_1 KV and 1,348 tokens/s with q8_0 on the same machine. Rebuilding with the relevant option enabled yielded about 1,162 tokens/s for q5_1. This is a single-machine issue report involving different configurations and a rebuild; the ratios should not be generalized to every quantization scheme.

## What should an investigation check?

Server flags and benchmark parameters indicate **what was requested**, not necessarily **where each operator actually ran**. To investigate unusual time to first token, compare the exact version, build options and K/V types with actual operator placement and CPU/GPU utilization. Support differs by version.

The report also discusses a build option and possible runtime warnings. This note describes the reporter's reproduction and root-cause analysis; it is neither an independent reproduction nor a statement about all current versions. A social post in the input lists different hardware and a different speed ratio, so those figures are not repeated here.
