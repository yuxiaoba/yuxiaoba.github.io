---
id: openrouter-zdr-review
title: 2026-11-23 | Why OpenRouter removed 125 endpoints from zero-retention routing
date: '2026-11-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Provider removal and endpoint eligibility answer different questions. Restoring
  a zero-retention route also requires checking who handles the payload.
long_read: true
source_url: https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/
permalink: /tech/en/openrouter-zdr-review/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
A customer who selects zero data retention (ZDR) delegates a routing decision to the gateway. Of the endpoints offering a particular model, which ones still qualify? OpenRouter describes how it narrowed that pool while the investigation was underway.

## Two actions with different units

Researchers found evidence of compromised data or discrepancies between stated policy and actual handling at some inference providers. OpenRouter removed three providers after investigation. It also withdrew ZDR eligibility from 125 endpoints. That second count includes both endpoints flagged by researchers and precautionary removals. It measures the change to the eligible routing pool. Neither the number of leaks nor the number of customers can be inferred from it.

## Following a request beyond the first provider

A provider accepting a request can forward it again, and the response also passes through intermediaries. OpenRouter says the findings showed no unauthorized access to its own platform. Enforcing a retention setting requires additional evidence about who handles the payload after it leaves the gateway. OpenRouter is checking network paths for third-party forwarding of requests and responses and adapting the researchers’ tests for recurring use.

## The evidence needed to reopen a route

Withdrawing eligibility immediately narrows the available routes. OpenRouter says reinstatement requires assurances and validation. Its announcement gives no testing frequency, coverage estimate or endpoint-level reinstatement results. The platform says it notified all potentially affected customers, including those whose providers had yet to publish an account. The four linked provider statements document individual events and do not identify the three providers removed by OpenRouter.

OpenRouter · 2026-11-22 · [Data Processing Incidents on Inference Providers](https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/)
