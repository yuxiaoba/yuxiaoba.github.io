---
id: deepseek-v41-flash
title: 2026年10月7日｜DeepSeek-V4.1-Flash：五倍吞吐背后的重放与内核优化
date: '2026-10-07'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: 拆解 SWA 有界重放、CUDA graphs、融合内核与并行策略，解释 AgentX 性能改善及其条件。
long_read: true
source_url: https://blog.vllm.ai/blog/2026-10-07-deepseek-v41-flash
permalink: /tech/zh/deepseek-v41-flash/
authorship: assistant
translation_source: assistant
published_at: "2026-10-20T09:29:16.460712+08:00"
updated_at: "2026-10-20T09:29:16.460712+08:00"
---
DeepSeek-V4.1-Flash 在 vLLM 上的进展，值得关注的是模型结构与服务实现一起优化。官方文章报告，相比发布首日，低并发交互速度提升约 1.9 倍，高吞吐配置约 5.3 倍。背后既有少算一部分 prefill，也有缓存表示、CUDA graphs、内核融合和并行策略的调整。要理解倍率，必须沿着请求的执行路径拆开看。

原文：[DeepSeek-V4.1-Flash on vLLM: 5x Agentic Throughput Since Day 0](https://blog.vllm.ai/blog/2026-10-07-deepseek-v41-flash)  
Inferact and the vLLM Team · 2026-10-07

## 先分清两类缓存的成本

V4.1 的因果编码器—解码器架构在 decode 时每 token 激活 16B 参数，prefill 为 8B。全局 KV 经过压缩、FP4 存储和跨层共享，约占每 token 890 字节；滑动窗口注意力（SWA）的 KV 则以未压缩 FP8 保存，覆盖 40 层各自最后 128 个位置。全局状态很小，不代表前缀缓存整体也便宜。

如果每个可能命中的前缀边界都保存 SWA 状态，它的存储成本会超过全局 KV 的十倍。另一边，旧 prefill 路径让第 21–39 层处理整个提示，而解码只读取这些层末尾的 128 个位置，长提示的大量工作没有直接留下可用窗口。缓存存太多与计算做太多，是两个相关但不同的问题。

## 用有界重放换空间与计算

直接重算 SWA 可以省存储，但精确重建有跨层依赖：上层窗口依赖下一层更早的位置，穿过 L 层大约要回放 L×128 个 token。有界重放只处理最后 128 个 token，并把各层窗口截在重放起点，因此结果不是逐位等价。这是有质量取舍的近似，不能理解成仅改变存储位置。

编码器侧在长度 H 的前缀命中后，只保留并读取全局 KV，再重放区间 [H−128, H) 来重建 SWA。它用一次窗口计算换取缓存空间。解码器侧利用第 20 层生成全局 KV、第 21–39 层共享这份 KV 的结构：第 20 层仍覆盖所有 token，后续层只处理最后一个窗口。长提示因此跳过接近半个模型的 prefill 工作。

两侧收益来源不同：命中后的重放本身增加计算，直接省时主要来自解码器裁剪。默认启用的 `--[no-]swa-bounded-replay` 选项控制这条路径；原文在 GSM8K、GPQA 等测试上观察到的准确率差距约在 1.5 个标准误以内，支持这些测试上的小差异，不能证明所有长程 Agent 任务都保持等价。

## 少算以后，启动开销可能成为主角

裁剪后的第 21–39 层 GPU 工作很少，逐个启动内核会让 CPU 调度成本盖过省下的计算。其输入形状也与前半段不同，不能简单捕获成同一张 CUDA graph。vLLM 利用可中断的 PIECEWISE graph，将第 0–20 层的完整批次与后半段裁剪批次分开捕获，分别选择覆盖尺寸。

单请求 prefill 实验在 NVIDIA GB200 上进行，关闭前缀缓存，取三次运行中位数。重放结合 CUDA graphs 将 prefill 计算时间降低约 30–40%；没有后半段图捕获时，DEP2 的 1K 提示甚至比关闭重放慢最多约 12%。这说明算术工作减少并不等于端到端等待同比减少，短提示尤其依赖发射开销是否被压住。

## 融合内核，缩短真正的关键路径

另一组改动减少中间结果写回和多次启动。Mega-mHC 把 post、延迟的 pre 和 RMSNorm 合并，在 GB200 上比旧 TileLang 路径快 1.14–1.51 倍。Mega-Gate 合并路由矩阵计算、评分、偏置和 top-k，中等批量的内核加速为 1.18–1.31 倍。它们是局部算子数字，不能直接相乘得到整机收益。

稀疏索引器只对固定的 16K 候选位置打分，避免随整个上下文增长。GB300 上，512K 上下文的单层加速可达 14–23 倍，但四张 GB300 的端到端 decode 改善是 3–6%。这个差距很有解释力：被优化的操作只占执行链的一部分，其余阶段仍消耗时间。

MegaAttention 将 RoPE、稀疏注意力、逆 RoPE 和 FP8 转换融合，直接写入后续投影所读的缓冲区；新的 NVFP4 压缩 KV 格式比此前 FP8 版本小 45%。此外，小批量路径把 mHC 系数计算放到独立 CUDA stream，与 attention/FFN 重叠，TP4 低延迟场景约省 4%。这些优化分别作用于数据搬运、缓存容量和关键路径，收益也随负载改变。

Engram 又呈现另一种瓶颈：它按 token n-gram 的哈希，从两张大型 FP8 表里查少量行，成本更多在查找延迟与表的放置，而非大量乘法。vLLM 异步预取卸载到 CPU 的表项，并与解码计算重叠；同一主机上的数据并行副本共享表，减少重复占用。透明大页能降低相关内存管理开销，文章报告 prefill 查找内核最高约十倍加速。这个结果同样只属于查找路径，不能替代整轮 Agent 延迟。

这些细节说明，融合不是把所有算子无条件并在一起。某些工作适合在单内核内保留中间值，另一些可以独立放到侧流执行，还有一些需要提前从主机取回。要选择哪条路径，先要知道数据依赖何时满足、计算与访存谁占主导，以及不同批量下是否仍有重叠空间。

## 为什么低延迟与高吞吐选择不同配置

<a class="note-image-link" href="/assets/images/tech/deepseek-v41-flash/agentx-results.png" target="_blank" rel="noopener" aria-label="GB300 NVL72 上发布首日与优化后吞吐及 P90 交互速度曲线 · 查看原图 ↗"><img src="/assets/images/tech/deepseek-v41-flash/agentx-results.png" alt="GB300 NVL72 上发布首日与优化后吞吐及 P90 交互速度曲线" loading="lazy"><span class="note-image-action">查看原图 ↗</span></a>

*读图：同一用户生成速度下向上比较每芯片吞吐；每条曲线最右端比较最高交互速度。图中 5.3 倍对应约 155 token/s/user，而正文概括为 150 TPS 约束。*

官方 AgentX 图比较 9 月 11 日与 10 月 2 日的最优配置，硬件为 GB300 NVL72。图中在约 155 token/s/user 的 P90 交互速度处，每芯片吞吐从约 27K 升到 144K token/s；最高交互速度则从 311 升到 599 token/s/user。两条箭头比较的是不同目标，不能同时视为同一工作点的收益。

低延迟配置采用 TP4 和 FlashInfer attention，将权重分摊到四卡，适合受内存带宽约束的小批量 decode。高吞吐配置切到 DEP2，使用数据并行 attention 并跨 GPU 划分专家；各卡只为自己服务的请求保存 KV，避免张量并行重复缓存。会话亲和性维持跨轮前缀局部性，MegaAttention 的 NVFP4 又进一步增加并发容量。

<a class="note-image-link" href="/assets/images/tech/deepseek-v41-flash/ttft-vs-throughput.png" target="_blank" rel="noopener" aria-label="GB300 NVL72 上每芯片吞吐与 P90 首 token 时延曲线 · 查看原图 ↗"><img src="/assets/images/tech/deepseek-v41-flash/ttft-vs-throughput.png" alt="GB300 NVL72 上每芯片吞吐与 P90 首 token 时延曲线" loading="lazy"><span class="note-image-action">查看原图 ↗</span></a>

*读图：固定吞吐后向左比较等待时间。图中约 94K token/s/chip 的标注为 1.86→0.32 秒、约降 83%；正文在约 100K 吞吐处描述近 70%，应保留各自比较点。*

## 怎样理解服务层的收益

图中的 P90 交互速度以每用户每秒 token 衡量，首 token 时延则以秒衡量；吞吐另按每芯片归一化。它们回答不同问题：生成过程中是否足够流畅、开始等待是否足够短，以及设备总共承接多少工作。高吞吐点可能让每个用户等待更久，所以比较时应固定交互或时延目标，再看能服务多少负载。

单请求关闭前缀缓存的实验，主要展示裁剪与图捕获的计算效果；多轮 AgentX 则涉及前缀局部性、容量和调度。两类证据互相补充，但无法用前者的三次运行中位数替代后者的尾部体验，也不能将不同硬件上的局部内核倍率拼成一个预测值。更值得跟踪的是这些路径在短提示、长上下文和不同并发区间如何切换。

这组结果包含配置切换和多项优化，并非只打开一个开关的消融。文章还说明，该基准全程不需要 KV 卸载；更高并发、prefill/decode 分离下可能受益于卸载，目前属于后续预期。适合优先阅读的是重放依赖、图捕获边界和配置选择：它们解释了为何模型结构允许的省算，仍需要缓存与执行调度配合才能转化为服务吞吐。
