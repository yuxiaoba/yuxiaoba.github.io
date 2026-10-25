---
id: agent-anomaly-detection
title: '2026-10-25 | Agent Anomaly Detection: Asynchronous Auditing of Session Behavior'
date: '2026-10-25'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- anomaly-detection
- observability
summary: 'Google Cloud expands its preview to GKE and Cloud Run: layered analysis,
  telemetry prerequisites, and the boundary between findings and blocking.'
translation_source: assistant
authorship: assistant
long_read: true
source_url: https://docs.cloud.google.com/gemini-enterprise-agent-platform/agent-anomalies-overview
permalink: /tech/en/agent-anomaly-detection/
published_at: '2026-10-25T08:48:16.922011+08:00'
updated_at: '2026-10-25T08:48:16.922011+08:00'
---
An agent can return no errors while scraping data, crossing an authorization boundary, or consuming resources repeatedly. Google Cloud's Agent Anomaly Detection extends monitoring to tool use and execution behavior across a session, screening candidates before asynchronous reasoning. Its October 22 preview update adds GKE and Cloud Run support, bringing that audit path to additional deployment environments.

Original: [Agent Anomaly Detection overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/agent-anomalies-overview) · Google Cloud documentation, feature update 2026-10-22  
Initial announcement: [Agent Anomaly Detection, now in Private Preview on the Gemini Enterprise Agent Platform](https://developers.googleblog.com/agent-anomaly-detection-now-in-private-preview-on-the-gemini-enterprise-agent-platform/) · Achuth Narayan Rajagopal · 2026-09-16

## Behavior that error metrics miss

An inventory tool can return valid responses while a user requests large pages and jumps through offsets to retrieve the entire catalog. Each call succeeds; the session nevertheless differs from ordinary browsing. The gap between tool success and acceptable business behavior motivates this service.

It analyzes OpenTelemetry traces and logs, including reasoning records, tool interactions, and execution flows. Default categories include tool misuse, identity and privilege abuse, cascading failures, rogue behavior, and resource exhaustion. Mapping findings to security categories helps existing incident workflows, but category coverage does not establish measured detection recall.

## How three layers allocate analysis

The first layer uses statistics and lightweight machine learning to identify outliers and narrow traffic for deeper analysis. The second asynchronously reasons about flagged sessions, producing verdicts and explanations. The third examines individual tool executions, states, and parameter histories. Expensive analysis is concentrated on candidates instead of treating every ordinary call equally.

Coverage depends on this selection. A session missed by the first pass may never receive deeper interpretation; an overly sensitive pass increases analysis load and alerts. Public material describes the pipeline without reporting layer thresholds, false-negative rates, or per-session cost. It therefore does not establish an optimal configuration for a particular business.

<a class="note-image-link" href="/assets/images/tech/agent-anomaly-detection/session.png" target="_blank" rel="noopener" aria-label="Inventory-agent session with an anomaly finding and explanation · View original image ↗"><img src="/assets/images/tech/agent-anomaly-detection/session.png" alt="Inventory-agent session with an anomaly finding and explanation" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*The session appears on the left, interaction in the middle, and resource-exhaustion assessment and recommendations on the right; 95% is this example’s probability field.*

In the official inventory example, a user asks for 100 items per page and uses varying offsets to retrieve the catalog. The finding shows resource exhaustion, Critical severity, 95% probability, and recommendations to restrict tool access. That 95% is a field in an example finding, not a 95% accuracy result on an evaluation set. General calibration across tasks is not established either.

## Asynchronous audit and immediate blocking

Analysis runs outside the synchronous request path, avoiding direct waiting for an assessment on each response. The corresponding trade-off is a window between action and finding. Findings support later investigation, and an API lets an ADK callback or plugin consult session anomalies before subsequent tool calls or the next turn.

The description does not establish that every dangerous action is blocked before it occurs. An irreversible tool action may still require independent synchronous authorization according to its risk and business rules. This is an engineering implication: asynchronous findings can support audits, escalation, and subsequent restrictions, but cannot alone certify admission of every action.

Findings integrate with Security Command Center, subject to supported tiers. Detection and coverage metrics enter Cloud Monitoring for dashboards and alerts. One helps explain incidents; the other helps establish what is actually monitored. Discovery of an agent and active analysis of that agent are separate states.

## What the runtime expansion requires

Current documentation lists Agent Runtime, Cloud Run, and GKE, with Python ADK 2.1.0 or later. The September announcement mentioned ADK 1.2 or later; the newer documentation is the relevant prerequisite here. Cloud Run services are discovered through telemetry exported to Cloud Trace and Cloud Logging. Eligible agents still require explicit enablement for analysis.

Discovery needs a complete data path: tracing and logging enabled, prompt inputs and response outputs captured, and enable_tracing not explicitly false. Regional scanner accounts need reader permissions over the relevant buckets; the log bucket needs the required analytics capabilities. Active telemetry is required because an empty configuration cannot establish enrollment.

Location constraints also matter. Logging and observability buckets must match the detection scope's location, with the documented global exception for US scopes and an eu log location for EU scopes. Eligible objects become known as monitored agents, but analysis starts only after explicit enablement. The preview remains restricted to approved users; supporting additional runtimes does not make access unconditional.

## Evidence retention is part of integration

The telemetry-reduction article in this issue removes bulky prompt and tool content, whereas this service explicitly requires content capture. If an upstream pipeline deletes that evidence, downstream intent analysis cannot reconstruct it. An engineering approach is to specify what each data path must answer before deciding which fields feed statistical monitoring and which remain inside a controlled behavioral-audit boundary.

That is an interpretation connecting the two sources, not an announced automatic compatibility feature. Business-specific custom detectors were described as forthcoming in the initial announcement and should not be treated as delivered. The useful follow-up measures are misses, false alarms, finding latency, coverage, and human triage quality. Current material explains the architecture and prerequisites without establishing a general solution to agent security.

## Preserve the action boundary in alerts

The inventory interface explicitly identifies a session-level anomaly rather than a specific threat in each invocation. Multiple individually valid calls form the suspicious pattern. A static tool allowlist may miss cumulative behavior, while a severe finding still needs interpretation against business purpose.

Operationally, the explanation, session, and suggested response should travel together rather than exposing only a label. Stopping tools, limiting usage, or escalating to a person should follow application authorization rules. The example's rate limits and authorization checks illustrate response options; they do not establish a universal threshold separating legitimate bulk access from scraping.
