---
id: phala-inference-exposure
title: 2026-11-23 | Why Phala’s exposure notice covers more than two days of canary
  evidence
date: '2026-11-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: An incompletely hardened GPU server served production traffic. Phala distinguishes
  when requests were sent, when credentials were misused and when containment finished.
long_read: true
source_url: https://phala.com/posts/phala-november-preliminary-incident-report
permalink: /tech/en/phala-inference-exposure/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
Phala’s November 10 preliminary report identifies one route for customers to check: DeepSeek V4 Flash 0731 requests that OpenRouter sent to Phala. Its precautionary window runs from October 21 at 00:00 UTC to November 8 at 05:35 UTC. Confirmed canary evidence points to requests sent on just two of those days. Reconciling those facts requires distinguishing the date of a request from the date someone later used its contents.

## Production traffic arrived before hardening was complete

Phala says a new GPU server was already handling production inference without the full production security configuration. Compromise of its inference VM made request contents visible during processing. Retention limits address a different exposure from access to live data. Confidential virtual machines were also affected, with subsequent misuse confirmed for some application credentials belonging to one tenant. Overlapping activity and infrastructure led Phala to provisionally treat the intrusions as one incident.

## Why the November 6 key rotation did not close the investigation

The team detected unauthorized activity and stopped unauthorized VMs on November 5. It rotated the key-management root key the next day. Researcher evidence received at 04:12 UTC on November 8 led the investigation to the affected inference deployment. Phala took the server and deployment offline and completed containment at 05:35. The two interventions addressed different assets. Rotating a platform root key also cannot recall third-party secrets already disclosed in a request.

## How two positive dates inform a longer warning

A researcher regularly sampled requests from July 1 through November 7. Subsequent misuse was observed only for canary credentials submitted on October 21 and 22. This detector depends on someone using a marker. It misses passive reading and cannot account for unsampled requests, so Phala retained the wider window. Its timeline records misuse of previously obtained data on November 9, compatible with its report that no new successful unauthorized access had been observed after containment. The full root cause analysis and verification of remediation were still underway.

Phala · 2026-11-10 · [Phala November Preliminary Incident Report](https://phala.com/posts/phala-november-preliminary-incident-report)
