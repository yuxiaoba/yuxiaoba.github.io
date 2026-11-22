---
id: microsoft-365-pir-2026-11-12-gateway-outage
title: 2026-11-22 | How routing around failed Microsoft 365 gateways spread the outage
date: '2026-11-22'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
- observability
summary: Microsoft’s final PIR traces lock contention on higher-core servers through
  maintenance, failover, global traffic redistribution and recovery in groups of capacity
  units.
translation_source: assistant
permalink: /tech/en/microsoft-365-pir-2026-11-12-gateway-outage/
long_read: true
source_url: https://tianyin.github.io/misc/pir_microsoft_365_11-12-2026.pdf
published_at: '2026-11-22T12:07:03.681801+08:00'
updated_at: '2026-11-22T12:07:03.681801+08:00'
---
On November 12, Microsoft 365 traffic management moved requests from unresponsive gateways to healthy ones. Ordinarily that lets users bypass a failed machine. On this occasion the receiving machines ran the same defective software. Within about two hours of broad failures in North America, servers in every region were affected. The November 20 final report connects the preliminary account of the same incident to a sequence of load, routing and recovery decisions.

Microsoft · EX1550543 / MO1550821 · 2026-11-20 · [Post Incident Report for Microsoft 365](https://tianyin.github.io/misc/pir_microsoft_365_11-12-2026.pdf)

## A July change meets its trigger in November

The Exchange Online gateway used a specific Windows configuration. A connection-handling change began staged deployment in July and had been live worldwide for more than three months. On newer hardware, more cores let more concurrent requests enter the processing path, increasing contention on an internal lock. Under the triggering load, requests accumulated, exhausting CPU and memory until machines stopped responding. Older, lower-core lab hardware made contention less likely, and test traffic missed the production combination. Microsoft scoped the defect to the gateway configuration and ruled out a cyberattack and AI tooling as causes.

Nearly 14% of gateway capacity was offline for routine maintenance. At 01:07 UTC on November 12, a US East routing issue moved Teams traffic to the redundant gateway that also served Exchange. Services remained broadly healthy for hours. Widespread failures developed near 16:00 as North American traffic approached its daily peak. Maintenance, failover and peak demand together would ordinarily fit within operating headroom. The defect changed the cost of extra concurrency, explaining both the delay after failover and the difficulty of diagnosing the incident from recent changes.

## A healthy destination can become the next failure

The gateway has thousands of capacity units, each containing servers and networking infrastructure. As servers stopped responding, the traffic manager sent requests to healthy units in the same region. Demand did not fall with capacity. Receiving units faced more concurrent work and became more likely to trigger the same contention. At the low point more than 80% of servers in North America were unresponsive. Once a region ran short of healthy capacity, redistribution crossed regional boundaries, exposing the same regression elsewhere.

Dependencies explain why users saw different recovery times. Teams, OneDrive and SharePoint could move some traffic off the affected gateway, restoring parts of those services earlier. Features that needed Exchange mailbox, calendar or people data remained impaired. An assistant could receive a request yet still fail to fetch the mailbox data it needed. Service availability depended on the operation the user was attempting.

## Why a restarted server did not immediately add capacity

Queued clients were waiting to reconnect. A server returned directly to rotation could be overwhelmed again. Once engineers identified the fix, each server had to leave rotation, restart out of its unresponsive state, receive the patch, restart again to activate it and then rejoin. The team removed groups of capacity units from rotation, repaired their machines concurrently and returned the groups to service before expanding the approach across regions. Looking back months to find the change, performing two restarts per server and reaching the whole fleet each contributed to recovery time.

Global Outlook on the web availability returned to expected levels at 14:17 UTC on November 13. Extended monitoring and mail-backlog recovery began at 16:10, and Microsoft declared resolution at 04:15 on November 14. It extended mail retries from 24 to 48 hours and delivered all queued enterprise messages. The report records a specific exception for consumer mail: some delayed messages to mailboxes inactive for more than 30 days expired, and senders received non-delivery reports.

## Which controls were in place by the report date?

Microsoft had incorporated the fix into its Windows image, added monitoring for redirection and connection health, and installed temporary guardrails on automatic redistribution. Follow-up work included separating workload pools, limiting Teams failover to the affected region and testing peak traffic on higher-core hardware with a production-like mix. Recovery plans also called for gradual readmission, admission control and improved backoff, some with dates still to be determined. The patch addressed the lock contention. The isolation and recovery changes address how much demand reaches newly recovered machines when many peers slow down together.
