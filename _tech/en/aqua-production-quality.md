---
id: aqua-production-quality
title: '2026-10-08 | Google AQuA: Finding Quality Issues in Production Traces'
date: 2026-10-08
reviewed_on: 2026-10-18
long_read: true
lang: en
source_type: tech
source_url: https://developers.googleblog.com/en/the-outer-loop-insights-first-an-ambient-quality-agent-that-diagnoses-your-production-agent/
repo: https://github.com/google/adk-recipes/tree/main/core/python/ambient-quality-agent
organization: Google
tags:
- agent-reliability
- observability
summary: Analyze sessions alongside deployment snapshots to turn scattered failure traces into verifiable, actionable issues.
published: true
maintenance: manual
approved_on: '2026-10-19'
layout: article
permalink: /tech/en/aqua-production-quality/
translated_on: '2026-10-19'
translation_source: /tech/zh/aqua-production-quality/
translation_method: assistant translation of the locally approved Chinese article
original_tags:
- AgentOps
- observability
- diagnosis
- evaluation
---
**Google · Reference implementation for quality engineering**  
Original article: The Outer Loop, Insights First: An Ambient Quality Agent That Diagnoses Your Production Agent

## Why quality can decline while the service stays healthy

In Google's travel-assistant example, a user requests seat 3A. The agent records it as confirmed without asking the seat-selection agent whether it is available. In another example, a dietary preference fails to reach a downstream agent, which recommends a steakhouse to a vegan traveler. Both interactions can return successful HTTP responses without tool-call errors.

Operational monitoring readily exposes latency, exceptions, and request volumes. Quality scores can reveal changes in task success. But identifying recurring failure patterns and deciding where to fix them still requires reading traces, configuration, and source code. AQuA moves this work alongside the production system, feeding findings back into development-time evaluation and repair.

## How it fits alongside scoring and runtime monitoring

Quality engineering involves three questions: does a version pass known test cases, has production behavior changed, and what actionable defects explain that change? Offline evaluation addresses the first question, online metrics help with the second, and AQuA primarily addresses the third.

For the incorrect seat confirmation, latency and error rates look normal. A task evaluator might detect a failure, but an engineer still needs to identify the recurring pattern. AQuA groups similar sessions and examines the corresponding deployment revision to check whether an instruction is missing: seat availability must be verified even when the user directly names a seat.

Its role also differs from a monitor that blocks actions during execution. Analysis outside the request path adds no synchronous judgment step to each business request. However, a separate repair and release process is still needed after an issue is found. AQuA therefore supports continuous defect discovery and triage; it does not replace authorization or safeguards before high-risk actions occur.

## Architecture: analyze sessions against the version that produced them

<a class="note-image-link" href="/assets/images/tech/aqua-production-quality/aqua-architecture.png" target="_blank" rel="noopener" aria-label="AQuA architecture for analysis outside the request path, view original"><img src="/assets/images/tech/aqua-production-quality/aqua-architecture.png" alt="AQuA architecture for analysis outside the request path" loading="lazy"><span class="note-image-action">View original ↗</span></a>

*Reading the diagram: the business agent handles requests and emits telemetry. AQuA separately reads sessions and deployment-time source snapshots, then stores findings. It neither intercepts requests nor writes changes back to the business agent.*

The crucial combination is **execution evidence plus the corresponding deployment revision**. Inspecting only the current repository risks explaining an old failure with new code. A deployment snapshot lets the diagnosis refer to the instructions, tool declarations, and orchestration logic actually in effect at the time. If the problem lies in an external dependency or a handoff, the diagnosis can identify that trajectory step without forcing a source-code patch.

AQuA organizes issues that have already occurred, leaving engineers or coding agents to implement repairs. Its outputs are evidence-backed findings and proposed changes; it does not apply edits or open pull requests automatically.

## What happens during a quality sweep

<a class="note-image-link" href="/assets/images/tech/aqua-production-quality/aqua-pipeline.png" target="_blank" rel="noopener" aria-label="AQuA sampling, review, clustering, verification, and tracking pipeline, view original"><img src="/assets/images/tech/aqua-production-quality/aqua-pipeline.png" alt="AQuA sampling, review, clustering, verification, and tracking pipeline" loading="lazy"><span class="note-image-action">View original ↗</span></a>

*Reading the diagram: sample sessions, review them individually, group related findings, verify against full transcripts, and track issues across runs. Root-cause diagnosis, shown at the lower right, runs on demand.*

