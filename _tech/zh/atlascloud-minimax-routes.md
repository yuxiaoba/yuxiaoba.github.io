---
id: atlascloud-minimax-routes
title: 2026年11月23日｜Atlas Cloud 按实际托管路径决定哪些 MiniMax 服务可继续运行
date: '2026-11-23'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: 同一模型可以自托管，也可以转交官方 API。Atlas 将停止转发、逐模型复测和客户通知分别落实到不同范围。
long_read: true
source_url: https://www.atlascloud.ai/blog/ai-updates/security-and-privacy-commitment
permalink: /tech/zh/atlascloud-minimax-routes/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
同一个 MiniMax 模型名，在 Atlas Cloud 上可能对应不同的数据处理方。Atlas 在安全公告中将能否继续提供模型的判断落在实际托管路径上。这解释了为什么它可以停用一条上游 API，同时保留部分同系列模型服务。

## 哪些请求出现了可观察的访问

据 Atlas 转述，研究者在测试提示词中放入私有链接，发现第三方打开了经 Atlas 送往 MiniMax 官方 API 的 M3 和 M2.7 提示词中的链接，涉及 2026 年第三季度及第四季度初。Atlas 称当时的证据把访问位置指向请求抵达 MiniMax 之后，并称自身没有存储这些请求的提示词或输出。对其他请求，公司给出的是可能暴露的判断，无法确认某个客户的具体内容是否被滥用。

## 切断一条路径后，哪些模型仍可用

Atlas 停止向 MiniMax 官方 API 发送请求。继续提供 MiniMax 模型有两种条件：由 Atlas 自行托管，或由托管方确认请求不会经过该 API。由此可见，模型目录显示的名字未必能回答数据去向问题。客户通知还把 M3.1 Flash 列入需要检查秘密信息的范围；公告中明确报告链接被访问的模型只有 M3 和 M2.7。

## 四次日测与逐模型重新上架

Atlas 称在核查期间主动将自己在 OpenRouter 上的所有模型撤下，并事先告知平台。它给出的恢复条件是每个模型分别通过测试。按公告说法，研究者目前每天四次测试 Atlas 所服务的模型。这个频率说明检查会重复进行，但采样到哪些路由、每次覆盖多少请求、静默读取能否被发现，都没有相应的覆盖率数据。其他模型当时未发现问题，仍被纳入检查。

Atlas Cloud · 2026-11-22 · [Security notice: MiniMax's official API and how we protect your data](https://www.atlascloud.ai/blog/ai-updates/security-and-privacy-commitment)
