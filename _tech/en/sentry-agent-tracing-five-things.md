---
id: sentry-agent-tracing-five-things
title: '2026-11-06 | Sentry Agent Tracing: turning production traces into evaluation
  and triage inputs'
date: '2026-11-06'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- observability
- agent-reliability
summary: How conversation linkage, production exports, successful-run triage, and
  cost alerts connect five observability workflows.
permalink: /tech/en/sentry-agent-tracing-five-things/
authorship: assistant
translation_source: assistant
editorial_status: source-checked
long_read: true
source_url: https://x.com/i/article/2118087303029510144
source_format: x-article
published_at: '2026-11-09T11:09:45.657368+08:00'
updated_at: '2026-11-09T11:09:45.657368+08:00'
---
Agent failures need not throw exceptions. A tool can fail repeatedly before a fluent answer appears, or successful steps can lose context during a handoff. Sentry's article follows tracing into operational workflows: export conversations for evaluation, inspect apparently successful runs during triage, and attribute cost changes to individual calls.

Original: [Five things you can do with Sentry’s Agent Tracing](https://x.com/i/article/2118087303029510144) · Sentry · associated official announcement dated 2026-11-05

## Link conversations across requests and execution within requests

A user conversation can span HTTP requests, each containing model calls, tools, database work, and other application spans. Model text alone cannot reveal whether a provider, database, or repeated tool call caused the delay.

The official evaluation recipe uses `Sentry.setConversationId()` to give related AI spans the same `gen_ai.conversation.id`, plus stable call names. Conversation views aggregate turns; traces follow execution within a request. These identifiers solve different problems: a conversation need not share one trace, and request-level spans do not automatically establish cross-turn identity.

The workflow needs captured inputs and outputs. The recipe uses tracing and the Vercel AI SDK integration; routes without recorded content cannot yield complete textual evaluation records. Sampling, redaction, and missing fields consequently affect dataset coverage, rather than merely the appearance of a dashboard.

## Export observations for evaluation without treating them as answers

The first workflow exports conversations with the CLI. The first user message becomes input, the final agent reply becomes output, and cost, token, and tool-error metadata accompany the record. Braintrust, Langfuse, promptfoo, or Phoenix can score it. This automates collection of real examples, without automatically supplying correct labels.

The recipe recommends code checks for requirements that can be formalized and model judges elsewhere. A production reply remains the object being evaluated, not ground truth. Reducing a conversation to first input and last output can also omit constraints added midway. Evaluations concerned with tool effects or interaction must retain the relevant trajectory instead of testing only the final sentence.

The [official export recipe](https://sentry.io/cookbook/agent-conversations-to-evals/) specifies conversation IDs and SDK prerequisites. A useful application turns actual failures, expensive loops, and boundary cases into regression tests with separately established acceptance criteria.

## Why daily triage samples successful conversations too

The second workflow has a scheduled assistant retrieve the previous twenty-four hours of aggregate statistics through Sentry MCP and inspect both failed and successful conversations. It looks for broken tools, loops, unusual cost, and conclusions unsupported by the execution. New findings are checked against the issue tracker before a ticket is created.

This goes beyond summarizing exception stacks. A successful request can contain retries that hide tool problems or an answer unsupported by its trace. The [triage recipe](https://sentry.io/cookbook/automate-ai-agent-triage-claude-routines/) connects MCP retrieval, assistant judgment, and ticket deduplication. It provides a workflow and prompt design, without measured triage precision, recall, or staff-time savings. Automatic execution does not establish detection of every semantic failure.

## Cost attribution and alerts use the same span chain

Two further recipes cover per-call attribution and spend alerts. The Next.js/Vercel integration exposes estimated model, call, and conversation costs, with trace navigation to investigate slow tools or repeated work. A dashboard recipe creates eight widgets and two hourly alerts: a user-defined spend threshold and a deviation from the normal range.

Sentry estimates cost from token counts rather than requiring applications to send dollar amounts. These estimates are diagnostic signals, not guaranteed invoice totals; missing usage, sampling, and pricing treatment affect them. An alert alone cannot distinguish traffic growth, model changes, cache changes, or runaway loops. Conversation and tool evidence supplies the next step in diagnosis.

## Add a destination to an existing OTel path

The fifth recipe adds Sentry as another destination for a Vercel application's existing OpenTelemetry setup. Standard gen_ai spans appear beside application and database spans from the same requests. Its appeal is reusing instrumentation while gaining agent-oriented interpretation; compatible environments can use the same principle.

Together, the workflows connect correlation, export, evaluation, triage, and alerts. They introduce neither a new tracing protocol nor a controlled performance result. Their value lies in turning product capabilities into routine AgentOps inputs. Correlated spans do not automatically explain causes, and model triage does not automatically yield reliable verdicts. Production traces become durable evaluation evidence only when linked to task requirements, tool effects, and adjudicated outcomes.
