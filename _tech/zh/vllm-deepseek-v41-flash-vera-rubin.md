---
id: vllm-deepseek-v41-flash-vera-rubin
title: 2026年11月13日｜vLLM 在 Rubin 上的优化：内存局部性与机架共享
date: '2026-11-13'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: 区分含缓存输入的总吞吐、单用户解码与 kernel 微基准，理解 Rubin 优化的三个层级。
long_read: true
source_url: https://vllm.ai/blog/2026-11-12-deepseek-v41-flash-vera-rubin
permalink: /tech/zh/vllm-deepseek-v41-flash-vera-rubin/
translation_source: assistant
authorship: assistant
source_published_at: '2026-11-12'
published_at: '2026-11-13T08:46:43.062448+08:00'
updated_at: '2026-11-13T08:46:43.062448+08:00'
---
Inferact and the vLLM Team · 2026-11-12  
原文：[DeepSeek-V4.1-Flash on Vera Rubin NVL72: 58x Throughput vs. GB300 NVL72 at 387 tokens/s](https://vllm.ai/blog/2026-11-12-deepseek-v41-flash-vera-rubin)

vLLM 的 Rubin 报告把优化从 kernel 推到了机架级缓存：芯片内尽量读取本地内存域，芯片间共享 KV 与 Engram 表，再让路由器摆脱会话固定绑定。它报告的高吞吐，需要连同 AgentX 工作负载及缓存计数口径一起阅读。

## 先分清三个性能数字

原文的 170 万 tokens/s/GPU、相对 GB300 NVL72 的 58×，采用总 token 口径，**包含缓存输入、未缓存输入和输出**；对应单用户速度为 387 tokens/s。它不是每张 GPU 每秒新生成 170 万 token。峰值总吞吐 252 万与单用户最高 1,810 也分别属于不同运行点，不能拼成一套同时达到的服务指标。

低延迟路径使用跨两个计算托盘的 TP8，batch 1 的 1,810 tokens/s 标为 P90。正文另外报告固定 DSpark 接受长度 3.51 时，AgentX 单会话 P50 从 1,117 到 1,844。分位数、接受长度、并行策略和并发都会改变含义；本文更关注支持这些结果的结构变化。

## 把数据放到读取它的 SM 附近

Rubin 每 GPU 有两个内存域，SM 读本域比交错或跨域数据更快。decode 的专家 GEMM 受权重带宽限制，vLLM 按输出列把专家权重分到两域，让各域 SM 处理本地 tile。prefill 的 mHC residual stream 同样使用分域任务计数，优先处理本域工作，再帮助另一域。

另一项改动针对数据并行负载不均：空闲 rank 不能按自己的少量 token 选择很小的 MegaMoE tile，因为它的专家还可能服务繁忙 rank。新规则参考本地与 DP 平均 token 数中的较大值，40 步回放中 MegaMoE 时间下降 55%。这展示了局部 batch 大小不一定代表本地专家真正工作量。

SM107 的 K64 FP8×FP4 MMA 每条指令做更多工作，低延迟路径还能以打包 FP4 放下更多权重加载 stage。attention 则提前取下一批索引和 KV，尽量让 tensor core 不等待加载。32K token/rank 的 DEP2 prefill 步耗时综合降低约 28%；各 kernel 的局部收益不能相加当作整机倍率。

## 缩短关键路径，而非让每个模块一起等待

Wide-EP dispatch 把远端加载尽早发出，减少每 token 的 NVLink 往返。combine 用不可能成为有效输出的 sentinel 标识未到达数据，CTA 只等自己的 GEMM 任务，而不等整组 barrier。mHC 则将下一层马上需要的 Post、route collapse 与 RMSNorm 留在关键路径，把后续 mixes 放到旁路 stream。

原文约 25% 的 DEP32 decode target-forward 改善是在单个四 GPU 节点模拟、每 rank 20 请求 × 6 token、DSpark k=5 的条件下比较早期 Rubin 实现；不是所有机架端到端请求都减少 25% 时延。TP8 的低延迟实现又有不同优化，例如融合 all-reduce 后的处理、保留部分 SM 给旁路工作，不能与 Wide-EP 实验互换解释。

## 共享缓存让路由不再受会话位置约束

原先按 rank 保存 CPU 前缀缓存并固定会话，在高并发下既可能缓存装不下，也可能一边排队、另一边空闲。新方案用 Mooncake 汇聚机架 DRAM，并实验性纳入空闲 HBM；任意 prefill rank 可通过 RDMA 装载前缀。Engram 的两张 94.4 GiB 表则分片放到 GPU HBM，经 NVLink 读取。**KV pool 的 RDMA 与 Engram 的 NVLink 是不同数据路径。**

缓存位置与会话解绑后，Dynamo 按未缓存工作量选择 worker/rank。三组 DEP2、并发 4,800 的测试中，池化加路由整体提高 68% requests/s，TTFT P50 从 29.8 秒到 4.2 秒，命中率从 91.8% 到 96.1%。更大的 12 × DEP2 结果属于模拟：一边空闲而另一边排队的时间比例从 10.3% 降到 1.3%。这两组证据不能当成同一规模的实测。

原文核心架构图使用交互式页面，本页保留文字解释，不以封面替代机制图。整篇最可迁移的观察是：更快的计算会改变缓存容量和排队瓶颈；只有把内存局部性、异步装载及路由一起调整，硬件速度才可能转化成用户体验。报告针对 DeepSeek-V4.1-Flash、AgentX 和特定机架，HBM pool 仍属实验性，不构成通用模型或低命中工作负载的同倍率承诺。
