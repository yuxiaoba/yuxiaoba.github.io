---
id: inference-optimisation-skill-2026-11-20
title: 2026年11月21日｜本地推理调优怎样识别一次真正的提速？
date: '2026-11-21'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: 同一块显卡上的两个速度数字，未必能说明哪项改动有效。
translation_source: assistant
writing_source: assistant
long_read: true
source_url: https://github.com/sybil-solutions/inference-optimisation-skill
permalink: /tech/zh/inference-optimisation-skill-2026-11-20/
published_at: '2026-11-21T08:47:17.687323+08:00'
updated_at: '2026-11-21T08:47:17.687323+08:00'
---
同一块显卡上的两个速度数字，未必能说明哪项改动有效。sybil-solutions 将本地推理调优写成一个可供智能体执行的实验流程，从估算上限、交错对照，到满缓存稳定性验收。项目的记录里，最容易被忽略的结果是某些目标从一开始就超出了硬件和草稿接受率允许的范围。

sybil-solutions · 2026-11-16 · [inference-optimisation](https://github.com/sybil-solutions/inference-optimisation-skill)

## 先判断哪段仍有优化空间

流程用实测带宽、每 token 读写字节、计算量和组件大小估计解码、预填充以及 KV 容量的上限。B390 集成显卡上，Ornith 的 256K 预填充已达 628 tok/s，估计上限约 670–684 tok/s。同一设备上，单用户解码若想冲到 100 tok/s，需要连续有效的投机草稿；深度 2 的接受率约 14%。作者据此下调目标。两项结果在同一台机器上，一个接近带宽和计算估计，另一个受到草稿有效性的额外限制。

## 让候选夹在两个对照之间

每次只改一项配置，串行运行原配置、候选、原配置。候选必须超过前后两个对照，且其他指标回退不超过流程设定的 3%。这样，预热、温度或运行时漂移较难伪装成持续收益。脚本使用服务端 usage 统计 token，避免把流式返回的文本块数当作 token 数；失败请求、循环输出和每次配置都写入记录。对于统一内存设备，驱动驻留也影响真实占用，仅看容器账面内存会高估余量。

## 快速配置还要能取回长上下文

长上下文检索检查与并发满 KV 持续负载安排在接收候选之后。其作用是发现短提示速度测试看不见的错误，例如容量看似增加却再也取不回远处的信息。最后从固定版本干净构建重新做验收，防止开发环境特有的改动混入成绩。

B70 上 Qwen3.8-27B 的单用户解码记录为 llama.cpp Q4_K_M 25.0 tok/s、vLLM 加自定义 XPU 内核和 EXL3 4 bpw 为 91.2 tok/s。两者同时改变引擎、内核和量化，只能作为两套可运行配置的比较。更能说明交付影响的是同一项目还追踪智能体会话回放，记录耗时从 193 秒缩到 147 秒；它把吞吐之外的提示处理和多轮等待也纳入了观测。
