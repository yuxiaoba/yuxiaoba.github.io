---
id: meta-jittesting
title: 2026-10-30 | Meta uses two test-generation paths to catch risky changes
date: '2026-10-30'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
- coding-agents
summary: Meta has deployed Catching JiTTests to generate executable tests for risky
  code changes and filter failures before they reach engineers. The tests expose behavioral
  differences; whether a difference is a bug still depends on the intended change.
long_read: true
source_url: https://engineering.fb.com/2026/10/29/security/catching-bugs-before-they-land-jittestings-human-on-the-loop-approach-at-full-scale/
permalink: /tech/en/meta-jittesting/
translation_source: assistant-authored paired Chinese/English reading notes
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-10-30T10:31:20.339125+08:00'
---
Meta has deployed Catching JiTTests to generate executable tests for risky code changes and filter failures before they reach engineers. The tests expose behavioral differences; whether a difference is a bug still depends on the intended change.

**Source:** Sreeja Thummala, Sophie Zeng, Mark Harman, Weini Liu and Eric Liu, [Catching Bugs Before They Land: JiTTesting’s Human-on-the-Loop Approach at Full Scale](https://engineering.fb.com/2026/10/29/security/catching-bugs-before-they-land-jittestings-human-on-the-loop-approach-at-full-scale/), October 29, 2026.

## From behavioral differences to candidate defects

The system uses spare overnight capacity to target the previous day's diffs selected by a risk model trained on past changes. Two paths run in parallel. The dodgy diff path treats the change itself as a mutant and generates tests that distinguish it from the parent. The intent-aware path infers intent and risks from the code, title and summary, constructs mutants representing potential mistakes, and generates tests to distinguish those mutants before running them on the actual diff. A failure on the real change is a weak catch for further assessment, not automatically a defect.

<a class="note-image-link" href="/assets/images/tech/meta-jittesting/workflows.png" target="_blank" rel="noopener" aria-label="View the original JiTTests workflow"><img src="/assets/images/tech/meta-jittesting/workflows.png" alt="JiTTests generates tests through direct mutation and intent-aware workflows, then filters behavioral differences" loading="lazy"><span class="note-image-action">View original ↗</span></a>

The two paths produce mutants and tests; tests passing on the parent and failing on mutants and the target diff become candidates.

## Filtering and the human role

An ensemble of LLM judges examines the test code, execution result, diff and inferred intent. A rule-based system called RubFake supplies deterministic checks; together they rank candidates, and only sufficiently strong ones trigger engineer outreach. People set criteria, review aggregate outcomes and confirm whether observed behavior was intended, reducing per-output review. Rules and human feedback still matter because model judgments are nondeterministic.

Meta reports that 589 engineers engaged, 64% of those contacted, and a 60% reported true-positive rate. In the first half of 2026, the system helped catch 74 serious privacy bugs at the diff stage; the company reports a 20% reduction in overall privacy SEVs during that period. These are internal operational figures, and the article does not provide a control design sufficient to isolate a causal effect. Results may differ with the codebase, risk selection and review policy.
