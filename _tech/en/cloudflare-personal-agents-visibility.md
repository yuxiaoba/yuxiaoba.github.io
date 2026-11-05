---
id: cloudflare-personal-agents-visibility
title: '2026-11-05 | Personal-agent traffic: identity is not user authorization'
date: '2026-11-05'
lang: en
published: false
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- observability
summary: Cloudflare adds personal-agent analytics and access policies while leaving
  broader user context as future work.
long_read: true
source_url: https://blog.cloudflare.com/personal-agents-visibility-control/
permalink: /tech/en/cloudflare-personal-agents-visibility/
translation_source: assistant
authoring_source: assistant
published_at: '2026-11-05T08:55:14.344660+08:00'
updated_at: '2026-11-05T08:55:14.344660+08:00'
---

Original: [See the agents, set the terms: new visibility and control for personal agents](https://blog.cloudflare.com/personal-agents-visibility-control/)<br>
Marina Elmore, Nicole Justus · Cloudflare · 2026-11-04

Cloudflare adds Personal Assistants to Security Analytics’ Bot Analysis categories, with agent-specific request volumes, paths, status codes, and network details. This turns generic automated traffic into observable agent behavior, including where agents encounter access failures.

Sites using the early-access Account Abuse Protection feature can associate agent activity with login, signup, and account views. The article describes mitigating an abused account through a Hashed User ID WAF rule rather than blocking every user of the agent. Supported personal agents can also receive individual allow, block-on-ad-pages, or block policies.

Agent identification does not establish what a user authorized, whether they subscribe, or which entitlements apply. The post explicitly leaves broader user context, reputation, and accountability for future work. This is an observability and policy-interface update, not a complete delegation protocol or measured identity-classification breakthrough. The noteworthy change is treating personal agents as distinct observable traffic while retaining the need to reason about accounts and user intent.
