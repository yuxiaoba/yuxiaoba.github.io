---
id: review-skyhook-radar-k8s-ai-sre-mcp
title: '2026-10-31 | Radar: open-source Kubernetes UI with built-in MCP server for
  AI agents'
date: '2026-10-31'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://github.com/skyhook-io/radar
tags:
- agent-reliability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-skyhook-radar-k8s-ai-sre-mcp/
---

Radar exposes shared cluster relationships, events and health to its UI and MCP with a read-only endpoint. In its author-run same-agent 50-fault comparison, mean diagnosis time is 64 seconds versus 191 with raw kubectl.

Product authors run the study with an LLM judge. Faults, dates and load differ between studies; cross-table rankings and real-repair claims are unwarranted.

[Radar: open-source Kubernetes UI with built-in MCP server for AI agents](https://github.com/skyhook-io/radar)
