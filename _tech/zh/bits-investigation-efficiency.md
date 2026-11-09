---
id: bits-investigation-efficiency
title: 2026年11月7日｜Bits Investigation：简化调查循环，把数据处理移到工具侧
date: '2026-11-07'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- observability
- agent-reliability
summary: Datadog 的调查 Agent 从多阶段编排转向 ReAct 与批量工具执行；成本、时间和质量指标仍需区分。
long_read: true
source_url: https://www.datadoghq.com/blog/bits-investigations-cost-speed-accuracy/
permalink: /tech/zh/bits-investigation-efficiency/
translation_source: assistant-authored paired Chinese/English notes
published_at: '2026-11-09T11:35:29.888596+08:00'
updated_at: '2026-11-09T11:35:29.888596+08:00'
---
**Datadog · Dan Green、Aurora Dai、Daniel Shan · 2026-11-02**  
原文：[Bits investigations are faster, more accurate, and cost less](https://www.datadoghq.com/blog/bits-investigations-cost-speed-accuracy/)

自动事故调查的成本不只在模型推理，也在调度、反复取数及把大量遥测送回上下文。Datadog 披露 Bits Investigation 从复杂多阶段 Agent 编排，转向更简单的 ReAct 循环，再把批量查询和关联处理移到工具执行侧的过程。这里最有用的是调查路径如何改变，而非把产品指标当作独立基准冠军。

## 从预先分工转向证据驱动循环

早期系统先收集相关上下文，再用目标遥测查询展开调查；Agent 生成与检验根因假设，并把有前景的分支进一步细化。这样的结构能形成证据链，但上下文检索、假设生成和测试各有专用阶段与工具，编排层较复杂。

后来采用的 ReAct 路径让每个 Agent 先根据已有证据判断，再选工具，根据返回结果决定下一步调查。新的信息可以直接改变行动，不必全部塞进预设阶段。官方报告这一代结合新模型与工具，把平均单次调查成本从初始约 25 美元降到约 6.50 美元；文章没有给出架构变化单独贡献多少的消融，因此不能说仅靠减少 Agent 就实现全部节省。

## 让代码处理数据，再把证据交给模型

最新路径通过 Datadog MCP Server 的代码执行，在单次工具调用中查询多个数据源、关联结果并汇总证据。若先把大量原始数据传给模型，再让模型逐次发起查询，工具往返和上下文都会膨胀；在工具侧先处理，模型更早获得用于判断的证据。

文章同时提到更新模型和改进路由，因此成本改善可能来自多个因素共同作用。它没有公开查询计划、执行限制、失败重试或根因决策的完整实现，无法据此还原一个可复现的系统。能迁移的是明确分工：模型决定接下来要验证什么，工具执行数据检索与关联，而非让所有原始遥测都经过文本上下文。

## 三个指标，以及尚未证明的部分

截至 2026 年 10 月，官方称平均单次成本约 4 美元、调查时间约两分钟，相比发布初期约 25 美元和十一分钟，分别减少 84% 和 82%。内部调查质量分数较 2026 年 3 月版本高 44%，评估方式是与历史事故的已知根因比较。44% 是评分相对变化，不是根因准确率提高 44 个百分点。

成本和时长是平均值；文章未披露足够的样本量、难度分布、尾延迟与质量评分细则，也没有证明人工修复、服务恢复或 MTTR 同比例改善。它提到面向 SRE 的 Scout 后训练与自动修复方向，但不能把未来自动修复算作本次已实现的结果。

这份工业更新值得 AIOps 关注，因为它给出复杂编排向简化循环、文本搬运向工具侧处理的实际演变。证据厚度支持理解机制与官方指标口径，尚不足以判断哪一个模型或路由策略在所有事故类型上更好。
