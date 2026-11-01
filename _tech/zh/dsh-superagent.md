---
id: dsh-superagent
title: 2026年11月1日｜DeepSeek 原型如何管理持续工作、授权与恢复
date: '2026-11-01'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- agent-reliability
- multi-agent
- systems-reliability
summary: 从 Ticket 与 Assignment 的分离，看事件驱动编码 Agent 怎样交接、恢复和保留权限边界。
translation_source: assistant
authorship: assistant
long_read: true
source_url: https://github.com/deepseek-ai/dsh-superagent-prototype
permalink: /tech/zh/dsh-superagent/
published_at: '2026-11-01T08:44:13.804154+08:00'
updated_at: '2026-11-01T08:44:13.804154+08:00'
---
持续运行的编码 Agent 面对的困难，往往出现在两次模型回答之间：CI 结果晚到、同一个问题被多人追问、进程重启时尚有工作未交付。DeepSeek 的 dsh-superagent 原型把这些问题放进工作项与执行状态，而不是只依赖对话历史。对 AgentOps，最值得看的是它如何区分“获准做什么”“本轮正在做什么”和“哪些外部动作还没完成”。

原始项目：[dsh-superagent](https://github.com/deepseek-ai/dsh-superagent-prototype) · deepseek-ai / DeepSeek Harness 团队 · 仓库创建于 2026-10-31。README 明确说明这是研究参考代码，公开实现经过调整，与 *Exploring Super-agent Design: Towards a More Autonomous Agent System* 的设计不完全一致，部分方向尚未实现。

## 一个工作项跨越多轮执行

原型面向一个 GitHub 仓库，可接收 GitHub 和可选的飞书事件。它把事件记录为 Trigger，经判断后建立 Ticket；Ticket 保存工作目标、授权依据、订阅线程和进展。实际执行由 Assignment 承担，拥有独立的 Executor Session 和工作目录。重试可以更换 Assignment，同时保留同一个 Ticket、会话、目录、分支与 PR。

这种拆分让一次模型调用结束不再等于工作结束。Executor 如果还有后台命令或子任务，工作槽位继续占用；只有本轮没有后台工作才进入等待。`ready` 也不总意味着 Ticket 已结束：关联 PR 的工作仍需按其关闭或合并状态推进。面板区分等待回答、等待评审、输入未送达、失败与排队，避免将所有未运行状态混成一个“idle”。

调度还给人的跟进保留一个额外槽位。当普通并发槽满了，人工消息或状态请求可以唤醒已有工作，并优先取得下一个空闲槽；CI 等自动输入则等待普通容量。这一机制针对的是长任务占满资源后，人无法继续介入的问题，不是模型推理速度的优化。

## 上下文可以传播，权限不能随之扩大

[授权文档](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/002-authorization.md)区分显式请求与推断候选。系统检查发送者和来源策略；在订阅线程中到来的消息可以作为上下文送入 Ticket，却不会因此产生新的授权。每个 Ticket 受自己的 Mandate 约束，超出范围的跟进应交回路由。

主动工作另有 `off`、`observe`、`auto` 三种模式。默认 observe 会记录“本会接受”的判断，但不实际接受推断任务；auto 中仍需规则匹配。这样可以先观察事件接纳决策，再决定是否让同类事件真正启动工作。普通聊天、引用文档和机器人评论本身都不是修改策略的渠道。

策略版本变化会重排正在进行的评估，并通知受影响的工作；它不会立即撤销所有运行中 Ticket 的授权。结束的工作恢复前还需重验。这个细节很重要：版本化授权提供了可追踪的依据，但不能将其解读成策略一改、全部外部动作就瞬间停止。

## 先保存决定，再执行外部动作

[架构文档](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/007-architecture.md)把 Engine 设为核心对象的唯一写入者。命令在事务里改变状态，外部操作先排入持久化工作，提交后再由适配器执行。Outbox 保存回复记录并排队发送，使“决定应当回复”与“消息已经送到”可以分别追踪。

这种设计有助于恢复失败的投递，但不意味着所有外部副作用获得恰好一次保证。例如，一次请求发出后进程崩溃，是否已在外部生效仍可能需要核查。执行文档要求恢复中的 Worker 先检查目录、历史和 GitHub 状态，再重复外部操作；恢复提示与持久化状态共同减少盲目重做。

错误也被分流处理。临时模型提供商或网络错误先进行三次递增退避重试；准备目录失败不走同样的自动重试。进入 blocked/failed 后，自动输入仍被记录，但不会继续唤醒 Executor。人工消息、重试或后续有效报告才能解除暂停。这里既保留了修复路径，也避免 CI 事件持续把同一个失败循环重新点燃。

## 分离会话仍需辨认隔离边界

工作目录和命令包装器建立默认执行环境，文档明确说它们不是安全边界：Worker 仍可能通过绝对路径调用程序，而且以操作者的操作系统身份执行命令。合并规则也有一部分属于 Agent 指令；要强制评审条件，仍依赖仓库保护规则。

原型的工程贡献在于把事件接纳、授权、后台任务、交付和重启恢复组织成可检查的生命周期。它没有给出相对其他系统的可靠性基准或生产故障率，因此不能仅凭文档推断自治能力或恢复收益。阅读时可沿授权 → 执行 → 架构的顺序，特别检查“收到消息”“读过消息”“做出决定”“完成外部动作”之间的区别。相关机制在文档中主要以表格和 Mermaid 描述，本篇保留文字解释，不另造架构图。
