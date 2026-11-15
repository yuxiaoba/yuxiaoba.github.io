---
id: lmcache-claude-code-reuse-pattern
title: 2026-11-13 | What a Claude Code trace reveals about prefix reuse
date: '2026-11-13'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- inference-serving
summary: A Django repair trace shows role-local context growth and reuse; structural
  overlap is not the same as a measured serving-cache hit.
long_read: true
source_url: https://blog.lmcache.ai/en/2025/12/23/context-engineering-reuse-pattern-under-the-hood-of-claude-code/
permalink: /tech/en/lmcache-claude-code-reuse-pattern/
translation_source: assistant
authorship: assistant
source_published_at: '2025-12-23'
published_at: '2026-11-13T08:46:43.062448+08:00'
updated_at: '2026-11-13T08:46:43.062448+08:00'
---
Kobe, Mengbing · 2025-12-23  
Original: [Context Engineering & Reuse Pattern Under the Hood of Claude Code](https://blog.lmcache.ai/en/2025/12/23/context-engineering-reuse-pattern-under-the-hood-of-claude-code/)

A small code repair can accumulate substantial input traffic. Kobe and Mengbing's December 2025 Django JSONField case reports 92 LLM calls, roughly two million input tokens, thirteen minutes and 92% prefix reuse.

## Several role-local histories

Three Explore agents investigate separate components; their summaries feed Plan before the main agent executes. Each role grows its own history. The authors interpret early prompt-only calls as cache warm-up, but observations do not establish internal intent or measured latency savings.

<a class="note-image-link" href="/assets/images/tech/lmcache-claude-code-reuse-pattern/figure.png" target="_blank" rel="noopener" aria-label="Claude Code exploration, planning and execution roles · View original image ↗"><img src="/assets/images/tech/lmcache-claude-code-reuse-pattern/figure.png" alt="Claude Code exploration, planning and execution roles" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Exploration summaries feed planning and execution; each role grows its own tool-loop history.*

## Overlap is not a serving-cache hit

Reported shared-prefix fractions are 92.06% of 546,104 Explore tokens, 93.23% of 528,286 Plan tokens and 97.83% of 827,411 later main-agent tokens. Repeated histories inflate cumulative input. These measure reuse opportunities, not request-hit rates or computation eliminated; actual reuse depends on residency, routing and valid prefixes.

## A case, not a population estimate

This is one task and run. The reported 92-call total also sits alongside a later mention of auxiliary call #93, leaving scope ambiguous. Pricing arithmetic is illustrative, not a bill. Repeated files behind different prefixes do not automatically share causal-attention KV. The useful AgentOps lesson is to distinguish role-local growth, summaries and repeated content before estimating cache benefits.
