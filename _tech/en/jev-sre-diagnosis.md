---
id: jev-sre-diagnosis
title: '2026-10-19 | Jev Diagnosis: Evidence Defines the Limits of Inexpensive Judgments'
date: '2026-10-19'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
long_read: true
source_url: https://www.sregym.com/blog/jev-driven-sre-diagnosis
tags:
- observability
- agent-reliability
- systems-reliability
summary: A 21-fault study shows how fast collection and choice-based judgments can
  be, and why wrong clues and missing dynamic evidence need different remedies.
writing_source: assistant
translation_source: assistant
permalink: /tech/en/jev-sre-diagnosis/
published_at: '2026-10-22T08:44:53.471250+08:00'
updated_at: '2026-10-22T08:44:53.471250+08:00'
---
This SREGym experiment separates diagnosis into two parts: programmatic collection and organization of cluster information, followed by Jev selecting investigation targets and supporting evidence from supplied choices. It does not use a freely acting LLM agent to generate commands or reports. The useful development is embedding inexpensive judgments in a constrained workflow while documenting the faults that workflow consistently fails to explain.

Original: [Jev-Driven SRE Diagnosis: What Worked and What Failed](https://www.sregym.com/blog/jev-driven-sre-diagnosis)  
Yiming Su, Saad Mohammad Rafid Pial, Jackson Clark, Tianyin Xu · First published: 2026-10-06

## Turn open-ended investigation into bounded choices

The collector first reads Kubernetes objects, events, recent pod logs, and resource state, summarizing anomalies by component. Jev chooses a component for closer inspection; the program gathers details and produces numbered evidence. Jev then judges whether the component is an origin, victim, or unrelated, and selects supporting items. Programmatic logic continues the investigation or assembles the report.

<a class="note-image-link" href="/assets/images/tech/jev-sre-diagnosis/workflow.png" target="_blank" rel="noopener" aria-label="Alternating collection and Jev judgments route investigation by origin, victim or unrelated verdicts · View original image ↗"><img src="/assets/images/tech/jev-sre-diagnosis/workflow.png" alt="Alternating collection and Jev judgments route investigation by origin, victim or unrelated verdicts" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: green boxes collect evidence and route execution; purple boxes contain Jev choices. A supported origin leads to submission, a victim points to a dependency, and unrelated or undetermined results trigger another candidate.*

This reduces the action space: the model need not invent commands or freely generate final diagnostic prose. Execution paths are easier to constrain, and outputs can be traced to supplied evidence identifiers. The trade-off is equally explicit: the answer set determines what can be expressed, while the collector determines what can be observed.

Success therefore belongs to the whole pipeline. Replacing the collector with simple log truncation or removing configuration-difference analysis produces a different diagnostic system even if Jev stays unchanged. That distinction is necessary to separate model capability from domain knowledge embedded in deterministic code.

## How much work the collector performs in a successful case

The article illustrates the division of labor with a webhook that changes memory limits. A Deployment template specifies 256Mi, but new pods receive only 16Mi and subsequently run out of memory. The collector identifies the template-to-instance discrepancy and narrows matching webhook candidates; Jev selects the component and key evidence. The report then explains the limit-rewriting mechanism.

Engineering-wise, this provides more information than handing a model an OOM log. OOM is an outcome; the mismatch between desired and actual objects points toward how configuration took effect. The collector organizes relationships scattered across objects, reducing the investigation the judge must perform itself.

That benefit also has maintenance costs. Changes to object versions, policy types, or application structure require checking whether relationship-extraction rules remain valid. A collector good at configuration differences may be much less effective at feedback loops visible only over time. This is an applicability boundary inferred from the successful example.

## Coverage and persistent blind spots

The authors run Jev 1.13.0 five times on each of 21 faults in the historical September 4 SREGym-Lite cohort. Diagnoses are scored by gpt-6-astra at high reasoning effort using a nine-question rubric and a 0.70 passing threshold. The pipeline passes 80/105 attempts, or 76.2%, with median diagnosis time of 14.6 seconds. Sixteen faults pass all five attempts; the remaining five fail all five.

Across 105 attempts, there are 252 Jev calls and 3.48 million input tokens. Estimated Jev inference cost totals approximately $0.15 at published prices. That excludes cluster operation, collection, engineering maintenance, and judging, and is not the full cost of resolving a production incident. Passing a diagnosis rubric also does not mean successful automatic repair.

The article compares against separate LLM-agent experiments on the same 21 faults, reporting similar pass rates at approximately 7× lower time and 200× lower inference cost. Jev has five attempts per fault and the LLM agents three. These are separate experiments, not synchronized controlled per-attempt comparisons, and they do not represent the current leaderboard cohort.

The all-pass or all-fail distribution is more informative than an average alone. Repeating the same workflow did not remove certain blind spots. Deployment assessment should inspect coverage and failure causes by fault type; repeated attempts may simply reproduce the same incorrect explanation.

## Wrong clues and missing clues require different fixes

In one failure class, the evidence exists but Jev selects the wrong clue. A CPU-saturation case provides both an expensive regular expression and a resource-limit change. Jev chooses the latter, identifying the affected component without explaining the actual mechanism. The relevant questions concern evidence comparison and stronger causal checks, rather than collecting the same configuration again.

In the other class, decisive dynamic evidence never reaches the input. A retry-amplification fault involves a feedback loop among queues, timeouts, and cross-service retries. The pipeline supplies no queue-depth or retry-count metrics and asks for a single root-cause component. Even a judge that always selects the most plausible available answer may be unable to express the correct multi-service explanation.

This suggests a useful debugging order: check whether required facts were present, whether the answer space could express the mechanism, and only then whether the selection was reasonable. Otherwise every failure becomes insufficient model intelligence, and changing models leaves the actual limitation untouched.

## A fast entry point, not a complete incident-handling loop

Such a pipeline could organize evidence for common configuration faults at the start of an investigation, leaving complex cases to a more flexible agent or a person. Escalation cannot simply depend on whether a report was generated: a fixed template can produce complete sentences from inadequate evidence. More useful conditions concern evidence coverage, cross-component explanations, and unresolved state.

Observation and action authority also need separation. A candidate diagnosis does not establish that a production configuration should immediately change. Extending the system to automatic repair requires action validation, impact boundaries, and recovery paths; diagnostic scores in this article do not validate those capabilities.

Assessment should also examine cases where no conclusion is justified. Allowing the system to acknowledge inadequate evidence for a candidate may aid further investigation, but reduce the rate of immediate answers. Correct localization, incorrect explanations, and deliberate withholding of judgment should therefore be measured separately rather than optimizing report-submission rate alone. This follows from the restricted answer structure; the reported pass rate does not resolve trade-offs among escalation policies.

**Prioritize the workflow and two failure cases.** The experiment makes the relationship between fast judgment and evidence engineering concrete. Inexpensive models can work within explicit boundaries, while complex incidents may require different collection granularity, a temporal view, and richer answer structures. Cross-service evidence that changes over time remains a future direction in the article.
