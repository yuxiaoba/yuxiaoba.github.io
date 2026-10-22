---
id: incident-replay-evaluation
title: '2026-10-01 | Incident Replay: Can the Agent See Enough Evidence?'
date: '2026-10-01'
lang: en
published: true
layout: article
maintenance: manual-research
source_type: tech
tags:
- observability
- agent-reliability
summary: Freeze evidence and investigation interfaces to distinguish model limitations, missing observations, and hindsight leakage.
long_read: true
source_url: https://zenn.dev/genax_corp/articles/5214d9e0228928
source_date: '2026-09-29'
permalink: /tech/en/incident-replay-evaluation/
authorship: assistant
translation_source: assistant
published_at: '2026-10-22T08:54:49.993592+08:00'
updated_at: '2026-10-22T08:54:49.993592+08:00'
---
Sho Okada · Gen-AX · 2026-09-29 · [Original article](https://zenn.dev/genax_corp/articles/5214d9e0228928)

Gen-AX copies telemetry around real incidents into a separate ClickHouse instance for repeatable Incident Agent investigations. A Collector load-imbalance case exposed an important boundary: telemetry showed the anomaly, but historical Kubernetes configuration needed to explain the network path was incomplete. Knowing a cause after the incident does not mean the agent's evidence can establish it.

<a class="note-image-link" href="/assets/images/tech/incident-replay-evaluation/replay-en.svg" target="_blank" rel="noopener" aria-label="Editorial diagram: separate investigation evidence from evaluation labels; this is not an experimental result. · Open image"><img src="/assets/images/tech/incident-replay-evaluation/replay-en.svg" alt="Editorial diagram: separate investigation evidence from evaluation labels; this is not an experimental result." loading="lazy"><span class="note-image-action">Open image ↗</span></a>

*Editorial diagram: separate investigation evidence from evaluation labels; this is not an experimental result.*

## Replay fixes the conditions of comparison

Repeating a query later can produce different results because of retention, late arrivals, or configuration changes. Freezing inputs separates model, prompt, and tool changes from changes in the environment. Offline evaluation also avoids repeatedly querying production stores.

An engineering extension is to freeze the investigation interface, not just database rows. Record schemas, permissions, time zones, tool versions, and result limits. Two experiments can read the same database yet expose different evidence through different interfaces.

## Current state cannot substitute for historical state

The [OpenTelemetry Kubernetes Objects Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/k8sobjectsreceiver) supports periodic pulls and watches. Pulls provide discrete states; watches track updates. Initial state, resource versions, and permissions also matter. Object selection and sampling frequency should follow the failure mechanisms being tested.

For routing investigations, reconstruct the service-selection relationship and receiving endpoints at the relevant time. For resource-limit investigations, distinguish the workload template from the actual running object. Saving only the final configuration can import a later fix into the original incident; saving only events can omit the baseline needed to interpret a change.

A practical evidence package could contain immutable observations, time-organized object states, and separately stored reference explanations. The investigator reads the first two, while the evaluator retains the third. Redaction should preserve entity relationships across signals, or anonymization itself may break causal analysis.

## Test fairness through evidence ablation

A controlled extension would remove one signal from a complete case while holding tools, budgets, and questions fixed. Measure changes in abnormal-object localization, mechanism explanation, and uncertainty. This is a way to estimate the signal's incremental value.

Do not demand the same complete answer from the reduced case. If the removed information is indispensable, a more cautious conclusion may be appropriate. Conversely, unchanged perfect answers after decisive evidence disappears should prompt a leakage check—or a search for a genuinely alternative evidence path.

The evaluator also needs validation. Have humans examine outputs with a correct conclusion but incorrect evidence, a correct location but incorrect mechanism, and an explicit acknowledgment of insufficient evidence. Check whether automatic scoring distinguishes them. One F1 score cannot represent all three dimensions.

## Static investigation is not interactive recovery

A frozen database does not change because an agent proposes a rollback. Evaluating remediation requires an executable environment, action permissions, state transitions, and success criteria. A plausible sequence of commands in a report is not evidence of recovery.

The most useful output of replay is therefore an evidence requirement, not only a model ranking: what must be retained, which observations distinguish candidate causes, and which conclusions depend on hindsight. That makes insufficient reasoning and insufficient observability separately testable explanations for a failed diagnosis.
