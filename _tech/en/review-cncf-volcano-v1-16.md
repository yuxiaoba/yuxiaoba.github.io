---
id: review-cncf-volcano-v1-16
title: '2026-10-29 | Volcano v1.16 Released: NamespaceQueue, fairshare, and a broader
  HyperNode ecosystem'
date: '2026-10-29'
lang: en
published: false
layout: article
maintenance: daily-research
source_type: tech
source_url: https://www.cncf.io/blog/2026/10/28/volcano-v1-16-released-namespacequeue-fairshare-and-a-broader-hypernode-ecosystem/
tags:
- agent-reliability
- coding-agents
- observability
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-cncf-volcano-v1-16/
---


Volcano 1.16 introduces NamespaceQueue, usage-based fairshare and HyperNode anti-affinity. Its unschedulable-job cache waits for relevant events before retrying rejected work, reducing backlog checks while retaining watchdog retries.

The cache is off by default and requires safe event hints from rejecting plugins. Release documentation is not a local performance or resilience validation.

[Volcano v1.16 Released: NamespaceQueue, fairshare, and a broader HyperNode ecosystem](https://www.cncf.io/blog/2026/10/28/volcano-v1-16-released-namespacequeue-fairshare-and-a-broader-hypernode-ecosystem/)
