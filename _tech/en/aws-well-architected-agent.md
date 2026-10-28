---
id: aws-well-architected-agent
title: '2026-10-20 | AWS Well-Architected Agent: from findings to reviewable changes'
date: '2026-10-20'
lang: en
published: false
editorial_status: withdrawn
editorial_review_date: "2026-10-27"
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- systems-reliability
summary: The preview connects resource scanning, business goals, and IaC reviews.
  Recommendation cadence, access boundaries, and pre-deployment validation determine
  its practical value.
long_read: true
source_url: https://aws.amazon.com/about-aws/whats-new/2026/10/aws-well-architected-agent/
permalink: /tech/en/aws-well-architected-agent/
authorship: assistant
translation_source: assistant-authored bilingual analysis and translation
published_at: '2026-10-23T12:22:02.560508+08:00'
updated_at: "2026-10-27T13:54:34.510124+08:00"
---
Cloud optimization often stops at a list of findings: oversized resources, a database without failover, or configurations that diverge from best practices. Teams then spend time deciding what to change first, what else a change affects, and how to turn advice into reviewable code. The AWS Well-Architected Agent preview connects business goals, resource and application context, and infrastructure-as-code (IaC) reviews into a recommendation workflow. The interesting question is how that workflow is constructed, rather than whether the word “agent” implies independent control of production changes.

Original: [AWS Well-Architected Agent is now available in preview](https://aws.amazon.com/about-aws/whats-new/2026/10/aws-well-architected-agent/)  
AWS · 2026-10-01

## Recommendations need a defined optimization target

The [service overview](https://docs.aws.amazon.com/wellarchitected/latest/userguide/agent.html) describes four optimization pillars: cost, security, resilience, and performance. Users define an agent profile and receive resource-, application-, or architecture-level recommendations. The service incorporates findings from existing optimization services and prioritizes them against business goals. Public material does not describe a new underlying reasoning algorithm or provide a remediation-success benchmark.

From an engineering perspective, the goal statement is part of input quality. Cost reduction and greater reliability can produce different rankings. A critical system that cannot tolerate downtime should not use the same constraints as a disposable test environment. An underspecified goal can yield advice that follows general best practices while violating local maintenance windows or recovery requirements.

The [concept documentation](https://docs.aws.amazon.com/wellarchitected/latest/userguide/agent-concepts.html) separates account and region scope, business goals, and application context. Application information can add criticality, architectural descriptions, and discovery tags. This exposes a useful design trade-off: discovery can inspect configuration without knowing the business role of every component. Teams still supply that meaning and scope.

## Distinguish discovery access from change authority

The [getting-started guide](https://docs.aws.amazon.com/wellarchitected/latest/userguide/agent-getting-started.html) explains that an execution role orchestrates scanning through access roles in workload accounts. Automatically created scanning roles are read-only. Creating a profile does not grant arbitrary modification rights. A script or IaC change in a recommendation makes it an executable candidate; deployment remains a subsequent decision.

Missing permissions also change the meaning of results. An application without findings may have an access-role, organizational-policy, or scope problem, rather than an absence of risk. Such systems need to distinguish covered resources, uncovered resources, and unreadable resources. Otherwise a shorter recommendation list can look healthier merely because less infrastructure was visible.

Cost inputs also need interpretation. Without Cost Explorer, the guide says costs are estimated using public prices. Environments with discounts or committed usage must still reconcile suggested savings with actual billing. The point is to identify the data supporting a recommendation's priority, not to dismiss optimization advice.

## Runtime resources and pre-deployment templates follow different paths

Resource and application recommendations refresh on a schedule; the service overview specifies a weekly cadence. Architecture reviews instead process submitted IaC projects on demand. The [architecture-review documentation](https://docs.aws.amazon.com/wellarchitected/latest/userguide/agent-architecture-reviews.html) describes S3 input, selected review pillars, and returned changes in the source template's language. On-demand generation supports only architecture recommendations; it cannot be used to force an immediate resource or application refresh.

That distinction determines use cases. Periodic scans can organize technical debt and configuration improvements, but are not second-level incident detection. Template review can expose some design gaps before deployment, yet sees the submitted material rather than necessarily observing manual runtime changes, external dependencies, or actual load behavior.

Consider a hypothetical engineering example: adding a database replica may improve availability under some failures while increasing cost and imposing replication or failover requirements on the application. Reviewing only whether the template deploys is insufficient. Connection handling, recovery steps, and observable outcomes also need examination. This is analysis of the execution workflow, not an AWS measurement from a real deployment.

## Quotas shape the review workflow

The [quota documentation](https://docs.aws.amazon.com/wellarchitected/latest/userguide/agent-quotas.html) lists default limits of 100 accounts and 10 goals per profile, 5 architecture reviews per day, and up to 30 recommendations per generation. That last limit is a particularly clear reason not to interpret one output list as a complete inventory of environmental problems.

Inputs are bounded too: a compressed archive may be at most 25 MB; an S3 folder may total 100 MB, with no individual file above 1 MB. Large repositories need review boundaries that preserve dependencies across modules. Splitting too narrowly can remove architectural context, while bundling too much can exceed limits. An entire repository is not unlimited context.

Profiles are hosted in US East (N. Virginia), US East (Ohio), or US West (Oregon), and can scan commercial-region resources. Current guidance further restricts eligibility to Business+ or higher support plans; the announcement's broader wording about having a support plan is insufficient to determine account eligibility. Application-level recommendations remain beta, and the overall service remains in preview.

## Bring candidates into the existing release process

Returned template code still needs an engineering workflow: identify the input version, review the diff, validate dependencies, and choose deployment and rollback procedures. If the live environment has drifted from its template, an apparently correct patch can overwrite undocumented configuration. Review outcomes should therefore remain bound to their inputs rather than becoming conclusions valid for every future version.

Application recommendations also need cross-resource counterexamples. A change that saves instance cost might move pressure into the database or network. Lower local expenditure does not establish lower total system cost. Check the target and adjacent bottlenecks over an appropriate business cycle, rather than only inspecting metrics immediately after the change.

This creates more concrete evaluation stages: a recommendation is accepted, successfully deployed, achieves its goal, and avoids related regressions. Record these separately to determine whether the agent saves drafting time, deployment time, or eventual operational cost.

## How to judge its usefulness

The public material establishes workflow and capability boundaries, but not accuracy, omission rates, or long-term savings against human review. A more useful evaluation unit is one recommendation: which visible configuration supports it, why it matches the goal, which resources it changes, what cross-component validation it needs, and what evidence will establish its effect after implementation.

This update advances the connection from findings to candidate changes. For reliability teams, the potential value is less manual context gathering, prioritization, and first-draft preparation, while final changes remain traceable to goals and evidence. Start with scanning scope and architecture-review behavior, then examine whether the organization's change process can handle those candidates. That is more informative than simply counting generated recommendations.
