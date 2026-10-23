---
id: knowledge-graph-context
title: 2026年10月20日｜Grafana Knowledge Graph：让诊断从实体关系出发
date: '2026-10-20'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- observability
- agent-reliability
summary: 将运行实体、健康信号和组织知识连接起来，为人和 Agent 提供共同上下文；关系图的覆盖、语义与更新仍决定诊断质量。
long_read: true
source_url: https://grafana.com/blog/full-stack-observability-with-knowledge-graph/
permalink: /tech/zh/knowledge-graph-context/
authorship: assistant
translation_source: assistant-authored bilingual analysis and translation
published_at: '2026-10-23T12:22:02.560508+08:00'
updated_at: '2026-10-23T12:22:02.560508+08:00'
---
一次告警可能同时涉及前端、服务、数据库和基础设施，但调查人员通常还要先回答更基础的问题：它们属于同一条业务路径吗，谁维护它们，最近改过什么？Grafana 的 Knowledge Graph 更新试图把这些联系整理成可查询的运行上下文。它值得关注的地方，是让人和 Agent 从同一组实体与关系开始调查，减少每次从散落遥测中重建系统轮廓的工作。

原文：[Full-stack observability in Grafana Cloud: More connections, richer context, and faster investigations for users and agents](https://grafana.com/blog/full-stack-observability-with-knowledge-graph/)  
Sarah Constant · Grafana Labs · 2026-10-20

## 先建立实体，再连接信号

[Knowledge Graph 概览](https://grafana.com/docs/grafana-cloud/platform/knowledge-graph/introduction/)将服务、Pod、节点、数据库等作为实体，把环境、版本和集群等信息作为属性。打开一个实体后，指标、日志、追踪与健康提示可以围绕该对象展示。这样，调查入口由“先想出查询”变为“先找到出问题的对象，再查看它的证据”。

这对 Agent 的意义可以理解为限制搜索空间。若已经知道受影响服务和相邻数据库，就不必首先让模型遍历所有仪表板寻找同名对象。不过，这只是对工作流的推论：关系更丰富能让查询更有方向，不能据此断言根因判断一定正确。

<a class="note-image-link" href="/assets/images/tech/knowledge-graph-context/entities.png" target="_blank" rel="noopener" aria-label="Knowledge Graph 中服务与前端、Agent、数据库、Pod 和节点的关系 · 查看原图 ↗"><img src="/assets/images/tech/knowledge-graph-context/entities.png" alt="Knowledge Graph 中服务与前端、Agent、数据库、Pod 和节点的关系" loading="lazy"><span class="note-image-action">查看原图 ↗</span></a>

*读图：从中间的服务沿连线查看前端、数据库与下方基础设施；这里展示实体类型之间的关系，不是故障因果证明。*

## 图是怎样建出来的

[实体与关系配置文档](https://grafana.com/docs/grafana-cloud/platform/knowledge-graph/configure/manage-entities-relations/)解释了较具体的构造过程：builder 查询 Prometheus 指标，从标签和数值提取实体及属性；关系可以来自属性匹配，也可以来自指标查询。实体名称加作用域共同决定身份，所以相同服务名在不同环境中不应自动合并。

由此可见，图的可靠性首先依赖观测与建模。缺少命名空间标签可能产生模糊身份；把业务归属误写成调用关系，会让后续推理混淆边的含义；下线资源没有及时更新，则可能留下过期邻居。这些是依据构图机制推导的风险，不代表公告已经测量了相应错误率。

自定义实体让团队把多个组件组合成一个产品或业务对象，但需要可维护的规则。比较稳妥的做法，是先为一条真实业务路径检查实体身份和关系，再扩大覆盖。图越大不一定越有用；如果连接缺乏明确含义，Agent 只会更快地沿错误边检索。

## 健康提示帮助排序，原始信号负责解释

[Insights 分类文档](https://grafana.com/docs/grafana-cloud/platform/knowledge-graph/reference/insights-categories/)区分资源接近上限、配置变化、异常模式、组件故障和请求错误。这些提示表达的是信号对系统的含义，而不只是它来自指标还是日志。配置变化可以作为时间线上的线索，与延迟或错误的出现时间对照。

这里仍需区分相关性和因果性。部署发生后数据库变慢，可能是新版本增加了查询，也可能恰好遇到外部依赖异常。关系图可以告诉调查者应该看哪些相邻组件，时间线可以提示先后顺序，最终解释仍需要查询、追踪或变更证据。把所有红色节点都当成独立根因，反而会重建告警风暴。

## 组织知识如何进入调查

本次公告把上下文扩展到服务归属、值班信息以及历史事故中尝试过的行动和结果；相关 Service Center 与 IRM 集成仍在私有预览。相比只挂一段事故总结，记录“试过什么、产生什么效果”更有助于下一次形成待检验假设，但不能保证旧方案在新故障中仍有效。[官方公告](https://grafana.com/blog/full-stack-observability-with-knowledge-graph/)

一个工程上的假设例子是：过去重启曾短暂恢复连接，随后错误复发。若仅保存“重启有效”，Agent 可能重复无效动作；若保留恢复持续时间和后续观察，下一次就能先检查是否存在连接泄漏。关键在于保留条件和结果，而不是把历史操作升级成永久有效的规则。

[Assistant 的 Knowledge Graph mode](https://grafana.com/docs/grafana-cloud/platform/grafana-assistant/platform/knowledge-graph/)主要处理建模、缺失连接及规则配置，文档将它与事故调查模式区分。它可以提出配置变更，但仍需审阅完整规则和差异。能够生成关系规则，与已经证明一次事故的根因，是不同能力。

## 共享上下文还需要共享时间边界

运行关系会随扩缩容、发布和路由规则变化。一次历史事故中的服务图，与调查时看到的当前图可能不同。工程上，Agent 查询某条依赖时，应同时知道它对应哪个环境和观察时段，否则容易把今天的拓扑解释成昨天故障发生时的拓扑。这是使用运行上下文时需要提出的要求，不是公告已证明的完整历史重建能力。

同样，缺少一条边有多种解释：组件没有交互、遥测没有采到、命名规则不匹配，或者该连接尚未被产品支持。合理的调查应保留这些备选解释，避免把“图上没有”直接等价为“系统中不存在”。这种不确定性表达，对自动执行下一步查询的 Agent 尤其重要。

因此，可以用两类问题检查图的价值：一类询问已知存在的关系是否可找回，另一类询问不存在的关系是否被错误连接。只有覆盖率和误连都受到检查，新增实体才真正缩小了搜索空间，而不是制造更复杂的调查起点。

这种检查还应在重命名、迁移和扩缩容后重复，因为连接正确性不会随最初配置永久成立。

## 开放状态与证据边界

Agent Observability 产品正式可用，不代表所有 Agent 入图能力都已经正式可用。发布文章把 Agent 入图标为公开预览，而当前概览文档标为私有预览；因此应把这项连接视为预览能力，具体开放情况以目标租户为准。前端和更多云资源连接的发布状态也应与服务目录、事故记忆等预览集成分别理解。

原文以产品说明和客户案例支持调查体验改善，没有提供可比较的根因准确率或 MTTR 对照实验。值得借鉴的是把诊断上下文建设作为系统工程：检查实体覆盖、连接正确性、历史知识的新鲜度，再观察一次调查是否少走弯路。对 AIOps 而言，这推动了 Agent 输入从零散文本向结构化运行证据发展；它的上限仍由图中证据的质量决定。
