---
id: decagon-autoresearch
title: 2026-10-30 | Testing inference optimization agents against production traffic
date: '2026-10-30'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- agent-reliability
summary: Decagon's AutoResearch turns inference optimization into a repeatable cycle
  of diagnosis, experimentation and validation. Its central idea is to test proposals
  against the same workload, latency constraints and noise threshold before searching
  for the next bottleneck.
long_read: true
source_url: https://x.com/DecagonAI/status/2115511110120120437
permalink: /tech/en/decagon-autoresearch/
source_format: x-article
translation_source: assistant-authored paired Chinese/English reading notes
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-10-30T10:31:20.339125+08:00'
---
Decagon's AutoResearch turns inference optimization into a repeatable cycle of diagnosis, experimentation and validation. Its central idea is to test proposals against the same workload, latency constraints and noise threshold before searching for the next bottleneck.

**Source:** Pavi Dhiman and Cyrus Asgari, [Building an inference stack that improves itself](https://x.com/DecagonAI/status/2115511110120120437), October 28, 2026 (UTC).

## Build an environment that can refute a hypothesis

Endpoints differ in model, hardware, request lengths and latency targets. The team reconstructs redacted requests from production logs, retaining message structure, tool definitions and generation settings, and checks whether redaction changes token lengths or shared prefixes. Capacity tests increase arrival rates to build latency–throughput curves; production-shaped replays reproduce bursts and exercise autoscaling. An open-loop sender does not wait for earlier requests to finish, exposing queueing when the service slows.

Candidates and baselines share the request pool, arrival schedule and latency requirements. Repeated baseline runs establish natural variation; a gain must exceed this noise and survive repetition. Capacity sweeps warm the engine and reset prefix caches for each load step, whereas production-shaped tests let cache state evolve. Matching average request rate alone can hide differences in request lengths, prefix reuse and burstiness.

## Diagnose, delegate and measure again

The orchestrator combines logs, configuration and GPU profiles to identify bottlenecks. It examines operator time and execution timelines, including prefill interruptions to decode, CPU/GPU overlap and gaps between kernels. Diagnostic workloads vary one property at a time. Subagents investigate competing explanations and must return evidence, a concrete intervention, a prediction and a falsifying outcome. The orchestrator schedules experiments through a common evaluation harness.

A confirmed improvement becomes the new working baseline, followed by another diagnosis. Controls and ablations test combinations because individually useful changes can compete for the same resource. Shared records retain model, hardware, workload and engine version, including negative and conflicting outcomes. Humans review production changes, particularly the quality trade-offs of lossy techniques such as quantization.

## From acceptance to served throughput

Speculative decoding is evaluated with the same replay and latency constraints rather than treating offline acceptance as the final goal. The team adapts drafter data, sampling and training to the target and workload, comparing against both the production drafter and the starting checkpoint. Correctness and repeated serving tests remain necessary. The authors report up to 65% higher replay capacity from prefill–decode interval tuning on a Gemma 4 26B-A4B endpoint, and 34% higher throughput than the production drafter after adapting DFlash2 for the select-playbook endpoint. These are endpoint- and baseline-specific company results; the article does not provide a complete independent experimental audit.

The transferable lesson is the experimental control: falsifiable proposals, representative replay, a noise floor and human deployment decisions constrain the agent beyond a single attractive benchmark.
