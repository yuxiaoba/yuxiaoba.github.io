---
id: sentry-agent-tracing-five-things
title: 2026年11月6日｜Sentry Agent Tracing：把生产轨迹变成评测与分诊输入
date: '2026-11-06'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- observability
- agent-reliability
summary: 围绕会话关联、真实数据导出、成功样本分诊和成本告警，解释五条工作流怎样连接起来。
permalink: /tech/zh/sentry-agent-tracing-five-things/
authorship: assistant
translation_source: assistant
editorial_status: source-checked
long_read: true
source_url: https://x.com/i/article/2118087303029510144
source_format: x-article
published_at: '2026-11-09T11:09:45.657368+08:00'
updated_at: '2026-11-09T11:09:45.657368+08:00'
---
Agent 的失败不一定表现为抛异常：工具调用失败后反复重试，最后仍返回流畅答案；或每步都执行成功，却在移交时丢失重要上下文。Sentry 这篇文章的实用之处，是把记录 trace 之后的工作继续往前推进：将会话交给评测、让自动分诊检查“成功”样本，并把成本变化关联到具体调用。

原文：[Five things you can do with Sentry’s Agent Tracing](https://x.com/i/article/2118087303029510144) · Sentry · 官方关联帖发表于 2026-11-05

## 先把多轮会话与请求内执行连在一起

一条用户会话可跨越多个 HTTP 请求，每个请求又包含模型调用、工具执行、数据库访问和其他应用 span。仅保留一段模型文本，无法判断慢的是模型供应商、数据库，还是 Agent 重复调用了工具。

官方 eval recipe 使用 `Sentry.setConversationId()` 将同一会话的 AI spans 标上相同 `gen_ai.conversation.id`，再为模型或 Agent 调用设置稳定名称。会话视图负责把多轮内容聚合起来，trace 负责沿本次请求继续向下追踪。两类标识解决的问题不同：相同会话并不意味着所有轮次共享一个 trace，也不能靠请求内 span 自动推断跨轮身份。

这个数据链条要求采集到必要输入和输出。recipe 使用启用 tracing 的 SDK 与 Vercel AI SDK 集成；若特定路线不记录输入输出，就无法从那里恢复完整的文本评测样本。采样、脱敏和缺失字段因此会改变后续数据集覆盖，而非只影响 dashboard 好不好看。

## 生产会话导出为 eval：观测值不是正确答案

第一条工作流通过 CLI 导出完整会话，把第一条用户消息作为输入、最后一次 Agent 回复作为输出，保留成本、token 和工具错误等元数据，再送进 Braintrust、Langfuse、promptfoo 或 Phoenix。它减少的是手工搬运真实案例的成本，不是自动获得正确标签。

对能形式化判断的要求，recipe 建议使用代码检查；其余部分可以交给模型 judge。原回复只是被评估对象，不能因为来自生产就作为 ground truth。多轮任务压成“首问—末答”时还可能丢掉中途新增约束；如果评测目标涉及工具副作用或交互过程，就应保留相关轨迹作为判据，不能只检查最后一句是否通顺。

[官方导出 recipe](https://sentry.io/cookbook/agent-conversations-to-evals/)明确了会话 ID 与 SDK 前提。最适合这条路径的是把真实出现的失败、昂贵循环或边界请求变成持续回归案例，再根据可检查的需求标注结果。

## 每日分诊为何还要读成功会话

第二条工作流让定时运行的助手通过 Sentry MCP 拉取最近 24 小时的聚合统计，同时抽取失败与成功会话细读。它寻找坏工具、循环、异常成本和理由不支持结论的情况；发现新问题后先查工单系统，再创建缺失工单。

这与只对异常堆栈生成摘要不同。成功请求中仍可能有被重试掩盖的工具故障，或答案看似正确、轨迹却不支持它。[官方分诊 recipe](https://sentry.io/cookbook/automate-ai-agent-triage-claude-routines/)把 MCP 数据读取、助手判断和工单去重连接成操作流程。文章给出的是 recipe 和提示设计，没有报告分诊准确率、漏报率或节省多少人时，不能把“可以自动运行”升级为“已可靠发现所有语义错误”。

## 成本观测和告警走的是同一条 span 链

另外两条工作流分别处理单调用成本归因与支出告警。使用 Next.js / Vercel AI SDK 集成后，可在模型、会话、调用维度查看估算成本，再回到 trace 找慢工具和重复步骤。支出 dashboard recipe 生成八个 widget，并设置两个每小时告警：一个跨越自定阈值，一个偏离历史正常范围。

Sentry 根据 token 计数估算费用，应用无需自行发送美元金额。由此获得的是诊断线索，不是必然与供应商账单完全一致的结算数；缺失用量、采样和定价处理都会影响估算。异常告警也只说明成本分布变化，无法单独区分流量增长、模型切换、缓存变化和失控循环，需要结合会话与工具轨迹继续排查。

## 已有 OTel 时，新增出口而非重做链路

第五条 recipe 针对已使用 OpenTelemetry 的 Vercel 应用，将 Sentry 加为额外接收端，让标准 gen_ai span 与原有应用、数据库和其他请求 span 一起出现。它的工程吸引力是复用已有采集路径，再在 Agent 视图解释模型与工具行为；同一机制可延伸至其他兼容运行环境。

这五条工作流形成了“关联—导出—评估—分诊—告警”的连接，但文章没有给出新的 trace 协议或受控性能实验。其价值是明确产品能力如何成为日常 AgentOps 的输入，边界则是关联数据不自动带来因果解释，模型分诊也不自动变成可靠判定。生产轨迹只有连到任务要求、工具效果和人工确认，才能沉淀为可长期复用的评测证据。
