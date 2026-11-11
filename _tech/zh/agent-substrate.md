---
date: '2026-11-11'
published: true
layout: article
maintenance: daily-research
authorship: assistant
translation_source: assistant-authored paired Chinese/English research notes
id: agent-substrate
title: 2026年11月11日｜Agent Substrate：会话可挂起，热 Worker 不必绑定一个 Agent
lang: zh
source_type: tech
tags:
- agent-reliability
- inference-serving
- systems-reliability
summary: 解释 Actor/Worker 解耦、请求排队与推理信号回传，并区分现有机制与实验集成。
permalink: /tech/zh/agent-substrate/
long_read: true
source_url: https://developer.nvidia.com/blog/agent-substrate-advancing-kubernetes-for-agents-at-scale/
published_at: '2026-11-11T08:53:13.850705+08:00'
updated_at: '2026-11-11T08:53:13.850705+08:00'
---
Agent 经常在两段动作之间等待：等模型、工具或人。一个会话对应一个常驻 Pod，会让大量内存和 CPU 绑定在空闲状态；每轮重建 Pod 又丢状态、增加冷启动。Agent Substrate 的核心是把逻辑会话与执行它的 Worker Pod 分开，让环境状态可暂存、可恢复，同时继续使用 Kubernetes 的集群调度。

原文：[Agent Substrate: Advancing Kubernetes for Agents at Scale](https://developer.nvidia.com/blog/agent-substrate-advancing-kubernetes-for-agents-at-scale/)  
Ekin Karabulut、Omer Yahud · 2026-11-10

## Actor 状态跨越 Worker 生命周期

Substrate 在普通 Kubernetes Pod 上维护较小的热 Worker 池，另设控制面映射大量 Actor 与环境。空闲 Actor 的内存、文件系统从 gVisor 或 microVM 沙箱中保存，释放 Worker；下次请求恢复到可用 Worker，而非重新经过 API server、admission、scheduler、kubelet 整条 Pod 创建路径。

这个边界适合三类负载：在仓库编辑和模型调用间切换的编码助手，突发产生浏览器/编译器等环境的 RL rollout，以及短时编译、计时或数值实验的 GPU 沙箱。共同点是环境需要持续，执行资源不必持续占有。它不是把所有 Agent 合并为无隔离的进程，也没有绕开 Kubernetes 对 Worker 的配额与放置策略。

文章只有装饰性头图，没有可用的机制架构原图；这里按 Actor → 挂起状态 → Worker 恢复的流程理解。

## 过载时排队，隔离时限制到容器

原先 Worker 满时，新一轮请求可能立即失败。router 的 request parking 改为保留请求并重试恢复，同时设置等待时限与队列容量。后续修复让已运行 Actor 的请求不被这条等待队列挡住，避免“还有资源可执行的会话也跟着排队”。这两处细节说明，热池之外还必须处理背压和队首阻塞。

microVM 沙箱还引入每容器 CPU/内存限制：日志、代理与主任务在同一环境中运行时，某个容器内存失控不应杀死整个沙箱。文章描述超限容器被单独停止，其余继续运行。它提供的是资源隔离粒度的改变，未给出完整恶意负载安全评测。

GPU 设备接入与挂起恢复则仍在开发。设计基于 Kubernetes DRA，由厂商声明安全暂停方式以及快照依赖的设备属性，恢复时匹配型号或驱动等条件；没有兼容设备则回退冷启动。不能把“恢复到任意空闲 Worker”解释为 GPU 状态可以任意跨卡迁移。

## 与 Dynamo 交换什么信号

Substrate 负责 Agent 在哪里执行工具，Dynamo 负责模型在哪里推理。会话 ID、工具调用边界、优先级和生命周期信号，可以帮助推理路由保留可复用 KV、避免热点，并优先交互请求。反向，Dynamo 可向环境层暴露预计 TTFT、完成时间、缓存就绪与 GPU 池饱和度。

这些信号允许一种更完整的调度：预计推理等待很长时挂起环境，回答接近完成时提前唤醒，而不是让 CPU 沙箱整段等待 GPU；GPU 已饱和时也不应盲目放大子 Agent。文章给出的是集成方向与部分机制，结尾明确 APIs 在变化、GPU 支持正重建，部分 Dynamo 集成实验性。不能把所有描述都当作已经稳定部署的自动策略。

## 密度声明与工程证据的层级

官方导语提出面向大规模 Agent 和更高密度，但没有在本文提供可核对的完整性能方法来支撑普适的“10 倍”结论，因而不将其作为选型数字。更扎实的证据是具体队列修复、资源限制和设备兼容设计，以及它们如何改变失败路径。

对 AgentOps 的推进，是让环境生命周期与推理生命周期交换状态，而非分别扩容后只比较利用率。KAI Scheduler 仍放置 Worker、训练器与推理 Pod；Substrate 在池内做高频 Actor 调度。两个层级互补，不能用会话数量代替可执行容量，也不能用挂起能力代替过载预算。
