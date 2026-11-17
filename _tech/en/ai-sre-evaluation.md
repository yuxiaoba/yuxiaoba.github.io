---
tech_deep_read: true
date: '2026-11-10'
published: true
layout: article
maintenance: daily-research
authoring_source: assistant
authorship: assistant
translation_source: assistant
editorial_status: source-checked
id: ai-sre-evaluation
title: '2026-11-10 | AI SRE Evaluation: Unpacking PoC Misjudgments Across Diagnosis,
  Citations, and Blast Radius'
lang: en
source_type: tech
source_url: https://one2n.io/blog/what-changed-in-how-we-evaluate-ai-sre-agents
long_read: true
tags:
- observability
- agent-reliability
- systems-reliability
summary: Tracing One2N's OpenSRE -1 PoC failure and coding-harness gaps to separate
  diagnosis accuracy, grounded evidence citations, and operational blast-radius gates
  with clear replay boundaries.
permalink: /tech/en/ai-sre-evaluation/
published_at: '2026-11-10T09:37:04.860576+08:00'
updated_at: '2026-11-16T12:00:00+08:00'
---
Biswa Prakash Mishra (SRE @One2N) · 2026-11-02 · [Primary Post: "What changed in how we evaluate AI SRE agents"](https://one2n.io/blog/what-changed-in-how-we-evaluate-ai-sre-agents) (subtitle: *"Why a coding harness is not an AI SRE agent"*) · Part 1 Context: ["How to evaluate AI SRE agents for production"](https://one2n.io/blog/how-to-evaluate-ai-sre-agents-for-production)

Once general-purpose coding agents gained MCP and CLI access to query Kubernetes clusters and read logs, nearly every infrastructure team started asking the same question: *"Why buy or build a dedicated AI SRE agent when I can just use Claude to root-cause incidents?"* One2N's November 2026 engineering retrospective does not answer that mindset with vendor slogans. Instead, it goes back to a concrete proof-of-concept failure during its earlier **OpenSRE** evaluation: when a coarse root-cause-analysis (RCA) rubric gave a `-1`, reviewers realized they could not even tell whether the agent aimed at the wrong resource, fabricated a deployment narrative, or spotted the right symptom without citing a single piece of telemetry.

> **Evidence & scope boundary**: This note synthesizes One2N's primary post alongside the three external references it explicitly cites ([Part 1 on OpenSRE v0.1 PoC evaluation](https://one2n.io/blog/how-to-evaluate-ai-sre-agents-for-production), the live benchmark paper [SREGym](https://arxiv.org/abs/2605.07161), and [Google SRE: AI in SRE](https://sre.google/resources/practices-and-processes/ai-engineering-reliable-operations/)). **One2N's November 2 post is a PoC-driven revision of evaluation criteria—it conducts no new empirical benchmark, publishes no comparative vendor scorecard, and reports no attributable MTTR experiment** (deferring performance-versus-cost measurements to follow-up posts). Where this note separates deterministic assertions from LLM rubric judges or maps progressive incident-replay boundaries, those engineering derivations are explicitly labeled and complement our companion reading on judge calibration, [Jev as a Judge for SRE](/tech/en/sregym-jev-as-a-judge/).

## Unpacking the `-1` PoC Failure: Separating Diagnosis, Evidence, and Operations

In its August 2026 Part 1 evaluation of OpenSRE, One2N scored five initial dimensions—**Actionability and control safety**, **RCA quality**, **Integrations and correlation**, **Incident memory**, and **Security**—around two practical questions: can the agent deliver an evidence-backed answer the on-call engineer can trust during an incident, and can that answer **safely** reduce time to mitigate?

In practice, those five buckets proved too coarse to diagnose why an investigation failed. During one PoC fault injection, the authors intentionally scaled a Kubernetes deployment's replicas to `0` using `kubectl`. OpenSRE blamed a **Helm rollback** as the root cause with zero supporting evidence and received an RCA score of `-1`. That single negative scalar collapsed three completely distinct engineering defects that demand non-interchangeable fixes:

1. **Wrong target / localization**: blaming the Helm release instead of the scaled-to-zero Deployment, pointing to missing topology or change-correlation plumbing;
2. **Wrong causal narrative**: claiming a rollback occurred when someone manually set replicas to `0`, pointing to plausible-sounding pattern completion substituting for missing change facts;
3. **Right symptom, zero grounded evidence**: even when an agent mentions a scaled-to-zero Deployment, omitting the underlying events, logs, or metric series leaves an on-call responder unable to verify or safely act on the claim.

More broadly, walking through how engineers actually debug with a laptop coding harness exposed why raw model intelligence is rarely the bottleneck. An engineer gets paged, opens a coding harness, pastes the alert link and whatever context is handy, lets MCPs or CLIs run queries, and reads a suggested root cause and mitigation. As One2N puts it, pointing Claude at a scaled-to-zero Deployment will often find the cause—**the real gap between a coding harness and an AI SRE agent lies in everything surrounding the answer**:

- **Ad hoc context**: a laptop session lacks shared architecture maps, service terminology, and up-to-date runbooks unless manually fed by whoever happens to be on call;
- **Credential masquerading**: commands triggered inside a local harness run under the engineer's personal credentials, making postmortems unable to separate human actions from agent actions while exposing overly broad developer access;
- **Opaque remediation scripts**: coding agents assemble hard-to-read bash scripts that operators either distrust completely or run under incident stress without fully understanding the blast radius.

To stop conflating reasoning quality with operational readiness, the revised evaluation breaks assessment across three orthogonal axes: **diagnostic accuracy**, **grounded evidence and shared auditability**, and **operational blast-radius guardrails**.

<figure class="note-figure">
  <a class="note-image-link" href="/assets/images/tech/ai-sre-evaluation/sre-eval-three-axes-en.svg" target="_blank" rel="noopener">
    <img src="/assets/images/tech/ai-sre-evaluation/sre-eval-three-axes-en.svg" alt="Three-axis AI SRE evaluation breakdown diagram: top row contrasts One2N's OpenSRE -1 scaled-to-zero PoC misdiagnosis and coding-harness blind spots; center columns separate Axis 1 Diagnostic Quality using SREGym's 3x3 localization, characterization, and scope rubric with a 7/9 pass rule, Axis 2 Grounded Evidence and Audit covering hypothesis links, stored traces, shared team views, separate agent IDs, and structured intent, and Axis 3 Blast-Radius and Guardrails covering least privilege, dry runs, action caps, loop breakers, risk scoring, PII scrubbing, and escalation; bottom bar summarizes the coding harness vs. AI SRE gap and scope limits." width="960" height="540" loading="lazy">
    <span class="note-image-action">Expand diagram ↗</span>
  </a>
  <figcaption>Assistant diagram (not an original figure): Decomposing One2N's OpenSRE -1 misdiagnosis and coding-harness limits into three independent evaluation axes.</figcaption>
</figure>

## Diagnostic Quality and Judges: Deterministic Checks vs. LLM Rubrics

A single RCA grade also hides how much clean sandbox tests flatter an agent. In One2N's OpenSRE PoC, tests used clear single-cause failures such as scaling a database to zero. Production environments rarely look that clean: systems constantly carry benign anomalies and background warnings unrelated to the active outage.

To evaluate diagnosis under production-like noise, One2N adopts two ideas from [SREGym](https://arxiv.org/abs/2605.07161): injecting faults across multiple stack layers alongside realistic background noise, and replacing holistic pass/fail grades with **nine binary yes/no questions graded by an LLM judge**—three each across **fault localization**, **fault characterization**, and **failure scope**. Because all three dimensions carry equal weight and a diagnosis passes at **7 of 9**, an agent cannot pass while failing an entire dimension (`0/3`). That structural constraint directly catches "named the right deployment, invented the wrong mechanism" failures.

Complementing our separate close reading of [SREGym's Jev-as-a-Judge calibration study](/tech/en/sregym-jev-as-a-judge/), applying One2N's PoC lessons to production acceptance highlights a crucial engineering split: **never use an LLM judge to verify invariants that deterministic code can check cheaply and strictly**. Objective facts—whether a cited pod, metric query, or deployment event exists in the telemetry snapshot, whether an agent uses its own non-human identity, whether PII/secrets were scrubbed, and whether a proposed action passes a dry run within deployment/AZ caps—belong in hard programmatic gates. Semantic LLM or calibrated decision judges remain valuable where prose varies legitimately, such as judging whether an explanation separates root cause from downstream symptoms—while keeping SREGym's own warning front and center: **agreement between judges is not independently established ground-truth accuracy**.

| Evaluation Plane & Artifact | One2N PoC / Coding-Harness Failure Mode | Deterministic Checks (Rules, Snapshots & Control Plane) | Semantic Rubric (LLM / Calibrated Judge) |
| :--- | :--- | :--- | :--- |
| **Diagnosis (Localization / Mechanism / Scope)** | Single `-1` score conflated wrong target, false Helm rollback narrative, and missing proof; clean single-cause tests hid noise fragility | Verify cited component IDs, namespaces, and time windows against ground-truth fault or change manifests | Apply SREGym's 3×3 binary rubric to judge whether prose separates origin, failure mechanism, and blast scope (`7/9` bar) |
| **Evidence Grounding & Refutation** | Report mentioned zero replicas with zero logs or metrics; fabricated rollback had no supporting deployment event | Assert every cited log query, metric series, or change hash exists in the captured investigation telemetry snapshot | Assess whether attached evidence semantically supports the accepted hypothesis and accounts for ruled-out alternatives |
| **Audit Traceability & Identity** | Terminal investigations stayed unlogged; running under engineer machine credentials merged human and agent audit trails | Enforce full trace ingestion (alert to queries, tool calls, actions, verdict) and non-human agent credential separation | Review whether the concise structured intent faithfully summarizes actual tool trajectories rather than post-hoc rationalization |
| **Mitigation & Blast-Radius Control** | Opaque generated bash scripts distrusted or run blindly under stress; no guard against cascading or repeated actions | Gate execution on pre-checks, dry-run exit status, rollback plan presence, rate limits, and single-deployment or single-AZ caps | Evaluate alongside action risk scores whether handoff escalation summaries give the second responder clear, safe next steps |

*Engineering derivation note: This table maps One2N's revised requirements and SREGym's 3×3 rubric into deterministic versus semantic verification layers; One2N's November 2 post does not run empirical judge-comparison experiments or report filter rates.*

## Initiation Timing, System Coverage, and Governable Memory

Even a well-grounded diagnosis loses value if it arrives too late or misses system-wide state. One2N's revised criteria treat **when** an investigation starts and **what** institutional context it sees as first-class evaluation gates rather than afterthoughts.

First, investigation triggers fall into three distinct tiers:

- **Reactive**: manually triggered by an engineer after getting paged—wasting the entire window between incident onset and human triage;
- **Proactive**: automatically started when an alert fires, completing initial queries, change checks, and evidence-linked hypotheses before the responder arrives;
- **Preventative**: running *before* any alert fires, such as watching error-budget burn rates or checking every new deployment against recent incidents in the same service.

Crucially, One2N stays disciplined about claims here: proactive and preventative workflows remove pre-arrival idle time in design, **but proving actual MTTR reduction still requires production incident timestamps and comparative baselines**, which this post does not provide.

Second, One2N separates **global read context** from **write authority**. Connecting only a log backend leaves an agent blind to Infrastructure-as-Code (IaC), CI/CD pipelines, code repositories, and feature flags. An AI SRE agent needs read coverage across five use cases (triage, RCA, remediation, postmortems, prevention), five environments (cloud, Kubernetes/VMs, on-prem, databases, network), and broad operational integrations—among which **change data is singled out as the most critical signal**, since correlating incidents with recent changes prevents false stories like "Helm rollback." Seeing the entire system read-only never implies permission to mutate it.

Third, laptop harnesses make incident quality dependent on who happens to be on call: two engineers investigating the same outage get different results depending on what context they paste and how they steer prompts. One2N's updated baseline requires shared **organisational context** (architecture, service ownership, dependencies, recent changes), codified **shared skills** extracted from institutional debugging workflows, bidirectional **runbook and postmortem updates**, and **governable agent memory** that engineers can inspect, edit, and delete so stale beliefs do not silently poison future incidents.

## Auditability, Shared Steering, Blast-Radius Guardrails, and Replay Boundaries

The final mile separating a compelling demo from trusted incident operations lies in team handoffs and execution control. In a personal terminal, steering commands like *"check the database instead"* and lists of ruled-out hypotheses stay trapped on one laptop; a second engineer joining the call arrives blind. Similarly, asking stressed responders to audit pages of raw chain-of-thought reasoning or improvised bash scripts breaks operational safety.

One2N's revised requirements replace terminal improvisation with hard operational contracts:

- **Shared, traceable investigation records**: link every considered hypothesis to supporting or rejecting logs, metrics, and traces; store every query, tool call, action, and conclusion in an observability backend for postmortem debugging and offline agent evals; enforce a **separate agent identity** so agent commands never masquerade as engineer-typed commands;
- **Structured intent and dry-run mitigation plans**: summarize reasoning concisely with traceable execution links rather than exposing raw CoT walls, attach pre-checks, **dry runs**, success criteria, and rollback steps to every proposed fix, and maintain a shared team hypothesis view for collaborative steering;
- **Strict action guardrails**: read-only default with short-lived credentials and per-action, per-service write/approval rules; rate limits, dry runs, and **blast-radius limits** (capping an action to one deployment or one availability zone) alongside control-plane loop breakers (halting repeated deployment restarts); **per-action risk scores**; **PII and secret scrubbing** before telemetry reaches the model or stored logs; and structured **escalation** handing over the entire investigation state whenever confidence or permissions fall short.

Bringing One2N's PoC lessons together with SREGym and [Google SRE's AI in SRE framework](https://sre.google/resources/practices-and-processes/ai-engineering-reliable-operations/)—which similarly warns that probabilistic agents require machine-speed guardrails and guaranteed undo paths—clarifies why teams must enforce explicit **incident-replay harness boundaries** across three progressive evaluation tiers instead of trusting any single sandbox.

<figure class="note-figure">
  <a class="note-image-link" href="/assets/images/tech/ai-sre-evaluation/poc-to-prod-eval-gates-en.svg" target="_blank" rel="noopener">
    <img src="/assets/images/tech/ai-sre-evaluation/poc-to-prod-eval-gates-en.svg" alt="PoC-to-production AI SRE evaluation gates diagram: top row compares Reactive, Proactive, and Preventative trigger modes and shared context readiness; middle layer splits Deterministic Gates covering citation checks, read-only agent ID, blast caps, dry runs, and PII scrubbing from the Semantic Judge using SREGym's 9-question 7/9 rubric; bottom row maps Tier 1 Single-Fault PoC, Tier 2 Noisy Replay and SREGym, and Tier 3 Read-Only Shadow Pilot with explicit failure-detection strengths and boundary limits." width="960" height="540" loading="lazy">
    <span class="note-image-action">Expand diagram ↗</span>
  </a>
  <figcaption>Assistant diagram (not an original figure): Connecting One2N's trigger and guardrail matrix, dual verification layers, and three-tier replay boundaries.</figcaption>
</figure>

| One2N Revised Criterion | PoC / Coding-Harness Failure Mode Exposed | Production Acceptance Gate & Evidence Artifact | Incident-Replay & Harness Boundary |
| :--- | :--- | :--- | :--- |
| **Trigger Timing & Read Coverage** | Reactive manual copy-paste wastes pre-triage time; missing IaC, CI/CD, or feature flags forces blind guesses | Measure alert-to-first-query readiness; verify read access across change feeds and editable/deletable agent memory | Static historical replay fixes the timeline in advance, so it cannot verify preventative pre-alert interception value |
| **3×3 Diagnosis & Citation Grounding** | `-1` collapsed localization, narrative, and proof errors; quiet single-fault PoCs hid ambient-noise sensitivity | Deterministic verification of every cited metric/log/change ID paired with multi-axis scoring preventing `0/3` axis collapse | Noisy fault injection and frozen replay test diagnostic resilience, yet omit live organizational terminology drift |
| **Auditability & Multi-Responder Handoff** | Personal laptop credentials polluted audit trails; terminal steering stayed hidden from second responders | Require distinct agent identity, full alert-to-verdict trace storage, shared ruled-out hypothesis UI, and traceable summaries | Automated single-run replay cannot score human steering ergonomics or mid-incident shift handoffs without live shadow drills |
| **Blast-Radius & Execution Guardrails** | Untrusted bash scripts under outage pressure; unbounded retries or missing per-service approval gates | Enforce read-only default, short-lived creds, risk scores, PII scrubbing, dry runs, rollback plans, and 1-deployment/1-AZ caps | Read-only shadow traffic validates citations and redaction, whereas action caps and loop breakers need destructive sandbox drills |

*Scope reminder: One2N states explicitly that performance and cost measurements applying this expanded matrix are deferred to upcoming posts; this framework should be used as a structured production-readiness acceptance checklist rather than treated as published benchmark results.*

---

> **Provenance**: Rewritten and expanded by the assistant from One2N's frozen primary article (*What changed in how we evaluate AI SRE agents*, Biswa Prakash Mishra, 2026-11-02; `authoring_source: assistant`, `translation_source: assistant`), retaining original `id`, `date`, `permalink`, `published_at`, and topic tags (`observability`, `agent-reliability`, `systems-reliability`). Both `v3-blue` diagrams (`sre-eval-three-axes-en.svg`, `poc-to-prod-eval-gates-en.svg`) are assistant-authored syntheses grounded strictly in the primary post and its cited references, introducing zero unverified benchmark claims.
