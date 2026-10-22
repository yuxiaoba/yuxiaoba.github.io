---
id: scout-sre
title: '2026-10-15 | Scout: Post-Training for Evidence-Based SRE Investigations'
date: '2026-10-15'
lang: en
published: true
layout: article
maintenance: manual-research
source_type: tech
tags:
- agent-reliability
- observability
summary: From verifiable simulations to grounded rewards and evaluation boundaries for specialized SRE models.
long_read: true
source_url: https://www.datadoghq.com/blog/ai/introducing-scout-sre-specialized-model-bits-ai/
source_date: '2026-10-15'
permalink: /tech/en/scout-sre/
authorship: assistant
translation_source: assistant
published_at: '2026-10-22T08:54:49.993592+08:00'
updated_at: '2026-10-22T08:54:49.993592+08:00'
---
Datadog AI Research · 2026-10-15 · [Original article](https://www.datadoghq.com/blog/ai/introducing-scout-sre-specialized-model-bits-ai/)

Scout 1.0 treats SRE investigation as a capability to post-train, rather than just attaching query tools to a general model. Datadog reports improved quality versus estimated inference cost on its internal AlertEval benchmark. Its score measures agreement with reference explanations, not the percentage of incidents resolved. Inference cost also excludes the full cost of engineering and telemetry infrastructure.

<a class="note-image-link" href="/assets/images/tech/scout-sre/cost-quality.png" target="_blank" rel="noopener" aria-label="The original AlertEval quality–cost plot: score is not resolution rate; lower cost is to the right. · Open image"><img src="/assets/images/tech/scout-sre/cost-quality.png" alt="The original AlertEval quality–cost plot: score is not resolution rate; lower cost is to the right." loading="lazy"><span class="note-image-action">Open image ↗</span></a>

*The original AlertEval quality–cost plot: score is not resolution rate; lower cost is to the right.*

## The interesting part is task construction

The [technical report](https://web-assets.dd-static.net/42588/1792156398-datadog-scout-post_training_a_model_for_sre_investigations-v3.pdf) describes two GenSim paths: CausalGen runs applications with injected faults, while SynthTel generates telemetry directly. Both supply queryable evidence and known causes. Hybrid rewards combine correctness, exploration, and grounding; training also varies optional tools and interaction budgets. A separate SREGym evaluation uses 90 noise-free tasks with Stratus. Those end-to-end outcomes are not interchangeable with AlertEval scores.

This makes data quality a more concrete question than model size: is the case solvable, can the tools expose its evidence, and do resource names or injector messages reveal the answer? A simulator that executes successfully can still produce a poor learning task.

## Engineering interpretation: three validity checks

First check **mechanism validity**. An injection should change system behavior, not merely leave an identifying marker. Verify that the intended symptom appears, that its scope is plausible, and that reversing the intervention changes the symptom. For generated telemetry, test temporal and entity consistency across signals instead of relying on realistic-looking prose.

Next check **evidence accessibility**. Specify the observations needed to distinguish the cause and confirm that the permitted tools can retrieve them. Missing permissions, expired retention, or an inadequate query interface can make a task unsolvable. A low score under those conditions is not sufficient evidence of poor reasoning.

Finally check **answer isolation**. The evaluator may retain complete injection records; the investigator should receive only what would have been visible at the relevant time. Audit deployment identifiers, filenames, ticket annotations, and tool errors as well as the prompt itself.

## Measure investigation behavior alongside rewards

A transferable experiment would separately record whether the conclusion is correct and whether supporting evidence was actually retrieved. Outcome alone cannot distinguish a well-founded diagnosis from a lucky guess. Process scores alone can reward an elaborate investigation that never resolves the question.

Insufficient evidence must also be a legitimate result. Construct paired cases with similar symptoms: one exposes the decisive observation, while the other withholds it. The desired behavior is a supported conclusion in the first and calibrated uncertainty in the second, rather than identical confident answers.

Compare costs under the same cases, tool permissions, time budgets, and stopping rules. Include tool-query overhead as well as model calls. A cheaper model that requires substantially more telemetry queries may transfer costs to the platform rather than remove them.

## What should transfer beyond this deployment?

Test held-out failure mechanisms, held-out service topologies, and changed tool interfaces separately. These probe different dependencies: memorized fault patterns, environment assumptions, and adaptation to investigation conditions. A single aggregate score conceals those differences.

Chaos engineering contributes controlled causal changes and repeatable observations. More injections do not automatically produce a better benchmark; symptoms, accessible evidence, and reference causes must agree. Scout is interesting for bringing those concerns into a specialized training pipeline. Whether the resulting gains transfer remains a question for independent environments, not something a vendor-specific score establishes by itself.
