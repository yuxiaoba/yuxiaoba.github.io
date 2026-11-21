---
id: inference-optimisation-skill-2026-11-20
title: 2026-11-21 | How a local inference tuning run distinguishes a gain from drift
date: '2026-11-21'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Two speeds on the same GPU rarely identify the change responsible.
translation_source: assistant
writing_source: assistant
long_read: true
source_url: https://github.com/sybil-solutions/inference-optimisation-skill
permalink: /tech/en/inference-optimisation-skill-2026-11-20/
published_at: '2026-11-21T08:47:17.687323+08:00'
updated_at: '2026-11-21T08:47:17.687323+08:00'
---
Two speeds on the same GPU rarely identify the change responsible. The sybil-solutions project turns local inference tuning into a sequence of experiments, from estimating limits through interleaved controls to qualifying a full cache under load.

sybil-solutions · 2026-11-16 · [inference-optimisation](https://github.com/sybil-solutions/inference-optimisation-skill)

## Identify which stage has room to improve

Measured bandwidth, bytes transferred per token, arithmetic and component sizes provide separate estimates for decode, prefill and KV capacity. On a B390 integrated GPU, Ornith reached 628 tok/s on 256K prefill against an estimated ceiling of 670–684. Single-user decode presented a different constraint: reaching 100 tok/s required useful speculative drafts, while depth-two acceptance was about 14%. That observation changed the target before further kernel tuning.

## Put the candidate between two controls

The workflow changes one setting and serializes control, candidate and control runs. A candidate must beat both neighbors and avoid a regression above the workflow’s 3% threshold elsewhere. This makes warm-up and device drift less likely to look like an improvement. The harness counts tokens from server usage records, records failed requests and looping output, and keeps the configuration ledger. Driver residency also matters on unified-memory devices, where container accounting alone can overstate available space.

## Require retrieval and concurrency at full context

Long-context retrieval and concurrent full-KV soak tests catch failures hidden by short-prompt speed runs. A configuration can advertise a larger cache and still lose access to distant information. Qualification from a clean pinned build checks that a development-only change has not become part of the result.

For Qwen3.8-27B on a B70, the project reports 25.0 tok/s for single-user llama.cpp Q4_K_M and 91.2 tok/s for vLLM with custom XPU kernels and EXL3 at 4 bpw. Engine, kernels and quantization differ, so the comparison identifies two operating points. A separate agent-session replay fell from 193 to 147 seconds, a measurement that also reflects prompt processing and repeated calls.
