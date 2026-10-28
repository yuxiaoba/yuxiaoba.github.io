---
date: '2026-10-28'
published: true
layout: article
maintenance: daily-research
authoring_source: assistant
translation_source: assistant
id: flashduty-rum-ai-sre
title: '2026-10-28 | Flashduty RUM: connect AI query edits with user undo'
lang: en
source_type: tech
long_read: true
source_url: https://docs.flashduty.com/en/changelog/changelog
tags:
- observability
- agent-reliability
summary: AI SRE can edit and run RUM queries, with distinct semantics for stopping,
  hiding, and undoing.
permalink: /tech/en/flashduty-rum-ai-sre/
published_at: '2026-10-28T15:24:19.938525+08:00'
updated_at: '2026-10-28T15:24:19.938525+08:00'
---
Flashduty’s October 25 update gives natural-language observability queries concrete interaction semantics. Authorized AI SRE users can let the agent fill conditions, event type, time range, and analytics charts, then execute the query. A status bar reports progress and outcomes. Undo remains available only while the query box still contains the AI-written value, protecting later user edits.

Original: [Query and analyze in the RUM Explorer with AI SRE, a custom dashboard belongs to one application, errors split into Issues by where they were raised](https://docs.flashduty.com/en/changelog/changelog#rum-explorer-query-and-analyze-with-ai-sre) · Flashduty · 2026-10-25.

Stop ends the turn; Escape or clicking the status bar merely hides the conversation. Without AI SRE or remaining credits, the entry retains basic natural-language-to-DQL conversion with preview before application. Those distinctions are useful control mechanisms beyond adding a chat box.

The release also binds dashboards to applications and groups Issues by error location. These change query scope and error grouping, not measured RCA accuracy. With no query-correctness or diagnostic benchmark, this is a focused engineering update on reversible agent interaction.
