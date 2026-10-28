---
id: sglang-quantization-stack
title: 2026-08-01 | Four Layers for SGLang Quantization
date: '2026-08-01'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: SGLang separates checkpoint formats from hardware execution, alongside a
  measured quantization trade-off.
long_read: true
source_url: https://lmsys.org/blog/2026-07-31-cleaner-quantization-stack/
translation_source: assistant-authored paired Chinese/English notes
permalink: /tech/en/sglang-quantization-stack/
published_at: '2026-10-28T15:30:52.583960+08:00'
updated_at: '2026-10-28T15:30:52.583960+08:00'
---
**SGLang X Ascend Team · 2026-07-28**  
Original: [Toward a Cleaner Quantization Stack in SGLang](https://lmsys.org/blog/2026-07-31-cleaner-quantization-stack/)

Quantized serving involves more than selecting a low-bit kernel. An engine must interpret checkpoints, register parameters, load weights, transform layouts and execute on different devices. This engineering article separates those responsibilities so adding a format or a backend need not repeatedly alter one large class.

## Four layers instead of one coupled path

An older quantization method could own parameter definitions, loading, layout conversion, backend selection and kernel invocation. As formats grow, platform branches become entangled with format code, and equivalent operations may be implemented separately.

<a class="note-image-link" href="/assets/images/tech/sglang-quantization-stack/scheme.png" target="_blank" rel="noopener" aria-label="Four layers of SGLang quantization, view original image"><img src="/assets/images/tech/sglang-quantization-stack/scheme.png" alt="Quantization path from model entry through Config, Method, Scheme and Kernel" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: Config interprets checkpoint metadata, Method connects the layer interface, Scheme describes the format and parameters, and Kernel executes on hardware.*

Config selects the quantization path. A Linear/MoE Method adapts SGLang's layer interface and delegates to a Scheme. The Scheme defines format-specific parameters, shapes and loading; the Kernel handles backend-specific transformations and execution. The key boundary separates checkpoint semantics from hardware execution: compatible formats can share a kernel without embedding hardware logic in every format class.

In the offline loading path, Scheme owns parameter definitions and loading, while Kernel handles post-load transformations and execution. The same kernel can also run independently in online quantization. The migration is incremental; moving more backend selection into the platform layer is a future direction, not a claim that every format and device has already migrated.

## Measurements describe quantization, not a refactor speedup

For Qwen3-30B-A3B, the article reports 61.08 GB of BF16 weights versus 21.59 GB for W4A4_W8A8. Inter-token latency falls from 26.23 ms to 23.84 ms, while GSM8K accuracy drops from 91.1% to 89.4%. Time to first token rises from 2084.41 ms to 2299.51 ms: smaller weights do not imply improvement in every latency metric.

The appendix uses Ascend NPUs, tensor parallelism of four, 64 requests with maximum concurrency 64, and random input and output lengths of 2048; GSM8K uses 1,319 questions. These compare quantization schemes and do not isolate a performance benefit from the four-layer refactor itself. Results can differ across workloads, models and hardware.

## Engineering significance and boundaries

Format detection, parameter registration and loading can be tested on CPU, while hardware tests focus on transformations, kernel correctness and performance. New formats and kernels can be reviewed separately. For serving across hardware, clearer ownership also makes it easier to locate whether a failure belongs to format handling or backend execution.

The roadmap includes a capability registry, broader low-bit and hardware coverage, and paths for MoE, KV cache and communication. These are future work, not capabilities that this article establishes as fully delivered.
