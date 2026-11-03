---
id: cloudflare-dns-targeted-zone-builds
title: 2026-11-03 | How Cloudflare Reduced DNS Build Work While Preserving Correctness
date: '2026-11-03'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://blog.cloudflare.com/dns-targeted-zone-builds/
long_read: true
summary: Change classification, shared metadata, Kafka acknowledgments and mirror
  comparison define the correctness boundaries of faster DNS builds.
tags:
- systems-reliability
- observability
permalink: /tech/en/cloudflare-dns-targeted-zone-builds/
translation_source: assistant-authored paired Chinese and English
published_at: '2026-11-03T08:33:39.690995+08:00'
updated_at: '2026-11-03T08:33:39.690995+08:00'
---
**Cloudflare · Engineering practice · 2026-11-02**  
Original: [How we halved DNS build delay and cut memory use by 85%](https://blog.cloudflare.com/dns-targeted-zone-builds/) · Alex Fattouche

After a DNS record or setting changes, Cloudflare's Zone Builder reads database state, generates data for authoritative DNS, and writes changes to Quicksilver. Some zones now exceed 20 million records. An old full build read, encoded and compared the entire zone even when the final write was small. The new design separates two decisions: a planner determines what must be rebuilt, while a unified scheduler combines queued work without losing message acknowledgment semantics.

## Decide what can safely be omitted

A record event usually identifies the affected DNS name. A zone-setting event can originate from several products and sometimes changes only a timestamp, leaving its cause ambiguous. Cloudflare changed event producers to include changed fields and previous and new values when available, then traced their effects on output. The planner chooses among five build types: specific names only; names and shared metadata; apex and metadata; purge; and a full-zone build.

The rule is that every key written by a targeted build should match the corresponding full-build output byte for byte from the same state. Ordinary record changes can target a name; wildcard and nameserver changes also affect metadata; settings such as Universal SSL can require apex and metadata. When the scope is unknown, the normal fallback is a full build. For each rebuilt name, old keys are also scanned and keys absent from the new output removed.

There is a deliberate exception: zones above a fixed record-count threshold cannot complete a full build. The system instead rebuilds the apex, metadata and names identified by queued events. Zone holds reduce some remaining risks, and rare cases may require manual per-name rebuilds. This is not an unconditional proof of full-build equivalence; it is a trade-off between capacity and prolonged blockage.

## Shared state and timing

During onboarding or offboarding, one public domain may have multiple internal zones. Record keys are separate, but a shared metadata key identifies the internal zones that may serve answers. Before execution, the builder rereads the current publishable set, reconstructs the shared key, and writes the triggering zone's records before metadata that refers to them.

An event describes the past; the database may change while a build waits. A fresh execution-time snapshot can escalate a targeted build to full, turn it into a purge, skip a zone that no longer belongs, or reconstruct shared metadata. Reads use database replicas, while Kafka delivery and replication progress independently: an event can arrive before its database update. The aggregator delays events, and a final database check rejects a replica that is still behind rather than relying solely on a fixed wait.

## Merge work without losing acknowledgments

The unified scheduler combines queued name and metadata requirements for a zone. Merging only adds work: if any event requires a full build, so does the combined plan; purge overrides rebuilds. It tracks DNS work separately from Kafka messages awaiting acknowledgment. Even when individual names are no longer needed in the merged plan, their messages remain until the result is safely written.

A Kafka partition's committed offset cannot pass an unfinished earlier message. Later builds can finish and be marked in memory, but a restart replays them if the offset remains blocked. Cloudflare chooses repeated work over lost changes. Fewer large builds shorten the time the oldest unfinished event blocks a partition. A per-zone rebuild interval prevents a busy zone from consuming every worker, with an exception for work that has waited too long.

## Validation and what the numbers mean

Tests compare targeted keys against full-build output from the same database state with time-dependent values pinned. Early rollout also ran the two builds side by side. A continuing mirror builder consumes the production Kafka stream and reads production database state but writes to a separate Quicksilver environment that serves no customers. A comparer samples 20% of zones. Because the environments do not always finish simultaneously, a transient difference is not automatically an error; the team looks for new difference types that persist after both catch up. The article's mirror illustration describes the validation arrangement; this note does not include an image.

In the reported 24-hour window, 92.95% of builds avoided a full-zone rebuild. Full builds accounted for 7.04%; the article's category comparison indicates an approximately 40% reduction. In a same-event production-versus-mirror comparison, the largest p99 build-completion delay spike fell from 14.6 minutes to 1.21 minutes. That compares peaks in the observed window, not a per-zone latency guarantee. Peak deployment working-set memory fell from 79 GiB to 12 GiB, about 85%.

The additional headroom then allowed shorter rebuild intervals; database rejection of lagging replicas also allowed a shorter aggregator wait. Together, the changes reduced median build completion delay from roughly 7.7 to 3.3 seconds. This metric ends when data is written to Quicksilver and excludes global edge propagation. The article also explains how coarse histogram buckets distorted percentile estimates and were later replaced by finer native histograms. **The design lesson is to build correctness into the optimization: classification, fresh state, stale-key deletion, retry acknowledgments and mirror comparison all matter.**
