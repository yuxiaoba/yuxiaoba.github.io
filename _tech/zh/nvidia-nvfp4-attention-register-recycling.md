---
date: '2026-11-26'
published: true
layout: article
maintenance: daily-research
translation_source: assistant
id: nvidia-nvfp4-attention-register-recycling
title: 2026年11月26日｜SM120 上的 NVFP4 注意力如何腾出半块寄存器
lang: zh
source_type: tech
long_read: true
source_url: https://developer.nvidia.com/blog/how-to-optimize-nvfp4-attention-on-nvidia-rtx-blackwell-through-register-recycling/
tags:
- inference-serving
permalink: /tech/zh/nvidia-nvfp4-attention-register-recycling/
summary: 分数打包后复用寄存器，让下一块矩阵乘与当前块交错执行。
published_at: '2026-11-26T08:45:51.058767+08:00'
updated_at: '2026-11-26T08:45:51.058767+08:00'
---
在 RTX PRO 6000 Blackwell 上，更低精度的矩阵乘法可以很快，但一块注意力分数还没用完，下一块就没有地方存。NVIDIA 的优化抓住了一个短暂的空位：一半分数已经打包成概率，另一半仍在做 softmax。此时便可启动下一块的部分矩阵乘。

## 计算有空档，寄存器却几乎已满

在 SM120 上，SageAttention3 用 NVFP4 计算查询与键的乘积 QK，再把 softmax 权重与值相乘得到 PV。概率值集中在很窄的范围内，先调整范围再量化能更充分使用低精度编码。原调度对每个 128 列的块依次执行 QK、softmax、缩放量化与 PV。做指数、缩放和整理数据时，消费线程仍在工作，Tensor Core 却出现空档。

每个线程块有四个生产者 warp 和八个消费者 warp。前者负责异步搬运，后者执行矩阵乘与中间计算。两组合计使用 62,464 个寄存器，约占一个 SM 容量的 95.3%。再分配一个完整的分数块会撞上容量限制。搬运端仍以完整块读取才能维持带宽，因此简单把所有操作的块尺寸减半，同样要付代价。

## 保留整块归一化，提前复用半块分数

优化只改变中间分数的存放与计算顺序。每次仍取完整的 128 列 K/V，分数却分成两个 64 列寄存器槽。先观察当前完整块的最大值、更新在线 softmax 状态并调整已有输出累加器，这一步必须在使用任一半块之前完成。随后第一半完成指数与 NVFP4 概率量化，后续 PV 读的是打包后的概率，原来的分数寄存器已经可以覆盖。

调度器就在这里把下一块前 64 列的 QK 写进刚释放的位置，同时推进当前块的 PV 和另一半的量化。第二个槽按相同方式交接。到下一轮开始，两个槽里已经装好下一块的分数。首块先填充，末块只消费，稳态中相邻块交错。这个细节解释了为什么既可以减少矩阵单元空闲，又无需双份完整的分数缓存。

## 核心加速与整段视频时间各比较什么

Reactor 在 96 GB RTX PRO 6000 Blackwell Server Edition 上对比两个 NVFP4 内核。两边使用相同的 Q/K/V、相同的打包数据和 log-sum-exp 设置，批量为 1，24 个头，头维度 128。8,192 token 的合成因果输入从 0.76466 毫秒降至 0.46659 毫秒，达到 1.64 倍；取自 LongLive 的 7,040 token 非因果输入则是 1.18 倍。核心计时排除了输入量化与输出布局恢复。

服务侧采用另一组对照：在同一模型的完整生成路径上，把指定注意力调用从 BF16 换成优化后的 NVFP4，其余权重和部分注意力保持 BF16。OmniDreams 的移动场景生成 2,045 帧、256 个 chunk 时，预热后的耗时从 155.92 秒降至 132.00 秒，下降 15.34%；Helios 的 33 帧场景只替换最大自注意力调用时为 1.70%。前者每组一个进程，后者取三个独立进程的中位数。端到端比较同时改变了精度和内核，不能把全部收益归到寄存器调度；报告的延迟表也不能替代输出质量评估。


Atharva Joshi · 2026-11-25 · [How to Optimize NVFP4 Attention on NVIDIA RTX Blackwell Through Register Recycling](https://developer.nvidia.com/blog/how-to-optimize-nvfp4-attention-on-nvidia-rtx-blackwell-through-register-recycling/)
