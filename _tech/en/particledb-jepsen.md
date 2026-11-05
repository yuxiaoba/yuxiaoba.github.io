---
id: particledb-jepsen
title: '2026-11-02 | ParticleDB: Testing Database Safety Promises on One Node'
date: '2026-11-02'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
summary: Jepsen uses generated SQL, transaction histories and WAL faults to expose
  gaps between configuration claims, semantics and recovery.
translation_source: assistant-authored Chinese and English paired content
long_read: true
source_url: https://jepsen.io/analyses/particledb-1.1.4
permalink: /tech/en/particledb-jepsen/
published_at: '2026-11-02T08:39:51.033336+08:00'
updated_at: '2026-11-02T08:39:51.033336+08:00'
---

A database's advertised isolation, the execution path used by a client and the state recovered from disk can disagree. Jepsen's ParticleDB analysis matters because many severe failures occurred with one node, one client and no injected faults. Distributed failure scenarios are not the starting point for establishing correctness.

Original: [Jepsen: ParticleDB 1.1.4](https://jepsen.io/analyses/particledb-1.1.4) · Kyle Kingsbury · 2026-10-31. Orkes funded the research under Jepsen's ethics policy.

## Establish the tested scope

ParticleDB aims to combine transactional SQL, key-value access, vector search and live analytics for AI applications. Orkes originally built version 1.0.0 around particular Conductor queries, then substantially refactored it. This report tests **1.1.4 through 1.1.18.11.rc-22**, not every earlier or subsequent release.

The supplied builds lacked replication, so tests covered single nodes only. They ran on Debian 13 in containers and EC2 VMs, using Postgres JDBC 42.7.11 and ParticleDB Java SDK versions 1.0.0–1.0.2. The harness exercised transaction modes and all three WAL sync modes, with process kills, LazyFS simulation of unsynced write loss and disk-file corruption. These results do not evaluate Raft replication correctness.

The report presents 96 issues; by rc-22, 86 appeared resolved and ten remained. Orkes subsequently released **1.1.19-rc.13**, claiming to address all remaining issues. Jepsen did not test that release. The vendor's statement and independently observed regression results must remain distinct, and old failures should not automatically be attributed to the new version.

## Setting an isolation level was insufficient

Tested versions rejected or ignored standard SQL isolation settings; startup `--txn-mode` controlled behavior. Documentation also conflicted. An internal operator guide mapped `occ-v3` and `zero-copy-occ` to Snapshot Isolation, `serializable-ssi` to Serializable, and `table-2pl` to Strong Serializable, while other material used imprecise concurrency-safety descriptions.

This affects the test oracle directly. Without knowing which anomalies the actual configuration promises to prohibit, successful commits and returned values do not establish isolation. Descriptions of `sync` and `groupsync` durability also disagreed, so a mode name alone could not establish what protected acknowledged writes. No advertised TLA+ specification was available during the engagement; Jepsen could not establish its properties or correspondence to the implementation. This is not a refutation of formal methods themselves.

## Three workload families narrow the problem

Random read/write and list-append transactions provide the first layer. The `rw` workload reads and writes values identified by unique keys; `append` adds unique integers to lists. Lists preserve recognizable write histories. Elle uses observed version order and transaction dependencies to find cycles and other anomalies. Varying datatypes, primary versus unindexed secondary keys and joins exercises different implementation paths.

A second layer checks internal consistency: does a transaction read its own earlier writes? Such failures can reveal basic state-management problems without first untangling complicated interleavings between transactions.

The `compare` workload generates schemas and SQL, executes them against ParticleDB and Postgres, and compares results. Although limited to sequential behavior, roughly two thousand lines of generative tests found many bugs. Legitimate database differences complicate this oracle. Later in the engagement, minor incompatibilities repeatedly occupied the minimizer and could conceal more serious failures. A differential generator needs a maintained understanding of known differences, rather than treating every mismatch as an equally important defect.

## From small counterexamples to lost acknowledged writes

One accessible example involved deleting a row inside a transaction: direct reads no longer saw it, while predicate-bearing aggregate queries still observed it. Other versions mishandled inserted column order, producing unreadable scans, misplaced values or rows that were difficult to delete. Different operators could expose inconsistent representations of ostensibly identical data.

Issue #110 is closer to application-level risk. Healthy single nodes in 1.1.18.11.rc-18 through rc-22 could discard acknowledged writes. In one append test with WAL mode `sync`, 31 of approximately 20,000 keys lost writes. A key repeatedly returned `[1,2,3]`, then exhibited a different growing list without those elements. This required no disk fault and cannot be reduced to an omitted `fsync`. The discussion specifically reports normal-operation data loss in rc-22's default `occ` mode; the stronger `serializable` mode still exhibited stale reads during normal operation and internal anomalies and Lost Update with process kills.

Fault injection adds another layer. In one WAL bitflip case, recovery detected checksum corruption but replayed a valid prefix and resumed serving. Previously acknowledged list elements then disappeared. The question is both whether corruption is detected and whether the service subsequently reports success over incomplete state. Simulated misdirected reads/writes also produced total state loss. Each finding has its own version and configuration boundary; they should not be collapsed into one universal failure mechanism.

## What reliability work can take from it

The transferable testing sequence moves from SQL semantics and single-transaction state to concurrent histories and disk recovery. Even a chaos-engineering effort needs normal-path tests that can demonstrably fail. Changing encodings, client interfaces and access paths then checks whether equivalent semantics actually share a correct implementation.

For agent backends, a successful tool call may indicate only that a request was accepted; subsequent workflow steps can still depend on inconsistent state. Performance comparisons likewise need explicit isolation and durability conditions. Throughput obtained under weaker semantics cannot be compared directly with throughput under stronger guarantees. These are engineering implications of the observed mechanisms.

Jepsen also discusses repair claims and poorly understood changes in LLM-assisted development. The audit is not a controlled comparison of development methods, however, and cannot estimate the causal effect of AI coding on defect rates. The actionable evidence lies in versions, transaction histories, counterexamples and regression testing. Start with Test Design and Discussion, then follow #110 and the WAL corruption cases to see how observations contradict specific safety properties.
