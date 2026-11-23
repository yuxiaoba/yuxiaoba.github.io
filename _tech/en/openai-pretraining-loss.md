---
id: openai-pretraining-loss
title: 2026-11-23 | What pretraining loss can tell us about recursive self-improvement
date: '2026-11-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- self-improvement
summary: Jakub Pachocki reports losses on a fixed internal code snapshot and asks
  what evidence would be needed to use such a measure to pace further development.
long_read: true
source_url: https://openai.com/index/perplexity-and-intelligence/
permalink: /tech/en/openai-pretraining-loss/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
When a downstream benchmark saturates, developers change the test. How can they track progress across those changes? Jakub Pachocki presents a series OpenAI has followed since GPT-3.5 and proposes using related measurements to inform decisions about the pace of frontier development. The argument depends on what the numbers 0.99, 0.91 and 0.76 actually measure.

## Predicting the next token on a fixed code snapshot

The reported measure is base-model log-perplexity, or cross-entropy loss, on a fixed held-out snapshot of OpenAI’s internal code. Assigning higher probability to the actual next token lowers average loss. Keeping the data fixed lets the lab ask the same question years later. Pachocki reports about 0.99 for GPT-3.5 and 0.91 for GPT-4, associating the latter with productive use of chain-of-thought reasoning. He also notes that reasoning can substantially improve task performance without changing this base-model loss. Predictive quality and the capability elicited at deployment require separate measurements.

## The inference from mathematics to pretraining research

Pachocki reports emerging capabilities in cybersecurity and mathematics below a loss of 0.8. After more than a year of posing open mathematics problems to models, the team began seeing results he describes as breakthroughs with a model around 0.76. These are points at which researchers observed capabilities in their model series. They do not establish prospective thresholds for a particular skill.

Discussions of recursive self-improvement often ask when the entire research process might be automated. Pachocki identifies an earlier possible acceleration point. A model that finds better algorithms for the next pretraining run could speed up its successors without automating the rest of the lab. He attributes most of the steeper 2026 loss curve to long-term research and compute investment, with a smaller role for automation. The mathematics experience motivates the hypothesis but does not measure the speed of that research feedback loop.

## What it would take to agree on a limit

Pachocki proposes that developers agree on a measurable limit and on a concrete monitoring or interpretability milestone required to cross it, such as a successor to current chain-of-thought monitors. The roughly 0.68–0.70 range he discusses is an extrapolation about possible new capabilities. No agreed industry ceiling is reported.

Changing the evaluation corpus can change a model’s loss, and labs train on different data mixtures. Code prediction can be a particularly poor proxy for earlier models trained primarily on general text. The inherent entropy of the data is also unknown, so equal reductions need not represent equal capability gains. Two empirical problems remain: calibrating a measure across labs and evaluating what a particular emerging capability can actually do.

Jakub Pachocki · 2026-11-22 · [Perplexity and Intelligence](https://openai.com/index/perplexity-and-intelligence/)
