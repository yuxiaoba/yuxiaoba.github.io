---
id: review-anthropic-provable-inference
title: 2026-11-04｜FlashProve：模型来源证明的性能与信任边界
date: '2026-11-04'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://www.anthropic.com/research/provable-inference
tags:
- agent-reliability
- self-improvement
- observability
- inference-serving
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-anthropic-provable-inference/
---

FlashProve 的问题是“哪个承诺的模型执行了这次计算”，而不是回答是否正确。提供者先对权重做隐藏承诺，再为请求生成 zkSNARK，持有承诺、输入和结果的人无需取得权重即可检查。系统隐藏权重与专家选择，但不以隐藏架构为目标；证明实际服务了获准模型，也不证明服务器没有同时执行其他工作。

实现采用事后证明：先完成文本，再按类似 prefill 的并行路径重算，被使用的 MoE 专家决定主要证明工作。权重分段从主机流入，允许单 H100 配合大量主机内存运行。测试采用 4-bit Llama 4 Maverick 与整数算术；每个请求含 1024-token 窗口，但每份证明只检查一个 token。24 个请求证明耗时约 223 秒，所谓 110 token/s 是上下文处理吞吐，不能写成每秒证明 110 个新生成 token。单份证明约 18.78MB，24 线程 CPU 检查约 17 秒；离线承诺还需约 39 分钟，并有可服务请求数上限。

可信边界同样重要。Lean 中形式化了随机 oracle 模型下的顶层性质，并提供有 soundness 联系的可执行 Lean verifier。日常 C++ verifier 只在测试中与其一致，本身没有该形式化保证；证明器代码与形式协议的对应关系仍需审计，尤其涉及零知识。顶层形式陈述是否符合意图也必须由人检查。

作者相对 FP8 vLLM 报告约 72–94 倍 GPU 时间开销。这不是零开销在线签名，也不是相同数值格式的纯 kernel 对比。适合继续研究的方向是低比例事后抽查、模型承诺生命周期，以及证明延迟与不可逆外部动作之间的时间窗口。代码库明确标为研究产物且不维护；这里没有运行证明、检查 Lean 构建或独立审核密码协议。

证明只涉及声明的量化、算术和协议，不保证原始浮点模型、事实正确性或整段响应的未抽查 token；高开销、事后延迟和实现对应关系仍是部署限制。

来源：[Progress on provable inference for large language models](https://www.anthropic.com/research/provable-inference)

实现与说明：[FlashProve](https://github.com/anthropics/FlashProve).

[Progress on provable inference for large language models](https://www.anthropic.com/research/provable-inference)
