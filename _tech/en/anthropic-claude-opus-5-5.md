---
id: anthropic-claude-opus-5-5
title: '2026-11-08 | Opus 5.5: reading the cost curve and the model actually serving
  a task'
date: '2026-11-08'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- agent-reliability
- coding-agents
summary: 'The official Claude Opus 5.5 article combines efficiency claims with changes
  to serving policy. Three details matter for agent systems: cache-read pricing, the
  cost curve across reasoning effort, and fallback to other models when safeguards
  intervene. Actual serving behavior can matter more than the requested model name.'
translation_source: assistant
authoring_source: assistant
long_read: true
source_url: https://www.anthropic.com/news/claude-opus-5-5
permalink: /tech/en/anthropic-claude-opus-5-5/
published_at: '2026-11-08T19:33:04.213507+08:00'
updated_at: '2026-11-08T19:33:04.213507+08:00'
---
[Introducing Claude Opus 5.5](https://www.anthropic.com/news/claude-opus-5-5)  
Anthropic · 2026-09-22

The official Claude Opus 5.5 article combines efficiency claims with changes to serving policy. Three details matter for agent systems: cache-read pricing, the cost curve across reasoning effort, and fallback to other models when safeguards intervene. Actual serving behavior can matter more than the requested model name.

## Token prices and task costs are different evidence

The page lists prices per million tokens of $4 for input, $20 for output, $0.20 for cache reads, and $5 for cache writes. Input and output are 20% cheaper than Opus 5; cache reads are 60% cheaper. The claimed roughly 40% reduction for typical tasks at default settings also depends on using fewer tokens, rather than following directly from the price change.

For multi-turn agents, the benefit depends on reuse. Repeated system instructions and history may make cache reads substantial, but unstable prefixes or model switches can erase that advantage. Fast mode is priced separately at $8 input and $40 output, with a claimed speedup up to 2.5×. Combining ordinary-mode prices with fast-mode speed would misstate the trade-off.

## Evaluation settings change what a score represents

Most results in the main table use adaptive thinking at max effort. Terminal-Bench 4.0 instead uses xhigh, scoring 66.4% with a ±2.6-point standard error. Cost curves show multiple effort settings, including the default medium. The highest reported score and the lowest-cost setting are not one configuration.

Some evaluations enable production safeguards and fallback: intervened cybersecurity tasks use Opus 4.8, while biology and frontier-model-development tasks can use Opus 5. Those scores describe a policy-equipped service, not necessarily one model completing every step. AutomationBench uses a different rule: no fallback, with safeguard interventions counted as failures. Its 40.0% result cannot be interpreted interchangeably with success under another fallback policy.

WANDR uses offline search and fetch tools, programmatic tool calling, code execution, and a 980k-token task budget, differing from its original published setup. Such conditions are essential when judging relevance to another harness.

## Safeguards also change integration contracts

The article describes a pre-execution action classifier, an auditable sandbox, and code review, alongside model-level injection resistance and boundary-crossing evaluations. The announcement does not isolate the contribution of each control. It describes an automated behavioral audit of nearly 2,000 scenarios while acknowledging that evaluation awareness makes real-world behavior difficult to assess.

Preserved thinking also constrains prior-context editing for applicable API users. The page states that it applies to API accounts created on or after August 31, 2026, and that thinking mode cannot be switched off. Clients relying on history rewriting or disabled thinking cannot assume that replacing a model identifier preserves their integration behavior.

## What transfers to AgentOps

The article supplies pricing, evaluation conditions, and concrete fallback behavior relevant to costs and compatibility. It does not disclose the training architecture or full task-level experimental records. Customer anecdotes about long jobs are not controlled measurements of general speedup.

Operationally, task records should distinguish the actual serving model and fallback, reasoning effort, cache reads and writes, and final task outcome. That separates savings due to prices, token usage, cache reuse, and model substitution, while keeping safeguard interventions distinct from ordinary execution failures.
