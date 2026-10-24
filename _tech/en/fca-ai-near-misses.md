---
id: fca-ai-near-misses
title: '2026-10-21 | AI Near Misses: Turning Blocked Errors into Reliability Evidence'
date: '2026-10-21'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://www.fca.org.uk/news/speeches/building-future-finance-age-ai
long_read: true
tags:
- agent-reliability
- observability
- systems-reliability
summary: The FCA's near-miss statement and practice examples focus attention on controls
  before AI actions, investigable records, and ongoing response capability.
authoring_source: assistant
translation_source: assistant
permalink: /tech/en/fca-ai-near-misses/
published_at: '2026-10-24T08:39:06.506729+08:00'
updated_at: '2026-10-24T08:39:06.506729+08:00'
---
If an AI proposes an incorrect operation but a permission check or human approval blocks it, does the absence of a loss mean there is no failure worth learning from? For agents that invoke tools and change business state, such an event can reveal two things together: an upstream decision defect and a downstream safeguard that worked this time. Counting only realized losses hides both.

**FCA · AI operational governance and engineering interpretation**  
Original: [Building the future of finance in the age of AI](https://www.fca.org.uk/news/speeches/building-future-finance-age-ai), Jessica Rusu, Bloomberg UK Policy Series, 2026-10-19. Companion publication: [AI in financial services: good practice and areas for improvement](https://www.fca.org.uk/publications/good-poor-practice/ai-financial-services), FCA, published 2026-10-19 and updated October 20.

## The signal: examine events before harm occurs

Rusu argues that major-incident reporting should encompass significant AI failures and near misses, and emphasizes ongoing assurance that responds to changing conditions for autonomous systems. The companion publication discusses interaction records, explicit escalation thresholds, and human intervention, while stating that its examples **create no new requirements**. These establish an operational direction, without a universal near-miss classifier, reporting threshold, or effectiveness benchmark. [Speech](https://www.fca.org.uk/news/speeches/building-future-finance-age-ai) · [Practice publication](https://www.fca.org.uk/publications/good-poor-practice/ai-financial-services)

The news lead, [UK finance watchdog wants firms to report AI failures and close calls](https://www.theregister.com/ai-and-ml/2026/10/20/uk-finance-watchdog-wants-firms-to-report-ai-failures-and-close-calls/5304078), was published by Lindsay Clark on 2026-10-20. The engineering question worth developing is what a system must retain to establish what an intervention means. The following analysis explores that question; it is not an implementation specification issued by the FCA.

## Separate an incorrect answer from an almost-executed error

Imagine a refund agent reading an amount as ten times its intended value, then calling a payment tool whose limit check rejects it. This is a hypothetical example. Looking only at the final tool status shows a rejection; looking only at the model output can obscure whether rejection actually prevented funds from leaving.

Investigation needs to connect at least four objects: the user's original intent, the agent's proposed action, the tool's executed action, and the final business state. Aligning them distinguishes an incorrect suggestion, a blocked unauthorized request, an operation that occurred and was subsequently remedied, and a normal rejection with no associated danger.

A near miss also involves a counterfactual: without a particular control, would material harm actually have occurred? A system can preserve evidence for that assessment, but should not let a model infer severity automatically from a narrative alone. Keeping uncertain cases pending assessment is more informative than forcing them into success or failure.

## Logs must explain how a safeguard worked

For the refund example, an investigable record could include a task identifier, authorization scope, model and prompt versions, proposed tool and parameters, triggered control rule, approval or rejection outcome, and final state of the business object. The purpose is to connect one action across components, beyond making each component's log longer.

Attempts and incidents also need separate treatment. Five retries of the same incorrect parameters need not represent five independent risks. But five attempts that progressively change tools or identities cannot simply be deduplicated. Event grouping should preserve the original sequence and its grouping rationale; otherwise cleaner statistics can erase the route around a safeguard.

More complete records generally support better investigation while increasing storage, access-control, and sensitive-data handling burdens. One possible design separates indexes from original payloads: routine statistics read necessary fields, while authorized investigations access detailed material. Retaining only summaries is cheaper but may remove the condition that determines whether an operation was authorized.

## Human approval must come with an ability to intervene

An approval button alone does not establish effective control. Investigation needs to establish what the reviewer saw, whether they could reject the action, whether execution preceded approval, and whether queued old work continued after rejection. Otherwise a human step may leave a confirmation marker without changing execution.

An engineering option is to place controls at explicit state transitions: verify authorization before execution, invalidate old permission when approval changes, and check business state afterward. This is a design option, not a requirement that every agent use one state machine. A tool generating internal drafts can justify different control costs from one directly changing account state, where stronger execution evidence is needed.

Controls also impose false-positive costs. Broad rejection rules can reduce erroneous executions while routing many valid requests to people and extending processing time. Evaluation should examine blocked dangerous actions, incorrectly rejected valid actions, and human queueing delays together to determine whether risk has merely moved elsewhere.

## Outcome metrics need meaningful denominators

More recorded near misses may indicate a worse model, wider monitoring coverage, growing traffic, or safeguards that detect more problems. A single incident-count curve cannot distinguish these explanations.

Group observations by business operation, model version, and authorization level, and examine incident counts alongside corresponding action attempts. Separately record whether a control fired, human intervention was needed, and business state actually changed. Tasks do not carry equal risk. Aggregation should preserve that difference so that numerous low-risk successes do not dilute a few high-impact failures.

Post-fix evaluation should return to the specific event. Does a prompt change prevent the original incorrect parameters? Does the problem recur under different wording? Does the safeguard still work under timeouts, retries, or concurrency? Such checks help identify which layer a repair affects, but one passing case does not establish lower overall risk.

Finally, an incident record needs explicit follow-through states. Detecting an anomaly, assessing impact, responding, and verifying a repair are distinct steps; assigning a ticket does not eliminate the risk. For an event that cannot currently be reproduced, a team can retain known triggers, evidence gaps, and a follow-up owner instead of deleting it from the statistics. When a model or tool version changes, this helps identify historical issues that need another check and responses that remain temporary measures.

## What the evidence supports

The FCA publication draws on industry engagement, supervisory work, and testing initiatives. It provides qualitative cases and observations, without a failure-rate reduction measured under standardized experimental conditions. It does not establish that a particular logging, approval, or backup-model design will necessarily work. [Scope and evidence](https://www.fca.org.uk/publications/good-poor-practice/ai-financial-services)

**Its value for agent reliability is making blocked errors available for analysis.** Start with the speech's discussion of autonomy and ongoing assurance, then the publication's monitoring, human-oversight, and operational-resilience sections. Useful follow-up would clarify what counts as a significant event and show complete evidence from detection through response to verified repair, beyond adding another incident form.
