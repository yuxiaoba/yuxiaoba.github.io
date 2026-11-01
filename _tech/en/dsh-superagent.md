---
id: dsh-superagent
title: 2026-11-01 | How the DeepSeek Prototype Manages Ongoing Work, Authority, and
  Recovery
date: '2026-11-01'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- agent-reliability
- multi-agent
- systems-reliability
summary: Ticket and Assignment lifecycles make handoffs, recovery, and authorization
  explicit in an event-driven coding agent.
translation_source: assistant
authorship: assistant
long_read: true
source_url: https://github.com/deepseek-ai/dsh-superagent-prototype
permalink: /tech/en/dsh-superagent/
published_at: '2026-11-01T08:44:13.804154+08:00'
updated_at: '2026-11-01T08:44:13.804154+08:00'
---
For an ongoing coding agent, difficult failures often happen between model replies: a CI result arrives late, several people follow up on one issue, or a process restarts before work is delivered. DeepSeek’s dsh-superagent prototype represents these situations through work items and execution state. Its AgentOps value lies in separating authority, current execution, and unfinished external effects.

Original project: [dsh-superagent](https://github.com/deepseek-ai/dsh-superagent-prototype) · deepseek-ai / DeepSeek Harness team · repository created 2026-10-31. The README describes research reference code adapted for publication. It differs from *Exploring Super-agent Design: Towards a More Autonomous Agent System*, and some design directions are not implemented.

## One work item spans multiple executions

The prototype serves one GitHub repository and receives GitHub and optional Feishu events. An event becomes a Trigger; an accepted request creates a Ticket containing scope, authority, subscriptions, and progress. An Assignment carries execution in a dedicated Executor Session and directory. Retrying can replace the Assignment while preserving the Ticket, session, directory, branch, and PR.

Ending a model turn therefore need not end the work. Background commands or subagents keep the worker slot occupied; waiting begins only when no background work remains. A `ready` report does not necessarily complete a Ticket either: PR-related work follows the relevant close or merge lifecycle. The panel distinguishes waiting for an answer, awaiting review, undelivered input, failure, and queueing.

Scheduling reserves an additional slot for a human message or status request. When normal capacity is full, a person can wake existing work and obtain priority for the next available slot. Automatic inputs such as CI results wait for normal capacity. This addresses human intervention being crowded out by long-running work, rather than accelerating model inference.

## Context propagation does not expand authority

The [authorization document](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/002-authorization.md) separates explicit requests from inferred candidates. The host checks sender and source policies. Subscribed thread messages may reach a Ticket as context without granting new authority. A Ticket remains bound by its Mandate; out-of-scope follow-ups return to routing.

Proactive work has `off`, `observe`, and `auto` modes. The default observe mode records positive assessments without accepting inferred work. Auto mode still requires a matching rule. Operators can therefore inspect admission decisions before allowing equivalent events to start work. Conversation text, quoted documents, and bot comments do not themselves modify policy.

A policy-version change requeues active evaluations and notifies affected work. It does not immediately revoke every live Ticket’s Mandate; ended work is revalidated before resumption. Versioned authority provides traceability, but should not be interpreted as instant cancellation of all external actions whenever a rule changes.

## Persist decisions before external effects

The [architecture guide](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/007-architecture.md) makes Engine the sole writer of core domain objects. Commands update state transactionally, enqueue external work, and let adapters perform it after commit. Outbox records replies and schedules delivery, separating the decision to reply from successful transmission.

This supports delivery recovery without establishing exactly-once semantics for every external effect. A process can fail after issuing a request but before recording its outcome. The execution guide tells recovering workers to inspect their directory, history, and GitHub state before repeating external actions. Recovery instructions and persisted state work together to reduce blind repetition.

Errors take different paths. Transient provider or network errors receive three retries with increasing backoff; directory-preparation failures do not receive the same automatic retry. Once a Ticket is blocked or failed, automatic inputs are recorded but do not wake its Executor. Human input, retry, or a later qualifying report releases the hold. This retains a recovery path while preventing CI events from repeatedly restarting the same failure loop.

## Session separation has a limited isolation boundary

Directories and command wrappers establish execution defaults, not a security boundary. The documentation explicitly notes that workers can invoke programs by absolute path and execute as the operator’s OS user. Some merge conditions are agent instructions; repository protection rules are needed to enforce review requirements.

The engineering contribution is an inspectable lifecycle spanning event admission, authorization, background work, delivery, and restart recovery. The project supplies no comparative reliability benchmark or production failure rate, so documentation alone cannot establish recovery gains or autonomous capability. Read authorization, execution, and architecture in sequence, watching the distinctions between receiving an input, reading it, deciding, and completing an external effect. These mechanisms are documented mainly in tables and Mermaid; this note retains a textual explanation rather than inventing an architecture image.
