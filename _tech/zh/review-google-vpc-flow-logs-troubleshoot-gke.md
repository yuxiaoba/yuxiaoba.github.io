---
id: review-google-vpc-flow-logs-troubleshoot-gke
title: 2026-10-29｜GKE Flow Logs：保留临时 pod 的网络归属
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://cloud.google.com/blog/products/containers-kubernetes/using-vpc-flow-logs-to-troubleshoot-gke-workloads
tags:
- agent-reliability
- coding-agents
- observability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-google-vpc-flow-logs-troubleshoot-gke/
---

VPC Flow Logs 在采样时把临时 pod IP 关联到工作负载、namespace 和 service，保留 pod 消失后的网络归属证据。文章用 Online Boutique 演示依赖映射与服务流量排查，适合补充 L3/L4 诊断。

采样日志不是全流量或因果证明；intranode visibility 可能重启组件并增开销，分析桶升级有前置条件。

来源：[Using VPC Flow Logs to troubleshoot GKE workloads](https://cloud.google.com/blog/products/containers-kubernetes/using-vpc-flow-logs-to-troubleshoot-gke-workloads)

[Using VPC Flow Logs to troubleshoot GKE workloads](https://cloud.google.com/blog/products/containers-kubernetes/using-vpc-flow-logs-to-troubleshoot-gke-workloads)
