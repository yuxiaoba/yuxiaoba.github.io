---
date: '2026-11-12'
published: true
layout: article
maintenance: daily-research
translation_source: assistant
writing_source: assistant
id: quarkus-ai-root-cause-analysis
title: '2026-11-12 | Quarkus AI RCA: prepare telemetry before asking for a diagnosis'
lang: en
source_type: tech
long_read: true
source_url: https://quarkus.io/blog/ai-root-cause-analysis/
tags:
- observability
- agent-reliability
summary: An MCP pipeline correlating traces, logs, and metrics, with a trade-off between
  context filtering and diagnostic evidence.
permalink: /tech/en/quarkus-ai-root-cause-analysis/
published_at: '2026-11-12T08:58:59.941917+08:00'
updated_at: '2026-11-12T08:58:59.941917+08:00'
---
[AI Root Cause Analysis: LLM-Powered Root-Cause Analysis for Distributed Systems](https://quarkus.io/blog/ai-root-cause-analysis/)  
Ales Justin · 2026-11-10

Distributed-system investigations often move between Tempo, Loki, and Prometheus. Quarkus AI Root Cause Analysis connects those steps in an application: start from recent traces, add related logs and metrics from the same time window, and ask an LLM for a structured diagnosis. This is a concrete integration report, without published RCA accuracy or a large incident benchmark.

## Build context around traces

The application queries Tempo through MCP for errors, latency, and unusual traces, retrieves associated Loki logs, and adds Prometheus system context. Reports distinguish proposed causes and symptoms and include severity and remediation. Trace/span and time-window relationships reduce irrelevant context, but correlation does not establish causal direction.

The gateway-latency, connection-pool-warning, and heap-pressure example illustrates a possible report. It is not an incident evaluation and does not substantiate a measured MTTR improvement over manual investigation.

## Filtering controls both context and evidence loss

A StripMcpClient decorator applies tool-specific filters between MCP and the LLM. It removes SDK/instrumentation metadata from traces, redundant log fields, and selected constant, internal, histogram-bucket, and regional metric details. The reported reduction from 586 metric entries to about 35 is approximately 94% less input, not 94% better diagnosis.

Deterministic filtering can make salient signals fit the context window, but regional or tail-latency faults may need the removed dimensions. That is an engineering implication of the mechanism; the article does not provide a before/after diagnostic ablation. Filter compatibility with the incident matters more than token reduction alone.

## Source inspection and dashboards are optional extensions

When monitored applications run in Quarkus development mode with Dev MCP enabled, the analyzer can inspect source locations and write generated Grafana dashboards into application sources. Without that connection, telemetry analysis still works and dashboard JSON can be imported manually. These modes have different permissions and output destinations; they should not be conflated with default production code modification.

The interface reports duration, LLM calls, and token use, making investigation overhead visible. Architecture and chaos-testing evaluation are deferred to a companion article. The immediate AIOps contribution is a concrete way to expose existing LGTM evidence to an agent. Dependable causal diagnosis still needs incident and intervention evidence. The source primarily supplies UI screenshots, so this note remains textual rather than presenting an interface as architecture.
