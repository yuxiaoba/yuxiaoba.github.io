---
id: baseten-fastest-delta-weight-syncs
title: 2026年10月31日｜用 GPU 权重作为父版本：Baseten 的增量同步
date: '2026-10-31'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: 从 GPU 读取变化位置、增量校验并缩短策略切换暂停，同时释放主机内存给 KV 缓存。
long_read: true
source_url: https://www.baseten.co/blog/the-fastest-delta-weight-syncs-in-the-world/
permalink: /tech/zh/baseten-fastest-delta-weight-syncs/
translation_source: assistant-authored bilingual research notes
published_at: '2026-10-31T08:34:05.438760+08:00'
updated_at: '2026-10-31T08:34:05.438760+08:00'
---
**Baseten · 2026-10-30**  
原文：[The fastest delta weight syncs in the world](https://www.baseten.co/blog/the-fastest-delta-weight-syncs-in-the-world/)

强化学习训练中，训练器持续产生新策略，推理集群则用策略生成 rollout。两者不共享基础设施时，权重需要跨环境传递；更新期间如果暂停请求过久，训练与服务的节奏都会受到影响。Baseten 描述了一次针对增量权重同步的改造：不再在 CPU 保存完整的父检查点，而是把 GPU 上正在服务的权重作为父版本。

## 从完整 CPU 副本转向稀疏读取

训练器向对象存储发布检查点和稀疏 delta，每个 delta tensor 是父版本和新版本字节异或后再用 zstd 压缩。rollout 副本下载并重建新策略。旧设计要保留完整父权重供解码，也要在每次更新后修改该 CPU 副本，才能正确处理下一次 delta。文章称 GLM-5.3 的副本约 770 GB，更新 CPU 父本约需 45 秒，且主机内存会与 KV cache 争用。

新设计启动时核验每个 tensor 并保存 Adler-32 校验值，之后删除本地父检查点。解码器直接遍历 zstd 命令，保留非零异或字节的位置与掩码；GPU worker 只读取变化位置的旧值，异或得到新值，并按推理引擎实际布局准备写入计划。旧策略在大部分准备过程中继续服务。

## 校验先行，暂停时只做必要写入

逐次重读整个 tensor 校验会抵消稀疏更新的收益。文章利用 Adler-32 可按位置计算每个变化字节对校验值的修正：从已存的父校验值出发，逐个累加变化，再与训练器发布的新校验值比较。校验失败在写入 GPU 之前拒绝更新。作者报告，在 Kimi K3 的 30 GB delta 上，这一优化使整次更新约从 230 秒降到 100 秒；这是该设置下的测量，不等于所有 delta 的收益。

进入切换窗口后，系统停止接收并暂停运行中的请求，原地写入新值、刷新派生权重；各 rank 都成功后发布新策略版本并恢复服务。对约 770 GB 的 GLM-5.3，文中报告从同步请求到新策略可服务约 15 秒，暂停约 0.8 秒；此前分别约 36 秒和 6 秒。全流程时间与请求暂停时间不是同一指标。

## 避免更新与推理争抢资源

更新工作仍会使用正在提供推理的机器。解码器按 tensor/expert 并行归属拆分变化，并映射到各 GPU 的实际布局。为避免 Python 事件循环中的 CPU 工作与 SGLang 调度争抢 GIL，规划工作放到不使用 CUDA 的独立辅助进程，通过共享固定内存交换数据。下载和解码也按分片流水执行，低优先级线程为服务保留 CPU 核心。

Kimi K3 的服务布局为 1.7 TB，作者在两个各含四张 GPU 的 GB300 节点上分别处理本节点拥有的 tensor；8.4 GB delta 从请求到上线为 75 秒，暂停 4.1 秒。两节点都必须写入成功才恢复请求。这说明亚秒暂停并非所有模型和配置都成立。

## 空出的主机内存还能做什么

去掉 CPU 权重副本后，主机内存可用于保存从 GPU 淘汰的 KV 页。文章报告一个 150k-token 共享前缀从 CPU 重新加载约 0.48 秒，重新 prefill 约 4.9 秒。在 Kimi K3 的 AgentX 测试中，并发为 16 时缓存已可放进 GPU，额外卸载没有区别；并发为 48 时，新设计的主机缓存让命中率从 2% 升至 92%，每 GPU 输出吞吐提升 3.2 倍。

这些结果来自单副本和模拟训练器形状的 fixture delta；它们展示的是特定 workload 的同步及缓存权衡，而非跨部署的保证。对训练—推理协同而言，值得关注的是把**更新正确性、暂停窗口、主机内存与缓存收益**作为同一条路径设计，而不只比较传输带宽。
