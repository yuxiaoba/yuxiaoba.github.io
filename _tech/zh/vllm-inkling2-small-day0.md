---
id: vllm-inkling2-small-day0
title: 2026年11月13日｜Inkling 2 Small：混合精度之外，还要消除层间开销
date: '2026-11-13'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: vLLM 的融合边界、六头 GQA 打包和 prefill 序列并行，解释长上下文服务的性能条件。
long_read: true
source_url: https://vllm.ai/blog/2026-11-12-inkling2-small
permalink: /tech/zh/vllm-inkling2-small-day0/
translation_source: assistant
authorship: assistant
source_published_at: '2026-11-12'
published_at: '2026-11-13T08:46:43.062448+08:00'
updated_at: '2026-11-13T08:46:43.062448+08:00'
---
Inferact and Thinking Machines; work led by Aurick Qiao and Woosuk Kwon · 2026-11-12  
原文：[Inkling 2 Small on vLLM: Day-0 Support](https://vllm.ai/blog/2026-11-12-inkling2-small)

Inkling 2 Small 的 day-0 支持包含比“模型能跑起来”更具体的工程内容：混合精度缩小专家存储，层间融合减少隐藏状态往返，专用 attention kernel 修复形状变化触发的慢路径。它与本期 Rubin 优化同样强调数据移动，但这里的主要问题是新模型结构如何映射到已有执行路径。

## 哪些结构改变了执行成本

模型共 594B 参数、每 token 激活 17B，48 层按五层滑窗、一层全注意力的比例组织，384 个专家每次 top-8，无共享专家。前 40 层专家用 NVFP4，后 8 层用 MXFP8；图文输入由新的 23 层 ViT 处理，输出为文本。1M 上下文是容量能力，不意味着每种并发都能同时使用该长度。

block attention residuals 将历史六层块的输出按学习到的 query 混合，每层仍含短卷积；attention 输出还有 gate 与 sink。这让层与层之间出现更多需要读写同一隐藏状态的步骤。Four Over Six 量化则在每个 16 元素块上尝试将最大值缩放到 6 或 4，选平均绝对重构误差更小的方案。低精度不是简单把所有层压成同一种格式，执行必须保持逐层数值约定。

自带的五层 DSpark 草稿网络使用 RNN head，一步提出七个 token。提出长度不等于接受长度，后者仍取决于工作负载及采样条件。

## 融合 decode 边界，分摊 prefill 的重复工作

在 attention residuals 下，一个子层边界可能包含 all-reduce、短卷积、residual 更新、历史块混合和 RMSNorm。vLLM 将它们合进 allreduce_conv_mix：通过 NVLink multicast 完成归约后，尽可能把后续计算留在寄存器，减少多个 kernel 对相同数据的反复访问。PDL 允许后继 kernel 的准备工作与前一 kernel 尾部重叠，尤其适合小 batch 的长串短 kernel。

激活量化也融进产生激活的 routing 与 SwiGLU kernel，避免额外遍历。prefill 则用序列并行解决另一种浪费：普通 TP 在 all-reduce 后让每张卡都处理全部 token 的卷积、混合和归一化；新路径先 reduce-scatter，每卡只处理自己的 token 切片，再 all-gather 给下一次 GEMM。作者报告 8K-token prefill 步耗时在 TP4/TP8 分别降低 22%/26%，每 GPU 多出 1.3–1.9 GiB 供 KV 使用。

## 六个 query head 如何触发 attention 慢路径

模型每层 48 个 query heads、8 个 KV heads，GQA 比例为 6:1。原先的 FlashAttention-4 decode 路径在这一比例下未启用 GQA packing，使同一 KV 的复用不够高效。

新的 Gluon kernel 把六个 query heads 放进一个 64-row tile，让 KV 只读取一次；TMA warp 流式加载 KV，tcgen05 warp 执行 MMA，四个 softmax warp 处理 relative bias。作者测得 batch 1、100K 上下文的 decode 步从 15.1 毫秒降到 4.8 毫秒。该数字绑定长上下文与特定路径，不能替代整个模型在任意长度的提速。

原文层级架构与融合图采用交互式嵌入，本页没有可直接使用的静态机制图，因而保留文字说明。

## 长上下文结果需要连同缓存命中率看

服务实验使用 TP8、两个四 GPU 节点，开启 DSpark 概率起草与前缀缓存。每轮追加上轮回答及约 2K tool output，新增约 3K token，然后以 temperature 1.0、开启 reasoning 生成 1,024 token。作者在每用户约 100 tokens/s 的运行点报告：32K 会话上下文时，每 GPU 输出约 1,070 tokens/s、约 84 并发会话、91% 命中率；256K 时约 450 tokens/s、37 会话、99% 命中率。

这些是**输出吞吐**，不能与 Rubin 报告包含缓存输入的总 token 数直接比较。TP4 单用户约 630 tokens/s、接受长度 3.5，又是另一运行点；七个草稿 token 并未全部被接受。

作者称保留参考实现各步 dtype，仅归约顺序和 all-reduce 的 BF16 partials 等存在差异，并在 NIAH 至 1M、MMMU-Pro 与 HLE 上比较开启或关闭 DSpark，分数相符。文章未列出完整逐项分数，不能将此扩大成所有提示词逐 token 等价。对于推理工程，最值得关注的是：新模型的 GQA 比例、残差结构和量化方式会触发旧 kernel 的隐藏假设，day-0 支持的质量应看这些路径是否被真正处理。
