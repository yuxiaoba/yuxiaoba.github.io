---
id: metr-agent-monitoring
title: '2026-10-23 | METR Red Teaming: Monitoring Coverage Must Follow the Execution
  Chain'
date: '2026-10-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- observability
- coding-agents
summary: Separating eligibility, triggering, complete delivery, and response to understand
  compaction and asynchronous monitoring gaps.
long_read: true
source_url: https://metr.org/blog/2026-10-22-red-teaming-openai-agent-monitoring/
permalink: /tech/en/metr-agent-monitoring/
translation_source: assistant
authorship: assistant
published_at: '2026-10-23T08:58:47.180720+08:00'
updated_at: '2026-10-23T08:58:47.180720+08:00'
---
A monitor can recognize dangerous behavior only if it receives that behavior. METR and Redwood Research's examination of OpenAI's internal agent monitoring shifts attention from the classifier to the complete chain: which inference is in scope, what triggers inspection, how trajectories arrive, and who responds afterward. It provides a concrete engineering view of AgentOps reliability.

Original: [Red-Teaming OpenAI's Internal Agent Monitoring Systems](https://metr.org/blog/2026-10-22-red-teaming-openai-agent-monitoring/) · David Rein and Adam Kaufman / METR · 2026-10-22

## Deep access to a historical system

Two external researchers conducted a three-week onsite pilot from July 21 to August 11, accessing internal code, monitor prompts and configuration, documentation, and interviews with approximately twelve researchers and engineers. The output was a 61-page internal report; the public article is an agreed high-level summary. The assessment concerns the system as it existed on and before July 21, excluding expansions then underway.

That boundary governs interpretation. The report shows where real monitoring infrastructure can fail at handoffs, but cannot establish present-day coverage of all internal agents. OpenAI subsequently stated that all identified vulnerabilities affecting its production safeguards stack had been patched. METR did not reassess those fixes or subsequent coverage changes. Historical findings and current status remain separate claims.

## Eligibility is not completed inspection

The researchers estimate that roughly 75%–94% of internal agentic Responses API traffic from models at least as capable as GPT-5.5 was eligible for monitoring, with substantial uncertainty in both directions. Within the internal Codex-agent subset, estimated eligibility was 99.2%. The denominators differ; the latter cannot stand for all internal inference.

Eligibility means traffic is intended to reach a monitor. Trigger omissions, implementation bugs, load shedding, or errors can still intervene. Other internal research inference services are outside this volume estimate. The report also says RL training runs were not covered at the start of the exercise, although researchers were told that some rollouts had been monitored between March and June. Establishing the scope was itself a major part of the assessment.

An engineering accounting scheme can separate execution volume, eligible volume, triggered requests, complete trajectories delivered, and successful decisions followed by response. Accuracy at the final classification stage cannot recover executions lost earlier. This layered accounting makes failures and ownership easier to identify than a single coverage percentage.

## Compaction and end-of-turn triggering

The report estimates that missing compaction-event monitoring left on the order of 10% of eligible internal Codex traffic unmonitored between May and July. The precise fraction is uncertain because historical logging lacked the information needed to determine it. OpenAI had independently identified the issue before the pilot and fixed it during the exercise.

At the time, monitoring triggered when agents returned control to the user. If compaction did not trigger a check, continued tool use without ending the turn could indefinitely postpone inspection. This is an event-scheduling failure: individual actions continue, while the monitor waits for a boundary that need not arrive. Checking every specified number of messages or minutes is one proposed design direction; the interval must balance cost, delay, and the acceptable unreviewed window.

Service health therefore does not establish coverage. Information shown to the researchers suggested monitor errors below 0.2% of requests and no load shedding during one 24-hour period. Those figures describe requests within the relevant pipeline, not executions omitted before triggering.

## Representation and control permissions belong to the monitoring surface

Public findings also include a potential sandbox and automatic-review bypass, a vulnerability affecting visibility of recent actions, differences between agent-visible and monitor-visible serialization, and client-controllable paths around monitoring. Some details are redacted, and the report distinguishes verified behavior from possibilities not tested in practice. These findings should not all be described as observed production exploitation.

The transferable lesson concerns representation consistency. If tool results, history, compacted summaries, and monitor requests use different encoding or filtering rules, the same execution can acquire different meanings. Transmitting text alone is insufficient if roles, provenance, or order are lost. The report's positive observation that monitors saw the agents' full trajectories with a few minor exceptions does not eliminate those specific representation vulnerabilities.

## Requirements for the response loop

Recommendations include reconciling inference and monitoring logs, retaining searchable tamper-resistant records, assigning incident-response ownership, repeated red teaming, and isolating execution from monitoring control. Together they aim to prevent the inspected agent from easily changing when it is checked, which evidence is provided, or whether records remain.

The public article has no suitable explanatory figure, so this note follows triggering, delivery, and response in text. Useful operational questions are whether long-running agents have checks independent of turn completion, whether actions reconcile across compaction, and whether monitor failures block, retry, or silently permit execution. The summary cannot estimate the incidence of actual malicious behavior. It does establish why monitoring must be evaluated as distributed infrastructure, beyond a classifier's capability score.
## Why accounting units change the conclusion

Imagine a long task with several tool calls, a compaction event, and only one eventual return to the user. Counting final turns may yield one monitoring opportunity; counting inference requests produces a larger denominator; counting externally consequential actions defines yet another risk window. This illustrates metric design rather than adding measurements to the report. Coverage comparisons first need to establish whether they count requests, messages, trajectories, or actions.

The distinction affects response as well. An asynchronous monitor may correctly flag behavior only after the action has completed. Lower detection latency, constrained action authority, and durable evidence solve different problems: shortening the undiscovered window, limiting impact, and enabling investigation. The public report supplies no complete distribution from anomalous action to human response, so low request-error rates cannot establish timely containment.

Depth of external access and public transparency also differ. Access to code and configuration enabled findings difficult to identify from external behavior, while disclosure remained subject to prior agreements and redaction. Readers receive engineering failure categories and some quantitative evidence, not enough to reconstruct the entire implementation or independently validate every fix. Follow-up assessments would be more informative with explicit versions, traffic denominators, and post-remediation retesting.

