---
id: review-openbmb-forgekernel
title: '2026-10-31 | ForgeKernel: Self-Evolving Kernels Catching and Surpassing Experts
  and Agents'
date: '2026-10-31'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://github.com/OpenBMB/ForgeKernel
tags:
- agent-reliability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-openbmb-forgekernel/
long_read: true
summary: "ForgeKernel milestones, probe-backed knowledge and reference promotion, with repository/paper evidence boundaries."
---

## Improving an existing reference

ForgeKernel's repository workflow starts from an executable kernel, runs and profiles it, and asks an architecture agent to derive milestones. It addresses repeated rediscovery of hardware constraints and plateaus that parameter tuning cannot cross. Source-visible, black-box and reference-generation modes expose different information and should not be compared as identical budgets.

Milestone M0 fixes kernel splits, tiles, warp roles, register/shared-memory budgets and resident data. Later milestones tune within that structure after its gate passes. When measurements indicate a structural limit, the architecture agent revisits M0 instead of accumulating local workarounds.

## Preserving validated progress across loops

The inner loop implements a decision and uses a GPU job for correctness, reference timing and profiling; failed candidates are reverted. The outer loop revises the curriculum after stagnation or a gate impasse. Milestones contain decisions and contracts rather than reference implementation bodies, while probe-certified hardware mechanisms enter a cross-operator knowledge base.

A confirmed faster kernel can become the next reference, with task semantics, shapes and inputs copied into a self-contained generation. Stopping uses same-job confirmation-ratio noise with a documented floor of 1.5%. A plateau means no reliable improvement was found, not that optimality was proved.

## Keep repository results tied to their evidence

The frozen README describes 27-operator results while its News paper link points to JustGoal, a goal-only baseline study. Those numbers cannot establish the reference-driven workflow's results interchangeably. The RMSNorm example fuses nine PyTorch launches into one and reports a specific B200 run; it does not predict gains against optimized expert kernels.

My interpretation is that the workflow fits tasks with executable references, explicit shapes and tolerances, and a budget for hours of GPU and model search. Requiring hardware probes usefully separates plausible explanations from measured mechanisms. Performance conclusions still need the corresponding paper version, reference implementation and same-job measurements.

Source: [Original engineering article](https://github.com/OpenBMB/ForgeKernel)
