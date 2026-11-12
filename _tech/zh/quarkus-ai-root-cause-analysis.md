---
date: '2026-11-12'
published: true
layout: article
maintenance: daily-research
translation_source: assistant
writing_source: assistant
id: quarkus-ai-root-cause-analysis
title: 2026年11月12日｜Quarkus AI RCA：先把遥测整理成可分析的上下文
lang: zh
source_type: tech
long_read: true
source_url: https://quarkus.io/blog/ai-root-cause-analysis/
tags:
- observability
- agent-reliability
summary: 经 MCP 关联 trace、日志与指标的实际流水线，以及上下文过滤与根因证据之间的取舍。
permalink: /tech/zh/quarkus-ai-root-cause-analysis/
published_at: '2026-11-12T08:58:59.941917+08:00'
updated_at: '2026-11-12T08:58:59.941917+08:00'
---
[AI Root Cause Analysis: LLM-Powered Root-Cause Analysis for Distributed Systems](https://quarkus.io/blog/ai-root-cause-analysis/)  
Ales Justin · 2026-11-10

分布式故障调查常在 Tempo、Loki 和 Prometheus 之间切换。Quarkus AI Root Cause Analysis 把这些操作串成应用：从近期 trace 出发，补充关联日志与同时间窗口指标，再让 LLM 输出结构化诊断。它是一项具体集成实践；原文没有给出根因准确率或大规模事故基准。

## 从 trace 开始建立关联

应用通过 MCP 查询 Tempo，找出错误、高延迟或异常形态的 trace，再从 Loki 取对应日志，并用 Prometheus 指标补充系统环境。最终报告包含原因、症状、严重度与修复建议。时间窗口和 trace/span 关联减少了模型面对互不相关遥测时的猜测空间，但关联本身不能证明因果方向。

文章用网关延迟、后端连接池告警和高堆占用举例说明输出可能如何组织。这个例子是说明情境，不是公开事故评测，不能把其中“数秒完成”与人工排查时间写成实测 MTTR 改善。

## 过滤器控制上下文，也决定什么证据会消失

StripMcpClient 在 MCP 与 LLM 之间按工具过滤字段。Trace 去掉 SDK 和 instrumentation 元数据，日志去掉重复信息，指标去掉静态值、部分内部指标、直方图桶及区域拆分。原文举出的指标条目从 586 减到约 35，约减少 94%。这说明输入体积变化，不等于诊断准确率提高 94%。

这种确定性整理能让重要信号更容易进入上下文，却可能删去某些故障需要的细粒度信息。区域性异常或尾延迟调查就可能依赖被过滤的维度。因而该实现最值得检查的是各工具过滤规则与所调查故障是否匹配，而不是只比较输入 token 数；这是由过滤机制带来的工程边界，原文未提供删减前后的诊断消融。

## 源码检查和 dashboard 是后续可选动作

若目标 Quarkus 应用运行在开发模式并启用 Dev MCP，可以让分析器读取源码，把遥测发现映射到具体位置，也能生成 Grafana dashboard 并写入应用源目录。没有这些连接时，核心遥测分析仍可使用，dashboard JSON 可以手动导入。两种模式的权限和输出位置不同，不应混为生产环境默认自动修改代码。

界面还报告耗时、LLM 调用数与输入输出 token，便于观察一轮调查的开销。当前文章重点是集成与使用路径，架构和混沌测试评估被放在后续文章。对 AIOps 的现实价值是展示如何把既有 LGTM 资产交给分析 Agent；是否稳定定位根因、能否区分相关性与因果性，仍需事故样本和干预证据。原文图片以操作界面为主，本笔记保留文字解释，不把 UI 截图当系统架构。
