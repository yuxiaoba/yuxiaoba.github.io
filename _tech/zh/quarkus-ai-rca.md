---
date: '2026-11-18'
published: true
layout: article
maintenance: daily-research
translation_source: assistant-authored Chinese and English; not user-supplied translations
id: quarkus-ai-rca
title: 2026年11月18日｜Quarkus AI RCA：从遥测关联到可重复故障评测
lang: zh
source_type: tech
tags:
- observability
- systems-reliability
- agent-reliability
summary: Quarkus 的 AI Root Cause Analysis 深入文章把自动排障拆成两个可检查的部分：模型怎样取得 trace、log、metric，以及团队怎样判断分析是否真的对应已知故障。它的价值来自具体工具接口、上下文过滤和混沌测试流程，而非一个泛称“AI
  能做 RCA”的演示。
long_read: true
source_url: https://quarkus.io/blog/ai-root-cause-analysis-deep-dive/
permalink: /tech/zh/quarkus-ai-rca/
published_at: '2026-11-18T08:55:23.659995+08:00'
updated_at: '2026-11-18T08:55:23.659995+08:00'
---
[AI Root Cause Analysis: Architecture, Testing, and Evaluation](https://quarkus.io/blog/ai-root-cause-analysis-deep-dive/)  
Ales Justin · 2026-11-17

Quarkus 的 AI Root Cause Analysis 深入文章把自动排障拆成两个可检查的部分：模型怎样取得 trace、log、metric，以及团队怎样判断分析是否真的对应已知故障。它的价值来自具体工具接口、上下文过滤和混沌测试流程，而非一个泛称“AI 能做 RCA”的演示。

## 从 trace 出发，而非把所有遥测一次塞进提示

系统通过 MCP 连接 LGTM 栈，应用侧已有 OpenTelemetry instrumentation 是前提。LangChain4j 的 AI service 加系统提示指导模型做三路关联、严重性分类和结构化输出。模型可用五类工具：取最近 N 个 trace ID、按 ID 读取 trace、查关联日志、取根 span 起始时间、查询该时刻指标。

用户调用分析入口后，模型自行决定哪些 trace 值得继续调查，逐个拉取 span 和日志，再用根 span 时间查询 Prometheus，最后汇总根因、最慢操作、错误模式和跨 trace 关系。时间关联使查询范围可控，但一个时刻的指标快照不等于覆盖整个故障过程。原文特别指出，瞬态压力可能只留在日志中，指标未出现同样尖峰不构成直接反证。

可选的源码检查与 dashboard 生成由另一个 Dev MCP service 在分析后执行。它与遥测分析分开，避免把“已查询到观测数据”混成“已经理解所有代码”。不过这些工具提供的是模型调查能力，并不自动让推断具备因果证明。

## 过滤怎样节省上下文，也怎样影响判断

StripMcpClient 在工具返回处按类型清理数据：trace 去 SDK 和本机属性，日志去冗余字段，metric 去 Netty 内部项、静态值、直方图桶及区域细分。文章例子把 586 个 metric 条目压到约 35 个。过滤发生在进入模型前，因此模型后续解释只能基于保留内容。

这是一种有取舍的工程压缩。去掉重复描述可以降低输入负担，但移除直方图桶也意味着某些尾部信息不再直接可见。原文提示把混沌日志当作强证据，有利于识别注入故障，却也让测试环境比没有显式故障标记的生产环境更容易。对 RCA 质量的判断，需要把遥测准备和推理效果放在一起看。

## 用已知故障构造可评分的调查

伴随应用提供 11 类混沌模式，包括延迟、CPU 消耗、内存分配或泄漏、异常、线程池阻塞、锁竞争、GC 压力、间歇错误和死锁。网络依赖则经过 Toxiproxy：数据库测试注入 3 秒延迟、以 4 秒延迟配合小连接池制造耗尽，或者直接切断连接；外部天气 API 也有延迟和中断场景。

测试不是只问模型“有没有报错”。每次先注入故障，等待遥测到达，运行分析，保存模型实际看到的工具输出，再调用独立 judge。评分输入同时包含原始遥测、分析提示、分析结果和场景专属标准。已知注入提供参考，保存工具输出则让“结论是否有依据”可以回到同一份输入检查。

## 通过矩阵意味着什么

judge 从完整性、根因准确性、三路关联质量和建议可执行性四个维度各给 0–25 分，默认总分至少 70 才通过。分析模型与评分模型可以跨 OpenAI/Grok 组合，官方报告 19 个场景在四种组合均通过，分别包含 12 个混沌/基线、4 个数据库和 3 个天气场景。

这支持测试流程可运行，也表明结果不只依赖一个模型给自己打分。但跨供应商不等于消除共同偏差，70 分通过不等于生产根因准确率 70%，19 个场景全过也不是未知故障全部可解。文章没有现场 MTTR 或大规模事故统计。更可靠的阅读结论是：它给出一个能够反复回归的 RCA 工程框架，尤其适合比较提示、过滤器和模型改动是否破坏已知故障的分析，而不是宣告自治排障已经完成。
