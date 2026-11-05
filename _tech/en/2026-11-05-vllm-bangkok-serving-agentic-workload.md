---
id: 2026-11-05-vllm-bangkok-serving-agentic-workload
title: '2026-11-05 | Technical reading: Serving the agentic workload: Simon Mo on
  what AI agents change in vLLM'
date: '2026-11-05'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://vllmbangkok.com/en/blog/serving-the-agentic-workload/
source_published_at: '2026-11-04'
tags:
- systems-reliability
authoring_source: assistant
translation_source: assistant
permalink: /tech/en/2026-11-05-vllm-bangkok-serving-agentic-workload/
---

[Serving the agentic workload: Simon Mo on what AI agents change in vLLM](https://vllmbangkok.com/en/blog/serving-the-agentic-workload/) · 2026-11-04

This summary of Simon Mo’s Runtime 2026 talk explains why repeated long prefixes, short outputs and bursty sub-agents make cache placement and routing central to agent serving. It discusses hybrid KV caches, prefill/decode separation and a distributed cache pool. The page explicitly separates talk material, benchmark traces and the summarizer’s additions. Theoretical prefix reuse is not a measured hit rate, and ratios of median input/output lengths are not per-request averages. Performance claims require the linked talk and benchmark configuration.

[Related source](https://x.com/agicafet/status/2117996070735433873)
