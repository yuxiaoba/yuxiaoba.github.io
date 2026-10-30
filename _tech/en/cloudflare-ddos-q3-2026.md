---
id: cloudflare-ddos-q3-2026
title: 2026-10-30 | Short, frequent attacks rise in Cloudflare’s DDoS observations
date: '2026-10-30'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
summary: 'Cloudflare''s third-quarter data highlights a reliability risk beyond extreme
  peaks: many short attacks can end before a human responds and can repeatedly affect
  a service.'
long_read: true
source_url: https://blog.cloudflare.com/ddos-threat-report-2026-q3/
permalink: /tech/en/cloudflare-ddos-q3-2026/
translation_source: assistant-authored paired Chinese/English reading notes
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-10-30T10:31:20.339125+08:00'
---
Cloudflare's third-quarter data highlights a reliability risk beyond extreme peaks: many short attacks can end before a human responds and can repeatedly affect a service.

**Source:** Cloudforce One, [Cloudflare DDoS Threat Report 2026 Q3: More swarms, fewer giants](https://blog.cloudflare.com/ddos-threat-report-2026-q3/), October 29, 2026.

Cloudflare reports mitigating 18.2 million network-layer DDoS attacks in Q3 2026, averaging approximately 8,226 per hour. Of these, 96% lasted under 10 minutes and 98% stayed below 1 Gbps. Attacks exceeding 1 Tbps fell from 805 in Q2 to 251; the report notes concurrent law-enforcement action, which does not establish causation.

Attack vectors also shifted: CLDAP reflection fell to 0.05% of attacks, DNS amplification rose 215% quarter over quarter, and other UDP floods grew from 14.06% to 31.31%. Reflection uses spoofed source addresses to direct amplified replies at victims; raw UDP floods consume network and compute resources with large packet volumes.

These figures reflect Cloudflare's own network and detection definitions, not an unbiased sample of the entire Internet. Reliability teams should observe frequency, duration and protocol mix alongside peak bandwidth.
