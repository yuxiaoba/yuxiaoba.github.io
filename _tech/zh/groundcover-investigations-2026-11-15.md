---
id: groundcover-investigations-2026-11-15
title: 2026年11月21日｜事故调查如何保留已被推翻的假设
date: '2026-11-21'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- observability
- multi-agent
summary: groundcover 的第一个内部原型让编码智能体针对真实事故分派子任务。
translation_source: assistant
writing_source: assistant
long_read: true
source_url: https://www.groundcover.com/blog/introducing-groundcover-investigations
permalink: /tech/zh/groundcover-investigations-2026-11-15/
published_at: '2026-11-21T08:47:17.687323+08:00'
updated_at: '2026-11-21T08:47:17.687323+08:00'
---
groundcover 的第一个内部原型让编码智能体针对真实事故分派子任务。它给出了答案，许多中间查证却留在各自的会话里。下一个值班工程师很难分清“已经检查并排除数据库”和“有人提过数据库但尚未查证”。Investigations 因此把调查对象从一串对话改成可共享的假设及其证据。

Anais Dotis · 2026-11-15 · [Introducing groundcover Investigations – collaboration ground for your agents and engineers](https://www.groundcover.com/blog/introducing-groundcover-investigations)

## 查询结果要归属到具体假设

一个问题可以分出多个假设，调查者查询遥测并把发现记在对应分支，还可以把复杂分支拆成子调查。结论保留支持或反驳它的查询和结果。在工程师接手时，已经排除的路径仍可检查，未处理的分支也保留开放状态。这一表示方式直接影响下一次工具调用：另一名调查者可以查看已有证据是否适用于当前时间窗口，然后再决定是否重查。

## 提议关闭与批准关闭是两个动作

Investigator 提出假设和判断，Moderator 检查发现能否支持这项判断。只有后者能把问题标为已解决，没有发现支撑的“已定位”不能完成状态转移。外部编码智能体通过 MCP 加入时遵循同一规则，每条贡献记录来自谁的会话及其时间。这个约束提供了可审计的交接点；判断者本身也是模型，引用了一条查询并不保证它选对了对照时间或服务实例。

## Slack 保留进度，调查树保留细节

团队尝试把所有发现送进事故线程，发现几十条中间记录会淹没值班者要看的决定。现在 Slack 显示新假设、获支持或被反驳的状态及简要理由，原始查询、可视化和分支留在调查界面；工程师也能从线程补充线索。官方文章说明可以从告警事项或 Slack 主动发起调查，按指定告警自动启动仍是后续计划。现有证据是原型经验、角色权限和可回查的记录结构，尚无结案准确率或 MTTR 对照数据。
