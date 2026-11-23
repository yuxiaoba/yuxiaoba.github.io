---
id: novita-forwarding-scope
title: 2026-11-23 | How a customer-specific forwarding rule affected other Novita
  requests
date: '2026-11-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Novita confirmed that a routing exception applied too broadly. Test markers
  revealed access while leaving upstream purpose and retention unresolved.
long_read: true
source_url: https://novita.ai/blog/minimax-requests-privacy-notice/
permalink: /tech/en/novita-forwarding-scope/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
A request that a customer expected Novita to host could instead reach the official MiniMax API. Novita confirmed this discrepancy for some requests. The consequential decision was which customers fell within the scope of a forwarding rule, because that decision changed who could see the prompt.

## A routing exception crossed its intended boundary

Novita attributes the forwarding to a configuration intended for specific customers that applied more broadly. Some requests consequently left Novita-hosted inference infrastructure. The notice covers potential exposure for MiniMax traffic through Novita from May 28 to November 11, 2026, including both direct customers and those using OpenRouter. The interval and entry point help identify requests for review. Novita did not disclose the fraction actually forwarded.

## Link access and credential use answer different questions

The researcher observed access to URLs and hostnames embedded in test requests and observed no use of the AWS test key markers. The positive signal shows that information from the prompt triggered external activity. The second observation narrows the kinds of activity seen. Novita inferred that automated content review might have been involved and was seeking confirmation from MiniMax. The observations alone cannot establish purpose, retention time or whether a person read an entire prompt.

## Questions left after suspending the endpoints

Novita says it suspended the affected models and was verifying their processing paths. It was following up with MiniMax on any retained customer data and its deletion. Novita says it does not retain customer prompts or outputs or use them for training. Forwarding introduces a separate question about the upstream processor’s practices. The company also describes changes to Partner API labeling and disclosure of provider retention policies and terms, so that customers can see that distinction when selecting an endpoint.

Novita AI · 2026-11-22 · [Privacy Notice Regarding MiniMax Requests on Novita](https://novita.ai/blog/minimax-requests-privacy-notice/)
