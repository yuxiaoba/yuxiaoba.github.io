---
id: 2026-11-05-vllm-bangkok-serving-agentic-workload
title: '2026年11月5日｜技术阅读：Serving the agentic workload: Simon Mo on what AI agents change
  in vLLM'
date: '2026-11-05'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://vllmbangkok.com/en/blog/serving-the-agentic-workload/
source_published_at: '2026-11-04'
tags:
- systems-reliability
authoring_source: assistant
translation_source: assistant
permalink: /tech/zh/2026-11-05-vllm-bangkok-serving-agentic-workload/
long_read: true
summary: "Agent 流量的前缀复用、Mooncake 数据路径及 3.8 倍吞吐对照的具体条件。"
---

## Agent 会话把负载变成长前缀复用

vLLM Bangkok 这篇是 Simon Mo 在 Runtime 2026 演讲的社区总结，不能把总结者补充当演讲原话。它描述编码 agent 多轮调用中旧历史反复出现、每轮只增加工具输出和少量生成的结构。AgentX 的输入中位数 142K、输出中位数 444 是两个总体统计量；相除得到的约 320 不是逐请求平均输入输出比，95% 以上的前缀可复用潜力也不等于实际缓存命中率。

缓存因而影响首 token 等待与整体服务成本：长历史可能占据数 GB，忙碌实例会淘汰它；下一轮为平衡负载路由到其他实例，又产生跨实例 miss。简单坚持同机亲和性可以留住前缀，却可能让部分实例过载。

## 从查询块位置到异步恢复

演讲总结所链接的 vLLM 官方 Mooncake 工程文章给出具体流程。scheduler 按 token block 哈希查询 master，master 管理块元数据与节点健康；worker 内嵌 client，将 GPU KV 注册为 RDMA buffer，通过后台 I/O 线程准备并发起搬运。GPUDirect 路径避免占用 SM 或额外暂存，后台线程则避免描述符准备阻塞主 CPU 启动路径。

MultiConnector 将 P/D 传输与共享 store 连接起来。该文章版本中，prefill 可以从池恢复前缀并转交 decode，decode 会写池但不直接读池；多路径读取仍是后续工作。不能因为较新的演讲架构图包含 DRAM 和 NVMe，就把旧 DRAM 实验写成 SSD 已验证收益。

## 数字对应特定基线与流量

官方实验用 Kimi-2.5 NVFP4、12 张 GB200、1P1D，610 条 Codex/SWE-bench Pro 轨迹；基线只缓存 system prompt。命中率由 1.7% 增至 92.2%，吞吐提高 3.8 倍，P50 TTFT 降低 46 倍。这说明大量可复用历史未被基线保存时的潜力，不能推广为已经充分缓存的服务也有同样收益。

扩到 60 GPU 的近线性结果来自另一个合成负载，session 数随资源增加，round-robin 刻意制造跨节点访问。我的理解是，选择系统时应先区分可复用前缀、实际驻留命中与恢复成本，再讨论吞吐和单用户交互性的取舍。这篇总结的价值是解释负载变化；其中口头硬件比较和实验 TPU 峰值不能替代同配置的部署评估。

[Mooncake 官方机制与实验说明](https://vllm.ai/blog/2026-05-06-mooncake-store)

来源：[原始工程文章](https://vllmbangkok.com/en/blog/serving-the-agentic-workload/)
