---
id: google-fararray-tpu-agents
title: 2026年10月30日｜Google 用智能体协作实现分布式图与 TPU 内核
date: '2026-10-30'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- multi-agent
- systems-reliability
summary: Google 描述了两项由人设定架构与验收标准、智能体实施和验证的系统工程：远程内存图计算 FarArray，以及避免边级中间张量的 TPU 稀疏图内核。
long_read: true
source_url: https://antigravity.google/blog/gemini-4-argon-trillion-edge-graphs-and-tpu-kernels
permalink: /tech/zh/google-fararray-tpu-agents/
translation_source: assistant-authored paired Chinese/English reading notes
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-10-30T10:31:20.339125+08:00'
---
Google 描述了两项由人设定架构与验收标准、智能体实施和验证的系统工程：远程内存图计算 FarArray，以及避免边级中间张量的 TPU 稀疏图内核。

**来源：** The Antigravity & Google Research Team，[How Gemini 4 Argon Upleveled Agents on Antigravity: Trillion-Edge Graphs and Custom TPU Kernels](https://antigravity.google/blog/gemini-4-argon-trillion-edge-graphs-and-tpu-kernels)，2026 年 10 月 26 日。

FarArray 将集群内固定的 DRAM 暴露为分区全局地址空间，支持通过 RDMA 直接执行远程读写和 64 位原子操作，减少远端 CPU 与通用键值服务开销。作者还用线程本地剪枝避免大多数冗余边访问网络。在两个连通分量基准上，Google 报告相对 TCP 键值基线运行时间快 40–180 倍、内存少 6–22 倍；另一个 1.14 万亿唯一边的案例使用 64 个目标节点共 148 GB 固定内存。不同任务和基线不应混为单一加速比。

TPU 侧的 Pallas kernel 将 COO 边分块流式处理，避免普通 gather 和 segment sum 形成按边数乘特征维度增长的 HBM 中间张量；反向传播仅保存整数边索引。作者报告在 TPU v6e 上前向和反向计算快 8–15 倍，2000 万条边的示例中临时 HBM 从 20.2 GiB 降至 111.5 MiB，并称数值一致。

团队称人类定义接口、内存布局及不使用 mock 的验证要求，专门的 proposer 与 verifier 智能体负责实现、调试及检查。这是企业内部案例和自报基准；“数月压缩到数小时”的开发时间比较依赖项目估计，不能据此推断一般开发加速。
