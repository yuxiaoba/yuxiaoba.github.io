---
id: pagerduty-ai-incident-triage
title: 2026-08-04 | First-Pass Triage for AI Incidents
date: '2026-08-04'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://www.pagerduty.com/eng/pagerduty-for-ai-how-the-sre-agent-triages-ai-incidents/
long_read: true
tags:
- agent-reliability
summary: First-Pass Triage for AI Incidents
translation_source: assistant-authored paired Chinese and English
permalink: /tech/en/pagerduty-ai-incident-triage/
published_at: '2026-10-28T15:48:27.004821+08:00'
updated_at: '2026-10-28T15:48:27.004821+08:00'
---
[PagerDuty for AI: How the SRE Agent Triages AI Incidents](https://www.pagerduty.com/eng/pagerduty-for-ai-how-the-sre-agent-triages-ai-incidents/) · PagerDuty · 2026-07-21

PagerDuty Engineering describes triage after an AI incident fires, not a demonstrated fully automated repair. A relevance drop can stem from prompts, retrieval, or the model, but an upstream service failure can also affect output; LLM-judge alerts themselves can be noisy.

The example concerns degraded tool selection in the internal Insights Agent. Through connectors, the SRE Agent reads Arize monitor state and relevant traces, looks for patterns in evaluation explanations, and checks GitHub code changes. The team encodes existing runbooks as skills to guide investigation. In this case the agent identifies a minor degradation and recommends closing the incident with follow-up improvements. A code-suggestion skill then constrains proposed system-prompt changes, which still need replay against failed traces and regression testing.

The useful operational idea is to combine AI-quality signals with conventional service context instead of treating every low score as an emergency. The article reports a practical example without a controlled study or quantified incident-response improvement. Automatic rechecking of noisy scores, routing by failure type, and further automation are presented as future directions, not validated capabilities.
