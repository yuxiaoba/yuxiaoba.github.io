---
id: review-grafana-trace-linkage
title: 2026-11-04｜Trace linkage：具体 SQL 执行与查询上下文
date: '2026-11-04'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://grafana.com/blog/trace-linkage-connect-the-dots-between-your-app-traces-and-database-queries/
tags:
- agent-reliability
- self-improvement
- observability
- inference-serving
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-grafana-trace-linkage/
---

Grafana trace linkage 先用 sqlcommenter 的 trace/span ID 匹配具体 SQL 样本，未命中时按规范化查询文本等信息关联历史。后者提供同类 query 上下文，并非该次执行的确定记录。

Alloy 轮询可能漏掉短查询，精确匹配也尽力而为；SQL comment 对数据库缓存的影响需评估，相关不等于根因。

来源：[Trace linkage: connect the dots between your app traces and database queries](https://grafana.com/blog/trace-linkage-connect-the-dots-between-your-app-traces-and-database-queries/)

[Trace linkage: connect the dots between your app traces and database queries](https://grafana.com/blog/trace-linkage-connect-the-dots-between-your-app-traces-and-database-queries/)
