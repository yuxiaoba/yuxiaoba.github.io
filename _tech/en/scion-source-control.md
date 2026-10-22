---
id: scion-source-control
title: '2026-10-13 | Scion: How coding agents change source-control scaling'
date: '2026-10-13'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- systems-reliability
summary: Scion’s incremental changesets, server-side queries, and tiered object caches,
  with implications for CI, review, and failure isolation.
long_read: true
source_url: https://www.anthropic.com/engineering/redesigning-source-control
permalink: /tech/en/scion-source-control/
writing_source: assistant
translation_source: assistant-authored paired Chinese/English analysis
published_at: "2026-10-20T10:29:21.485154+08:00"
updated_at: "2026-10-20T10:29:21.485154+08:00"
---
## When code production outgrows development infrastructure

Anthropic's Scion case is useful because it shows how coding agents can move the bottleneck from writing code to storing, distributing, and validating it. The team reports growth from about 2,500 daily merges in May 2026 to more than 30,000 in September, with a five-month migration of its monorepo to an in-house version-control system. Understanding the change requires examining data structures, fetching, and development workflows together; adding more mirrors no longer explains the solution.

Original: [Redesigning source control at Anthropic](https://www.anthropic.com/engineering/redesigning-source-control)  
Nick G. and the source control team (S.G., R.K., Dan C., Garrett H., Ben L., Colin M., Joe P.) · First published 2026-10-13; updated 2026-10-15

## Why fetching on demand was not enough

The reported scale is substantial: nearly 100 GB of main-branch history, a compressed working copy exceeding 25 GB, and about 25 million CI checkouts per day. Naively transferring a complete copy each time would exceed 600 PB daily. That is an illustrative estimate of scale, not measured network traffic.

Shallow clones, sparse checkouts, promisor remotes, mirrors, and repository snapshots had all helped. However, growing commit volume made snapshots fall behind main more quickly and made history-dependent operations on partial clones harder to maintain. Scion changes the assumptions: agents and jobs are generally online, so clients need not independently provide the full version-control feature set. Commits, merges, rebases, history, and blame move to the server; clients retain a bounded object cache, working-directory management, and filesystem monitoring.

This shifts work from maintaining a repository for every consumer to answering queries through a shared service. CI that needs a diff or ancestry information can use APIs without creating a working copy. The trade-off is dependence on a reachable server; offline autonomy is no longer a central design goal.

## Separate incremental writes from query structures

Scion's basic unit is a changeset: a write-ahead-log entry describing files changed relative to the first parent, with content-addressed references to compressed file contents. Changesets are created on the server. The design aims to make write cost track the size of the change, reducing repeated work that grows with the whole repository.

<a class="note-image-link" href="/assets/images/tech/scion-source-control/changeset.png" target="_blank" rel="noopener" aria-label="Scion changesets, derived trees, and file contents · View original image ↗"><img src="/assets/images/tech/scion-source-control/changeset.png" alt="Scion changesets, derived trees, and file contents" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: Spanner holds changeset metadata and file changes above, while cloud storage holds immutable contents below; dashed tree boxes are derived by the server.*

A change list alone cannot answer every history query efficiently. Scion therefore builds derived structures for blame, path history, and commit-graph queries. Each type can be computed recursively from its parents' derived values, either eagerly or on demand. Clients do not depend on the internal format, allowing server-side index changes. This separates simple writes from efficient reads; it does not eliminate index-construction costs.

The team also limits routine dependence on refs. Creating a changeset and moving a branch pointer are separate operations, with the latter using compare-and-swap on one Spanner row. Consequently, the description of cheap, lock-free commits should not be read as an absence of consistency coordination throughout the system: mutable pointers still require their own updates.

## Design fetching around shared caches

Starting from the desired root tree, clients recursively request only missing tree and file objects. Each request identifies an immutable object rather than requiring the server to calculate a client-specific difference and build one enormous response. Interrupted fetching can resume by requesting the remaining objects. Sparse and virtualized checkouts follow naturally from demand: unneeded directories are not requested, and unread files need not immediately materialize on disk.

<a class="note-image-link" href="/assets/images/tech/scion-source-control/checkout.png" target="_blank" rel="noopener" aria-label="Scion clients, node caches, regional caches, and authoritative servers · View original image ↗"><img src="/assets/images/tech/scion-source-control/checkout.png" alt="Scion clients, node caches, regional caches, and authoritative servers" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: control operations reach the server above; orange object requests traverse node and regional caches, continuing upstream only on a miss.*

On cluster nodes, scion-daemon shares objects across local jobs, with periodic snapshots seeding new nodes. Misses go to regional scion-cache servers and then to scion-server, which accesses Spanner or cloud storage. Regional caches stream objects directly from memory in the daemon's on-disk format, avoiding repeated compression and client-specific difference calculations.

All three tiers implement the same RPCs, but their relationships are strictly enforced operationally. This matters because allowing every request to bypass a failed regional cache and reach the origin could turn a local failure into global overload. Content addressing reduces cache-consistency work without removing capacity-planning and failure-isolation responsibilities.

## Which costs do the performance numbers describe?

The authors report cache hit rates above 99% at each tier and Scion infrastructure CPU and memory requirements around 1/200 of the previous Git-mirroring footprint. CI and research-job checkouts become two orders of magnitude faster, moving from minutes to seconds; CI gains 25% CPU capacity. These describe infrastructure resources, one operation's latency, and system-level CI savings respectively. They should not become a claim that all development costs fall by a factor of 200.

These are internal migration results. The article does not supply a standardized workload, tail-latency distributions, or a cost breakdown sufficient for external recalculation. Its mechanisms explain why shared objects and avoided checkouts can help, but the reported multipliers do not automatically transfer to smaller repositories or different cache locality. A useful assessment first separates time spent fetching contents, querying metadata, and building code.

An implication of this design is that cache benefits depend on repeated object access across jobs. When jobs on a node share substantial code, the daemon reduces repeated fetching. If they mostly read distinct new contents, pressure still reaches regional caches and storage. The reported high hit rate should therefore be understood as a workload characteristic rather than an inherent protocol guarantee.

## Version control changes propagate into CI and review

Scion is not an isolated command replacement. The team also built Antique for code review, code search, permissions, and merge workflows. Seven people completed the five-month migration while daily merges increased tenfold. The article acknowledges that hundreds or thousands of changes can land while tests are running. The team consequently invested in post-merge and pre-deployment testing rather than successfully reproducing a conventional merge queue guarded by a global repository lock.

This shifts consistency risk and repair work to later stages; higher merge throughput does not itself establish better software quality. The article describes simulations, fuzzing, rate limiting, and directory-level permissions, but provides no unified improvement metric for defects or incidents. Engineers still review every change request and constrain agents' design decisions, for example preventing linear commit-log scans for information already available from another service.

## The design judgments worth retaining

This is industrial experience under unusual conditions: an enormous monorepo, many online consumers, and Anthropic's high internal token expenditure together shape the design. The authors explicitly say Scion is unsuitable as a general Git replacement, and full migration involves bespoke review, search, and CI systems.

Three judgments are more transferable: determine whether a job actually needs a working copy; expose frequent history queries through a shared service; and make immutable-object fetches directly answerable by multiple cache tiers. Start further reading with the changeset and checkout sections, track which work disappears and which moves to the server, then revisit the coordination costs introduced by the changed development workflow.
