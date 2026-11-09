---
id: 2026-11-04-pagerduty-pd-labs-sre-agent
title: '2026-11-04 | Technical reading: Lessons from PD Labs: From experimentation
  to a production-ready SRE Agent'
date: '2026-11-04'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://www.pagerduty.com/eng/lessons-from-pd-labs-from-experimentation-to-a-production-ready-sre-agent/
source_published_at: '2026-11-03'
tags:
- systems-reliability
authoring_source: assistant
translation_source: assistant
permalink: /tech/en/2026-11-04-pagerduty-pd-labs-sre-agent/
long_read: true
summary: "How revisable hypotheses, code-derived topology and live-fault evaluation support an SRE agent."
---

## Investigations maintain revisable hypotheses

PagerDuty frames the problem as sustained incident investigation: decisive evidence may not exist at the first alert, and the alerting service may not be the failing component. SRE Workbench shares timelines, logs, deploys, dependencies and notes between people and agents. Deep Investigation localizes a component and then asks what failed inside it, retaining multiple candidate explanations.

Evidence connects a specific claim to a log line, metric, deploy or transcript and distinguishes direct from circumstantial support. A missing required configuration can reveal a mechanism; a simultaneous error spike only suggests where to look. The article describes an early agent blaming a co-occurring symptom, motivating retention of rejected explanations and counterevidence. Investigation continues as telemetry and human guidance arrive.

## Building queryable topology from code facts

Topology lets an investigator walk upstream toward causes and downstream toward impact. Collectors parse source, deployment configuration and infrastructure definitions into facts about hosts, databases and queues, with file/line references. A central engine joins facts across repositories to resolve environment variables, Helm values and Terraform outputs.

Most graph construction does not require an online agent. AI works offline to identify unfamiliar framework idioms and propose reusable extraction rules; established rules execute deterministically. This turns architecture inference into traceable fact resolution. Alert co-occurrence is a separate blast-radius signal: simultaneous alerts may share an external cause and do not establish a dependency edge.

## Evaluation changes architectural choices

The team combines historical replay with injected faults in a private EKS microservice system. Configuration, code, data and operational scenarios use Helm, Chaos Mesh, PR merges and AWS control-plane changes. The latest report contains 17 scenarios, with a three-provider model-judge ensemble scoring root cause, localization, mitigation, misdirection and latency. An early complex multi-agent design was slow, costly and mid-field on some incidents; rebuilding parts reportedly improved diagnosis by roughly 20 points.

This remains a vendor-built evaluation, not an independent cross-product verdict. Historical replay can leak hindsight and omit context; the live benchmark cannot yet reproduce the value of human input. My interpretation is that the transferable design treats agent topology as testable and preserves evidence and hypothesis revisions in a persistent investigation. Counterevidence and misdirection metrics address on-call needs more directly than one plausible root-cause answer.

Source: [Original engineering article](https://www.pagerduty.com/eng/lessons-from-pd-labs-from-experimentation-to-a-production-ready-sre-agent/)
