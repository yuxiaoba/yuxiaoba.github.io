---
id: modal-observability
title: '2026-10-22 | Modal observability: connect multi-cloud incidents into one investigation'
date: '2026-10-22'
lang: en
published: false
editorial_status: withdrawn
editorial_review_date: "2026-10-27"
layout: article
maintenance: daily-research
source_type: tech
tags:
- observability
- systems-reliability
summary: A reading of Modal’s Datadog case study covering cross-cloud telemetry, agent
  investigation and indexing costs, with explicit metric boundaries.
long_read: true
source_url: https://www.datadoghq.com/case-studies/modal/
permalink: /tech/en/modal-observability/
authoring_source: assistant
translation_source: assistant-authored bilingual editorial and translation
published_at: '2026-10-22T09:38:48.907626+08:00'
updated_at: "2026-10-27T13:54:34.510124+08:00"
---
AI infrastructure involves more than supplying GPUs. A user sees a function call, while the platform coordinates scheduling, containers, networks and several providers' hardware. Similar failures can originate in customer code or underlying infrastructure. Modal's case is useful because it places observability across these responsibility boundaries: establish cross-layer context, then let engineers and investigation agents use the same production evidence. Reliability percentages are customer-reported outcomes; the operational mechanism is more transferable than a universal performance claim.

**Source: Datadog / Modal · First published 2026-10-09**  
Original: [Modal scales the next generation of AI with unified observability from Datadog](https://www.datadoghq.com/case-studies/modal/). The interviewee is Akshat Bubna, Modal's CTO and co-founder.

## The problem is cross-layer attribution

The case describes more than 20 cloud providers and approximately 26 million container launches daily. Network behavior, hardware and failure modes vary by provider while workloads keep changing. A CPU spike alone cannot determine whether a slow request comes from customer code, platform scheduling or a provider network. Operations must narrow the fault and identify the responsible party.

The article does not publish a scheduler algorithm, detection model or automated remediation architecture. Its contribution is an account of a unified investigation surface: infrastructure, networking, Kubernetes, application and cloud-service signals can be correlated, and new services are instrumented during development. Coverage needs to evolve with services rather than merely with machine count.

## Data volume is different from an investigable execution

Modal uses Infrastructure Monitoring, APM, Network Monitoring, CI Visibility, logs, metrics and traces. These signals answer different questions: metrics expose deviations, logs describe events, traces connect request components, and network data helps examine host and cloud paths. The article says a unified platform reduces tool switching, but does not disclose correlation algorithms or tagging conventions.

An engineering implication is that signals must identify the same service, execution and relevant time window. Otherwise, co-located dashboards remain separate observations. For short-lived containers, identifiers and invocation context must remain useful after an instance disappears. These are design conditions inferred from the problem, not claims that Modal has published a particular schema.

Collection volume and investigability should therefore be assessed separately. More data can increase coverage while also adding cardinality, noise and query cost. Extensive logs elsewhere cannot repair a missing context link in a critical service.

## MCP exposes evidence to agents; engineers retain the investigative judgment

Datadog MCP Server is a timely part of the case. Modal gives AI agents access to production telemetry so they can correlate logs, traces, infrastructure metrics and networking signals and suggest likely causes to engineers. Assistance is grounded in production context rather than an explanation generated from an alert title alone.

The article describes assisted investigation, not autonomous remediation. It supplies no investigation-accuracy measurement, tool-success rate or permission configuration. The supported interpretation is that agents reduce manual information gathering and organization, while engineers use the resulting context to confirm causes. Treating a likely cause as established causality would skip timeline comparison, impact scoping and intervention checks.

For AgentOps, this suggests evaluating whether an assistant retrieves relevant telemetry, distinguishes correlation from causation and presents traceable evidence. Those are implications drawn from the case, not reported experimental results.

## The two reliability percentages measure different things

The case reports detection of 99% of incidents within five minutes and resolution of approximately 96% of issues before customer impact. One measures a detection window; the other concerns ordering between resolution and customer impact. Their denominators are not established as identical. Multiplying them would not yield an overall success rate, nor do they determine mean repair time, annual availability or universal early detection.

The page does not disclose observation periods, sample sizes, severity distributions or a comparison period for these percentages. This limits causal claims about product benefits: team processes, changing workloads and service maturity may also contribute. The supported finding is a customer-reported high rate of early detection and pre-impact resolution. Stronger comparisons require additional data.

## Separate ingestion and indexing, with consistent denominators

The article reports about 116 billion monthly log events, nearly 246 TB of logs, 66 production services, approximately 1,300 hosts and about 2,700 metric names. Metric names are not time-series cardinality: tag combinations can generate many series from one name, so 2,700 does not describe the complete monitoring footprint.

Two APM figures need separate treatment. One passage reports approximately 97 billion spans collected monthly. A later cost discussion reports approximately 120 billion ingested and 2.3 billion indexed. The page does not explain differences in scope or time, so these must not become one total. Within the latter passage alone, indexing is approximately 1.9% of ingestion. This arithmetic illustrates differentiated ingestion and indexing, not sampling accuracy. It does not establish retention duration, query access or loss rates for the remainder.

The trade-off makes cost questions concrete: evidence requiring fast queries should be chosen alongside investigation needs. The case does not disclose storage tiers, retention rules or complete cost curves, so cost per investigation cannot be calculated and the same indexing ratio cannot promise the same reliability elsewhere.

The original offers a presentation image rather than a complete technical architecture; it is not treated here as a dataflow specification. Read cross-layer responsibility first, then MCP investigation and ingestion/indexing distinctions. The transferable practice is timely, correlatable service instrumentation and shared context for human and agent investigation. Reliability outcomes still need interpretation through each system's detection, response and customer-impact records.

The case is therefore useful for examining evidence completeness, not selecting a fixed sampling fraction. Detection, valid diagnosis and timely response are separate stages, each needing its own records and denominator.
