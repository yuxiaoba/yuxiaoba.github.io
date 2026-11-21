---
id: groundcover-investigations-2026-11-15
title: 2026-11-21 | Keeping refuted hypotheses in the incident record
date: '2026-11-21'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- observability
- multi-agent
summary: In groundcover’s first internal prototype, a coding agent delegated work
  on a real incident.
translation_source: assistant
writing_source: assistant
long_read: true
source_url: https://www.groundcover.com/blog/introducing-groundcover-investigations
permalink: /tech/en/groundcover-investigations-2026-11-15/
published_at: '2026-11-21T08:47:17.687323+08:00'
updated_at: '2026-11-21T08:47:17.687323+08:00'
---
In groundcover’s first internal prototype, a coding agent delegated work on a real incident. It produced an answer, but much of the investigation remained inside separate agent sessions. A responder joining later could hardly distinguish “database checked and ruled out” from “database mentioned and never checked.” Investigations makes hypotheses and their evidence the shared objects of work.

Anais Dotis · 2026-11-15 · [Introducing groundcover Investigations – collaboration ground for your agents and engineers](https://www.groundcover.com/blog/introducing-groundcover-investigations)

## Attach findings to a hypothesis

One question can branch into several hypotheses. An investigator queries telemetry, publishes findings to the relevant branch and can split substantial work into a sub-investigation. The queries and results underlying support or refutation remain available. A handoff preserves both eliminated explanations and genuinely open work. Before repeating a query, a second investigator can check whether the available evidence covers the right time window.

## Separate proposed resolution from approval

The Investigator proposes hypotheses and assessments. The Moderator checks whether findings support a proposed conclusion and alone can mark the issue resolved. External coding agents contribute over MCP under the same rule, with attribution to the contributing session and time. This creates an auditable handoff. A model still judges the evidence, and a cited query may use the wrong comparison period or service instance.

## Slack carries progress and the tree carries detail

Sending every finding to the incident thread buried the decisions responders needed. Slack now carries new hypotheses, changes of status and short assessments. Exact queries, visualizations and branches remain in the investigation view, while engineers can add context through the thread. The original article describes manual starts from a monitor issue or Slack and presents automatic starts from selected alerts as future work. Its evidence covers prototype experience, roles and records. It provides no controlled estimate of resolution accuracy or MTTR.
