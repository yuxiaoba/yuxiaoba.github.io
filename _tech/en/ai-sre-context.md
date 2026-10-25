---
id: ai-sre-context
title: '2026-10-25 | An AI SRE Baseline: Better Context for the Agent You Have'
date: '2026-10-25'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- observability
- coding-agents
- systems-reliability
summary: A 50-fault comparison shows the value of prepared context, with permission
  differences and single-run limits on causal interpretation.
translation_source: assistant
authorship: assistant
long_read: true
source_url: https://www.cncf.io/blog/2026/10/21/before-you-evaluate-an-ai-sre-give-your-existing-agent-context/
permalink: /tech/en/ai-sre-context/
published_at: '2026-10-25T08:48:16.922011+08:00'
updated_at: '2026-10-25T08:48:16.922011+08:00'
---
AI SRE diagnosis can be constrained by what the agent can see. This CNCF experiment gives the same coding agent either raw cluster commands or organized read-only context. Final correctness differs by one fault, but the fraction diagnosed correctly within a deadline changes substantially. It provides a useful baseline for evaluating how much evidence preparation contributes before changing the reasoning system.

Original: [Before you evaluate an AI SRE, give your existing agent context](https://www.cncf.io/blog/2026/10/21/before-you-evaluate-an-ai-sre-give-your-existing-agent-context/)  
Roy Libman, CPO, Radar (Skyhook.io) · CNCF · 2026-10-21

## Data in the cluster is not yet diagnostic context

Pod status, events, logs, and release history live behind different interfaces. A broken application can have every pod Ready and no obvious event. Investigation must reconstruct relationships and identify changes preceding the failure. An agent with kubectl still has to choose where to look, connect objects, and search history, adding tool calls and model turns.

Radar's read-only MCP tools organize four inputs: ranked current failures; configuration and Helm history retained beyond Kubernetes event expiry; resources joined to owners, topology, and related issues; and error-focused logs with secrets redacted. This shortens the path from raw objects to usable evidence. The model still decides what caused the fault, and the interface can still omit a critical object.

Architecturally, some repeated reasoning work moves into a maintained context layer. Multiple agents can reuse the same relationships and history, but collection, retention, and association must remain correct. A stale timeline or wrong relationship can accelerate an incorrect explanation. More context therefore needs to mean evidence that answers specific questions, rather than simply more text.

## What the 50-fault comparison measures

The authors ran 50 SREGym faults on a live three-node Amazon EKS cluster. Both arms used Claude Code with Claude Sonnet 5 through Amazon Bedrock. One used shell and kubectl; the other used Radar's read-only MCP tools with kubectl fallback blocked. Claude Opus 5 at temperature 0 graded the first submitted diagnosis. Each arm ran each fault once.

| Metric | Shell + kubectl | Read-only context |
| --- | --- | --- |
| Correct diagnoses | 45/50 | 46/50 |
| Correct within 2 minutes | 60% | 86% |
| Correct within 5 minutes | 78% | 90% |
| Mean submission time, including wrong answers | 191 s | 64 s |
| P90 submission time | 632 s | 94 s |
| Mean tool calls | 16.3 | 9.8 |

The deadline result matters more than 45 versus 46. Both arms correctly diagnosed the same 44 faults, and context did not generally eliminate judgment errors. Evidence discovery improved more clearly. For the 14 faults where all pods were Ready despite a broken application, mean submission time fell from 326 to 79 seconds.

In one Astronomy Shop case, the frontend Deployment had lost its CART_ADDR environment variable. The shell arm used 58 calls and 701.6 seconds; the context arm used seven calls and 34.8 seconds. Both found the cause, but the latter could directly query recent changes. Similar final correctness can therefore conceal a substantial difference in incident-response value.

## Permissions are another experimental variable

This was not a strictly isolated change to information content. The shell arm could write; the MCP arm was read-only. The authors acknowledge that the experiment cannot separate the contribution of individual context categories, much less prove a universal advantage for one MCP product. Their team maintains Radar, which is relevant when interpreting the comparison.

Permissions also changed behavior. The shell arm launched pods on 13 faults and used exec, cp, port-forward, or debug on 21. It brought Secret data into context on four faults and decoded it on three. In one case it deleted application database collections to test a theory, then submitted a wrong diagnosis. These actions occurred in a benchmark that permitted modification and described a subsequent repair stage; they should not be presented as disregard for a read-only constraint.

The engineering implication is to evaluate diagnosis and remediation identities separately. A role described as read-only may still expose credentials if it can read Secrets; container execution may enable more than observation. Hold identities, allowed actions, and audit records constant, or faster diagnosis may partly reflect greater authority.

## Product value and evidence boundaries

The article separates an AI SRE into triggering, context, reasoning, delivery, and governance. An existing coding agent supplies part of the reasoning loop but may not start on an alert, deliver findings to the incident channel, or govern remediation. Better context establishes a stronger diagnosis baseline; the surrounding capabilities still matter in product comparisons.

SREGym injects faults shortly after application deployment, favoring recent-change tracking. Real incidents may involve long-term drift, cross-system dependencies, or incomplete records. One run per fault cannot establish a stable accuracy advantage from a one-fault difference. The outcome is diagnosis, not repair success or recovery time.

The most informative reading follows the public per-fault replays: which evidence arrived first, and which exploratory calls disappeared? A subsequent evaluation can repeat faults with the same model, read-only identity, and deadline, then add incidents from the target environment. The advance worth following is the treatment of current failures and change history as first-class diagnostic inputs. The path by which evidence reaches a model is itself an optimization target.

## What the tool sequences reveal

Every shell run began with pod and event queries; on 24 faults it then searched ReplicaSets, rollout records, or Helm for history. Every context run started with current issues, and 35 queried the change timeline second. The interface changed the starting point: inventory before hypothesis versus existing anomaly candidates followed by temporal checks.

That can also create anchoring. Among three faults both arms missed, one involved selecting a real but unrelated misconfiguration instead of the DNS cause. An engineering implication is that ranked issues should preserve access to raw objects and counterevidence. Context must support testing relevance, not merely presenting a likely answer.

Fewer tool calls often imply fewer model turns, but the article does not provide complete per-fault token-cost comparisons. A definite cost-reduction percentage is therefore unsupported. Submission time and deadline correctness remain the strongest evidence; broader efficiency accounting should include tokens, context preparation, and retained history.

For shared failures, inspect whether the decisive object entered context. If visible evidence was misinterpreted, reasoning or verification may need improvement. If it was absent, changing the model may not repair the interface gap.
