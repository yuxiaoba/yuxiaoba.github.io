---
id: gcp-london-failover
title: '2026-10-21 | London Cloud Outage: Failover Depends on Capacity and Control
  Paths'
date: '2026-10-21'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://status.cloud.google.com/incidents/Xs2XTHzAVC9YnafnPyzj
long_read: true
tags:
- systems-reliability
- observability
summary: 'Two constraints on failover in the Google Cloud London incident: surviving
  capacity and control paths that still wait for the failed zone.'
authoring_source: assistant
translation_source: assistant
permalink: /tech/en/gcp-london-failover/
published_at: '2026-10-24T08:39:06.506729+08:00'
updated_at: '2026-10-24T08:39:06.506729+08:00'
---
The useful question for a multi-zone architecture is whether the surviving system can complete the same business operation after one zone disappears. That requires available replicas, executable control paths, and sufficient capacity together. The London cloud outage provides a concrete starting point for separating deployment across zones into recovery conditions that can be examined individually.

**Google Cloud · Preliminary incident analysis and engineering interpretation**  
Primary source: [Multiple services were experiencing issues in the europe-west2 region.](https://status.cloud.google.com/incidents/Xs2XTHzAVC9YnafnPyzj) · Incident: 2026-10-20; this note incorporates the Preliminary Incident Report published on 2026-10-22. News lead: [Google Cloud's London zones takes a nap, multiple services disrupted](https://www.theregister.com/paas-and-iaas/2026/10/20/google-clouds-london-zones-takes-a-nap-multiple-services-disrupted/5304084), Paul Kunert, 2026-10-20.

## What the preliminary report establishes

Google attributes the europe-west2-b outage to power loss: primary and backup PLCs failed to start/transfer generators, and UPS depletion took equipment offline. Cross-zone control calls waited on the failed zone while displaced load strained surviving capacity. Reported impact lasted **6 hours 10 minutes**; over **99% of Compute Engine VMs** were healthy by October 20, 13:10 BST. Response included endpoint isolation, resource reallocation, and gradual traffic restoration. Investigation remains preliminary; final preventive actions are pending. [Preliminary incident report](https://status.cloud.google.com/incidents/Xs2XTHzAVC9YnafnPyzj)

The models below are engineering deductions about failover conditions. Their capacity numbers and examples do not describe Google's actual configuration.

## Why an available replica may not complete a request

Consider a hypothetical query service with workers across several zones that must consult a directory before accepting each new job. Workers and data replicas in a healthy zone can remain available while a synchronous directory lookup waits on the failed zone. The job never reaches execution. A diagram showing another replica does not identify where the request stops progressing.

For one business operation, trace three paths: dependencies of work already running, checks needed to admit new work, and operations needed to rebuild instances after failure. These paths may differ. Existing jobs continuing does not establish that new jobs can be submitted; readable data does not establish that a scheduler can reassign resources.

This distinction also changes monitoring. A worker-liveness probe may miss admission failure, while a successful API response may hide prolonged queueing. A useful probe completes a minimal business operation and records the stage where progress stops, distinguishing unreachable services, blocked control calls, and resource shortages.

## A capacity calculation for failover pressure

Assume three equal zones, each with sustainable processing capacity C, serving evenly distributed total load L. After losing one zone, the idealized condition without extra overhead is:

$$L < 2C$$

If normal per-zone utilization is u, then L = 3uC. Average utilization across the two survivors becomes:

$$u_{after} = \frac{3u}{2}$$

At 60% normal utilization, failover raises utilization to 90%. At 70%, the survivors would need 105% of their capacity, exceeding stable processing capacity in this model. This threshold assumes equal capacity and even redistribution; it is not a production configuration recommendation.

The calculation excludes recovery work. Replica catch-up, connection rebuilding, and retries may consume resources, while changing cache hit rates can alter the cost of each request. Capacity planning must therefore ask both whether the business load fits and whether the transition has room to proceed. Maintaining spare capacity costs money. A system should explicitly distinguish operations that require full service from those that can queue, be rate-limited, or temporarily offer reduced functionality.

## Recovery is also traffic scheduling

In a hypothetical recovery phase, let B be the job backlog, μ the number of jobs processed per second, and λ the arrival rate. When μ exceeds λ, ignoring differences among jobs, approximate drain time is:

$$T_{drain} \approx \frac{B}{\mu-\lambda}$$

If processing capacity is only slightly above new arrivals, the queue can take a long time to shrink even after connectivity returns. If μ does not exceed λ, the backlog will not drain by itself. Power restoration, resumed service responses, and normal user waiting times therefore deserve separate measurements.

Recovery control has trade-offs. Restoring all traffic immediately uses recovered capacity sooner but may trigger simultaneous cache warming and connection surges. Gradual admission makes anomalies easier to observe but prolongs waiting for some requests. A verifiable recovery policy needs staged acceptance conditions: for example, admit a small amount of work after health validation, then expand according to errors and backlog trends, rather than treating process startup as sufficient.

Apply the same question to retries: are they waiting for recovery, or adding requests to an already congested system? Evaluate backoff and limits through total recovery work and business completion time, beyond whether one call eventually succeeds.

State consistency is another easily missed recovery condition. In a hypothetical order service, a timeout means the caller did not receive a timely result; it does not establish that no order was created. A recovery script that resubmits every timed-out request without a stable business identifier can turn an availability failure into duplicate operations. Recovery work therefore needs to distinguish safely retryable tasks from those whose outcomes must be queried before deciding what to do next.

This also explains why recovery exercises need application-state observations alongside connectivity checks. After traffic to a failed zone is disabled, clients may retain old connections or cached locations, and background work may still reference old resources. The user path may not have fully switched. Recording entry-point switching separately from residual-dependency cleanup helps distinguish time spent rebuilding resources, confirming state, and rediscovering services on clients.

## Turning the reading into a useful exercise

A failure exercise can compare three scenarios: remove one zone's execution resources; retain execution resources but force critical control calls to time out; and remove resources while also introducing a backlog. These separately examine placement redundancy, dependency isolation, and surviving capacity, preventing one successful-failover metric from hiding different bottlenecks.

Each scenario needs a business success criterion. Do existing jobs retain progress? Are new jobs admitted within the target time? Do duplicate requests produce duplicate execution? Does a small subset remain stuck after recovery? These are evaluation dimensions proposed here, not assertions about Google customer losses or internal implementation.

**The reading is valuable for reconsidering failure boundaries.** The preliminary report identifies a propagation chain worth following, but does not disclose per-service spare capacity, retry policies, or a complete control-component topology. One incident cannot establish a universal recovery time for a deployment pattern. The final report is worth reading for its explanation of simultaneous backup-control failure and whether corrective work addresses control dependencies and failover capacity alongside power restoration.
