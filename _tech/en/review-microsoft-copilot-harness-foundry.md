---
id: review-microsoft-copilot-harness-foundry
title: 2026-10-29 | Introducing the Microsoft Copilot harness in Foundry Agent Service
date: '2026-10-29'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://devblogs.microsoft.com/foundry/microsoft-copilot-harness-in-foundry/
tags:
- agent-reliability
- coding-agents
- observability
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-microsoft-copilot-harness-foundry/
---

Foundry distinguishes its preview managed Copilot harness from hosted-agent long-running recovery. The platform restarts interrupted work with original input; applications persist checkpoints and prevent duplicate external actions. Conversation history alone cannot restore work in progress.

This documents capabilities and responsibility boundaries without recovery-latency or reliability benchmarks. Restart does not guarantee exactly-once external actions.

[Introducing the Microsoft Copilot harness in Foundry Agent Service](https://devblogs.microsoft.com/foundry/microsoft-copilot-harness-in-foundry/)
