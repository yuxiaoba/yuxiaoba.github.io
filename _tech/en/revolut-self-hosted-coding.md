---
id: revolut-self-hosted-coding
title: 2026-11-04 | How Revolut Tuned Coding-Model Serving on a Fixed GPU Fleet
date: '2026-11-04'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- coding-agents
summary: Revolut describes tuning, costs and operational controls for self-hosted coding models, with context, cache and parallelism sized to its workload.
source_url: https://ai.engineer/nyc/2026/talks/revolut
permalink: /tech/en/revolut-self-hosted-coding/
translation_source: assistant-authored paired Chinese and English
---
Coding-agent cost and user experience depend on more than model capability: request context, cache reuse and serving parallelism all matter. At [AI Engineer NYC 2026](https://ai.engineer/nyc/2026/talks/revolut), Revolut's David Abitbol described its self-hosted coding-model deployment. This note draws on the conference page and its talk transcript.

## Tune the workload on a fixed fleet

The speaker reports serving GLM 5.3 to roughly 2,000 engineers using about 56 B200 GPUs. Across the migration-to-stable period shown in the talk, the GPU count stayed fixed while request volume increased about 76% and time to first token fell from 14.26 to 1.68 seconds. Demand and configuration both changed over time: this is an internal operational observation, not a controlled measurement of one optimization.

The deployment sizes context to actual requests because a large reservation competes with concurrent requests for KV Cache. The speaker also discusses low-precision quantization on Blackwell, checking cache-hit rates for coding tasks, and testing whether eight-way tensor parallelism leaves a better KV budget than four-way parallelism even when the weights fit in four GPUs. Speculative decoding and prefill/decode disaggregation are mentioned as directions to evaluate; the talk does not isolate each technique's contribution.

## Balance experience, cost and control

The team's empirical target is a time to first token under three seconds; the speaker reports noticeable user complaints beyond five seconds. He reports a blended cost of about $0.30 per million tokens and a self-hosted bill roughly one tenth of the prior external-model bill. These are deployment-specific claims tied to its hardware, utilization and workload, not portable price estimates.

Self-hosting also brings operational responsibility: the talk discusses sandboxes and approvals that restrict agent actions, plus telemetry for incident investigation. The speaker's statements about regulation and data residency describe his organization's circumstances and do not establish compliance for other deployments.
