---
date: '2026-11-10'
published: true
layout: article
maintenance: daily-research
translation_source: assistant-authored paired Chinese/English research notes
authoring_source: assistant
editorial_status: source-checked
id: ai-sre-evaluation
title: '2026-11-10 | Evaluating AI SRE: separate diagnosis, evidence, and operational
  responsibility'
lang: en
source_type: tech
source_url: https://one2n.io/blog/what-changed-in-how-we-evaluate-ai-sre-agents
long_read: true
tags:
- observability
- agent-reliability
- systems-reliability
summary: A mistaken Helm-rollback diagnosis motivates separate criteria for evidence,
  shared knowledge, traceability, and action control.
permalink: /tech/en/ai-sre-evaluation/
published_at: '2026-11-10T09:37:04.860576+08:00'
updated_at: '2026-11-10T09:37:04.860576+08:00'
---
[What changed in how we evaluate AI SRE agents](https://one2n.io/blog/what-changed-in-how-we-evaluate-ai-sre-agents) · One2N · 2026-11-02

General coding agents can already investigate incidents through MCP or CLI tools. Dedicated AI SRE platforms need to explain their additional value. One2N revisits an OpenSRE proof of concept and replaces broad criteria with questions about investigation initiation, system coverage, evidence, and responsibility for actions.

## One wrong answer can contain several different defects

The authors deliberately scaled replicas to zero with kubectl, but OpenSRE attributed the incident to a Helm rollback. One negative RCA score could not distinguish wrong localization, a fabricated mechanism around the right symptom, or an unsupported reference to the zero-replica deployment. These imply different repairs: broader tools, better characterization, and decisive verification are not interchangeable.

The post describes SREGym’s finer diagnosis rubric: localization, characterization, and scope, each with three binary questions, requiring seven of nine to pass. This is One2N’s account of another evaluation approach, not a newly conducted benchmark or a comparable scorecard for multiple products.

Like Cloud-OpsBench in this issue, it resists treating a final answer as a complete investigation. Their contributions differ: One2N discusses deployment and acceptance criteria, while Cloud-OpsBench implements matched incident evidence and scored tool trajectories.

## Initiation determines what can happen before the responder arrives

The article distinguishes manually triggered, alert-triggered, and pre-alert preventative investigation. A platform can perform initial queries before the engineer arrives or watch error budgets and deployments. Demonstrating reduced mitigation time still requires incident timestamps and comparative evidence; this post provides no attributable MTTR experiment.

Coverage extends beyond one log backend to IaC, code, CI/CD, feature flags, dependencies, and change history. System-wide read context does not require system-wide write authority. Shared architecture, ownership, debugging skills, and past incidents should be available regardless of the responder, while agent memory remains inspectable, editable, and deletable so stale beliefs do not persist unchecked.

## Traceable execution supports handoffs and correction

A private terminal investigation may hide context and human steering from a second responder. The proposed criteria retain queries, tool calls, actions, and conclusions, linking supporting or rejecting logs, metrics, and traces to hypotheses.

A separate agent identity distinguishes its actions from commands typed by the engineer. Mitigation plans should expose readable intent, pre-checks, dry runs, success criteria, and rollback steps. A concise rationale is easier to review than raw reasoning, but must remain traceable to execution evidence.

This is an engineering-PoC-derived assessment framework. Its evidence rests on a concrete misdiagnosis and explicit design requirements, rather than a large controlled effectiveness study. The source contains no suitable mechanism diagram, so this note remains textual. **Use it as an AI SRE acceptance question set:** assess diagnosis, shared knowledge, auditability, and action control separately, then measure whether they improve real incident response.
