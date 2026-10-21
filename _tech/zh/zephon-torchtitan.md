---
id: "zephon-torchtitan"
title: "2026年10月16日｜Zephon：换 GPU 数量后仍保持相同训练批次"
date: "2026-10-16"
lang: "zh"
published: true
layout: "article"
maintenance: "daily-research"
source_type: "tech"
tags: ["systems-reliability"]
summary: "解释 accumulator、逻辑 lanes 与 flush/replay 如何支持在线数据处理的弹性确定性，并区分数据相同与数值逐位相同。"
authoring_source: "assistant"
translation_source: "assistant-authored paired Chinese/English editorial notes"
long_read: true
source_url: "https://pytorch.org/blog/bringing-elastically-deterministic-data-loading-to-torchtitan-with-zephon/"
permalink: "/tech/zh/zephon-torchtitan/"
---

**Josh Wills, Maximilian Böther, Ties Robroek and the Zephon team · PyTorch 官方技术文章**  
原文：[Bringing Elastically Deterministic Data Loading to TorchTitan with Zephon](https://pytorch.org/blog/bringing-elastically-deterministic-data-loading-to-torchtitan-with-zephon/)

## 改了数据配方，也可能同时改了数据顺序

数据混合、过滤、分词与打包直接影响训练结果。传统离线预处理需要先扫描语料、产生一份新数据再开始实验，失败的配方也留下存储成本。把这些操作搬进训练过程，可以使用训练节点的 CPU，减少一次性副本，却带来新的重现性问题：处理过程有状态，而且 GPU 数量可能因资源调度或故障恢复改变。

许多数据加载器按物理 rank 划分样本。一旦卡数改变，样本进入分词、打包、混合的次序也可能改变，模型看到的全局批次便不相同。这样，一次数据配方消融可能同时比较了另一条训练序列。Zephon 的目标是在在线、有状态处理中保住相同全局批次，让物理并行度尽量只影响处理速度。

## 三种对象把配方与执行拆开

官方示例由 Dataset、WorkSource 和 Pipeline 组成。Dataset 描述原始数据，WorkSource 决定数据集混合与顺序，Pipeline 将样本转成训练张量，串接分词、打包、打乱和组批。课程规划与处理算子分开后，改变配方不必重写处理流水线，也更容易辨别究竟改了哪部分实验。

混合比例还有一个细节：示例的 0.5/0.5 是 token 比例，不是样本数比例。原始字符串长度不同，直接等量抽样并不能得到等量训练 token。TokenEstimation 从小样本估计 token/字节比，调整计划以接近目标混合；它是估算工具，不能将示例权重理解为每个短窗口都精确一半。

每个算子可以设置自己的并行度，最耗时的分词用更多 worker，而不是强迫整个链条采用相同配置。为使这种调节不改变结果，Zephon 必须把顺序相关决策与昂贵计算分离。

## Accumulator 决策，worker 执行

每个算子包含一个按序看记录的单线程 accumulator，负责打包等状态决策；无状态函数把重计算分给多个 worker。工作组在派发前编号，虽然可以乱序完成，但交给下游前恢复原顺序。这样，提高分词并行度不必同时改变进入打包器的文档顺序。

这不是让有依赖的数据处理任意并行。顺序决策依然存在，只是让可并行的重工作围绕它展开。工程收益取决于计算与顺序部分的比例，以及结果重排、缓冲和进程通信的成本。文章中的完整视觉语言流水线包含图像解码、分词、打包与组批；作者报告 Zephon 能跟上所测最快的 Google Grain，同时提供更强的弹性确定性，但没有给出所有负载都更快的承诺。

文章与已有加载器的区别也集中在状态约束上：Mosaic Streaming 和 Google Grain 能在样本顺序可预先索引时保持跨卡数批次一致，但这不覆盖在线打包；Megatron-Energon 的对应能力要求所有 GPU 上加载 worker 总数保持不变。Zephon 将顺序决策固定在逻辑流内，使 worker 数量可以独立调整。这是原文针对相关模式的比较，不应扩展成这些系统不具备其他确定性能力。

## 用逻辑 lanes 承接状态

第二层拆分是把数据分配给固定数量的逻辑 lanes，而非直接绑定 GPU。每条 lane 持有自己的有序样本与打包、打乱状态。物理数据并行 rank 数量变化时，只重新分配 lanes；逻辑流不变，组合出的全局批次也保持不变。Accumulator 解决 lane 内的确定性，lanes 解决跨物理资源变化的确定性。

代价是提前选择 lane 数。它应是计划使用的数据并行规模的公倍数；若计划在 8、16、32 卡间切换，32 lanes 可覆盖这些配置，但并不允许任意数量的卡。TorchTitan 集成还检查 lanes 能否均分给副本，以及每步全局 batch 能否均分给 lanes。启动时拒绝不合适配置，比运行数小时后默默改变数据更容易诊断。

lane 数也不是越多越好。每卡负责的 lane 越多，恢复需要重建的工作越多。为偶尔可能出现的扩容预留过大的逻辑规模，会增加恢复开销；这需要结合实际可用的资源配置选择。

## 小检查点靠重放恢复，而非保存所有缓冲

在线打包和 shuffle 缓冲可能很大，直接序列化会增加检查点负担。Zephon 定期让 flush sentinel 通过流水线，要求有状态算子吐出持有内容并清空状态。检查点仅记录仍在处理的输入 chunk；恢复时从最近 flush 重放，重建状态，再丢弃训练循环已经消费过的输出。

作者实验中检查点为几 MiB，但这是通过重算换体积。它没有承诺零恢复时间，也不意味着 flush 对打包和吞吐没有代价。原文给出的是设计与示例，实际故障恢复仍需在目标配方、lane 数和数据访问成本下评估。Zephon 状态与模型一起进入 TorchTitan 检查点，恢复时保留所有 lanes 的进度。

## 实验把数据一致与数值一致分开

作者在 TorchTitan 训练 1B 模型，16 卡运行到第 150 步保存检查点，再分别用 8、32、64 卡恢复，并与原运行比较。标准加载器出现不同损失曲线；Zephon 的曲线重合，且每个全局 batch 的 SHA-256 与基准匹配。哈希验证的是批次内容，不能证明训练全过程逐位一致。

另一组从零训练 20B token 的实验比较 8、16、32、64 卡。标准加载器的 DCLM Core v1 分数跨度最高 0.82 分，FineWeb 评测跨度 0.64 分；Zephon 分别缩至 0.05 和 0.011 分。文章将前两者描述为相关数据筛选阈值约四倍，说明资源数量足以干扰小幅配方收益判断；这些仍是特定模型与设置下的实验。

原文图表通过官方交互页面嵌入，未取得适合本批静态发布且经过核验的原图，故不以重绘曲线代替。可在原文查看恢复损失、下游评测与吞吐图。

## 保证成立需要固定什么

弹性恢复要保持数据、tokenizer、seed、混合配方、上下文长度和全局 batch 大小不变；可调的是处理并行度等性能参数。GPU 数量变化仍会改变浮点归约次序，因此相同数据不等于权重和损失逐位相同。这个边界尤其适合自动实验系统：先排除输入序列这个混杂因素，再讨论数值噪声与模型质量。

文章还报告 Python 3.14t 的线程 runner 在所测视觉语言取样上比标准 Python 进程 runner 快约 3.7×，不能推广成整个训练快 3.7×；动态课程组件仍在开发。**优先读 lanes 与 flush/replay 的组合，以及 TorchTitan 的配置检查。** 它们把资源弹性与数据重现性连接起来，但在线预处理是否省成本，仍要同时考虑 CPU、I/O、恢复重放和 GPU 等待时间。
