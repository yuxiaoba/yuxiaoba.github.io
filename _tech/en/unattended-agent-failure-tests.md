---
id: unattended-agent-failure-tests
title: '2026-10-20 | Unattended Agents: Seven Failure Scenarios to Validate Before
  Release'
date: '2026-10-20'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_format: x-article
long_read: true
tags:
- agent-reliability
- systems-reliability
- observability
summary: A practical reading of tool failures, approval changes, crash recovery, and
  the external evidence needed to validate agent execution boundaries.
source_url: https://x.com/themahis/status/2112235354585497922
permalink: /tech/en/unattended-agent-failure-tests/
authoring_source: assistant
translation_source: assistant-authored paired Chinese/English interpretation
---

**MASA · AgentOps practice guide · 2026-10-19**  
Original: [Before You Let Your AI Agent Run Unattended, Make It Pass These 7 Tests](https://x.com/i/article/2112230476458930176)

## From task completion to controlled failure

A successful demonstration usually shows which path an agent can complete. Unattended execution raises different questions: will an unavailable service trigger unlimited retries, what happens when an approved action changes, and will recovery repeat an external action that succeeded before local state was lost? The final answer alone cannot resolve these questions. Execution and external state both matter.

MASA organizes seven categories of failure and boundary tests around an agent that researches sources, produces a report, and requests permission to email it. This is a practical testing proposal rather than an experiment reporting pass rates. Its useful shift is in the unit of evaluation: from the model's answer to a running system comprising tools, authorization, persistent state, and external effects.

The following systems interpretation turns those concerns into a validation workflow. The important questions are who can prevent an action, where failure remains recorded, and which observations establish that a constraint was enforced.

## Seven scenarios and their evidence

| Scenario | Controlled intervention | Decisive external evidence |
| --- | --- | --- |
| Tool failure | Error responses, timeouts, or temporary unavailability | Request counts, spacing, and terminal status |
| Insufficient budget | A resource allowance too small for every planned step | Actual calls, reserved allowance, and rejections |
| Instructions in external content | An unauthorized request embedded in source material | Blocked actions and mock-endpoint records |
| Permission violation | Different tools attempting the same restricted access | Actual rejection by tools or infrastructure |
| Changes after approval | A changed recipient, attachment, or validity period | Correspondence between approved and executed payloads |
| Crash and recovery | Interruption after an external action but before local bookkeeping | Receiving-service state and logical operation identifiers |
| Stopping execution | A stop request during queued or active work | Stop timing, in-flight work, and subsequent actions |

The distinction is between behavior that sounds correct and controls that actually took effect. An agent saying it sent no email does not establish that no email arrived. A recovery log does not establish that recovery avoided duplication. Prefer evidence from the component that can observe the consequential result.

## Make the fault reproducible first

A test environment need not begin with a real mailbox and paid services. A controllable retrieval endpoint, a simulated sending service that records requests, and an execution trace can expose many problems. Specify the initial state, injection point, allowed outcomes, and forbidden outcomes before each case. Compare both the report and environment state afterward.

Even a retrieval failure needs more than one case. Temporary unavailability and invalid credentials call for different responses: bounded retry may make sense for the former, while the latter normally requires ending that access path or waiting for authorization. Testing just one error can reward an agent that keeps switching tools until it gets around a boundary.

AWS's discussion of remote calls explains that a timeout does not establish the absence of side effects, while retries can amplify load on a failing dependency. Backoff, jitter, and retry limits need to be considered together. [AWS Builders’ Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

For an agent, validation must also cross the planning layer. After a tool exhausts its retries, a model may replan and initiate another call for the same operation. An SDK counter therefore captures only part of the behavior. The useful unit is the complete logical operation, not one function invocation.

## Connect authorization, execution, and recovery with one operation identity

Consider an illustrative sequence: a user approves a report, a sending service accepts it, and the executor crashes. After restart, the queue still contains a send-report item. The dangerous inference is that an absent local success record means the action should simply be repeated.

A better design question is whether the approval, execution request, and receiving-service result identify the same logical operation. Organize the evidence around this sequence:

```text
Fix the action payload → Record approval → Assign an operation ID
→ Execute the request → Check the external result → Record completion
```

This is an evidence-organizing sequence, not a proposed new architecture. It lets a test ask whether changing the attachment invalidates approval, whether a restart recognizes the existing operation, and whether uncertain outcomes trigger a check of external state.

An idempotency key is one useful mechanism, but generating a key does not establish global exactly-once behavior. Stripe, for example, documents result storage, parameter comparison, and the retention scope of its keys. Those are service-specific contracts, not guarantees that automatically extend to email, storage, or deployment interfaces. [Stripe: idempotent requests](https://docs.stripe.com/api/idempotent_requests)

Where the receiving service lacks idempotency support, test the pause-and-reconcile path for uncertain outcomes. An explicit unresolved state is more useful than a fluent model explanation substituted for an external fact.

## Follow the stop signal beyond the current conversation

Ending a conversation establishes that an interaction ended. Runtime control also concerns waiting requests, executors that already claimed jobs, and operations already dispatched to external services. A timeline is helpful: record when the stop request arrived, when the stopped state became effective, when each operation was dispatched, and when external confirmation occurred.

Schedule delayed mock operations and stop the workflow at different points. The desired result is not that every action disappears. Distinguish completed actions, in-flight effects that cannot be recalled, and new actions that should have been prevented. Observe another restart to detect stop state held only in process memory.

This connects directly to chaos engineering: deliberately change timing and failure conditions to validate an explicit runtime constraint. Keep a normal-execution control as well. A system that refuses every action produces few side effects, but has not demonstrated that it can perform useful work.

## Build a regression collection that remains informative

I would prioritize traces that identify responsibility boundaries over collapsing all seven categories into a single score. For each failure, identify the enforcing component, the state that diverged, and the external outcome that violated expectations. Recheck alternate access paths after changing permissions, and critical crash windows after changing recovery. That is more informative than mechanically repeating a normal task.

Agent trajectories vary. A single pass establishes only that a particular execution did not expose a problem. Anthropic's evaluation guidance discusses repeated trials and examining trajectories alongside outcomes. These practices also help fault experiments, but a small number of repetitions cannot establish a very low production failure rate. [Anthropic: agent evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

**The useful contribution is making unattended operation concrete through observable, preventable, and recoverable behavior.** For AgentOps research, the next questions are which faults cross component boundaries, whether available evidence distinguishes their causes, and whether a repair improves one trajectory at the expense of another valid path.
