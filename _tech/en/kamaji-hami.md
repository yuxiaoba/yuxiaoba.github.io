---
id: kamaji-hami
title: 2026-10-25 | Testing Kamaji and HAMi Tenant Scheduling Without GPUs
date: '2026-10-25'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
- inference-serving
summary: Mock hardware tests admission tunnels, fractional quotas, and tenant visibility;
  eight passing tests do not establish runtime GPU isolation.
translation_source: assistant
authorship: assistant
long_read: true
source_url: https://www.cncf.io/blog/2026/10/23/multi-tenant-gpu-kubernetes-on-simulated-hardware-with-kamaji-and-hami/
permalink: /tech/en/kamaji-hami/
published_at: '2026-10-25T08:48:16.922011+08:00'
updated_at: '2026-10-25T08:48:16.922011+08:00'
---
A GPU platform's control path can be tested before real GPUs are available. This CNCF lab combines Kamaji's hosted tenant control planes with HAMi's fractional-resource scheduling. It checks whether the API server can reach a tenant-side webhook through Konnectivity and whether memory and compute requests influence scheduling. The result is useful evidence about wiring and allocation decisions before hardware procurement.

Original: [Multi-tenant GPU Kubernetes on simulated hardware with Kamaji and HAMi](https://www.cncf.io/blog/2026/10/23/multi-tenant-gpu-kubernetes-on-simulated-hardware-with-kamaji-and-hami/)  
Anish Bista · CNCF · 2026-10-23

## Different layers of the platform

Separate clusters give teams independent APIs and control policies but consume control-plane resources. Shared clusters require other tenant boundaries. Kamaji runs tenant control planes as pods inside a management cluster, retaining separate API servers, schedulers, and controller managers without dedicated control-plane machines per team.

HAMi changes GPU allocation inside each tenant. Workloads request memory in MB and compute percentages, allowing multiple pods on a card. Kamaji manages cluster/control-plane boundaries; HAMi allocates GPU shares on tenant workers.

In the lab, tenant-a and tenant-b have separate workers and API servers. They share management infrastructure and the kamaji-etcd datastore service, with tenant data separated. This does not demonstrate two tenants contending on one physical GPU, nor remove shared infrastructure failure points. Isolation should be described by layer.

<a class="note-image-link" href="/assets/images/tech/kamaji-hami/architecture.jpg" target="_blank" rel="noopener" aria-label="Kamaji and HAMi lab with shared management and separate tenant workers · View original image ↗"><img src="/assets/images/tech/kamaji-hami/architecture.jpg" alt="Kamaji and HAMi lab with shared management and separate tenant workers" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Two control planes are hosted above; separate workers below run HAMi and mock GPUs. Dashed arrows show webhook tunnel paths.*

## The critical cross-boundary call

The tenant API server runs in the management cluster, but HAMi's webhook runs on the tenant worker. GPU pod admission must traverse Konnectivity so the webhook can establish the scheduling path and HAMi can select a node. A running hosted control plane does not itself prove this reverse connection works.

The integration value is an inspectable chain from pod creation through admission, scheduling, and binding. If the webhook is unreachable, control-plane pod status alone is insufficient. schedulerName, allocation annotations, and events reveal whether the intended scheduler received the request. This dependency deserves early testing in separated control and data planes.

## What the mock device simulates

The lab uses Docker containers on one Linux host, with a suggested minimum of four CPU cores, 8 GB free RAM, and 20 GB disk. A kind cluster hosts management components and both tenant control planes. Separate kindest/node worker containers join through kubeadm. MetalLB, Calico, and Konnectivity complete the network arrangement.

The real HAMi device plugin requires an NVIDIA driver. The mock skips discovery and registers capacity from node annotations while webhook, scheduler, and quota logic follow the software path. Tenant-a models one A100 80 GB with 81,920 MB and 100 compute units. Tenant-b models two L4 24 GB cards totaling 49,152 MB and 200 units. These are resource-model units, not counts of physical GPU cores.

The nvidia.com/gpu capacity represents sharing slots here: 10 for the single simulated card and 20 for two cards. Reading those integers as physical-card counts would be incorrect. Device identity, capacity, and slots must be distinguished when checking fractional scheduling.

## What eight passing tests establish

The author reports eight passing tests. Three pods each request 20,000 MB and 30% compute and are scheduled on tenant-a's one mock card, totaling 60,000 MB and 90%. A fourth equivalent pod would require 120% compute and stays Pending with CardInsufficientCore. A 90,000 MB request exceeds card capacity and is rejected with CardInsufficientMemory.

These failures exercise separate compute and memory constraints. Tenant-visibility checks query each API server for nodes, pods, and capacity, returning only that tenant's worker and objects. This supports API visibility separation in the demonstrated configuration, not claims about network attacks, storage isolation, or real GPU interference.

An important manual step sits between allocations. The real device plugin completes allocation and releases the node lock; the mock does not. The author marks bind-phase successful and removes the lock, allowing subsequent pods to bind instead of waiting up to five minutes. This is incomplete mock lifecycle behavior, not evidence of a production Kamaji/HAMi defect. Manual unlocking is not a general production procedure.

## Moving beyond the control path

No CUDA workloads ran. The lab measures neither actual memory/compute enforcement nor throughput or noisy-neighbor effects. Workload containers wait rather than exercise a GPU, so Running status does not establish runtime resource guarantees. Real deployment still needs driver-level enforcement, reclamation, interference, and recovery tests.

The worker-container approach is experimental; Kamaji's supported routes use kubeadm on real machines or Cluster API. Shared management capacity, availability, and tenant upgrades also remain subsequent questions. These delimit the next evaluation stage.

The transferable sequence is to verify hosted-API-to-webhook reachability, then allowed and rejected allocations and tenant visibility, and finally runtime isolation and performance on real GPUs. The article moves project compatibility from expectation to an inspected lab with concrete failure behavior. It does not establish a production-isolated GPU platform by itself.

## Negative tests say more than Running

Three Running pods alone would not show whether HAMi allocated them or another scheduling path placed them. Rejecting the fourth compute request and oversized memory request, together with annotations and events, establishes that requests reached the intended scheduler, capacity was accumulated, and specific excess conditions were recognized. That chain concerns control logic, not device execution.

Separate API queries similarly provide stronger evidence than two control-plane names, but do not simulate malicious administrators or compromised management infrastructure. The eight tests are a functional-regression starting point rather than a complete attack-surface assessment.

Real hardware evaluation should add the lifecycle omitted by the mock: discovery, allocation completion, lock release, reclamation after process exit, and capacity updates following driver failure. Without observing those events, correct static quotas need not ensure consistent long-running allocation. These are follow-up checks inferred from the simulation boundary, not production defects demonstrated by the article.
