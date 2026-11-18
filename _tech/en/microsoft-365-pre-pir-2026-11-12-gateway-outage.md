---
id: microsoft-365-pre-pir-2026-11-12-gateway-outage
title: 2026-11-17 | Why rerouting accelerated the Microsoft 365 gateway outage
date: '2026-11-17'
lang: en
published: true
layout: article
maintenance: daily-research
translation_source: assistant
summary: Microsoft’s preliminary report on almost a day of Exchange Online disruption
  describes an unusual recovery signal.
tags:
- systems-reliability
- observability
source_type: tech
source_url: https://tianyin.github.io/misc/prepir_microsoft_365_11-12-2026.pdf
long_read: true
permalink: /tech/en/microsoft-365-pre-pir-2026-11-12-gateway-outage/
published_at: '2026-11-18T12:32:52.327837+08:00'
updated_at: '2026-11-18T12:32:52.327837+08:00'
---
Microsoft’s preliminary report on almost a day of Exchange Online disruption describes an unusual recovery signal. A gateway could pass a health check and then stop responding soon after receiving redirected traffic. Knowing which endpoints were alive answered only half of the routing question. The other half was how much traffic they could survive.

## Why a three-month-old change surfaced that day

A gateway-specific Windows fix began rolling out in July. It reached the global fleet over several weeks and ran worldwide for more than three months without observed impact. Under a particular load mix, contention inside a Windows process could exhaust CPU and memory. Newer machines with more cores experienced worse contention, whereas lab load tests favored smaller machines and a different traffic mix. Both a successful phased rollout and a successful lab test were consistent with a latent common failure mode.

At 01:07 UTC on November 12, Teams moved from an alternative gateway onto the primary gateway shared with Exchange Online. This routine failover changed both volume and traffic composition. At the same time, nearly 14% of capacity was offline following an unrelated issue the previous day. The report says available headroom could absorb that reduction on its own. During the US peak, the combined conditions exposed the old defect and queues accumulated across more servers.

## Health detection worked while isolation failed

At 16:03, connectivity monitoring detected more user-facing errors. At 16:17, automation began redirecting traffic to healthy endpoints. A high-priority Exchange Online alert at 16:20 marks the reported start of impact. By 19:20 engineers had determined that overall traffic growth did not explain the observed load. Fewer servers were carrying the same demand. Each destination was running the same vulnerable code path, so a successful reroute could set up the next failure.

The gateway normally partitions infrastructure into thousands of capacity units grouped into regions. A separate issue let the cascade cross these boundaries. The preliminary report gives no mechanism for that isolation failure. Within two hours the defect had spread across the fleet. At the worst point more than 80% of gateway servers were unresponsive, a server count rather than a user failure rate. Teams, OneDrive and SharePoint could shift some traffic away. Exchange Online could not do so at its scale. Many users lost mailbox access or saw delayed mail, while other services experienced more selective failures in Exchange-dependent features.

## Recovery had to change what happened when traffic returned

At 23:55 on November 12 the team observed that restarted servers initially appeared healthy, then stopped responding upon receiving traffic. Normal recovery assumed enough live capacity to absorb waiting requests. Here the backlog concentrated on the first machines to return, and restarting them left the faulty code path intact. At 01:53 the next day, engineers disabled some automatic redirection. Regional traffic measures produced partial improvements that did not hold. An ordinary rollback or feature flag could not quickly reverse a change deployed months earlier.

At 07:20 engineers applied an update to part of the fleet to restore the previously working code path. Stability on those machines at 08:00 justified expansion. Engineers removed groups of servers, patched and restarted them, then readmitted them to traffic. A group could cover more than half of a region’s infrastructure. The incident window ended at 16:10 UTC on November 13, after 23 hours and 50 minutes. The telling comparison in the timeline is between an early restart that failed under returning traffic and a patched group that stayed healthy under load.

Microsoft · 2026-11-15 · [Preliminary Post Incident Report for Microsoft 365](https://tianyin.github.io/misc/prepir_microsoft_365_11-12-2026.pdf)
