---
id: vllm-torchtpu
title: 2026年10月21日｜vLLM TorchTPU：复用服务控制层，把硬件适配放进后端
date: '2026-10-21'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: 插件复用 vLLM 模型、调度与 KV 管理，以 TPU 编译、Pallas kernel 和状态传输支撑新硬件上的服务。
long_read: true
source_url: https://blog.vllm.ai/blog/2026-10-20-vllm-torchtpu
permalink: /tech/zh/vllm-torchtpu/
authorship: assistant
translation_source: assistant
published_at: "2026-10-21T13:08:08.256303+08:00"
updated_at: "2026-10-21T13:08:08.256303+08:00"
---
Inferact and Google Teams · vLLM · 2026-10-20  
原文：[Introducing vLLM TorchTPU](https://blog.vllm.ai/blog/2026-10-20-vllm-torchtpu)

vLLM TorchTPU 的价值在于把新的 TPU 执行后端接到已有服务系统下面。模型定义、请求 API、调度器和 KV cache 管理不必另建一套，硬件差异由平台插件、编译路径和专用 kernel 承担。对需要服务快速更新的开源模型的团队，这种组织方式可能比单个算子加速更有意义：模型更新可以沿共享代码进入不同硬件。

但共享上层代码不意味着各种 GPU 配置能原样获得最佳 TPU 性能。原文分别讨论并行维度、缓存迁移和硬件验证状态，说明真正可用的服务仍需要把逻辑行为、设备布局与运行时状态一起安排。它是一份功能与架构发布说明，未提供统一条件下的端到端性能对照表。

## 插件把变化限制在哪一层

vllm-torchtpu 是仓外平台插件，通过 vllm.platform_plugins 入口被发现。模型走标准 model runner，再由 torch.compile 的 tpu backend 下降到 XLA；每 TPU 设备一个 worker 进程，设备之间用 torch.distributed 通信。调度、worker 框架、KV 管理器和 API server 继续复用上游。

专用操作以 custom op 接入编译图，复杂计算主要由 JAX/Pallas kernel 实现。原文列出分页 attention、稠密及稀疏 MLA、Gated DeltaNet、Kimi Delta Attention、专家并行 MoE，以及 FP8、INT8、MXFP4、NVFP4 矩阵乘。这些支持描述的是 kernel 能力集合；某个 checkpoint 是否可用，还取决于模型、量化、并行布局与版本的组合。

从维护角度看，清晰的后端边界可以减少每次上游调度改动都同步改一套服务引擎的成本。反过来，后端必须准确实现 custom op 语义、状态更新和设备通信；接口看起来一样，不能替代这些正确性验证。原文仅有发布横幅，没有可用于解释机制的架构图，因此此处保留文字说明。

## 首次编译是请求路径之外的准备成本

安装说明要求 Cloud TPU VM 上的 Python 3.12，并使用配套的 vLLM、torch、torch_tpu 和 libtpu。首次启动会为配置的形状编译 TPU 图，可能需要几分钟；编译缓存可跨重启复用。对服务运维而言，这意味着 readiness 不能只等进程启动，还要覆盖预热完成，否则第一批请求可能承担初始化开销。

这里进一步的工程推论是，比较部署方案时应分开统计冷启动、缓存命中重启和稳定流量。编译产物重用也依赖兼容的代码与配置；“保存了缓存”不是任意版本都能免编译的保证。发布文保留既有 CLI 和 OpenAI-compatible server，让调用层迁移较轻，但容量规划仍要计算这些准备时间。

## 六种并行维度不是六个独立加速开关

插件支持 tensor、data、pipeline、expert、prefill context 和 decode context parallelism，单机和多机 slice 都可组合。大 MoE 的一个推荐例子是在单个 v7x host 上使用 DP=8、TP=1，再开启 EP：attention 尽量本地执行，专家分布到整个 slice。长上下文则可用 PCP 和 DCP 拆分 prefill 与 KV 状态。

这些布局解决的问题不同。增加副本能够分摊请求，但不自动降低一条长请求的首 token 时延；拆分上下文可以降低每设备状态压力，却增加通信。最合适的方案取决于输入/输出长度、并发、模型结构与设备拓扑。原文的示例是选择起点，不是覆盖所有流量分布的最优结论。

## 多轮服务需要把缓存从 HBM 容量里解放出来

TPU Sync 是可在 Python runtime 之外访问设备 buffer 的 C++ 库。通过 vLLM KV connector，插件支持把 KV offload 到 host DRAM，也支持跨 TPU host 的 prefill/decode 分离。文中以 prefill 的 PCP=4、TP=2 和 decode 的 DP=8、TP=1 为例，传输时还需重分片。

“零拷贝”描述访问与传输路径中的实现选择，不表示网络没有字节移动或时间成本。对多轮 Agent，保留更长前缀有机会省掉重复 prefill，但只有检索、传输、重分片和安装的总成本小于重算时才获益。后一点是缓存设计的一般成本判断，发布文没有给出可代入的统一带宽与时延测量。

混合模型还要处理固定大小的线性 attention state。原文称 Qwen3.5 和 Kimi K3 的自动前缀缓存将其与 KV 一起保存；它不是“只要 token 相同就复制任意 buffer”的接口。状态必须与正确的模型、位置、执行布局和生命周期对应，错误命中首先是正确性问题。

## 已验证范围与下一步不能混在一起

v7x Ironwood 是推荐硬件，每个 PR 都进入 CI；v6e、v5e、v5p 被标为 experimental。推测解码、多 LoRA、结构化输出和多模态等功能沿用通常的 flags，但完整可用组合应以验证矩阵为准。“大多数 vLLM 模型可复用定义”比“所有模型与功能都已验证”弱得多。

## 为什么 Agent 流量会放大状态管理问题

多轮 Agent 请求常有稳定指令和不断增长的工具结果，因此相邻调用可以共享很长前缀；但历史裁剪、工具输出变化和提示顺序调整又会破坏共享。缓存容量扩展到 DRAM 后，命中机会可能更多，代价却转移到了状态定位与搬运。工程上更需要知道省掉多少 prefill token、传了多少字节、请求等了多久，不能仅用命中率判断服务是否更快。

prefill/decode 分离也有相似取舍。长输入的计算密集阶段和逐 token 输出的状态读取阶段可以选择不同布局，但请求跨越这条边界时必须转移有效状态。若负载较小或输出很短，分离带来的额外排队和搬运就可能占较大比例。这个判断来自执行路径本身，发布文没有承诺所有请求都从分离获得净收益。

推测解码再增加一层配置相关性：草稿提出候选、目标验证，实际节省取决于接受率、额外计算和硬件利用。文章列出 MTP、EAGLE-3、DFlash、DSpark、n-gram 与 suffix 等方法，说明接口覆盖方向；不应把“支持某种推测方法”直接替换成固定加速倍数。与缓存、量化、并行布局组合时，验证矩阵和运行条件比单独功能名称更能帮助阅读判断。

服务维护的长期收益，最终也要由共享控制层与硬件特有路径之间的稳定接口兑现：上游模型变化能否快速通过正确性检查，新的 kernel 是否保留状态语义，编译缓存是否与部署版本一致。这些问题构成后续跟踪重点，而不是发布当天已经全部完成的结论。

新模型发布后 24 小时内自动接入和发布矩阵、会话及前缀感知路由、扩展到 diffusion serving 等属于路线图。此次进展是一个可共享模型代码的 TPU serving 后端，以及围绕缓存与并行的具体集成点。值得先读 How It Works 与状态传输部分，再用目标 checkpoint 的验证记录判断成熟度；不能仅从插件存在就推断成本或吞吐优于其他硬件。
