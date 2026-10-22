---
id: building-ai-sre
title: '2026-10-12 | Building an AI SRE: The Engineering Beyond an Answer'
date: '2026-10-12'
lang: en
published: true
layout: article
maintenance: manual-research
source_type: tech
tags:
- agent-reliability
- observability
summary: How backtesting, findings, notifications, and memory maintenance shape trust in incident investigation.
long_read: true
source_url: https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre
source_date: '2026-10-01'
permalink: /tech/en/building-ai-sre/
authorship: assistant
translation_source: assistant
published_at: '2026-10-22T08:54:49.993592+08:00'
updated_at: '2026-10-22T08:54:49.993592+08:00'
---
Martha Lambert · incident.io · 2026-10-01 · [Original article](https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre)

incident.io describes substantial work around the model: historical backtesting, evidence-backed findings, decisions about when to notify responders, and knowledge maintenance as environments change. Investigations combine sources, form hypotheses, and try to challenge them. This is a team's engineering account, not a benchmark whose outcomes transfer automatically to every organization.

<a class="note-image-link" href="/assets/images/tech/building-ai-sre/evaluation.svg" target="_blank" rel="noopener" aria-label="Original backtesting illustration: fixed incident inputs for two versions; the pictured scores are illustrative, not measured gains. · Open image"><img src="/assets/images/tech/building-ai-sre/evaluation.svg" alt="Original backtesting illustration: fixed incident inputs for two versions; the pictured scores are illustrative, not measured gains." loading="lazy"><span class="note-image-action">Open image ↗</span></a>

*Original backtesting illustration: fixed incident inputs for two versions; the pictured scores are illustrative, not measured gains.*

## Maintain investigation state, not just an answer

A useful interpretation is that incident investigation continually revises explanations as observations arrive. Long summaries create two risks: substantially different wording without new evidence, and outdated hypotheses that continue to anchor later reasoning.

An engineering design could represent each finding with an entity, time range, observation, inference, reference, and status. Observations are directly supported by data; inferences connect them into explanations. New evidence should be able to weaken, retract, or replace an inference instead of merely appending another paragraph.

This also helps responders inspect what changed without rereading the whole investigation. Structured state supports human handoff as well as model reasoning.

## Backtesting asks what was knowable then

The most dangerous contamination may be information that is correct but arrived too late. Consider an illustrative case where the code revision is frozen before the incident but retrieval returns a later fix description. The model appears to diagnose accurately while reading the answer.

Record event time, ingestion time, and visibility time for each evidence class. Replay should reproduce permissions and delivery delays, not simply apply one timestamp filter. Reference labels belong in a separate channel that cannot leak through indexes, document links, or tool output.

Hold out services, fault mechanisms, and time periods separately. This tests more than a small random sample of familiar incidents. Improvement confined to known services should be treated as a local result rather than organization-wide generalization.

## Notification is a separate capability

A correct diagnosis does not necessarily justify a message immediately. Redundant, late, or uninformative updates consume responder attention. Investigation quality and notification quality should therefore be evaluated separately.

A testable notification policy could ask whether evidence is new, whether it changes the hypothesis, whether it affects the next action, and whether a responder has already supplied the same information. The goal is not to hide uncertainty, but to communicate changes and confidence briefly while keeping complete evidence accessible.

Evaluate subsequent action changes, duplication, and human corrections rather than message count alone. A more active bot is not necessarily a more useful one.

## Give memory an invalidation mechanism

Remembering successful queries can lower the cost of future investigations. Service renames, schema migrations, and permission changes can also invalidate those memories. Store their scope, source version, and last validation time, and check those assumptions before reuse.

The practical value of this account is a set of questions for an AI SRE prototype: can it explain how a judgment formed, retract an incorrect hypothesis, detect stale knowledge, and hand an investigation back to a person? Each can become an explicit test. None needs to wait for a major production outage to reveal a missing capability.
