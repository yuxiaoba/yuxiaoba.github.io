---
date: '2026-11-18'
published: true
layout: article
maintenance: daily-research
translation_source: assistant-authored Chinese and English; not user-supplied translations
id: quarkus-ai-rca
title: '2026-11-18 | Quarkus AI RCA: telemetry correlation and repeatable fault evaluation'
lang: en
source_type: tech
tags:
- observability
- systems-reliability
- agent-reliability
summary: 'Quarkus’s AI Root Cause Analysis deep dive makes two parts inspectable:
  how the model obtains traces, logs and metrics, and how the team checks its analysis
  against known faults. The substance is in tool interfaces, context filtering and
  chaos-test evaluation rather than a generic AI-RCA demonstration.'
long_read: true
source_url: https://quarkus.io/blog/ai-root-cause-analysis-deep-dive/
permalink: /tech/en/quarkus-ai-rca/
published_at: '2026-11-18T08:55:23.659995+08:00'
updated_at: '2026-11-18T08:55:23.659995+08:00'
---
[AI Root Cause Analysis: Architecture, Testing, and Evaluation](https://quarkus.io/blog/ai-root-cause-analysis-deep-dive/)  
Ales Justin · 2026-11-17

Quarkus’s AI Root Cause Analysis deep dive makes two parts inspectable: how the model obtains traces, logs and metrics, and how the team checks its analysis against known faults. The substance is in tool interfaces, context filtering and chaos-test evaluation rather than a generic AI-RCA demonstration.

## Start from traces instead of dumping all telemetry

The system reaches an LGTM stack through MCP and assumes applications already have OpenTelemetry instrumentation. A LangChain4j AI service and system prompt guide correlation, severity classification and structured output. Five tools retrieve recent trace IDs, full traces, correlated logs, root-span start time and metrics at that time.

After an analysis request, the model chooses traces to investigate, retrieves spans and logs, queries Prometheus using root-span timestamps and synthesizes causes, slow operations, error patterns and cross-trace relationships. A point-in-time metric query constrains scope but does not capture an entire incident. Transient pressure can appear in logs without a matching metric snapshot.

Optional source examination and dashboard generation run afterward through a separate Dev MCP service. Telemetry access is therefore distinct from code inspection. Neither tool access nor correlation itself proves causality.

## Filtering saves context and shapes the available evidence

StripMcpClient removes SDK and localhost attributes from traces, redundant log fields, and metric details such as Netty internals, constant values, histogram buckets and regional breakdowns. An example reduces 586 metric entries to about 35. Filtering occurs before the model receives the data, so subsequent reasoning is limited to retained information.

This is an engineering trade-off. Removing duplicates reduces burden, while removing histogram buckets can hide tail detail. The prompt treats chaos-related logs as strong evidence, helping identify injected failures but making tests easier than incidents without explicit fault markers. Telemetry preparation and reasoning quality must be assessed together.

## Construct investigations with known causes

Companion applications expose 11 chaos modes, including delay, CPU load, memory allocation or leakage, errors, thread-pool blocking, lock contention, GC pressure, intermittent failures and deadlock. Toxiproxy covers network dependencies: database tests inject three-second latency, combine four-second latency with a small pool to provoke exhaustion, or cut connections. Weather-API tests similarly exercise delay and outages.

Each test injects a fault, waits for telemetry, runs analysis, captures the tool outputs actually shown to the model, and invokes a separate judge. The judge receives telemetry, the analysis prompt, the answer and scenario-specific criteria. Known injections provide a reference; captured inputs make the evidence behind a conclusion inspectable.

## Interpret the passing matrix carefully

The judge assigns 0–25 points each for completeness, root-cause accuracy, correlation and actionability, with a default passing total of 70. Analyzer and judge can use different OpenAI/Grok providers. The article reports all 19 scenarios passing in four combinations: 12 chaos/baseline, four database and three weather cases.

This supports a working regression process and reduces dependence on one model scoring itself. Cross-provider judging does not eliminate shared bias. A 70-point threshold is not 70% production RCA accuracy, and 19 passing scenarios do not cover all unknown failures. No field MTTR or large incident study is reported. The useful advance is a repeatable engineering framework for checking whether prompt, filter or model changes damage analysis of known faults.
