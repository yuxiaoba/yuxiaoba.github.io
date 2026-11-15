---
id: deepseek-ultrafast
title: '2026-11-15 | DeepSeek Ultrafast: speculative decoding and cross-server KV
  state'
date: '2026-11-15'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: Decode measurements on a coding workload, Redis ownership and RDMA cache
  transfer, and model, hardware, and interface constraints.
translation_source: assistant-authored bilingual content
long_read: true
source_url: https://github.com/basetenlabs/deepseek-ultrafast
permalink: /tech/en/deepseek-ultrafast/
published_at: '2026-11-15T15:30:22.801784+08:00'
updated_at: '2026-11-15T15:30:22.801784+08:00'
---
DeepSeek Ultrafast has two distinct points of interest: speculative decoding reduces the wait for generated code, while transferable KV state lets a multi-turn conversation continue on another serving replica. The first determines how many tokens a decode step emits; the second determines whether moving a request requires processing a long prompt again. Separating them clarifies both the high decode rate and the million-token context claim.

Source: [DeepSeek Ultrafast](https://github.com/basetenlabs/deepseek-ultrafast) · Baseten · Official announcement 2026-11-13; mechanisms below refer to repository snapshot `76766a97308b`.

## An execution path for a specific model and hardware

This Rust and CUDA engine targets DeepSeek-V4.1-Flash on `sm_100a` and `sm_103a`. Documentation requires CUDA 13 and specified multi-GPU B200, B300, or GB300 configurations. It does not promise general performance across models and accelerators. Repository components separate CUDA support, kernels, model handling, the engine, the server, and KV transfer; the server exposes the engine through HTTP interfaces compatible with common clients.

“From scratch” does not mean dependency-free. The README lists deepseek-recipe for prompt rendering and response parsing, tokenizers for tokenization, cuDNN/cuBLAS for the vision encoder, OpenCV for image decoding, and Velo for RDMA transfer. It also says coding agents could consult FlashInfer and SGLang source while optimizing kernels. Runtime implementation, third-party components, and development references are different facts.

## Decode rate combines step time and accepted tokens

Each decode step drafts a block of tokens and verifies it. Accepted tokens can be emitted together, so a 3.30 ms step does not imply one token every 3.30 ms. The README reports a mean acceptance length of 5.6 tokens per step. Block generation is essential to interpreting the output rate. Acceptance varies with request content; the demo rate is not a fixed property of the model.

| Author-reported configuration | 4×GB300, TP4 | 8×B300, TP8 |
| --- | --- | --- |
| Decode output rate | 1,740 tokens/s | 2,060 tokens/s |
| Step time | 3.30 ms | 2.71 ms |
| Prefill of 1,000,000 tokens | 13.2 s | 11.7 s |

Decode measurements use a specific request to implement Tetris and output HTML directly; the reproduction example disables thinking. Over 30 runs, TP4 step times range from 3.24–3.37 ms and acceptance lengths from 5.1–6.1. TP8 ranges are 2.69–2.74 ms and 5.3–6.1. Logs expose `average_iteration_ms` and `average_accept_length`, separating execution speed from acceptance efficiency.

The example client computes tokens/s between the first text output and stream completion, printing the initial wait separately. These rates exclude that initial delay and are not aggregate high-concurrency throughput. Million-token prefill is a separate measurement: it does not establish the same decode rate at a million-token context. The README does not provide a full matrix across tasks, long contexts, and concurrent workloads.

## Redis manages ownership; RDMA moves payloads

Servers retain recent conversations’ KV caches in host memory. If the next turn reaches another replica, that replica can locate the owner and transfer state directly between host memories over RDMA, avoiding repeated prompt computation. Redis holds the ownership directory and broadcasts changes; cache payloads do not pass through Redis. The design aims to reduce dependence on prefix-aware routing so load balancing need not keep every conversation on one machine.

Multi-turn requests require a session ID and return HTTP 400 without one. More fundamentally, sharing requires identical model, tokenizer, maximum sequence length, GPU count, and decode numerics. In `peer.rs`, the cache profile fingerprint includes configuration and tokenizer digests, TP size, and numerical-path information. Supporting both TP4 and TP8 does not imply that snapshots can be exchanged freely between them.

The directory represents ownership revisions with an epoch and increasing sequence number. Atomic Lua scripts perform lookups, claims, and checks; a claim with an obsolete expected revision receives a stale error. A new epoch after Redis restart invalidates old ownership revisions. This manages ownership validity, not full request recovery: losing cache hints without losing model state does not establish lossless continuation of every in-flight request.

## Protocol and capacity limits affect agent integration

The documented default capacity is 1,048,576 tokens, including prompt and output, with additional speculative headroom required. The HTTP body limit is 64 MiB, a separate constraint. JSON escaping, tool history, and image descriptions affect wire size, so a sufficiently large token window does not guarantee that a request body is accepted.

Compatibility also does not mean support for every client feature. Current documentation fixes temperature and top_p at 1 and rejects other values. Unsupported logprobs, structured-output controls, and tool definitions using `strict: true` are rejected before enqueueing. The server parses tool calls but does not execute client tools. Harnesses depending on these controls may encounter protocol issues before performance becomes the deciding factor.

## What this release establishes

The interesting combination is low-latency decoding with movable conversation state, accompanied by step-time, acceptance-length, and cache-compatibility details. Available evidence supports the authors’ measurements on a particular coding request and the mechanisms described by code and documentation. It does not establish universal superiority over other engines or end-to-end reliability during Redis or RDMA failures.

The license is Elastic License 2.0, restricting hosted or managed services that expose a substantial set of the software’s functionality to third parties. The release should be described as source-available rather than simply repeating the social announcement’s “open-source” wording. The repository offers a game-demo GIF but no suitable cache or execution architecture figure; this note uses mechanism explanations and a measurement table instead of treating demo imagery as design evidence.
