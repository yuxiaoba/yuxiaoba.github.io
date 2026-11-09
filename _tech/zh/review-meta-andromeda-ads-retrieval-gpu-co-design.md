---
id: review-meta-andromeda-ads-retrieval-gpu-co-design
title: 2026-10-29｜Meta Andromeda：融合执行与 GPU 共置的边界
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://engineering.fb.com/2026/10/28/ml-applications/meta-andromeda-next-gen-ads-retrieval-gpu-co-design/
tags:
- agent-reliability
- coding-agents
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-meta-andromeda-ads-retrieval-gpu-co-design/
long_read: true
summary: "Andromeda 如何分别减少中间张量与跨机候选搬运，并区分评分峰值和完整流水线。"
---

## 从候选检索到内存带宽瓶颈

Andromeda 位于广告推荐的检索阶段，要在毫秒预算内把巨大候选池缩成少量广告，再交给更昂贵的排序模型。Meta 的新架构用多个用户专家表达不同兴趣，广告表示融入实时上下文，交互层用 MoE gating 选择相关专家。原文报告相对 2024 检索模型约减少 300 倍推理 FLOPs；这个模型变化给系统融合留下了空间。

候选吞吐达到每秒数十亿后，小型中间张量也会累积成 TB/s 级流量。瓶颈不只是算术量：embedding gather、用户广告交互和评分若分别启动 kernel，就要反复把中间结果写入 HBM。模型变轻后，搬运反而成为限制。

## 融合执行与共置解决两段搬运

第一层优化把每个用户广告对的 gather、MoE 交互和评分放入一个 kernel，中间结果留在寄存器和共享内存，避免跨 kernel 的 HBM 落地。第二层优化针对主机间传输：旧流程在 CPU 执行索引匹配和 top-K，把大候选列表发给远端 GPU 评分；即使评分很快，网络仍会饱和。

新流程把索引匹配、评分和 top-K 放在同一 GPU 服务器。网络只发送用户特征和 targeting query，返回最终 top-K，原文报告流量约减少 100 倍。这里还要重新设计支持复杂广告定向逻辑及实时更新的 GPU 索引，不能把共置理解成简单挪动进程。后续共同优化也调整匹配与评分的数据布局，减少组件之间的间接访问。

## kernel 峰值与生产流水线不能互换

Meta 报告单 GH200 评分 kernel 超过每秒百亿广告，而完整共置生产流水线超过十亿；索引匹配的峰值又更高。这些数字覆盖不同工作量，不能把最快组件当端到端结果。INT8 相对优化 FP16 kernel 的最高额外两倍也属于另一项对照。自 2025 年起的转化率改善是业务累计指标，不能全部归因于本次某个 kernel。

我的理解是，可迁移的是在模型、内存层次和部署边界之间联合寻找瓶颈。只有当候选评分足够紧凑、索引能保留原有语义、数据布局适合 GPU 时，这条路线才成立。广告评分每秒处理量既不是 LLM token 吞吐，也不是任意 MoE 模型可获得的收益。

来源：[原始工程文章](https://engineering.fb.com/2026/10/28/ml-applications/meta-andromeda-next-gen-ads-retrieval-gpu-co-design/)
