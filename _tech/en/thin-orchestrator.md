---
id: thin-orchestrator
title: '2026-10-21 | Thin Orchestrator: Moving Domain Reasoning Out of the Router'
date: '2026-10-21'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- multi-agent
- coding-agents
summary: 'Fixed workflows route work and enforce checks while isolated specialists
  make domain changes: lessons and limits from Meta data-pipeline automation.'
long_read: true
source_url: https://engineering.fb.com/2026/10/19/ml-applications/thin-orchestrator-ai-agent-architecture/
permalink: /tech/en/thin-orchestrator/
authorship: assistant
translation_source: assistant
published_at: "2026-10-21T13:08:08.256303+08:00"
updated_at: "2026-10-21T13:08:08.256303+08:00"
---
Plawan Rath, Akhil Jindal, Ashwini Verma · Meta Engineering · 2026-10-19  
Original: [The Thin Orchestrator: How We Made Our AI Agents More Reliable by Giving the Router Less to Do](https://engineering.fb.com/2026/10/19/ml-applications/thin-orchestrator-ai-agent-architecture/)

Giving a central agent all domain knowledge can reduce handoffs while mixing incompatible subsystem conventions. Meta's data-column onboarding spans three repositories, three programming languages, and up to six pipeline stages. Naming rules, code generation, and data-source conventions differ. Concentrating them in one agent led to rules from one subsystem being applied to another; more context did not automatically make changes more reliable.

The thin-orchestrator pattern redistributes responsibility. The router sequences work, gathers inputs, and checks reliability conditions. Specialists perform domain reasoning in isolated contexts. The article describes an approximately 1,300-line orchestrator connecting 14 specialists across more than 20 workflows. Line count is not the mechanism; the useful question is which decisions can move out of probabilistic reasoning.

## Fix the deterministic parts of the process

Every request follows seven steps: read the specialist instructions; check whether the target already exists; gather required fields; discover inferable facts such as repository type and existing configurations; check warnings and required reviewers; delegate; and handle results, errors, or success. According to the authors, LLM reasoning occurs only inside the delegated specialist step. The other stages use deterministic logic.

Existence checks establish state before retries. Gathering fields prevents a specialist from guessing requirements while editing. Reliability gates make warnings and review requirements prerequisites for delegation. These reduce opportunities for errors to enter downstream work. The engineering interpretation is that programmatically decidable facts should remain programmatic, reducing the dimensions in which the model controls the workflow. The checks themselves must still be implemented correctly.

<a class="note-image-link" href="/assets/images/tech/thin-orchestrator/workflow.jpg" target="_blank" rel="noopener" aria-label="The router coordinates requests on the left, workflow templates select the sequence, and domain-scoped contexts handle schema, validation, onboarding, and testing on the right. · View original image ↗"><img src="/assets/images/tech/thin-orchestrator/workflow.jpg" alt="The router coordinates requests on the left, workflow templates select the sequence, and domain-scoped contexts handle schema, validation, onboarding, and testing on the right." loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*The router coordinates requests on the left, workflow templates select the sequence, and domain-scoped contexts handle schema, validation, onboarding, and testing on the right.*

## Evolve templates separately from specialists

Column onboarding follows schema→validation→population→testing. Event onboarding changes the order and adds event processing. Migration uses assessment→planning→population→validation→monitoring. Templates constrain phase order while reusing specialists. The authors say that migration support combined existing specialists without new agent code.

That makes interfaces more important than role names. Each specialist has a uniform structure: runtime knowledge sources, required inputs before delegation, execution steps, repository discovery patterns, and troubleshooting guidance. The orchestrator knows what to provide and how to handle the result; the specialist need not read every other domain's details. However, undeclared assumptions shared between steps would remain coupled even after splitting them into agents. That is a transfer question for this architecture.

More than 25 domain-organized knowledge files are loaded on demand, typically a few thousand tokens each. An update reaches the next session without embedding all instructions into the orchestrator. This separates domain maintenance from routing-code changes, while raising a version-consistency question: a cross-stage task should know which knowledge version it used. That is an engineering inference from the architecture, not a reported version-control experiment.

## What was actually observed

The authors report that configuration preparation for a new column took three to four days manually, about a day with an earlier configuration-driven system, and less than an hour with the thin orchestrator. Approximately two-thirds of changes land without substantial human editing. These measure time and editing effort respectively. Neither is a fully autonomous success rate, nor evidence that every stage reaches production within an hour.

An alternative single-agent approach reportedly achieved 70–80% success with task-specific prompts manually prepared by engineers, versus 10–20% without that assistance. These numbers illuminate the earlier operational burden, but the article does not provide complete sample counts, paired tasks, or a unified success definition. They do not support a strict causal effect calculation. Accuracy and token savings cited from another study are also not measurements of Meta's system.

The plausible mechanism is narrower knowledge reducing interference and fixed state machines removing unnecessary control decisions. The system trades breadth for deep support of specific pipelines. Stable internal workflows are especially compatible with that trade-off; an open-ended research agent might be constrained too early by a fixed template.

## Context isolation does not automatically isolate effects

The article proposes retrying or escalating specialist failures to prevent contamination of other contexts. That helps reasoning isolation, but shared repositories, external services, and partially completed changes can still carry effects across stages. A system-level containment guarantee requires knowing which actions are idempotent, which results can be verified, and where retries begin. Those are interface properties, not consequences of adding another role.

## Decide which steps can be fixed in advance

The pattern does not require every intent classification to collapse into a few keywords. A more practical test asks whether inputs and outputs have stable contracts: can repository metadata determine the target, do required fields have a schema, does an equivalent configuration exist, and which warnings must block progress? With authoritative answers, the router need not repeatedly ask the model to guess. Genuine ambiguity should remain visible rather than hiding unconstrained reasoning behind a deterministic label.

Likewise, a specialist's “done” message is not sufficient evidence of completion. Configuration work can be checked against artifacts and build results; migration can identify which old paths remain and which new paths are enabled. These are implementation inferences from the architecture, not additional reported experiments. They explain why a thin router still has substantial responsibility: converting each stage's outcome into an input that the next stage can rely on.

Adoption should therefore not aim to reproduce fourteen specialists or thirteen hundred lines. More useful comparisons concern human clarification effort, whether failures can be localized to a stage, and whether knowledge changes unexpectedly alter other workflows.

Future work includes identifying failure patterns from production feedback, proposing knowledge-file improvements, and requiring human review before applying them. Continuous improvement therefore needs its own change boundary. The useful practice is to assign routing, input validation, domain reasoning, and execution checks explicitly, then test whether templates and specialists can truly evolve independently. For well-defined internal engineering workflows with extensive domain knowledge, this is a more substantive direction than simply enlarging the central prompt.
