---
date: '2026-11-26'
published: true
layout: article
maintenance: daily-research
translation_source: assistant
id: pytorch-vllm-singapore-meetup-2026-11-25
title: 2026年11月26日｜vLLM 的长前缀预填充为何会受益于流水线并行
lang: zh
source_type: tech
long_read: true
source_url: https://pytorch.org/blog/vllm-singapore-meetup-faster-prefill-agent-written-kernels-and-the-road-to-vera-rubin/
tags:
- inference-serving
permalink: /tech/zh/pytorch-vllm-singapore-meetup-2026-11-25/
summary: 从 GB300 预填充、SM12x 分派到视频会话缓存，按硬件与时延目标读 vLLM 实测。
published_at: '2026-11-26T08:45:51.058767+08:00'
updated_at: '2026-11-26T08:45:51.058767+08:00'
---
一次携带约十万输入 token 的智能体请求，即使前缀命中约 95%，仍有约五千个新 token 要在首 token 时限内处理。11 月 13 日的新加坡 vLLM 技术聚会给出了一组对照：当目标是不断处理这类新输入时，拆分模型的方式、队列中的微批大小，以及负责搬运激活的硬件都会改变结果。

## 少做集合通信也会带来流水线空档

Thien Tran 的报告把两张 GB300 上 MiniMax-M3.1-Flash 的两级流水线 PP2，与双卡 TEP2 加序列并行比较。流水线把不同阶段放在不同卡上，减少和计算争抢资源的集合通信，最高吞吐达到对照的 1.37 倍。但单个微批要走过两级，刚开始和接近结束时都会有一级空闲。把层数平均分给两张卡，也不保证两级耗时相等，最慢的一段会限制整条流水线。

团队按实测耗时分配阶段，并限制每个调度步的规模以缩短填充和排空。随后把阶段间激活传输交给拷贝引擎，在接近饱和时让首 token 中位延迟下降 13%–20%。固定调度步长时，0.75 秒的严格首 token 目标仍由对照布局占优；允许更长等待，流水线才有足够工作摊薄空档。新的调度器按队列决定微批大小，让 PP2 在报告中从约 0.5 秒目标起占优。读取吞吐结果时，首 token 约束应和硬件一起保留。

## 内核是否被调度到，比内核是否存在更早决定性能

Jie Fang 展示的是另一类平台。SM12x 工作站卡之间走 PCIe Gen5，没有上述 NVLink 条件。对 DeepSeek 路径，一行分派修正让实际运行选中合适实现，吞吐增加 17.7%；优先使用 W4A4 处理 NVFP4 线性层的另一项调整报告增加 23.8%。这是两项独立变更的结果，不能直接相加。在该平台上用 TP2 × PP2 替代 TP4，预填充吞吐达到 1.37 倍。这里数字与 GB300 案例相同，机型、布局和基线却都不同。

这也解释了为什么“某后端已支持”很难回答部署问题。计算图实际进入哪个分支、跨卡激活走什么互连，以及内存访问是否接近设备实测带宽，决定了新增内核能不能影响用户等待时间。

## 交互式视频让缓存跨越一个请求

vLLM-Omni 的报告从另一个角度解释如何选择执行路径。普通扩散请求结束即可释放其中间状态；交互式世界模型还要沿用前几个视频块的历史。团队为后一类模型设计 AR-Diffusion 引擎，复用分页 KV 管理器，按块生成，并在整个会话中保存需要的状态。LingBot-World 2.0 的实验使用四张 H200、一个会话。Ulysses 序列并行让单块耗时从 2,397 毫秒降至 725 毫秒。

报告对每个 12 帧块给出了两个工作点：主线实现较九月版本快 1.9 倍，并报告保持质量；开启全部可选优化后达到 22.5 fps、约 2.75 倍加速。后一个数字不能继承前一组的质量条件。它也描述单会话实时性，没有测出许多用户同时交互时的吞吐。三组报告串起来，最值得保留的测量口径是工作何时就绪、数据需要保留多久，以及结果覆盖一个内核、一个请求还是整条会话。


Ebba Simpson · 2026-11-25 · [vLLM Singapore Meetup: Faster Prefill, Agent-Written Kernels and the Road to Vera Rubin](https://pytorch.org/blog/vllm-singapore-meetup-faster-prefill-agent-written-kernels-and-the-road-to-vera-rubin/)
