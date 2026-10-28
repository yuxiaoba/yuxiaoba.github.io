---
date: '2026-10-28'
published: true
layout: article
maintenance: daily-research
authoring_source: assistant
translation_source: assistant
id: flashduty-rum-ai-sre
title: 2026年10月28日｜Flashduty RUM：把 AI 查询写入与用户撤销连起来
lang: zh
source_type: tech
long_read: true
source_url: https://docs.flashduty.com/en/changelog/changelog
tags:
- observability
- agent-reliability
summary: AI SRE 可修改查询条件、事件类型、时间范围与图表；停止、折叠和撤销各有不同语义。
permalink: /tech/zh/flashduty-rum-ai-sre/
published_at: '2026-10-28T15:24:19.938525+08:00'
updated_at: '2026-10-28T15:24:19.938525+08:00'
---
Flashduty 的 10 月 25 日更新给自然语言观测查询增加了具体的交互边界：有权限且启用 AI SRE 的用户，可以让它填写查询条件、事件类型、时间范围和分析图表，并直接执行。状态条反馈填写、查询、完成、无数据或失败；Undo 只在查询框仍保留 AI 写入内容时有效，避免覆盖用户后续修改。

原文：[Query and analyze in the RUM Explorer with AI SRE, a custom dashboard belongs to one application, errors split into Issues by where they were raised](https://docs.flashduty.com/en/changelog/changelog#rum-explorer-query-and-analyze-with-ai-sre) · Flashduty · 2026-10-25。

Stop 会结束当前轮次，Esc 或点击状态条只折叠对话，不取消正在运行的工作。没有 AI SRE 或额度耗尽时，同一入口保留“自然语言转 DQL、应用前预览”的基础模式。这些区别对 Agent 界面的可控性比一个聊天入口本身更有信息量。

同批更新还让 dashboard 绑定具体应用，并按错误发生位置细分 Issue；这些改变涉及查询范围和错误归组，不是新增 RCA 准确率证据。公告没有给出查询正确率或诊断收益，因此适合当作可回退交互设计的工程动态。
