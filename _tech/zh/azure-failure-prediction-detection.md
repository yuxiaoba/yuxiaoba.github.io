---
id: azure-failure-prediction-detection
title: 2026年11月5日｜Azure AFPD：预测之后，还要完成迁移与维修
date: '2026-11-05'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
- anomaly-detection
summary: 故障预测系统如何通过禁止新分配、迁移、通知与维修调度减少硬件中断。
long_read: true
source_url: https://azure.microsoft.com/en-us/blog/predicting-and-detecting-failures-how-azure-strengthens-reliability-for-mission-critical-workloads/
permalink: /tech/zh/azure-failure-prediction-detection/
translation_source: assistant
authoring_source: assistant
published_at: '2026-11-05T08:55:14.344660+08:00'
updated_at: '2026-11-05T08:55:14.344660+08:00'
---
原文: [Predicting and detecting failures: How Azure strengthens reliability for mission-critical workloads](https://azure.microsoft.com/en-us/blog/predicting-and-detecting-failures-how-azure-strengthens-reliability-for-mission-critical-workloads/)  
Mark Russinovich · 2026-11-04

Azure 的 AFPD 把硬件故障处理拆成预测／检测、缓解、维修三个阶段。它自 2024 年起全面运行，本次文章以 SAP 为例说明客户如何接入通知，不是新发布一个仅服务 SAP 的预测模型。系统还覆盖通用计算、专用计算、HPC／AI 和部分存储场景。

检测端结合机器学习、规则、节点行为与 SSD 等硬件遥测。一旦节点被标记，缓解服务禁止新工作负载分配；符合条件的现有 VM 热迁移到健康节点，通常只暂停数秒。并非所有 M 系列规格都支持热迁移，不能把这一流程理解为所有 VM 都无重启切换。无法迁移时，系统通过 Resource Health 与 Scheduled Events 提供重新部署期限和建议，客户高可用逻辑仍需处理这些通知。

维修阶段将节点移出生产，携带诊断信息并提前准备备件，避免重新从头排查。作者报告月度节点维修率提高 80%、硬件重启总数减少超过 36%。文章开头还用“硬件相关 VM 中断预防改善 36%”描述收益；两个措辞不应扩写成所有故障或所有停机减少 36%。这是平台自报的硬件可靠性结果，未给出预测精确率、误报迁移成本或分工作负载的对照细节。

客户侧可以通过 Resource Health 查看单 VM 事件，用 Resource Graph 做跨资源查询，通过 Event Grid 接入推送自动化，并让 VM 内的高可用组件消费 Scheduled Events。前三种渠道的通知内容一致，区别主要在接入方式；Scheduled Events 提供提前事件通知，包括需要处理的 NotBefore 时间。

对 AIOps 的启示是，预测模型只是闭环入口。能否及时阻止新分配、确定哪些工作负载可迁移、给不可迁移负载留下处理时间，以及把诊断交给维修流程，共同决定预测能否变成少一次中断。原文更适合作为这一运营闭环与客户通知界面的介绍，模型结构与训练细节需要进一步阅读其引用的技术论文。
