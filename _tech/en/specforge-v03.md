---
id: specforge-v03
title: 2026-08-04 | SpecForge Separates Target Inference from Draft Training
date: '2026-08-04'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://lmsys.org/blog/2026-08-04-specforge-v0-3/
long_read: true
tags:
- inference-serving
summary: SpecForge Separates Target Inference from Draft Training
translation_source: assistant-authored paired Chinese and English
permalink: /tech/en/specforge-v03/
published_at: '2026-10-28T15:48:27.004821+08:00'
updated_at: '2026-10-28T15:48:27.004821+08:00'
---
[SpecForge v0.3.0: a Unified Disaggregated and Colocated Speculative Decoding Stack, and New Open SpecBundle Draft Models](https://lmsys.org/blog/2026-08-04-specforge-v0-3/) · LMSYS / SGLang · 2026-08-04

SpecForge v0.3 separates frozen target-model inference from draft-model optimization into producer and consumer pools that can scale independently. Previously both shared a lifecycle and fixed resource layout, making it difficult to adjust only the bottlenecked side.

In online disaggregated mode, patched SGLang servers capture target features, Mooncake carries the large tensors, and the control plane passes lightweight SampleRef metadata. Training workers resolve those references when assembling batches. Capture, delivery, and lifecycle contracts handle ownership and release, rather than letting a process boundary hide buffering and failure concerns. One entry point also supports online, offline, and colocated workflows and draft families including EAGLE3 and DFlash.

The team reports approximately 10% higher end-to-end training throughput than its earlier colocated implementation on an 8×H20 testbed with three SGLang servers and five training workers. This is a result for that topology and environment, not a universal gain. A training-serving consistency gate checks capture, training, export, and SGLang serving on a controlled example before a full training run.
