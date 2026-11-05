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
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-lmsys-miles-mi355x-agentic-rl-swe-agents/
---

The Miles MI355X study finds long tails, sandbox startup and fixed concurrency caps bottleneck agent RL before GPUs. It separates roughly 3× faster steps from length caps on one node from roughly 4× rollout throughput after scale-out and fixes, and identifies infrastructure failures as contaminated zero rewards.

The 4× comparison increases inference nodes and is not resource-matched. Accuracy covers 100 stratified tasks, not the complete SWE-bench suite.

[Training SWE agents with Miles on MI355X: taming long-tail trajectories and complex sandbox coordination](https://lmsys.org/blog/2026-10-22-miles-mi355x-agentic-rl)
