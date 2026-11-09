---
id: review-nvidia-dynamo-validated-kubernetes-runtime
title: 2026-10-31｜Dynamo AICR：固定依赖与运行时验证
date: '2026-10-31'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://developer.nvidia.com/blog/build-a-validated-kubernetes-runtime-for-nvidia-dynamo/
tags:
- agent-reliability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-nvidia-dynamo-validated-kubernetes-runtime/
long_read: true
summary: "AICR 如何分离运行时部署与行为验证，以及 Dynamo 两条路由路径的事件和转发责任。"
---

## 模型部署对象下面还有一层运行时

DynamoGraphDeployment 描述 worker 如何运行，却不能保证驱动、GPU 发现、资源分配、gang scheduling、网络与监控已经兼容。AICR 将这些依赖写成指定平台的 recipe，固定版本、配置、约束和验证预期。文章使用 Dynamo 1.4.2 的组合，不能将其版本表理解为任意环境的最新安装建议。

流程先 snapshot 捕获集群，再生成 recipe，渲染 Helm 或 GitOps bundle，部署运行时后执行 deployment/conformance 检查，最后才安装应用图。离线对另一个 snapshot 验证只检查声明约束，行为检查明确跳过；生成 bundle 不等于集群可运行。性能阶段另外启动临时服务负载并占用 GPU，不能与基础健康检查混为一谈。

## 路由选点与转发由谁承担

原生路径由 Frontend 分词，根据前缀重合和当前负载选 worker，再转发请求，适合应用团队持有单模型入口。Gateway 路径则由 HTTPRoute 匹配 InferencePool，调用 Dynamo EPP 选点，实际 HTTP 转发仍由 gateway 完成；worker 中的 Frontend sidecar 使用 direct 模式，避免再次路由。

因此两者的关键差异是转发、超时和重试责任在哪一层，而非谁拥有更神奇的缓存。文章版本的请求面默认 TCP，KV 事件面为 ZMQ。worker 从本地引擎接收原始事件，规范化后发布给路由器，两种入口都可使用同一份实际缓存状态。

## 为什么历史请求不能代替实时缓存事件

只记录“过去把请求发到哪里”可以预测前缀位置，却看不到淘汰。内存压力下，预测视图可能越来越偏离真实缓存，路由到看似命中但必须重算的 worker。recipe 启用 worker 上报事件，正是为了把缓存亲和性建立在当前状态上。

我的理解是，这篇工程实践的价值在于把配置产物和运行证据关联起来。健康、DRA、调度、扩缩容及指标检查各有覆盖范围，选择 native 或 gateway 路线还要明确平台所有权。它不是任意模型的吞吐保证，也没有证明一个通过声明校验的离线 bundle 已验证了网络和 GPU 行为。

来源：[原始工程文章](https://developer.nvidia.com/blog/build-a-validated-kubernetes-runtime-for-nvidia-dynamo/)
