---
id: google-cost-per-task-routing
title: 2026年11月5日｜模型路由：先确认便宜路径真的省钱
date: '2026-11-05'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- coding-agents
- systems-reliability
summary: 50 道短任务的实验显示，输出上限不是思考预算，路由还会与上下文缓存发生冲突。
long_read: true
source_url: https://developers.googleblog.com/cost-per-task-using-cheap-classifiers-to-route-across-gemini-models-and-thinking-levels/
permalink: /tech/zh/google-cost-per-task-routing/
translation_source: assistant
authoring_source: assistant
published_at: '2026-11-05T08:55:14.344660+08:00'
updated_at: '2026-11-05T08:55:14.344660+08:00'
---

原文: [Cost per task: Using cheap classifiers to route across Gemini models and thinking levels](https://developers.googleblog.com/cost-per-task-using-cheap-classifiers-to-route-across-gemini-models-and-thinking-levels/)<br>
Sergio Villani · 2026-11-03

Google Developers 的实验用廉价分类器决定短任务是否需要多步推理，再选择 Gemini 模型与 thinking 档位。它最值得读的并非某个分类器胜出，而是两个容易漏掉的基线：便宜路径到底便宜多少，以及不加路由、只降低思考档位是否已经足够。

作者以 16 道开发题写规则，再加 34 道未见题，合计 50 道可自动判分的编码代理小任务。基于关键词和长度的固定启发式在开发题上为 93.8%，未见题降至 70.6%；Jev 在未见题上的难度标签一致率为 34/34，全集为 48/50。这是与手工难度标签的一致率，不是完整软件工程任务成功率。

第一轮把 maxOutputTokens 从 4096 降到 300，并未减少简单题的思考用量，却让 25 道难题中的七道失败。因此，即使路由判断正确，把简单题送给这样的“低上限”配置也不一定省钱。更强的无路由基线是 Flash 的 low thinking，已经答对全部 50 题。Flash-Lite 与该配置结合的 Jev 路由也全对，并在作者测量中降低成本和响应时间；应比较这两个方案，而不是只对比昂贵默认档位。

实验仅每种配置运行一次，题目短、难度人工标注，代码尚待开源审查，不能外推到长程 coding agent。文章也指出模型缓存相互独立：长上下文每轮切换模型，可能需要两份缓存或失去复用折扣。适合短日志解析的路由策略，未必适合带大型仓库上下文的连续工作。

可迁移的衡量单位是“成功完成任务的总成本”，包括分类、模型、重试与思考开销。先测试一个足够强的低成本固定配置，再评估路由是否真正增加收益，会比只比较每百万 token 单价更接近服务优化目标。
