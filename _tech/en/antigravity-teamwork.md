---
id: antigravity-teamwork
title: '2026-11-15 | Antigravity /teamwork: organizing independent verification for
  long tasks'
date: '2026-11-15'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- multi-agent
- agent-reliability
- systems-reliability
summary: Clean-context review, dependency-aware rewrites, unchanged tests, and the
  scope of Google’s reported production gains.
translation_source: assistant-authored bilingual content
long_read: true
source_url: https://research.google/blog/advancing-science-engineering-with-antigravitys-teamwork-feature/
permalink: /tech/en/antigravity-teamwork/
published_at: '2026-11-15T15:30:22.801784+08:00'
updated_at: '2026-11-15T15:30:22.801784+08:00'
---
Long-running agent systems need more than parallel attempts. Candidates need checks that can reject them, completed work must survive handoffs, and tests must retain their constraints as implementations change. The most useful part of Google’s report is how these requirements become different /teamwork workflows, illustrated through code migration, optimization, and production scheduling.

Original: [Advancing science & engineering with Antigravity’s /teamwork](https://research.google/blog/advancing-science-engineering-with-antigravitys-teamwork-feature/) · Vahab Mirrokni · Google Research · 2026-11-13

## Constraining parallel exploration with independent checks

The report identifies two difficulties. First, individual generations are unreliable. More agents increase opportunities to find a solution, but can also produce several plausible mistakes. /teamwork pairs exploration with dedicated falsifiers: Lean proof checking, unchanged software tests, execution simulators, or hardware counters. Acceptance relies on executable checks in the relevant domain rather than the producer’s confidence in its answer.

These tools provide different guarantees. Lean checks proofs of formal statements, tests cover their specified conditions, and hardware timing measures a particular workload. The article explicitly retains a role for mathematicians in checking that formal statements match the original problems. Independent verification makes the source and scope of evidence clearer; a successful tool check does not uniformly establish that an entire project is correct.

The second difficulty is context drift over multi-day tasks. The described workflow restricts each agent to the files and tools required for its step. Coordinators hand work to fresh successors, while critics and auditors inspect results in clean contexts without the original producer’s reasoning. This aims to reduce interference from accumulated history, although successors still need sufficient requirements and artifacts. It is a workflow description: the article does not isolate the benefit of clean context through an ablation.

## Rewrites preserve dependencies and original tests

Migration supplies a concrete example. An agent might stub out a difficult dependency or change tests until an incorrect implementation passes. The reported rewrite pattern schedules modules only after their dependencies compile and links leaf modules against the original, unchanged test suite. Scheduling and acceptance jointly constrain generation, reducing the risk that independently “completed” modules cannot work together.

Google reports that, starting from an approximately 25% Zircon port, a two-week campaign rewrote the remaining C++ into roughly 800,000 lines of safe Rust, passed all kernel unit tests, and booted on arm64 hardware. It also reports rewriting libgav1 into about 170,000 lines of Rust with bit-exact parity across a broad conformance suite. The initial port was about four times slower. After access to profiling tools and an optimization objective on sample videos, the reported result was 20–30% faster than the original C++ and hand-optimized assembly on x86_64 and ARM.

These are vendor-reported project outcomes. Passing tests, booting, and bit-exact agreement each cover different acceptance scopes. The article does not provide the full test matrix, hardware configurations, or video distributions, so it does not establish that Rust rewrites generally improve performance. The more specific lesson is to anchor behavior in checks before adding performance optimization. The rewrite pattern is described as forthcoming; demonstrated workflows are not all features available on the publication date.

## Sequential revision and cheap evaluation address different constraints

/teamwork expresses workflows as declarative natural-language patterns and routes requests to suitable patterns. For tightly coupled code, the report says analysis of earlier trajectories led /boost toward sequential implementation and revision stages. Parallelism is not the only optimization axis: when division boundaries are unstable, sequential refinement may better preserve a coherent implementation. No quantitative comparison is supplied for this change, so it is best read as engineering experience.

For expensive kernel search, DuoDiscover instead has four parallel agents construct fast yardsticks and continuously validate their candidate rankings with full hardware evaluations. The report’s Argon setting achieves 4.09× geometric-mean acceleration over reference implementations across 17 JAXBench kernels, and 2.99× over seven hand-optimized vLLM TPU Pallas kernels. These belong to the blog’s setting. The paper’s main experiments use a different backbone and report 4.62×/2.68×; the two pairs must not be combined into one experiment or assigned interchangeable baselines.

The article gives examples of full evaluations taking 7–32 minutes and proxies taking about 23 seconds. The point is not that small tests automatically represent a system. Periodic full evaluation checks whether their rankings have drifted. This shares an engineering principle with keeping original rewrite tests: the producer may change the implementation, while the evidence accepting that change retains separate constraints.

## Production gains and their scope

Google reports two shipped Borg scheduling changes that reduced TPU workload preemption by 24% on some hardware types while preserving SLOs and utilization. This concerns preemption on specified hardware, not a 24% increase in throughput across Borg. The memory section describes identifying opportunities from fleet metrics and past optimizations, alongside a human-in-the-loop monitoring agent. Identified opportunities should likewise not be equated with fully realized savings.

For AgentOps, three controls stand out: domain checks for candidate selection, dependencies and handoffs for long-running work, and existing tests and production metrics for accepting changes. The report supplies mechanisms and implementation cases across several projects, but no unified experimental protocol. It supports transferable workflow ideas rather than a universally validated long-task algorithm. The original provides no static architecture figure that explains these mechanisms, so this note uses text.
