---
date: '2026-10-28'
published: false
layout: article
maintenance: daily-research
authoring_source: assistant
translation_source: assistant
id: agent-judgment
title: 2026-10-28 | Does expert sign-off still imply independent judgment?
lang: en
source_type: tech
long_read: true
source_url: https://www.anthropic.com/research/agents-judgment-calls
tags:
- agent-reliability
summary: Randomized agent preferences reveal how professional analysts make open-ended
  judgment calls.
permalink: /tech/en/agent-judgment/
published_at: '2026-10-28T15:24:19.938525+08:00'
updated_at: '2026-10-28T15:24:19.938525+08:00'
---
Human review is often treated as an independent final check on agents. Yet reviewers may already have adopted the agent’s preferences when choosing goals and analytical methods. Anthropic studies that influence where several answers are defensible.

Original: [How AI agents shape experts’ judgment calls](https://www.anthropic.com/research/agents-judgment-calls) · Amaç Herdağdelen, Hailey Joren, Alex Tamkin · 2026-10-27.

### Randomize the agent’s preference

Sixty-one screened professional analysts participated; 50 used Claude Code and 11 chose not to. A fictional farming-cooperative task required four analytical choices—outcome, comparison method, target population, and weighting—followed by a recommendation.

For each decision, hidden instructions randomly assigned the agent a preference. It had to argue honestly within the evidence and change its mind if warranted. The model was Claude Opus 4.8. Randomization estimates the average influence of these preferences; AI use itself was not randomly assigned.

<a class="note-image-link" href="/assets/images/tech/agent-judgment/study-design.png" target="_blank" rel="noopener" aria-label="Task choices, randomized agent preferences, and between-group comparisons · View original image ↗"><img src="/assets/images/tech/agent-judgment/study-design.png" alt="Task choices, randomized agent preferences, and between-group comparisons" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Each decision has defensible alternatives. The experiment randomizes the agent’s lean and compares analysts’ choices across those leans.*

### Influence precedes the final signature

Across the four analytical choices, participants matched the agent’s lean 86% of the time. In 38 cases where analysts expressed a preference first, they switched 60% of the time when the agent disagreed, versus 6% when it agreed; that small subset gives an imprecise estimate. Direct influence on the final recommendation was weaker, but earlier choices had already shaped the estimated effect.

In the post-task survey, 77% of analysts repeated an agent argument in at least one explanation, while 15% credited the agent anywhere. Those are participant-level proportions, not proportions of sentences. Self-reported ownership of a judgment may therefore be insufficient evidence of independent review.

Nonusers took longer and made more serious methodological errors, but self-selection and experience differences prevent a causal interpretation. The main experiment also deliberately strengthened agent preferences and covers one model, task, and domain.

For AgentOps, computational correctness and independent judgment require different evidence. Checking code cannot reveal how preferences entered a choice of metrics or thresholds. Presenting both sides or eliciting expert views first are proposed design directions, not interventions established effective by this study.