A sweep samples recent sessions and evaluates them against the agent's instructions, tool definitions, and optional business goals. Findings that appear to share a failure mechanism become candidate clusters. A separate model checks complete sessions and discards unsupported clusters. Verified issues enter ongoing tracking; those worth investigating can trigger source-level diagnosis.

This turns many individual failures into a manageable queue while retaining a path back to the original evidence. However, verification reads at most three full transcripts per cluster. **It checks the proposed pattern, not the correctness of every member's classification.** Occurrence counts help prioritize work but should not automatically be treated as exact defect counts.

## What makes a finding suitable for an issue queue

**Describe the discrepancy before explaining its cause.** Initial reviews record actual versus expected behavior. Saving a seat into session state is an observed action; explaining why availability checking was skipped requires further inspection of the trajectory and source. Keeping these stages separate reduces the risk of guessing a cause first and selecting evidence to fit it.

**Clusters still need verification.** In the published example, the verifier rejected three candidate clusters. Some behavior had been explicitly requested by the traveler; another cluster had combined unrelated problems from different sub-agents. Similar-looking outcomes do not necessarily share a failure mechanism. Having another model read full conversations provides a check on compression and clustering.

**Issue status is not proof of repair.** Issues can be classified as new or recurring, or automatically resolved after 14 days without another observation. The last status is a tracking rule: absence from sampled traffic does not prove that a defect has been eliminated through counterfactual testing. That distinction matters when using the queue as a quality metric.

Source-level diagnosis also requires references to files and lines that exist in the deployment snapshot. Invalid references are rejected. This prevents nonexistent locations from appearing in a finding, but the existence of a cited file does not by itself establish that the diagnosis is correct.

## What improvement did the example demonstrate?

Google replayed four scripted travel scenarios across 32 sessions. Review produced 42 findings, which became nine candidate clusters and then six verified issues. After instruction changes addressing seat verification and dietary-preference handoffs, replaying the same sessions produced these results:

| Observation | Before changes | After changes |
| --- | --- | --- |
| Sessions bypassing seat checks | 15 | 2 |
| Sessions omitting the vegan preference | 7 | 0 |
| Fully passing sessions | 5/32 | 13/32 |

These results demonstrate a useful scan–diagnose–edit–recheck workflow in the authors' controlled example. They are not evidence of a general production success rate across products. Only 13 of 32 sessions passed completely, and defects that were not addressed remained.

## Why cost depends on trajectory complexity

The authors report approximately $0.70 for a sweep of 96 shorter single-agent sessions, versus $3.76 for 32 travel-assistant sessions with roughly 50 spans each. These figures describe the configurations in the original article; the first cannot simply be extrapolated into a universal per-session price.

Deeper trajectories contain more instructions, tool results, and handoffs, increasing the context that review and verification must process. Root-cause diagnosis is triggered separately rather than reading the repository for every session in every sweep. This separation is more useful for understanding cost than a single average price.

The reference implementation bounds work through random sampling, verification of at most 50 clusters per run, and at most three full transcripts per cluster. Coverage is therefore incomplete. A rare but important silent failure may never enter the sample. Filtering only by timeouts or high latency can instead repeatedly select the same obvious failure class.

## Three prerequisites for adoption

**Enough evidence.** Sessions need to be associated with the effective instructions, tool declarations, and deployment revision. Fragmented logs can leave diagnosis without essential context.

**Explicit business goals.** A model does not know every product rule. A requirement such as “verify availability even when the user directly specifies a seat” is more actionable than a general instruction to improve quality.

**A way to revalidate.** Replaying user inputs does not reconstruct the original environment. Changed database records, non-idempotent tools, or different dependencies between turns can all cause replay to diverge from the original failure.

## Engineering assessment

Teams with centralized traces, deployment-version management, and explicit business rules can study the combination of discovery, verification, diagnosis, and feedback into evaluation. Where those records are incomplete, the first step is to identify which conclusions the evidence can support, rather than hiding missing information behind automated review.

Human review of candidate issues and representative sessions remains valuable. It can expose false positives and refine the business goals used by the system. Proposed fixes should then return to isolated testing and the release process: maintaining an issue queue and validating a repair are connected but distinct activities.

**AQuA is a useful reference for teams that already collect production trajectories but still investigate quality manually.** It offers an implementation path for triage and revision-aware diagnosis. Random sampling can miss rare silent failures, and model-based verification still needs calibration. The official repository includes a local demonstration with synthetic data. This article reviews the materials; it does not report a deployment or reproduction of the system.
