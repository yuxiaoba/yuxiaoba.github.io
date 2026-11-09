---
id: review-google-gke-networking-dataplane-agentic-ai
title: 2026-10-29 | GKE networking dataplane for large agentic AI workloads
date: '2026-10-29'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://cloud.google.com/blog/products/networking/gke-networking-dataplane-for-large-agentic-ai-workloads
tags:
- agent-reliability
- coding-agents
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-google-gke-networking-dataplane-agentic-ai/
long_read: true
summary: "How high-cardinality Pod labels delay identity allocation, and when annotations or precise exclusions preserve policy semantics."
---

## Why networking can delay sandbox startup

Google discusses frequent Pod creation and destruction in workloads such as agent reinforcement learning. A model cannot advance while its code-execution sandbox is starting, even when GPU capacity is available. Controllers commonly attach agent IDs, timestamps or claim UIDs to each Pod. GKE Dataplane V2 derives numeric network-policy identities from labels, so unique label combinations can give every sandbox a distinct identity.

Identity allocation and eBPF map updates then enter the startup path; serial allocation can delay initialization under churn. The article also identifies a cluster-wide limit of 65,536 network identities. This is not a Pod or IP-address limit: instance metadata can make identity count grow even when the sandboxes have similar security requirements.

## Two ways to reduce identity cardinality

The first approach separates selection semantics from observational metadata. Fields that do not participate in Service selectors or core resource grouping can move from labels to annotations. They remain available as metadata but no longer affect this identity calculation, allowing equivalent sandbox types to share an identity.

The second approach uses precise Cilium label exclusions. The article illustrates the cilium-config-emergency-override ConfigMap in kube-system, excluding dynamic fields such as sandbox-name-hash or timestamp. This handles frameworks that continue attaching those labels: the labels remain, but identity calculation ignores them. Both approaches depend on the excluded field carrying no required isolation semantics. Removing a dimension used by a security selector changes authorization, so high cardinality alone is not sufficient justification.

## Interpreting the throughput and recovery numbers

The article reports 300 sandbox creations per second with sub-second latency. A separate Agent Substrate validation with 200,000 agents reports 500 activations per second and suspend/resume latency below 500 milliseconds. Substrate also bypasses Kubernetes scheduling limits; these are different operations and system paths, not interchangeable measurements of one network optimization. Customer observations of hundreds of thousands of environments across clusters and spikes above 30,000 sandboxes in one cluster have different scopes again.

My interpretation is a specific metadata-modeling lesson: when startup delays grow with identity count but actual security classes are few, check whether per-instance tracking fields have accidentally become policy identity. The article does not establish those rates for arbitrary GKE deployments or isolate networking, scheduling and state-recovery contributions in one controlled comparison.

Source: [Original engineering article](https://cloud.google.com/blog/products/networking/gke-networking-dataplane-for-large-agentic-ai-workloads)
