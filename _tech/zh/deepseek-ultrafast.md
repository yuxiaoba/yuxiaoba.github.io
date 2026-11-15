---
id: deepseek-ultrafast
title: 2026年11月15日｜DeepSeek Ultrafast：投机解码与跨机 KV 状态
date: '2026-11-15'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: 拆解特定编码任务上的解码数据、Redis 所有权目录与 RDMA 缓存传输，以及模型、硬件和接口限制。
translation_source: assistant-authored bilingual content
long_read: true
source_url: https://github.com/basetenlabs/deepseek-ultrafast
permalink: /tech/zh/deepseek-ultrafast/
published_at: '2026-11-15T15:30:22.801784+08:00'
updated_at: '2026-11-15T15:30:22.801784+08:00'
---
DeepSeek Ultrafast 的看点分成两层：一层用投机解码降低生成一段代码的等待时间，另一层让多轮对话的 KV 状态能跨服务副本续接。前者决定一次解码步能产出多少 token，后者决定下一轮请求换机器后是否必须重新处理长提示。把两者分开，才能读懂高解码速度与百万 token 上下文的实际含义。

来源：[DeepSeek Ultrafast](https://github.com/basetenlabs/deepseek-ultrafast) · Baseten · 2026-11-13 官方公告；以下机制依据仓库快照 `76766a97308b`。

## 特定模型和硬件上的执行路径

这是面向 DeepSeek-V4.1-Flash 的 Rust 与 CUDA 引擎，支持 `sm_100a` 和 `sm_103a`，文档要求 CUDA 13，以及指定的 B200、B300 或 GB300 多卡配置。它不是一个针对所有模型、所有 GPU 的通用性能承诺。仓库按 CUDA、kernel、model、engine、server 和 KV transfer 分层，服务层将引擎封装为兼容常用客户端的 HTTP 接口。

“从零写”也不意味着没有依赖。README 列出 deepseek-recipe 负责提示渲染与响应解析、tokenizers 负责分词、cuDNN／cuBLAS 用于视觉编码器、OpenCV 解码图像、Velo 处理 RDMA 传输。作者还说明，编码 Agent 优化 kernel 时可参考 FlashInfer 与 SGLang 源码。需要区分运行时实现、第三方组件和开发过程中的参考材料。

## 解码速度由步耗时和接受长度共同决定

每个 decode step 先草拟一块 token，再执行验证；成功接受的 token 可以在同一步输出。因此，3.30 ms 的 step time 并不意味着每次只生成一个 token。README 给出的平均接受长度为 5.6 token/step，块式生成正是高输出速率的关键解释。接受长度会随请求内容变化，不能把一个 demo 的速率当作固定模型常数。

| 作者报告的设置 | 4×GB300，TP4 | 8×B300，TP8 |
| --- | --- | --- |
| 解码输出速度 | 1,740 token/s | 2,060 token/s |
| 每步耗时 | 3.30 ms | 2.71 ms |
| 1,000,000 token prefill | 13.2 s | 11.7 s |

解码数据来自“生成 Tetris 游戏并直接输出 HTML”的特定请求，复现示例关闭 thinking。30 次运行中，TP4 的步耗时为 3.24–3.37 ms，接受长度为 5.1–6.1；TP8 分别为 2.69–2.74 ms 和 5.3–6.1。文档提供 `average_iteration_ms` 与 `average_accept_length` 日志，能够把变化拆到执行速度和接受效率两部分。

示例客户端从首个文本输出到流结束计算 token/s，并单独打印首输出等待时间，所以这些速率不包含最初等待，也不是高并发服务的总吞吐。百万 token prefill 是另一项测量，不能据此推断百万上下文下仍有相同 decode 速度。README 未给出覆盖多任务、长上下文和并发负载的完整性能矩阵。

## Redis 管所有权，RDMA 搬缓存内容

服务将近期会话的 KV cache 保存在主机内存。下一轮请求若落到其他副本，接收方可查询哪个副本持有状态，再通过 RDMA 将缓存从远端主机内存搬到本地，减少重算提示的开销。Redis 保存的是所有权目录并广播变更，缓存主体并不经过 Redis。其设计意图是减少对前缀感知路由的依赖，让负载均衡不必总把会话绑在一台机器上。

多轮请求必须携带会话 ID；没有 ID 的多轮请求会返回 400。更重要的是，共享状态要求模型、tokenizer、最大序列长度、GPU 数量和解码数值配置一致。`peer.rs` 将配置摘要、tokenizer 摘要、TP 大小与数值路径等信息写入缓存 profile 指纹，用于区分兼容状态。TP4 和 TP8 都支持，并不意味着两种配置之间可以随意交换快照。

目录实现还用 epoch 与递增序号描述所有权版本。查询、认领与检查通过原子 Lua 脚本完成；认领时若期望版本已经过时，就返回 stale 错误。Redis 重启后新的 epoch 使旧所有权版本失效。这里处理的是缓存位置与所有权有效性，不能把“缓存提示丢失而模型状态不丢失”理解成所有进行中请求都能无损恢复。

## 接口兼容和容量边界影响 Agent 接入

服务文档给出的默认容量是 1,048,576 token，包含提示和输出，还需留出投机解码余量。HTTP 请求体上限为 64 MiB，与 token 容量是两个不同限制：JSON 转义、工具历史和图像描述都会影响传输大小，足够大的上下文窗口不保证请求体一定能通过。

接口也不是所有客户端功能的完整替代。当前文档固定 temperature 与 top_p 为 1，拒绝其他值；不支持的 logprobs、结构化输出控制及工具定义的 `strict: true` 会在入队前报错。系统提供工具调用解析，不负责执行客户端工具。需要这些控制的 Agent harness，可能在性能比较之前就遇到协议兼容问题。

## 该如何判断这次发布

值得关注的是将低延迟解码与可迁移的会话状态放进同一个实现，并公开步耗时、接受长度和缓存兼容规则。当前证据支持特定编码请求上的作者实测，以及代码和文档所描述的状态管理机制；尚不足以声称普遍快于其他推理引擎，或证明 Redis／RDMA 异常下的端到端可靠性。

许可文件为 Elastic License 2.0，包含不得向第三方提供覆盖软件实质功能的托管或管理服务的限制，应称为 source-available，不能仅沿用社交公告里的“open-source”。仓库提供的是游戏演示 GIF，没有合适的缓存或执行架构图，本文用机制说明与测量表呈现，避免把演示画面当作设计证据。
