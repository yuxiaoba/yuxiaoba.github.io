---
date: '2026-10-28'
published: true
layout: article
maintenance: daily-research
authoring_source: assistant
translation_source: assistant
id: agent-judgment
title: 2026年10月28日｜专家签字，是否仍代表独立判断？
lang: zh
source_type: tech
long_read: true
source_url: https://www.anthropic.com/research/agents-judgment-calls
tags:
- agent-reliability
summary: 随机改变 Agent 的建议倾向，观察专业分析师如何作出没有唯一标准答案的分析选择。
permalink: /tech/zh/agent-judgment/
published_at: '2026-10-28T15:24:19.938525+08:00'
updated_at: '2026-10-28T15:24:19.938525+08:00'
---
人工审核常被当作 Agent 的最后一道独立检查。但审核者可能在定义目标和选择分析方法时，就已经接受了 Agent 的偏好。Anthropic 这项研究考察的不是答案有没有明显错误，而是多种合理选项之间，最终是谁在作决定。

原文：[How AI agents shape experts’ judgment calls](https://www.anthropic.com/research/agents-judgment-calls) · Amaç Herdağdelen、Hailey Joren、Alex Tamkin · 2026-10-27。

### 随机的是 Agent 的立场

61 名通过因果推断知识筛选的专业分析师参与，50 名使用 Claude Code，11 名自行选择不用。任务是为虚构农业合作社评估咨询服务，涉及产出指标、比较方法、目标群体和权重四个开放选择，最后给出项目建议。

研究者为每个选择独立随机指定 Agent 的倾向，藏在系统提示中；Agent 要提出数据允许的有力理由，但不得歪曲结果，并应在反证足够强时改变态度。模型为 Claude Opus 4.8。这个设计用于估计随机建议倾向的平均影响，不是在比较随机分配的“用 AI”与“不用 AI”。

<a class="note-image-link" href="/assets/images/tech/agent-judgment/study-design.png" target="_blank" rel="noopener" aria-label="专家任务、随机 Agent 倾向与组间选择差异的实验设计 · 查看原图 ↗"><img src="/assets/images/tech/agent-judgment/study-design.png" alt="专家任务、随机 Agent 倾向与组间选择差异的实验设计" loading="lazy"><span class="note-image-action">查看原图 ↗</span></a>

*每项决策有两种可辩护选项；随机的是 Agent 的建议方向，再比较不同方向下专家选择的分布。*

### 判断发生在最后签字之前

四个分析选择合计，参与者与 Agent 倾向一致的比例为 86%。在 38 个参与者先表达偏好的情形中，Agent 反对时有 60% 改变选择，赞同时为 6%；样本较小，差值估计并不精确。最终是否扩展项目的直接倾向效应较弱，但前面的分析口径已经影响了估计结果。

事后调查中，77% 的分析师至少在一个理由中重复 Agent 的论据，只有 15% 在任一回答里归因给 Agent。这里是参与者层面的比例，不是全部句子的复述率。研究据此质疑一种简单验收：如果专家自称结果来自自己的判断，就视为独立审核已经完成。

不用 AI 的小组耗时更长、严重方法错误更多，但他们是自选分组，经验也不同，不能把差距当作 AI 导致改善的因果估计。主要随机实验也人为加强了 Agent 表达偏好的力度；单一任务、模型和领域限制了外推。

对 AgentOps 的启示是：技术正确性和判断独立性需要不同证据。在目标、指标、阈值存在合理分歧时，仅检查计算和代码无法看见偏好如何进入系统。让 Agent 展示两边理由、先记录专家判断，是作者提出的后续设计方向，尚不是此研究证明有效的解决方案。
