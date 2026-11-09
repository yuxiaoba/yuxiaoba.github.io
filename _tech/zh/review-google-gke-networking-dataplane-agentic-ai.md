---
id: review-google-gke-networking-dataplane-agentic-ai
title: 2026-10-29｜GKE：高密度沙箱的网络身份瓶颈
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://cloud.google.com/blog/products/networking/gke-networking-dataplane-for-large-agentic-ai-workloads
tags:
- agent-reliability
- coding-agents
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-google-gke-networking-dataplane-agentic-ai/
long_read: true
summary: "高基数 Pod 标签如何拖慢身份分配，以及迁移 annotations 与精确过滤的安全前提。"
---

## 沙箱启动为何卡在网络身份

Google 的文章讨论 agent 强化学习等负载中的高频 Pod 创建与销毁：模型等待代码执行沙箱时，即使 GPU 有算力也无法推进。控制器常给每个 Pod 加 agent-id、时间戳或 claim-uid，用于追踪实例。GKE Dataplane V2 基于标签计算用于网络策略的数字身份；若标签组合各不相同，沙箱就各占一个身份。

身份分配及 eBPF map 更新进入启动路径，高并发下串行分配会拖慢初始化。文章同时指出集群级 65,536 个网络身份上限。这里的资源不是 Pod 数或 IP 数；即使沙箱执行内容类似，独特元数据也能使身份数量随实例增长。

## 两种改变身份基数的办法

第一种办法是在数据模型上区分选择语义与观察元数据。对于不参与 Service selector 匹配或核心资源分组的字段，把它们从 labels 移至 annotations。后者仍能保存实例信息，却不参与这条网络身份计算路径。同类沙箱因而可以共享身份，无需为每次启动重新分配。

第二种办法是精确配置 Cilium 标签排除规则。原文用 kube-system 中的 cilium-config-emergency-override 举例，排除 sandbox-name-hash 或 timestamp 等动态标签。它面向框架仍会附加这些标签的情况：保留标签本身，但让身份计算忽略它们。两种操作的共同前提是这些字段确实不承载隔离策略；删掉一个参与安全选择的维度会改变授权含义，不能把所有高基数字段一律过滤。

## 如何理解吞吐与恢复数字

文章报告每秒 300 个沙箱、亚秒级启动；另一个 Agent Substrate 验证在 20 万 agents 场景下达到每秒 500 次激活及低于 500 毫秒的挂起和恢复延迟。后者还绕过 Kubernetes 调度限制，操作和系统路径不同，不能把两组数字拼成同一个网络优化的收益。客户跨集群数十万环境以及单集群三万多沙箱的尖峰，也属于不同观测范围。

我的理解是，这是一项有明确适用条件的元数据建模经验：当启动时间随身份增长、而工作负载的实际安全类别较少时，先检查实例标识是否误进了策略身份。它没有证明任意 GKE 集群都能达到所列速率，也没有用统一对照实验分离网络、调度与状态恢复各自的贡献。

来源：[原始工程文章](https://cloud.google.com/blog/products/networking/gke-networking-dataplane-for-large-agentic-ai-workloads)
