---
id: tensorrt-edge-llm-spark
title: 2026年11月1日｜端侧推理的生成加速，不等于首 token 更快
date: '2026-11-01'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: TensorRT Edge-LLM 的 DGX Spark 实测显示 DSpark 提升生成速度，但首 token 延迟近乎不变。
translation_source: assistant
authorship: assistant
long_read: true
source_url: https://developer.nvidia.com/blog/run-ai-models-for-edge-application-development-with-just-a-few-commands/
permalink: /tech/zh/tensorrt-edge-llm-spark/
published_at: '2026-11-01T08:44:13.804154+08:00'
updated_at: '2026-11-01T08:44:13.804154+08:00'
---
[Run AI Models for Edge Application Development with Just a Few Commands](https://developer.nvidia.com/blog/run-ai-models-for-edge-application-development-with-just-a-few-commands/) · Joe Halabi, Lin Chai, Maximilien Breughe, Michael Ferry, Charlotte Mallo · NVIDIA · 2026-10-30。

TensorRT Edge-LLM 用轻量 C++ 运行时连接 DGX Spark 开发与 Thor 系列部署，CLI 负责下载模型、构建或复用匹配引擎，并提供本地兼容 API。本文最有信息量的是 DSpark 推测解码的条件实测：草稿模型先提出三个 token，由主模型验证。

在 DGX Spark 64GB、Nemotron-3.5 Lightning NVFP4、thinking 开启、batch=1、单并发流式请求、输出上限 128 token 下，HumanEval 提示的平均生成速率从 73.4 升至 126.9 tok/s，TTFT 中位数却从 98.1 变为 98.7 ms。SpeedBench 1K/2K 的生成速度分别从 73.3/72.8 升至 108.5/105.3 tok/s，TTFT 为 201.0/329.5 → 203.0/331.6 ms。

生成速度排除首 token 时间；三组平均输入长度为 139、1,153、2,247 token，DSpark 开启时含操作系统的峰值总内存为 27.9GB。它说明低并发生成阶段可能获益，不能直接推断高并发服务、长输出或 Thor 设备上的收益。原文没有适合解释核心机制的架构图，本篇以实测条件为主。
