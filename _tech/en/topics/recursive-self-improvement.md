---
id: topic-recursive-self-improvement
title: 'Recursive self-improvement: how agents change their execution systems'
date: '2026-11-11'
updated_at: '2026-11-11'
lang: en
published: true
layout: article
topic_guide: true
long_read: true
tags: [self-improvement, agent-reliability]
authoring_source: assistant
translation_source: assistant
permalink: /tech/en/topics/recursive-self-improvement/
summary: Compare InfraRSI, BOXBOX, and JoMoHa through what changes, where feedback comes from, and what verification actually establishes.
---

Recursive self-improvement (RSI) now describes several different systems: optimizing training infrastructure, rewriting tools during a long task, and jointly training a model and its execution framework. Each feeds experience into a later decision, but **what changes, where feedback comes from, and how errors propagate** differ.

This guide organizes the reading around those questions. New work should change or clarify the map before it earns a place here.

## Who changes what?

A harness is the system around the model that organizes execution: tools, context management, task loops, recovery, and evaluation. Revising a prompt, editing executable code, and training weights are distinct interventions. Automatically finding a faster configuration does not establish an ability to recursively upgrade every part of an agent.

| Work | Main object of improvement | Where the loop runs | Feedback and checks |
| --- | --- | --- | --- |
| [InfraRSI](https://arxiv.org/pdf/2611.11558) | Training launch configurations and code patches | Between training-optimization trials, with experience carried across environments | A fixed training contract, time and memory measurements, and candidate retesting |
| [BOXBOX](https://arxiv.org/pdf/2611.09218) | The executable harness used by the agent | Within one ongoing long task | Performance-task feedback; a separate kernel checks and activates revisions |
| [JoMoHa](https://arxiv.org/pdf/2611.11499) | The Engineer policy that generates harnesses and the Solver policy that executes tasks | Joint reinforcement learning | Shared task executions coordinate the two policies |

These are not successive capability levels. Start with the problem: finding a better training setup, repairing an agent that is already running, or training a better-matched model–harness pair.

## InfraRSI: keep the work comparable

InfraRSI fixes workload, loss, and timing invariants before profiling and searching configurations and patches. Its useful distinction is between recording a fast trial and checking whether it performed comparable work; unsuccessful trials also inform the search. [Paper](https://arxiv.org/pdf/2611.11558)

Read it with one verification question in mind: **after a change to batch size, precision, or the timed region, is the shorter duration still comparable?** Transferring experience also requires checking model, hardware, and topology compatibility. Local numerical checks cannot replace full convergence validation.

→ [Daily reading: InfraRSI’s task contract and validation loop](/digest/en/daily/2026-11-11/#paper-arxiv-2611.11558)

## BOXBOX: revise a harness without restarting the task

BOXBOX gives the agent a review entry point. A separate kernel pauses execution, preserves context, checks the revised harness, and activates it, with rollback if activation fails. It changes the execution system for the current task rather than updating the base model’s weights online. [Paper](https://arxiv.org/pdf/2611.09218)

The reading question becomes **what survives a version transition?** What happens to pending tool actions? Can the new runtime interpret the old records? Could recovery repeat an external side effect? These are engineering checks to make, not guarantees that follow merely from supporting hot reload.

→ [Daily reading: BOXBOX’s runtime revision and experimental setup](/digest/en/daily/2026-11-10/#paper-arxiv-2611.09218)

## JoMoHa: does the model still fit its harness?

JoMoHa learns both an Engineer that generates executable harnesses and a Solver that performs tasks. Its concern is compatibility: improving the two separately can make them work worse together. Shared execution experience coordinates joint learning. [Paper](https://arxiv.org/pdf/2611.11499)

Separate **a weaker model** from **a mismatch with an older harness**. Testing saved models with fixed harnesses and different pairings can reveal more than a combined score. The evaluation uses ALFWorld, WebShop, and DBBench; that scope does not establish long-term autonomy in production.

## Different gains do not make one leaderboard

Training throughput, speedup of the software being optimized, and agent task success answer different questions. Calling all three an improvement does not make them interchangeable.

| Question to ask | Why it matters |
| --- | --- |
| Are the workload and correctness requirements fixed? | Changing the task can create an incomparable gain |
| Are search, failed trials, and verification included in cost? | Cheaper inference need not mean cheaper optimization overall |
| Is the test on the current task or on unseen tasks? | Adaptation and generalization need different evidence |
| Who authorizes promotion? | Self-assessment, hidden tests, and independent review provide different assurances |
| How are state and rollback handled? | Restoring code does not undo an external action |
| Can the optimizer change permissions and safety constraints? | Better task performance does not grant broader authority |

## What should we watch next?

I would prioritize three questions: **whether verification cost grows with the complexity of revisions; whether experience transfers without contaminating evaluation; and whether accumulated changes preserve the original permissions and task semantics.** These are conclusions from comparing the works, not findings jointly established by all three papers.

A new search algorithm within an existing route can belong in the daily digest. A change to feedback, state management, or validation may justify updating this guide. Read along the progression from fixing the task definition, to revising execution, to coordinating model and execution—without treating every RSI title as the same kind of system.

## Original papers

- [InfraRSI: Harnessing Recursive Self-Improvement for Training Infrastructure](https://arxiv.org/pdf/2611.11558)
- [BOXBOX: Recursive Harness Self-Improvement for Long-Running Performance Optimization](https://arxiv.org/pdf/2611.09218)
- [JoMoHa: Joint Model–Harness Optimization with Reinforcement Learning](https://arxiv.org/pdf/2611.11499)
