---
id: minimax-m31-flash
title: '2026-10-20 | MiniMax M3.1 Flash: Evaluating Low Prices Across Complete Agent
  Tasks'
date: '2026-10-20'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- agent-reliability
- inference-serving
summary: Checking M3.1 Flash evaluation conditions, sparsity claims, and token pricing
  while separating model speed from whole-task gains.
long_read: true
source_url: https://www.minimax.io/blog/minimax-m31f
permalink: /tech/en/minimax-m31-flash/
authoring_source: assistant
translation_source: assistant-authored paired Chinese/English technical notes
published_at: "2026-10-20T08:44:36.800552+08:00"
updated_at: "2026-10-20T08:44:36.800552+08:00"
---
Original: [MiniMax M3.1 Flash: Redefining Agent Performance and Cost](https://www.minimax.io/blog/minimax-m31f) · MiniMax · 2026-10-19  

## Long workflows and usage cost are the focus

M3.1 Flash brings complex business workflows, coding, Computer Use, and cybersecurity into one release. MiniMax identifies the anonymously operated Space Bunny as an early version and reports that it processed more than 200 trillion tokens. That describes the vendor’s claimed usage scale; it does not replace reliability, task-success, or application-specific evaluation.

The notable direction is lower-priced multi-step agent execution rather than only single-response capability. Long workflows repeatedly ingest history and tool results and generate intermediate actions, so small unit-price changes can accumulate. Conversely, retries and longer trajectories can consume the advantage. Reading the release requires connecting pricing to task behavior and successful outcomes.

## What the announcement reveals about the mechanism

The disclosed explanation for inference efficiency is more aggressive sparsity. MiniMax reports nearly threefold faster online inference, everyday output speeds reaching 200+ TPS, and P50 speeds of 170+ TPS. The article does not reveal expert counts, activation ratios, training procedures, or serving-scheduler details sufficient to reconstruct the implementation. Nor does it specify the hardware, context length, concurrency, and request distribution behind those speeds.

The supported interpretation is therefore a vendor-described mechanism direction and service observation, not an undisclosed MoE architecture we can fill in. How sparsity reduces computation per token and interacts with communication or routing is a general engineering question; this announcement does not quantify those contributions for M3.1 Flash. It contains no suitable architecture figure. The official benchmark table below retains its complete evaluation notes.

<a class="note-image-link" href="/assets/images/tech/minimax-m31-flash/benchmarks.webp" target="_blank" rel="noopener" aria-label="Official MiniMax M3.1 Flash benchmark table with complete evaluation footnotes · View original image ↗"><img src="/assets/images/tech/minimax-m31-flash/benchmarks.webp" alt="Official MiniMax M3.1 Flash benchmark table with complete evaluation footnotes" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Read the highlighted model column, then the harness, context, and dataset notes below; evaluation sources differ across columns and blanks are not zeros.*

## The scores measure different tasks

Reported results include 73.7% on DeepSWE v1.1, 76.2 on BankerToolBench, 61.7 on OSWorld 2.0, and 29.6 on Agents’ Last Exam (ALE). These cover software tasks, tool workflows, computer operation, and complex professional work. Their scores cannot be added or used to compare difficulty directly. The announcement text gives CyberGym as 82%, while the figure gives 82.2; this difference in precision is retained rather than treated as two results.

Figure footnotes matter. DeepSWE uses mini-SWE-agent 2.4.5 with a maximum 512K context; BankerToolBench uses OpenCode 1.17.18 and MiniMax-M2.7 as judge; CyberGym uses Claude Code 2.1.263 with a maximum 1M context. AutomationBench v1.0.6 uses 600 public tasks. These measure model–harness combinations, so simply changing the model in another stack need not reproduce the score.

The ALE table includes only official Overall full-set results; blanks are not zeros. OSWorld uses the recommended 0808 Full Release, taking most other models’ highest scores at release while using an internal reproduction for DS-V4.1. These notes clarify the table but also show that it is not a controlled same-day rerun of all models with one harness and budget.

## From unit prices to task cost

The announced prices per million tokens are **$0.15 for ordinary input**, **$0.60 for output**, and **$0.015 for cached input**. MiniMax also reports 70% lower overall agent-task usage cost than its predecessor. The latter claim lacks a complete workload and denominator, so it is not a guarantee about every user’s bill.

Consider an explicitly illustrative calculation: one task with one million uncached input tokens, 200,000 output tokens, and another two million cache-hit input tokens would cost 0.15 + 0.12 + 0.03 = **$0.30** in model tokens at the announced prices. This is not a MiniMax experiment and excludes tools, browser environments, retries, and human review. Cached pricing applies only to actual hits; historical input should not automatically be assumed cached.

A more useful engineering quantity is total cost per accepted successful task. If a cheaper model takes more actions or retries, total cost may not fall proportionally. Stable success rates and trajectory lengths make the unit-price reduction more likely to translate into savings. This is reasoning from the billing structure, not a conclusion established by the announcement.

## TPS is not total waiting time

The 200+ TPS figure describes output-token rate, and P50 describes its median level. Neither covers time to first token, tool execution, interface interactions, or queuing. Computer Use may mostly wait for web responses, while coding may mostly wait for tests. Faster token generation need not make either workflow nearly three times faster.

Long-workflow evaluation also needs retries, termination conditions, and final external state. A model saying it finished, a tool returning success, and the business objective actually being achieved are different observations. Benchmark scores help prioritize reading but do not establish reliability for arbitrary unattended workflows. Cybersecurity benchmark scores likewise do not directly establish real-world defensive effectiveness.

## Turn a model update into answerable questions

If existing tasks already complete reliably, compare cost and waiting time under unchanged acceptance criteria. If they often fail, first ask whether the new model reduces failures before focusing on unit prices. The denominators differ: the first question concerns successful-task overhead, while the second must include spending on failed attempts. Counting only completed tasks can silently remove difficult cases.

Caching also needs separate treatment. The announcement gives a cached-input price but does not specify cache lifetime, prefix-matching conditions, or actual hit rates for a business workload. Even a low cache price may have limited effect when tool results keep changing context. Estimates should retain separate ordinary-input and cache-hit counts rather than applying the cheapest rate to everything.

For long workflows, occasional serious errors can matter more than average benchmark scores. A patch may need inspection for unintended changes after tests pass; a desktop task may need checks that unrelated files were untouched. These are engineering evaluation dimensions, not observed defects of this model. The announcement provides no such detailed error breakdown, so model rankings cannot answer these questions.

## What can be concluded now

MiniMax says M3.1 Flash is available through its API, M Plan, and MiniMax Code, with weights to follow later. Service access and downloadable weights are different release states. The article supplies no weight-release date, parameter count, or complete local-reproduction deployment conditions. This note does not verify account-level availability or turn the announcement into a purchasing recommendation.

The useful follow-up is whether capability, trajectory length, and low prices hold together, not only a leaderboard position. For an existing agent system, a meaningful comparison fixes tasks, tool permissions, harness, and budgets while recording success, output quality, total tokens, cache hits, cost, and end-to-end latency. The release supplies a new candidate to test; service conditions and detailed architecture remain evidence gaps in the announcement.
