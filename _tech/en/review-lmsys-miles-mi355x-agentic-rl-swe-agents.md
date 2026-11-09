---
id: review-lmsys-miles-mi355x-agentic-rl-swe-agents
title: '2026-10-29 | Training SWE agents with Miles on MI355X: taming long-tail trajectories
  and complex sandbox coordination'
date: '2026-10-29'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://lmsys.org/blog/2026-10-22-miles-mi355x-agentic-rl
tags:
- agent-reliability
- coding-agents
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-lmsys-miles-mi355x-agentic-rl-swe-agents/
long_read: true
summary: "Separating trajectory tails, sandbox limits, scale-out throughput and infrastructure-induced reward errors."
---

## Why one sample can hold up training

Miles trains SWE agents on MI355X using complete code-editing episodes: read an issue, call tools, edit code and receive a repository-test reward. Attempts at the same task vary in length, while a GRPO group needs its attempts to finish before scoring. The article reports that 32% of rollout time occurred after 90% of trajectories had completed, leaving near-single-sequence decoding in the tail.

Training and inference run on separate nodes. Harbor manages per-trajectory sandboxes; Miles supplies finished trajectories to Megatron-LM and returns updated weights to SGLang. Asynchronous training reduces waiting, while length caps curb unsuccessful looping. Step time falls from 850 to 284 seconds on the same eight-GPU inference node. That comparison is separate from scale-out throughput.

## KV capacity and CPU sandboxes impose different limits

Without an engine context cap, a few requests grew to 113K–186K tokens; roughly ten filled a 1.5M-token KV cache and other requests timed out in the queue. A 64K engine cap addressed this runaway case. Per-turn output limits do not bound accumulated context, which also includes tool results.

Moving sandboxes to E2B cloud microVMs reduced median startup to 1.9 seconds, but agent installation and testing slowed on two-vCPU instances and tunneled calls added overhead. At 384 concurrent trajectories, engines used at most 23% of KV capacity: sandbox concurrency was the limit. Fixed HTTP-pool, proxy-CPU, Docker-network and download caps also required changes. Infrastructure errors must be recorded separately and filtered because scoring them as zero rewards penalizes the policy for failures it did not cause.

## Read results with their resource and sample scope

Rollout throughput rose from about 860 to 3,480 trajectories per hour while inference expanded from one eight-GPU node to three and sandbox/concurrency settings changed. This is not a fourfold fixed-hardware software gain. Qwen3-30B-A3B-Instruct received SFT on about 4,000 traces, then RL on about 1,350 SWE-smith tasks. On a stratified 100-task SWE-bench Verified subset with four attempts per task, reported pass@1 moved from 7.3% to 12.8% after SFT and 27.5% after RL.

My interpretation is that the article is most useful for diagnosing cross-layer waiting in agent RL, rather than selecting a GPU. Step time, completed-trajectory throughput, sandbox failures and policy quality need separate accounting; collapsing scaling, caps and infrastructure repairs into one speedup hides resource budgets and reward contamination.

Source: [Original engineering article](https://lmsys.org/blog/2026-10-22-miles-mi355x-agentic-rl)
