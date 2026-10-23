---
id: grafana-autonomous
title: '2026-10-23 | Grafana AI: From Continuous Observation to Reviewable Patches'
date: '2026-10-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- observability
- agent-reliability
- coding-agents
summary: Watchers, Investigations, and Managed Sandboxes connect observation, investigation,
  and proposed fixes while preserving evidence and release decisions.
long_read: true
source_url: https://grafana.com/blog/grafana-ai-autonomous-operations/
permalink: /tech/en/grafana-autonomous/
translation_source: assistant
authorship: assistant
published_at: '2026-10-23T08:58:47.180720+08:00'
updated_at: '2026-10-23T08:58:47.180720+08:00'
---
A service can remain available after deployment while a subset of requests becomes progressively slower. Someone watches dashboards, someone decides whether the change matters, another investigates traces, and a developer reconstructs the problem before changing code. Grafana connects continuous observation, incident investigation, and proposed code changes to reduce context loss between those steps.

Original: [From production problem to proposed fix: Implement autonomous operations with Grafana AI](https://grafana.com/blog/grafana-ai-autonomous-operations/) · Maurice Rochau / Grafana Labs · 2026-10-20

## Three capabilities with different responsibilities

The availability stages differ: Assistant Watchers and Investigations are generally available, while Managed Sandboxes is in public preview. Watchers assess changes worth attention, Investigations examine incidents, and Sandboxes carry findings into a code environment. Connecting them does not make their maturity identical or imply automatic production deployment.

Watchers take a natural-language concern and selected data sources. Assistant analyzes historical telemetry, establishes a baseline, calibrates checks, and periodically assesses signals with supporting evidence. For a checkout service, that concern might be persistent errors or slower responses while tolerating a brief deployment disturbance. The addition is contextual judgment around service behavior.

<a class="note-image-link" href="/assets/images/tech/grafana-autonomous/overview.png" target="_blank" rel="noopener" aria-label="Grafana Watcher objective, data sources, and calibration interface · View original image ↗"><img src="/assets/images/tech/grafana-autonomous/overview.png" alt="Grafana Watcher objective, data sources, and calibration interface" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the image: the watcher states its monitoring objective and anomaly types alongside its data sources. Calibration and run records help explain the basis for subsequent assessments.*

The article preserves existing alerts for dependable paging on known conditions. That division is practical: explicit urgent conditions need not wait for open-ended reasoning, while watchers add assessment across signals and context. BigQuery support extends the possible inputs to business signals, without by itself establishing reliable explanations for business anomalies.

## An investigation should deliver an evidence chain

A critical watcher finding can trigger Investigations. The agent explores metrics, logs, traces, and profiles, tests hypotheses, and attaches source queries to findings. A useful handoff identifies affected requests, when behavior changed, and the observations supporting an explanation rather than merely saying that the database is slow.

The article's example concerns repeated database calls in a request path. That narrows code exploration and provides a testable hypothesis. Whether those calls are the dominant bottleneck still depends on load, caching, and dependencies. Preserving the result as an evidence-backed hypothesis helps prevent an unconfirmed inference from becoming an asserted root cause at the next handoff.

An engineering implication is to retain the time range, query conditions, and observed entities. Running the same query later may return different data, making the original situation difficult to reconstruct. The release demonstrates source-linked findings but provides no controlled diagnostic-accuracy or investigation-time comparison. It currently supports an assessment of workflow capability, not an automatic-RCA success rate.

## Sandboxes turn recommendations into reviewable changes

Managed Sandboxes provides controlled cloud environments. With a repository connected and coding enabled, an agent can inspect code, prepare changes, and run available checks. Repository-specific environments can provide build and test dependencies so investigation context reaches implementation rather than ending in chat.

For the checkout example, the next task is to examine data access, prepare a targeted change, and add a regression test. The desired output is a pull request explaining the modification, its relationship to the hypothesis, checks performed, and remaining uncertainty. Ending automation at a concrete review artifact lets developers inspect code rather than approve only a natural-language suggestion.

Passing tests establishes only the tested behavior. If the root-cause hypothesis is wrong, a functionally correct patch may not improve production latency. The team still judges suitability and rollout, then checks recovery and recurrence using production telemetry. Investigation, code, and recovery measurements must connect before PR creation can count as incident resolution.

## Autonomy distributes decisions across stages

The combination delegates recurring observation, evidence gathering, and patch preparation while preserving important release decisions. The article also permits fuller delegation for suitable tasks. The engineering question is therefore what inputs, outputs, and actions each stage receives, and which results require confirmation by people or existing systems.

A low-risk periodic analysis might produce only a report. An investigation leading toward production changes needs traceable queries, bounded repository scope, and explicit acceptance signals. These are engineering implications of the workflow, not additional default-permission promises from the announcement. During public preview, teams should verify that sandbox environments and available checks fit their projects rather than infer complete boundaries from the word controlled.

## Judge value through the handoffs

The article recommends beginning with a familiar service: define behavior, calibrate a watcher, inspect findings, and then connect a repository for a bounded coding task. This helps identify which stage saves time: earlier detection, less evidence gathering, or a faster path to a reviewable patch.

Useful measures include evidence validity, repeated investigation needed by the recipient, project-test outcomes, and production recovery after release. They are closer to operational value than conversation or PR counts. No common MTTR or cost-benefit measurement is published, so connecting the workflow should not be described as a proven remediation speedup.

## Make each checkout handoff independently testable

The checkout example suggests three separate acceptance artifacts. A watcher should explain why the slowdown exceeds ordinary deployment disturbance. Investigations should supply queries and traces supporting repeated database calls. The sandbox should connect its code change to that path and describe regression-test coverage. Even if the patch is rejected, the earlier investigative work can retain value.

If every handoff contains only prose, details can disappear: the original time boundary is dropped, a possible cause becomes a definite claim, and the patch adds tests around that claim. Each stage appears complete without continuing to test the original problem. This is general engineering reasoning about chained agent workflows and explains why source queries and reviewable changes matter more than longer explanations alone.

A pilot should therefore support stopping between stages: retain findings when evidence is insufficient, deliver a bounded proposal when the test environment is incomplete, and revisit the hypothesis when production recovery disappoints. Expressing those states clearly can matter more than always reaching the final step. The announced features connect stages; teams still need service-appropriate stopping conditions.

**The development is observability context entering the coding environment.** The next question is whether that evidence survives every stage, so automated observation, investigative reasoning, sandbox development, and human release continue testing the same failure hypothesis.
