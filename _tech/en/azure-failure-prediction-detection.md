---
id: azure-failure-prediction-detection
title: '2026-11-05 | Azure AFPD: prediction must connect to migration and repair'
date: '2026-11-05'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
- anomaly-detection
summary: How prediction connects to allocation exclusion, migration, notifications,
  and repair to reduce hardware interruptions.
long_read: true
source_url: https://azure.microsoft.com/en-us/blog/predicting-and-detecting-failures-how-azure-strengthens-reliability-for-mission-critical-workloads/
permalink: /tech/en/azure-failure-prediction-detection/
translation_source: assistant
authoring_source: assistant
published_at: '2026-11-05T08:55:14.344660+08:00'
updated_at: '2026-11-05T08:55:14.344660+08:00'
---

Original: [Predicting and detecting failures: How Azure strengthens reliability for mission-critical workloads](https://azure.microsoft.com/en-us/blog/predicting-and-detecting-failures-how-azure-strengthens-reliability-for-mission-critical-workloads/)<br>
Mark Russinovich · 2026-11-04

Azure AFPD connects prediction/detection, mitigation, and repair. Fully operational since 2024, it is presented here through SAP workloads and customer notifications, not as a new SAP-only predictor. Coverage also includes general and specialized compute, HPC/AI, and selected storage scenarios.

Machine-learning models and rules examine node behavior and component telemetry such as SSD health. Flagged nodes stop accepting new allocations. Eligible VMs live-migrate to healthy nodes, typically with a pause of a few seconds; not every M-series size supports this. Where migration is unavailable, Resource Health and Scheduled Events communicate a redeployment deadline and recommended action. Customer high-availability logic still needs to consume those signals.

The repair stage removes the node from production, supplies diagnostic information, and stages spare parts. The author reports an 80% increase in monthly node repair rate and more than 36% fewer hardware reboots. The introduction also describes a 36% improvement in preventing hardware-related VM interruptions. Neither wording establishes a 36% reduction in all failures or downtime. These are platform-reported hardware results without detailed predictor precision, false-positive migration cost, or workload-specific controls.

Resource Health supports per-VM inspection, Resource Graph fleet queries, Event Grid push automation, and Scheduled Events advance notifications for VM-side handling. The first three expose consistent notification content through different access patterns.

The AIOps lesson is that prediction is only the start. Allocation exclusion, migration eligibility, time for non-migratable workloads to respond, and diagnostic handoff to repair determine whether a prediction prevents an interruption. The post is strongest as an account of that operational loop and its customer interfaces; model and training details belong to its linked technical paper.
