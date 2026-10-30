---
id: vllm-mistral-large-4
title: 2026年10月30日｜vLLM 如何支持稀疏注意力与跨层 KV 共享
date: '2026-10-30'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Mistral Large 4 的 vLLM 支持展示了模型结构与服务系统如何共同决定长上下文性能：稀疏索引减少注意力读取，跨层共享减少缓存写入，服务端还要处理并行、图执行和分离式传输。
long_read: true
source_url: https://vllm.ai/blog/2026-10-29-mistral-large-4
permalink: /tech/zh/vllm-mistral-large-4/
translation_source: assistant-authored paired Chinese/English reading notes
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-10-30T10:31:20.339125+08:00'
---
Mistral Large 4 的 vLLM 支持展示了模型结构与服务系统如何共同决定长上下文性能：稀疏索引减少注意力读取，跨层共享减少缓存写入，服务端还要处理并行、图执行和分离式传输。

**来源：** vLLM，[Day 0 support for Mistral Large 4 on vLLM](https://vllm.ai/blog/2026-10-29-mistral-large-4)，2026 年 10 月 29 日。

模型采用 72 层 MoE，注意力结合 MLA 和 DSA 索引器，每个查询选取最多 2048 个键。九个 NoPE 层读取第 35 层的 latent KV，而不再各自写入缓存；vLLM 的 V2 runner 将这些消费者映射到目标层缓存，72 层中 63 层拥有自己的缓存。文章指出该机制正在作为通用能力上游化。

长上下文下，decode context parallelism 将 latent KV 分片到多个 rank；作者在 TP8 配置下报告约 7.9 倍 KV 容量，结合 prefill context parallelism 时首 token 时间最高降低 1.6 倍。内置 DSpark drafter 在文中 TP8 测试中每步接受约 2.9 个 token，输出吞吐约为原来的 2 倍。服务还支持 NIXL prefill/decode 分离，以及 HiSparse 的主机内存稀疏 KV 卸载和跨层共享。

这些数字对应文章所述模型与配置，并非所有工作负载的普遍收益。真正值得跟踪的是共享 KV、稀疏索引和并行方式的组合：它们既改变缓存占用，也改变不同阶段的通信与执行路径。
