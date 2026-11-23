---
id: openrouter-zdr-review
title: 2026年11月23日｜OpenRouter 撤销 125 个端点的零留存资格
date: '2026-11-23'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: 三家供应商退出与 125 个端点失去 ZDR 资格是两项处置。重新开放零留存路由，还要查明请求和响应经过谁。
long_read: true
source_url: https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/
permalink: /tech/zh/openrouter-zdr-review/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
客户选择零数据留存（ZDR）时，实际把一项决定交给了网关：在提供同一模型的多个端点中，哪些仍符合条件？OpenRouter 的事故说明给出了它在证据尚不完备时如何收紧这张名单的实例。

## 三家供应商和 125 个端点分别代表什么

OpenRouter 表示，研究者发现部分推理供应商的数据遭到泄露，或其实际行为与数据政策不符。调查后，平台下架了三家供应商，并撤销了 125 个端点的 ZDR 资格。后一个数字包含被研究者指出的端点，也包含出于预防而移除的端点。它统计的是路由选择发生变化的范围，无法据此计算泄露次数或受影响客户数。

## 一次 API 调用背后可能还有下一跳

即使客户只连接 OpenRouter，接单方仍可能把请求交给第三方，响应也会经过返回路径。OpenRouter 称，调查结果没有显示平台本身遭到未授权访问。对于零留存承诺，平台还需回答另一个问题：它把流量交给谁，对方又把流量交给了谁？平台正在对网络路径做技术核验，检查请求和响应是否被转发，同时把研究者的测试方法纳入持续检查。

## 恢复资格需要哪些证据

撤销资格可以立即收紧可选路由，重新纳入则需要相关保证和验证。公告没有公布检查频率、完整路径覆盖率或各端点的恢复结果。平台称已通知所有可能受影响的客户，包括供应商尚未公开发文的情形。文末列出的四份厂商说明因此只能用于了解各自事件，不能据此推断哪三家被平台下架。

OpenRouter · 2026-11-22 · [Data Processing Incidents on Inference Providers](https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/)
