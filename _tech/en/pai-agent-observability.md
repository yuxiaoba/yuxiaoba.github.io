---
id: pai-agent-observability
title: '2026-10-07 | PAI: What Agent Monitoring Needs from Telemetry'
date: 2026-10-07
reviewed_on: 2026-10-18
long_read: true
lang: en
source_type: tech
source_url: https://partnershiponai.org/resource/the-observability-gap-in-ai-agents/
organization: Partnership on AI
tags:
- agent-reliability
- observability
summary: Work backward from monitoring goals to identify missing records of agent identity, permissions, memory, and human intervention.
published: true
maintenance: manual
approved_on: '2026-10-19'
layout: article
permalink: /tech/en/pai-agent-observability/
translated_on: '2026-10-19'
translation_source: /tech/zh/pai-agent-observability/
translation_method: assistant translation of the locally approved Chinese article
original_tags:
- AgentOps
- observability
- telemetry
- monitoring
---
**Partnership on AI · Observability assessment report**  
Original report: The Observability Gap in AI Agents · [Report PDF](https://partnershiponai.org/wp-content/uploads/2026/10/PAI_obervability-gap-in-ai-agents.pdf)

## What is missing even when a trace exists?

A trace can show that an agent read a file without establishing the identity or permissions under which it acted. If approval requirements changed during a session, or a sub-agent inherited different authority, successful tool calls alone may not be enough to reconstruct what was authorized.

PAI asks a question that precedes the choice of monitoring tools: **does the framework emit the records needed to answer these questions?** Downstream analytics can correlate and display events, but generally cannot recover state changes that were never recorded.

## Understanding the gap through a permission change

Consider this explanatory example, rather than an additional measured incident: an agent initially requires human approval for a class of actions. During the session, it switches to automatic execution and successfully calls a tool. The log records the tool name, arguments, output, and duration.

These records explain what was executed, but not whether the mode change was expected. We also need the old and new modes, who triggered the change, the identity under which it took effect, and the permissions active when the action occurred.

If one of these facts was never recorded, retrospective analysis must retain that uncertainty. A model's plausible explanation does not recover the actual event. The report treats this as a telemetry-generation gap: correlatable records must exist before useful monitoring signals can be derived from them.

## Work backward from monitoring goals

<a class="note-image-link" href="/assets/images/tech/pai-agent-observability/pai-framework.png" target="_blank" rel="noopener" aria-label="PAI framework linking monitoring goals, processing techniques, telemetry gaps, and responsible actors, view original"><img src="/assets/images/tech/pai-agent-observability/pai-framework.png" alt="PAI framework linking monitoring goals, processing techniques, telemetry gaps, and responsible actors" loading="lazy"><span class="note-image-action">View original ↗</span></a>

*Reading the diagram: move downward from the monitoring goal to the processing technique, the missing record, and the actors who can address the gap. This is the report's analytical framework, not the architecture of an implemented product.*

The report identifies six goals: detecting unauthorized actions, policy violations, failures of human oversight, behavioral drift, and multi-agent risks, and supporting auditability. It then examines the processing required for each. Detecting unauthorized actions requires linking behavior to effective identity and permissions. Detecting drift requires baselines across runs. Following delegation requires connecting events from multiple agents.

The useful ordering is to identify the failure that must be detected, then check whether the available fields and relationships support that goal. Log volume and a comprehensive dashboard are not substitutes for this analysis.

## Four processing techniques and their inputs

The report distinguishes four techniques rather than assigning every monitoring goal to one evaluator. They can be combined, but cannot replace one another's missing underlying records.

- **Context binding:** connect an action to the acting identity, effective permissions, and external authorization records to determine whether it was allowed. An allowed action can still be a poor business decision.
- **Provenance and attribution:** connect parent and child agents, instructions, data, and evidence to establish who authorized a delegation and which inputs supported a conclusion. Isolated single-agent logs are insufficient.
- **Semantic comparison:** compare outputs or behavior with policies, task intent, or reference evidence. This requires a clear reference and remains subject to evaluator error.
- **Aggregation and baselining:** examine how behavior, configuration, and memory change across sessions. Without persistent identity and state-change history, different instances can be conflated and the source of drift can remain hidden.

In the permission-change example, semantic evaluation might flag an action as suspicious. Establishing that it exceeded authorization still requires trustworthy identity and permission-state records. More sophisticated analysis often makes the requirements on upstream fields more explicit.

## Which records are missing?

The report assesses documentation for OpenAI Agents SDK, Claude Agent SDK, LangGraph, and CrewAI. Its findings should be read as **a snapshot of that documentation assessment**, not a live test of every deployment configuration.

Four gaps concern execution records directly:

| Record | Question it should help answer |
| --- | --- |
| Persistent agent identity | Can the actor be identified across sessions and sub-agents? |
| Permission-mode changes | When, and by whom, were approval or autonomy settings changed? |
| Memory changes | Which write affected later behavior, and what caused it? |
| Human intervention | Why was review requested, who reviewed it, with what authority, and what was decided? |

The other two concern reasoning traces and token-level probabilities. Their availability depends more heavily on what model providers expose, and interpreting them remains uncertain. The report does not assume that a reasoning transcript reveals the actual cause of a decision, or that token probabilities reliably measure task correctness.

The engineering paths differ accordingly. Explicit execution events can be improved through fields, standards, and instrumentation. Signals about how a decision was reached still need research into their usefulness.

## Why recording a field is not enough

A field must support the required relationship, not merely exist. A name unique within one run may not map to an enterprise-recognized agent identity. A Boolean saying “human approved” does not establish that the reviewer had the authority to approve the action.

Memory presents a similar problem. Start and end events for a save operation establish that a call occurred, but may not reveal what was written, why it was written, or how it influenced later decisions. Monitoring only final behavior can delay discovery of an incorrect experience being repeatedly reused.

The report grades telemetry as fully, partially, or not emitted, then aggregates fields by category. The main matrix makes the distribution easy to scan, but adoption decisions still require the field-level explanations. A color does not explain collection scope, version, or correlation semantics. For sensitive content, collecting more should not be the default goal; the required records should follow from an explicit monitoring objective.

## How strong is the evidence?

The authors begin with two hypothetical financial use cases, derive monitoring goals through a working group, and review framework documentation field by field using an AI-assisted first pass followed by human vetting. The result is an inspectable set of fields and reasoning, not a measurement of how many production failures these gaps cause through large-scale traffic analysis or fault injection.

This determines how the report should be used. It can help identify missing records in a stack, but the color-coded comparison should not be treated as a ranking of which product is safest. Framework versions, additional instrumentation, and an organization's identity systems can change actual observability.

## Engineering assessment: a checklist for monitoring requirements

A practical use of the report is to list the events that must be detected, specify the minimum evidence chain for each, check whether the framework and external systems can supply it, and run a controlled test to confirm that the records reach the analysis layer. This is an engineering interpretation of the report, not a diagnostic product evaluated by its authors.

“No risk detected” must also be distinguished from “insufficient records to decide.” An execution without a permission-change event might have kept the same permissions, or the event might never have been captured. Those situations should not share one green success indicator.

Start with a concrete risk and follow its dependencies. To detect approval bypass, for example, the evidence needs to connect the action, permission state at that time, mode-change events, and reviewer identity. A successful tool call alone cannot answer that question.

The report makes “better observability” concrete by identifying data requirements. For systems already scoring trajectories or diagnosing failures, establishing that the input evidence is sufficient can matter more than adding another analysis dashboard. The report does not provide a deployable diagnostic system, and its documentation findings should be checked against the versions actually being adopted.
