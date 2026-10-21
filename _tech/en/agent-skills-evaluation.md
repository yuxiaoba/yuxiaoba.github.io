---
id: agent-skills-evaluation
title: '2026-10-20 | Agent Skills: Does Following Instructions Actually Help?'
date: '2026-10-20'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_format: x-article
long_read: true
tags:
- coding-agents
- agent-reliability
- self-improvement
summary: Separate skill loading, instruction adherence, task outcomes, and added cost
  before interpreting a busier agent trace as greater capability.
source_url: https://x.com/sermakarevich/status/2112198653469241856
permalink: /tech/en/agent-skills-evaluation/
authoring_source: assistant
translation_source: assistant-authored paired Chinese/English interpretation
---

**Sergii Makarevych · Agent evaluation methodology · 2026-10-19**  
Original: [How to write and test agent skills with evals](https://x.com/i/article/2112186374052802560)

## Why an apparent improvement after installation is not enough

A Skill can make an agent read more documentation, write tests first, record plans, or use a particular toolset. The resulting trace may look more thorough, but whether those changes improve task quality is a separate question. If the outcome stays the same while context, tool calls, and waiting time increase, the observation is behavioral change rather than necessarily greater capability.

The article's useful distinction is between **following an instruction and obtaining a better outcome by following it**. The author proposes starting with a measurable objective, decomposing a Skill into behavioral hypotheses, measuring adherence and effect separately, and using controls and ablations to decide which rules to keep. The article synthesizes research and a test-first example; it does not obtain every cited conclusion from one unified experiment.

For evaluation design, a third question comes before both: was the Skill actually loaded? Failure to load, failure to follow, and failure to benefit lead to different diagnoses.

## Turn a long prompt into inspectable hypotheses

Consider an instruction to write a defect-reproducing test before changing production code. That sentence specifies an action order. A testable hypothesis also needs an expected benefit: does it expose the original defect, prevent a superficial repair, or reduce regressions?

An evaluation record can be organized into four layers:

| Layer | Question | Useful observations |
| --- | --- | --- |
| Loading | Did this execution actually receive the Skill? | Load events, version, and activation conditions |
| Adherence | Did the prescribed behavior occur? | File-edit order, commands, outputs, and exit codes |
| Effect | Did task quality improve? | Hidden checks, regressions, and artifact validity |
| Cost | What did the change require? | Model calls, context usage, elapsed time, and retries |

This organization supports diagnosis rather than merely scoring. If loading fails, inspect discovery and routing. If the action does not occur, inspect ambiguity or conflicting instructions. If the action occurs without better quality, reconsider the underlying method.

Avoid rewarding a proxy in place of its objective. More tests do not establish stronger defect detection; longer plans do not establish more reliable execution. For every metric, identify the real benefit expected to move with it. An unclear connection is a reason not to make that metric the headline result.

## Separate instruction content from extra context

The author recommends comparing no Skill, the target Skill, and unrelated text of equal length. This attempts to distinguish the contribution of specific instructions from the effects of adding context. If a package includes a session hook, also separate the complete installation from its body alone; loading policy and instruction quality otherwise become one aggregate score.

For a project evaluation, I would fix the model version, toolset, repository state, and task input first, then specify how each condition invokes the Skill. Two experiments should remain distinct: whether the content helps when loading is guaranteed, and whether a realistic installation routes suitable tasks to that content. Accidental non-loading should not contaminate the former, while forced activation should not conceal selection problems in the latter.

Equal-length unrelated text is not automatically an inert placebo. Its content, position, and length need to be recorded. A poor control could make the target Skill appear unusually effective. A stronger interpretation looks for agreement across task quality, observed behavior, length controls, and targeted rule ablations.

## Establish whether generated tests detect anything useful

For a testing Skill, the artifact that matters is a test's ability to distinguish correct from incorrect behavior, not the number of files produced. A test that always passes may lack an effective assertion or miss the task-relevant difference. Descriptive names and comments do not replace execution evidence.

One concrete approach is to run generated tests against the pre-fix code and a small set of task-relevant changes or faulty variants. Also use acceptance tests hidden from the agent, so the same generation process does not define the requirement, implement the solution, and grade itself.

Failure causes must remain separate. An import error, missing dependency, and assertion exposing the target defect can all produce nonzero exit codes. Counting all three as successful reproduction inflates apparent adherence without establishing defect detection.

Anthropic distinguishes tasks, individual trials, trajectories, outcomes, and graders in its agent evaluation discussion, and considers different roles for deterministic checks and model-based grading. This separation helps avoid treating a record of tool activity as evidence of task success. [Anthropic: agent evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

## Make retention a reasoned decision

The following table translates the reading into maintenance decisions; it is not the outcome of an experiment:

| Observation | First diagnostic question | Next step |
| --- | --- | --- |
| The Skill often is not loaded | Are discovery, routing, and activation working? | Repair selection and evaluate content separately |
| Loading succeeds but adherence is low | Are instructions ambiguous, conflicting, or infeasible? | Narrow the rule and inspect concrete traces |
| Adherence is high but quality is unchanged | Does the method fit this task and model? | Remove one rule in a controlled ablation |
| Quality improves at substantially higher cost | Is the benefit worth the overhead? | Compare shorter instructions and alternative procedures |
| Mean quality improves but some tasks regress | Are gains concentrated in one task family? | Restrict scope and report the failure distribution |

Evaluating many conditions is itself an engineering undertaking. For example, **20 tasks × 5 configurations × 3 trials = 300 executions** is an arithmetic statement about evaluation size, not an effectiveness result. A small initial sample can expose configuration mistakes before budget is spent on discriminating tasks and key contrasts. Repeatedly revising rules against the same tasks also means those tasks are no longer an untouched final check.

## Maintain the evidence with the Skill

The durable artifact is more than an instruction file. Preserve the intended objective, applicable tasks, inspectable behaviors, evaluation conditions, and known regressions. A model, tool, or dependency change may invalidate those conditions. Effectiveness for one version does not establish effectiveness for its successor.

As a direction in the field, the article usefully shifts attention from writing instructions that sound expert to establishing which instructions deserve a place in routine execution. However, correlation between adherence and quality does not establish causality by itself: task difficulty can influence both. Controlled comparisons and ablations are needed to separate them.

**Prioritize the worked example, the definitions of adherence and effect, and the comparison design.** For AgentOps, loading failures, execution deviations, ineffective methods, and cost regressions can form distinct failure categories. Keeping them separate makes it easier to decide whether to revise the prompt, repair routing, or avoid the Skill altogether.
