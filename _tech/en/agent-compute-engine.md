---
id: agent-compute-engine
title: '2026-10-24 | Agent Compute Engine: Designing for Waiting, Resumption, and
  Authorization'
date: '2026-10-24'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- systems-reliability
summary: How microVMs, external credential brokering, snapshots, and shared fleets
  fit together.
long_read: true
source_url: https://cloud.google.com/blog/topics/ai-infrastructure/agent-compute-engine-deep-dive/
permalink: /tech/en/agent-compute-engine/
authoring_source: assistant
translation_source: assistant
published_at: '2026-10-26T11:44:51.392682+08:00'
updated_at: '2026-10-26T11:44:51.392682+08:00'
---
Agent compute demand is uneven. An execution environment may wait while a model reasons or a user is away, yet the next tool call needs files, processes, and dependencies ready again. Google Cloud’s Agent Compute Engine incorporates that lifecycle while separating untrusted execution from long-lived credentials. The engineering perspective joins isolation, idle cost, and persistent state in one design. [Original: Inside Agent Compute Engine: Building the compute foundation for the agentic era](https://cloud.google.com/blog/topics/ai-infrastructure/agent-compute-engine-deep-dive/).

**Ramanathan Venkatapathy, Rohit Jnagal · Google Cloud · 2026-10-23**

## A session need not be a continuously running VM

Traditional VMs offer full operating systems and isolation, but lifecycle operations can be slow relative to short tool calls. Containers start quickly but share the host kernel. Agents may require root, compilers, and browsers while spending much of their time waiting, making continuous resource reservation wasteful.

The design separates the harness, which plans and calls the model, from the sandbox, which executes dispatched commands and returns output. Each session has a single-tenant microVM. Host controls include immutable, read-only root filesystems and no persistent local state, with hardware-rooted node and workload attestation. This separation supports correlating sandbox activity with harness tool requests.

## Keep persistent credentials outside the sandbox

Zero-secrets refers to long-lived user credentials, OAuth refresh tokens, and cloud service-account keys. Sandboxes do not directly hold them or obtain them through ordinary instance metadata. They still require ephemeral session-scoped workload identity, so the phrase does not mean an absence of all identity material or authentication.

Outbound requests pass through a local mediation proxy and an off-node Agent Gateway. The gateway validates user delegation, agent identity, and node identity, applies egress and data-loss-prevention policies, then substitutes the required backend credential. A model influenced by malicious content cannot simply read a persistent backend token from its filesystem. However, the broker must still authorize operations correctly; externalizing credentials does not prevent every improper call.

<a class="note-image-link" href="/assets/images/tech/agent-compute-engine/mechanism.png" target="_blank" rel="noopener" aria-label="The four identities distinguish user, delegation, workload, and the agent’s own account; the gateway evaluates the relevant identities together."><img src="/assets/images/tech/agent-compute-engine/mechanism.png" alt="The four identities distinguish user, delegation, workload, and the agent’s own account; the gateway evaluates the relevant identities together." loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*The four identities distinguish user, delegation, workload, and the agent’s own account; the gateway evaluates the relevant identities together.*

## Four identities express different responsibilities

User identity identifies the task initiator or owner. On-behalf-of delegation authorizes specified harness work. Workload identity identifies the sandbox originating traffic. Workforce identity lets an agent act with its own account and resources. Separating them avoids treating session origin as unrestricted user authority.

MicroVMs also lack ordinary external network interfaces, default gateways, and direct VPC access. Communication crosses an isolated virtio-vsock boundary and mediation proxies. Workspace and private-network access can consequently use the same external authorization and audit path.

## Idle detection must understand the application

The command runtime signals idleness after tool execution ends and no background work remains. The host checkpoints the sandbox, releases active resources, and preserves resumable state. This is application-aware lifecycle management, not arbitrary suspension whenever CPU use is low.

A transferable design question is how long-running jobs, background processes, unfinished I/O, and external side effects relate to snapshot boundaries. The report describes snapshot, clone, and rollback primitives but does not guarantee rollback of every application side effect. Restoring memory or files does not revoke an operation already sent to an external service.

## Share static pages and persist meaningful changes

Many agents use identical base images, Python runtimes, and browsers. Pre-warmed snapshots, DAX, and copy-on-write share static pages and allocate private deltas, with reclamation and compression returning memory. This reduces redundant environment state; it does not eliminate user data.

Storage separates disposable scratch overlays, read-only shared images/toolchains/caches, and durable workspaces and artifacts. Shared volumes also support collaboration. The arrangement preserves work across turns and days without copying an entire environment per agent, although persistence cost still depends on workspace size and write behavior.

## Use timing differences across workloads

Personal interactive sessions, enterprise business hours, and internal RL evaluations have different demand peaks. A unified pool can let low-priority work yield during interactive surges and run deferrable evaluation, research, or migration in quieter periods. Global placement must respect geography, data-location requirements, and enterprise policy rather than selecting available capacity alone.

Efficiency comes from idle reclamation, shared base state, and time-flexible scheduling together. The article provides no comprehensive independent performance benchmark. Near-zero active resources is not zero total cost, and rapid resumption should not become an invented latency number. At publication, the service was targeted for preview in coming months, not general availability.

Read identity brokering and lifecycle management first: they explain how authority is separated from execution and resources are concentrated on active work.

## Restoring state is not restoring old authority

A resumed session can load yesterday’s files and memory after today’s permissions have changed. Off-sandbox delegation and policy checks offer a way to avoid permanently embedding old authority in snapshots. Resuming progress should not automatically restore revoked access, although the article does not promise identical propagation latency for every enterprise permission change.

Shared static pages and session isolation also need joint evaluation. A platform assessment should examine simultaneous resumptions, growing private writes, base-image updates, and fleet pressure, rather than cold start alone. The article provides no detailed results for all these conditions, making it an architecture report rather than a performance guarantee.

A long-lived agent need not continuously own the same physical host. Workspace and identity semantics can remain stable while placement changes with policy and capacity, provided the control plane, storage, and audit trail preserve a consistent session identity.
