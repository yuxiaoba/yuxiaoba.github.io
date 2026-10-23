---
id: adaptive-telemetry
title: 2026年10月20日｜Adaptive Telemetry：节省存储之后，还能找回哪些证据
date: '2026-10-20'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- observability
- systems-reliability
summary: 从分组采样、稀有路径覆盖和 24 小时 trace 找回，理解遥测成本优化的证据边界，以及自动聚合为何不等于账单保证。
long_read: true
source_url: https://grafana.com/blog/cut-costs-keep-what-you-need-adaptive-telemetry/
permalink: /tech/zh/adaptive-telemetry/
authorship: assistant
translation_source: assistant-authored bilingual analysis and translation
published_at: '2026-10-23T12:22:02.560508+08:00'
updated_at: '2026-10-23T12:22:02.560508+08:00'
---
遥测降本最难回答的问题，往往发生在删减之后：事故来了，还能查到需要的证据吗？Grafana 的 Adaptive Telemetry 更新把这个问题拆成三件事：怎样分配保留预算，怎样留下稀有行为的样本，以及怎样为某些已丢弃数据保留有限的找回通道。值得关注的是数据保留策略开始表达诊断需求；节省多少字节只是其中一个结果。

原文：[Break the link between data volume and your observability bill with Adaptive Telemetry](https://grafana.com/blog/cut-costs-keep-what-you-need-adaptive-telemetry/)  
JK Basra、Steven Dungan · Grafana Labs · 2026-10-20

## 同样的采样比例，可以保留不同的信息

若一个高流量服务占据绝大多数请求，统一概率采样也会把大部分空间分给它。其工程后果是健康检查可能留下很多相似记录，偶尔调用的关键路径却难以找到样本。这里需要优化的并不只是数量，还包括样本如何覆盖系统行为。

[Volumetric sampling 文档](https://grafana.com/docs/grafana-cloud/observe-and-act/adaptive-telemetry/adaptive-traces/manage-recommendations/volumetric-policy/)说明，系统按 span 属性分组，并持续调整组内采样率，使总保留量趋近配置比例。关键细节是比例针对字节量，而非 trace 条数；同样的百分比可能对应不同数量的 trace。它倾向于改善低流量组的代表性，但没有承诺完整捕获每种行为。

因此，采用后不宜直接拿保留 trace 的原始计数比较服务请求量。采样策略已改变不同组进入样本的机会。诊断需要的“看见稀有路径”和统计需要的“估计真实频率”是两个目标，不能因为前者改善，就假设后者自然无偏。

## 稀有路径需要最低覆盖

[Diversity sampling](https://grafana.com/docs/grafana-cloud/observe-and-act/adaptive-telemetry/adaptive-traces/manage-recommendations/diversity-policy/)把服务、路由、状态码等属性组合成指纹，每 15 分钟为每种指纹至少保留一条 trace。它补充的是样本多样性：即使某种请求很少，也有机会留下可检查的实例。

<a class="note-image-link" href="/assets/images/tech/adaptive-telemetry/diversity.png" target="_blank" rel="noopener" aria-label="Adaptive Traces 中按属性组合保留独特 trace 的采样建议 · 查看原图 ↗"><img src="/assets/images/tech/adaptive-telemetry/diversity.png" alt="Adaptive Traces 中按属性组合保留独特 trace 的采样建议" loading="lazy"><span class="note-image-action">查看原图 ↗</span></a>

*读图：这条建议为独特的属性组合保留样本；它展示策略入口，不表示每个请求都会被保留。*

一条代表样本可以帮助发现新路径，却不足以描述该路径的延迟分布，也未必包含同一指纹内的所有失败方式。例如，相同路由和状态码可能对应不同内部原因。工程上应把指纹理解为有限的分类规则，而不是系统行为的完备语义。与其他采样策略叠加后，总保留量也不一定随全局比例线性下降。

## 找回通道有时间与入口条件

[Query dropped traces 文档](https://grafana.com/docs/grafana-cloud/observe-and-act/adaptive-telemetry/adaptive-traces/query-dropped-traces/)给出一个有用的恢复窗口：摄入后 24 小时内，可以凭 trace ID 查询未被采样保留的 trace。首次找回会将其写入 Tempo；未在窗口内查询的数据最终丢弃。找回后的搜索可见性仍是尽力提供，可靠入口是已知 ID，较大的 trace 还可能标记为部分截断。

这意味着日志、错误报告或支持工单是否保留 trace ID，直接决定这项能力的价值。若调查只有“昨晚某地区变慢”，却没有具体 ID，找回机制不能替代按条件搜索。若问题数天后才被发现，24 小时窗口也已经关闭。它降低了一类误采样损失，并没有恢复无限期的全量可检索性。

## 日志与指标各有另一种取舍

原文还介绍将日志归档到用户对象存储，以及指标建议自动应用。日志 Archive 和采集端过滤处于公开预览，Replay 尚待推出；不能把归档存在直接等同于完整回放工作流已经可用。归档方案需要单独评估恢复时延、对象存储费用和数据保留策略。[官方更新](https://grafana.com/blog/cut-costs-keep-what-you-need-adaptive-telemetry/)

[Auto-Apply 文档](https://grafana.com/docs/grafana-cloud/observe-and-act/adaptive-telemetry/adaptive-metrics/additional-configuration/auto-apply/)区分 Coverage-first 与 Cost-first：前者可为新查询需求恢复更多细节，后者依据最近分析中的序列数量估算约束推荐变更。Cost-first 不是实时比较变更前后的序列数，也不是任何情况下都不增长的硬保证。关键指标应先设置豁免，再决定在哪些分段自动应用。

从工程角度看，“最近没被查询”只能说明已观测到的使用需求有限。某些低频审计或灾难恢复问题可能尚未出现。自动化应减少重复审核劳动，同时保留表达例外需求的办法；否则省掉的恰好可能是未来事故才会用到的维度。

## 保留策略会改变诊断系统的输入

对基于遥测的异常检测或 Agent 调查，采样器本身也是数据生成过程的一部分。策略调整后，某类 trace 的数量增加，可能只是它更容易被保留，并不意味着服务实际变得更忙。比较前后效果时，应保留策略版本与变更时间，否则模型可能把采样变化当成工作负载变化。

还可以用一组预先选定的故障案例评估删减方案。先问每个案例原本依赖什么：完整调用链、某个错误码、某段低频日志，还是高基数标签。再检查策略是否保留足以区分原因的部分。即使保存的样本数量没有下降，丢失关键关联也可能让调查更加困难。

这类验证需要覆盖常见与少见事件。常见故障容易证明新策略仍有用，稀有故障才更能检验最低覆盖与恢复窗口。最终应明确哪些调查可以在线完成，哪些需要先找到 ID，哪些必须等待归档恢复，把诊断时间也纳入成本讨论。

因此，删除策略不仅是存储配置，也在决定未来能够回答的问题集合。团队需要知道哪些证据已不可逆地消失，哪些仍有条件恢复，才能给调查结果合适的置信程度。

## 怎样理解公开结果

Grafana 报告在相同数据量下，Volumetric sampling 的信息密度比概率采样高约 25%。文章没有给出足够的工作负载和度量定义，不能把这一数字解释为故障定位准确率提高 25%，也不能从标题中的体量降幅推导出等比例账单下降。这里得到的是厂商测试信号，而不是跨业务的统一收益保证。

更有说服力的验收方式，是同时检查保留字节量、低流量路径是否有样本、已知事故证据能否找回，以及调查需要等待多久。对 Agent 工作负载，还应检查一次任务跨模型调用与工具调用的关联是否仍然连贯。这些是从机制推导出的评估重点。该更新最值得借鉴的设计思想，是把“保留、可搜索、可按 ID 找回、可离线恢复”明确区分，再为每一层付出相应成本。
