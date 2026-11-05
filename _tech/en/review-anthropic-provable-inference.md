---
id: review-anthropic-provable-inference
title: 2026-11-04 | Progress on provable inference for large language models
date: '2026-11-04'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://www.anthropic.com/research/provable-inference
tags:
- agent-reliability
- self-improvement
- observability
- inference-serving
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-anthropic-provable-inference/
---

FlashProve addresses which committed model performed a computation, rather than whether its answer is correct. A provider commits to hidden weights and produces a zkSNARK that anyone holding the commitment, input and result can check without the weights. It hides weights and expert choices, not architecture. Proving that approved inference occurred does not prove that the server performed no other work.

The implementation proves after the fact. Finished text is recomputed through a parallel, prefill-like path; work scales with the MoE experts actually used. Segmented host-to-device streaming lets one H100 work with substantial host memory. Evaluation uses 4-bit Llama 4 Maverick and integer arithmetic. Each request contains a 1,024-token window, but each proof checks one token. Proving 24 requests takes about 223 seconds: the quoted 110 tokens/s counts contextual processing, not 110 newly generated tokens proved each second. A proof is about 18.78MB and takes about 17 seconds to check on 24 CPU threads. Offline commitment takes around 39 minutes and has a request-count lifetime.

The trust boundary matters. Lean formalizes top-level properties in the random-oracle model and supplies an executable verifier connected to the soundness theorem. The everyday C++ verifier agrees in tests but lacks that formal guarantee. Correspondence between the prover implementation and formal protocol still requires auditing, particularly for zero knowledge. Humans must also assess whether the formal statements express the intended claims.

The authors report roughly 72–94× GPU-time overhead relative to FP8 vLLM. This is neither zero-overhead online attestation nor a same-numerics kernel comparison. Useful follow-up questions include sampled post-hoc verification, commitment lifecycle management and the interval between proof arrival and irreversible external actions. The repository explicitly describes an unmaintained research artifact. No proof generation, Lean build or independent cryptographic audit was performed here.

Proofs concern declared quantization, arithmetic and protocol, not original floating-point models, factual correctness or unchecked response tokens. Overhead, post-hoc delay and implementation correspondence remain deployment limits.



Implementation and documentation: [FlashProve](https://github.com/anthropics/FlashProve).

[Progress on provable inference for large language models](https://www.anthropic.com/research/provable-inference)
