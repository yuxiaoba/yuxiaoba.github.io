---
id: habitat-storage-part2
title: '2026-10-24 | Habitat: Balancing Multi-Tenant Isolation and Latency'
date: '2026-10-24'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
- observability
summary: From partition throttling to regional caching, explaining Habitat’s evolution
  and the scope of its 12× median-read improvement.
long_read: true
source_url: https://openai.com/index/scaling-storage-one-billion-users-part-two/
permalink: /tech/en/habitat-storage-part2/
authoring_source: assistant
translation_source: assistant
published_at: '2026-10-26T11:44:51.392682+08:00'
updated_at: '2026-10-26T11:44:51.392682+08:00'
---
At shared-storage scale, resource boundaries and ownership boundaries can diverge. A hot key for a minor feature can contend with login traffic; moving the feature into its own container can instead create a launch-day capacity failure. Habitat’s second engineering report is valuable for its journey from shared to dedicated and back to shared-by-default storage, and for explaining why caching needs a reliable change pipeline. [Original: Rapidly scaling online storage to serve over 1 billion ChatGPT users (Part II)](https://openai.com/index/scaling-storage-one-billion-users-part-two/).

**Jon Lee, Hrachya Hakobyan, Chaomin Yu · OpenAI · 2026-10-23**

## Logical partitions do not own independent throughput

Habitat initially relied heavily on Azure Cosmos DB primitives and shared containers. Client-selected logical keys such as user_id or workspace_id could collide across use cases. More fundamentally, limits are enforced at physical partitions shared by multiple logical keys. A documented per-key maximum does not reserve that throughput for every key.

Storage growth changes the boundary too. When a physical partition splits while total provisioned container throughput stays fixed, each partition receives a smaller share. Active keys can therefore lose capacity even at unchanged request rates. Diagnosing this requires storage volume, partition count, and throughput allocation, not QPS alone.

## Dedicated containers distribute planning responsibility

Dedicated containers for critical workloads reduced cross-product blast radius. Scripts adjusted provisioned throughput as partitions multiplied. But each product team then needed to anticipate launches and demand. Growth that barely changed a shared pool could mean a thousandfold jump for a new dedicated container.

Single tenancy removed interference while losing the headroom of mixed workloads. The lesson is not that dedicated containers are inherently wrong: isolation policy is also capacity-planning policy. More containers can distribute database operations to teams poorly positioned to manage them.

## Returning to shared storage required new controls

The shared-by-default design adds hot-key throttling, lower-priority QoS for offline work, and an improved serverless mode that splits on RU demand as well as storage and scales each physical partition to 10K RU/s. These controls jointly change how the shared pool fails; serverless alone does not explain the result.

The team reports several subsequent months without provisioning or noisy-neighbor incidents. This is an operational observation, not a universal guarantee across workloads. Dedicated placement and data movement remain useful where stronger isolation is needed.

## Validate recovery at the actual scale

A regional power outage exposed failover times of several hours for large accounts. A later failback caused a connection stampede against the gateway. Disaster-recovery functionality existed, but neither team had tested its behavior at this scale. They subsequently used a production-sized non-production account and jointly tested SDKs, gateways, connection reuse, and metadata caching.

A transferable reliability lesson is to test failover and failback separately. Normal data-plane throughput, account control operations, and reconnection have different bottlenecks. A database outage visible to a product may require coordinated fixes across clients, proxies, and provider infrastructure.

## Three layers improve global reads

Reads represent over 90% of Habitat requests. Placing data close to users helps, but regional storage, power, and cooling constrain placement; broad replication consumes substantial capacity. Only small, highly latency-sensitive datasets are widely replicated. Other reads use Valkey lookaside caches near compute, while proxy overhead is reduced separately.

Short TTLs hurt hit rates; long TTLs increase staleness. Habitat consumes the Cosmos DB change feed to propagate cache invalidations globally within seconds, then refills on subsequent reads. Change-delivery speed and reliability become essential. This design should not be interpreted as globally strongly consistent caching.

## The 12× result belongs to the combined changes

The authors report global read p50 falling from roughly 120 ms to 10 ms. Nearby replication, regional caching, and the Rust proxy rewrite all contribute. The full improvement cannot be assigned to Rust, nor assumed for tail latency. Misses can still require distant cross-region reads.

CDC also supports indexes, migration, and analytics at millions of changes per second. It requires robust leases and worker lifecycles, isolation between streams, dead-letter queues, and alternate-region readers. Permanent delivery failures must not block a whole queue. Adding caching therefore makes change propagation a reliability-critical path. The source uses interactive illustrations; no suitable independent static original was obtained, so the explanation preserves these dependencies in text.

## Follow a request across capacity, caching, and recovery

A read may pass through identity checks and placement routing before hitting a regional cache or reaching a remote physical partition. Each layer affects latency and blast radius. Even after median latency improves, operations should distinguish hits from misses, interactive from offline traffic, and normal operation from recovery. Otherwise rare failures on critical paths can disappear inside the aggregate.

Invalidation is asynchronous to database writes. A backlog can first appear as stale results and later as retries or additional reads. The article does not quantify that entire feedback process, but the dependency suggests observing change-consumption lag alongside request metrics. Database error rates alone cannot explain cache behavior.

Isolation also need not allocate equal treatment to every request. Interactive traffic and bulk extraction can merit different priorities under pressure. Nearby storage capacity can compete with inference capacity. The useful theme is aligning local optimizations with product latency and availability rather than maximizing every layer’s utilization independently.

The proposed in-house storage system remains in development, trading lower flash requirements for lower peak throughput. Treat it as a future direction, separate from observed Cosmos DB and caching improvements.
