---
id: supplement-2026-11-04
title: 2026-11-04｜补读：论文与技术进展
date: '2026-11-04'
lang: zh
published: false
layout: article
maintenance: daily-research
translation_source: assistant-authored paired Chinese/English reading notes
source_type: paper
permalink: /digest/zh/supplement/2026-11-04/
summary: 63 条经原始来源核对的论文与技术补读。
tags:
- agent-reliability
- self-improvement
- observability
- inference-serving
- systems-reliability
---


[返回当日论文集](/digest/zh/daily/2026-11-04/)

## ParetoSaddler: Pareto-Guided Optimization of Agent Harnesses for Quality and Cost
{: #reading-arxiv-2611.02079}

ParetoSaddler 不用最终部署偏好提前淘汰中间候选，而是根据重复执行的 Bayesian bootstrap Pareto 支持度保留质量或成本进展，再做最终选择。两个跨域基准上质量与单任务成本共同改善。

局限：重复评估增加搜索成本；bootstrap 反映固定题目上的运行波动，不覆盖任务抽样不确定性或全部优化投入。

来源：[ParetoSaddler: Pareto-Guided Optimization of Agent Harnesses for Quality and Cost](https://arxiv.org/abs/2611.02079)

## WebHarbor: Docking Real Websites for Evolving GUI Agent Environments
{: #reading-arxiv-2611.03634}

WebHarbor 重建 153 个可执行网站环境、3518 个任务，通过人工与 agent 协作逐步扩展工作流，在确定性环境中覆盖登录后操作。它缓解真实网站变化造成的评估漂移。

局限：重建不等于完整原站，实时地图等采用替代；训练仅一个 4B 模型，脚本与模型评分仍会漏判。

来源：[WebHarbor: Docking Real Websites for Evolving GUI Agent Environments](https://arxiv.org/abs/2611.03634)

## TLAPS-Bench: Formally Proving Correctness of Real-World System Specifications with TLA+ Proof System
{: #reading-arxiv-2611.02849}

TLAPS-Bench 提供系统 TLA+ 规格的证明开发环境，包含 95 个规格的 265 个目标。实际评估是 12 个规格的 70 个目标，最佳配置在 pass@3 口径下证明 31 个。

局限：不是全部 265 个目标的单次成功率；证明针对形式规格与目标，不能推出实现完全正确。

来源：[TLAPS-Bench: Formally Proving Correctness of Real-World System Specifications with TLA+ Proof System](https://arxiv.org/abs/2611.02849)

## An Agentic OS Kernel for Flexible and Enhanced Semantics
{: #reading-arxiv-2611.00002}

IntentOS 通过 isyscall 接受意图，将 syscall 拆为可组合 micro-syscall，由 LLM 规划并缓存经过检查的执行计划。复用计划让命中路径绕过推理，尝试减少固定接口导致的重复操作。

局限：约三十个意图和四个 kernel 版本不足以验证任意组合安全；PDF 日期与 arXiv 编号不协调，未据此推定首次发布日期。

来源：[An Agentic OS Kernel for Flexible and Enhanced Semantics](https://arxiv.org/abs/2611.00002)

## SpecGuardBench: Can Coding Agents Construct Reliable Validation Harnesses from Natural Language Specifications?
{: #reading-arxiv-2610.16870}

SpecGuardBench 同时提供违规实现与符合规格的不同实现，检查 agent 写的验证器是否忠实规格。291 个任务中，没有 agent 超过 63% 的 faithful 比例；关键失败是把参考实现细节误当要求。

局限：忠实度只针对基准保留的实现，不能证明对所有程序都成立；参考代码也可能诱导过拟合检查。

来源：[SpecGuardBench: Can Coding Agents Construct Reliable Validation Harnesses from Natural Language Specifications?](https://arxiv.org/abs/2610.16870)

## Don't Guess, Just Ask: Evaluating Interactive Requirement Clarification for Repository-Level Software Development
{: #reading-arxiv-2610.13022}

ReqClarifyBench 用 341 个仓库级任务和不同 persona 的模拟用户，评估把模糊意图澄清成需求的能力。更多有效澄清不一定产出更好需求文档，coding harness 也未进一步提高文档质量。

局限：LLM 模拟用户不代表真实用户互动；需求质量、后续代码效果和 persona 分布应分别解释。

来源：[Don't Guess, Just Ask: Evaluating Interactive Requirement Clarification for Repository-Level Software Development](https://arxiv.org/abs/2610.13022)

## LARK: Lean-Assisted Reasoning for LLM-Generated GPU Kernels
{: #reading-arxiv-2611.02028}

LARK 用 Lean 验证 kernel 分段及与参考程序的功能、内存行为等价，把人工信任集中到算子语义。它在所测库 kernel 中验证九个，并在另一个发现 race；附录明确实验使用固定 kernel 的 verify-only 模式。

局限：精确算术保证不含浮点误差等价；语义模型仍需人工可信，报告不能改写为整个生成流水线的实测成功率。

来源：[LARK: Lean-Assisted Reasoning for LLM-Generated GPU Kernels](https://arxiv.org/abs/2611.02028)

## Ask, Don't Equip: Question-Driven Coding Agents for Deep Kernel Optimization
{: #reading-arxiv-2611.03517}

KernelSeek 在最小验证 harness 中用问题推动 agent 改变优化假设，后来将问题整理为可自行调用的 bank。Hopper 与 Blackwell attention kernel 均检查 182 个场景；作者保留人工消息与工具轨迹。

局限：大收益发生在提问后是观察性归因，非随机因果证明；人工投入不可忽略，有限测试也不是全输入正确性。

来源：[Ask, Don't Equip: Question-Driven Coding Agents for Deep Kernel Optimization](https://arxiv.org/abs/2611.03517)

## SpecPilot: Autonomous Algorithm Discovery and Systems Optimization for Speculative Decoding
{: #reading-arxiv-2611.02501}

SpecPilot 用成本上限定位部署瓶颈，让 agent 探索并集成优化，逐 token 对照 stock 的 token forcing 防止性能“作弊”。其结果强调单请求与 batching 需要不同优化。

局限：报告的 10.87 倍是相对 AR 而非相对 stock；有限对照验证不替代所有输入的分布等价证明，搜索开销也需计入。

来源：[SpecPilot: Autonomous Algorithm Discovery and Systems Optimization for Speculative Decoding](https://arxiv.org/abs/2611.02501)

## SpecOPD: Branch-Parallel On-Policy Distillation for Speculative Decoding
{: #reading-arxiv-2611.02846}

SpecOPD 在固定参考前缀后采样当前 drafter 分支，复用主干计算并保持分支历史独立。16.09 倍监督 token 吞吐由更新速度和每次监督量共同构成，与推理最高 3.56 倍 AR 加速是不同指标。

局限：原生配置不同且不含离线参考准备；监督吞吐不等于达到相同质量时间缩短 16 倍，架构和任务增益差异较大。

来源：[SpecOPD: Branch-Parallel On-Policy Distillation for Speculative Decoding](https://arxiv.org/abs/2611.02846)

## AgentPRO: Coordinating Compiler Optimizations for LLM Agent Workflows
{: #reading-arxiv-2611.00628}

AgentPRO 区分工具执行依赖与模型生成所需观察，合并兼容生成区域并删除冗余上下文，配合运行时 guard 回退。优化后 115 个任务完成 110 个，平均 token 减少 41.85%。

局限：115 任务先按基线成功筛选，基线满分是构造结果；每任务一次，且 component time 不是完整用户耗时。

来源：[AgentPRO: Coordinating Compiler Optimizations for LLM Agent Workflows](https://arxiv.org/abs/2611.00628)

## SNAPPerf: Software-Aware Tabular Foundation Model for Retraining-Free Performance Prediction of Configurable Systems
{: #reading-arxiv-2611.00944}

SNAPPerf 在合成可配置系统上预训练，再用少量新测量作上下文，无需每系统重新训练。12 个真实系统上，同测量预算误差比前沿基线平均低 38%。

局限：无需重训练不等于无需测量；跨版本即时可用是研究愿景，误差和省样本比例依赖系统与预算。

来源：[SNAPPerf: Software-Aware Tabular Foundation Model for Retraining-Free Performance Prediction of Configurable Systems](https://arxiv.org/abs/2611.00944)

## Agent Stack for ML Training Lifecycle: Generation, Validation, and Optimization
{: #reading-arxiv-2611.00384}

LinkedIn 的 AutoTorch 用可执行检查生成和迁移模型，AutoResearch 由外部编排器管理实验。115 次流程中 92 次完成训练，其中 77 次达质量要求；另一批 100 条流水线有 28 条改善。

局限：约四倍迁移提速来自团队估计，非随机对照；完成训练与达到质量要求的分母不同，不能合并为 80% 全流程成功。

来源：[Agent Stack for ML Training Lifecycle: Generation, Validation, and Optimization](https://arxiv.org/abs/2611.00384)

## Characterizing and Predicting the Longest CI Builds in Machine Learning Projects
{: #reading-arxiv-2611.00667}

该研究发现所测 ML 项目中最长 18% 构建消耗 80.30% 时间，且 39.09% 最终失败。近期构建历史与工作流结构可帮助执行前识别长任务，时间顺序评估的 XGBoost F1 为 .775。

局限：这些阈值来自该数据集，关联不证明复杂结构导致耗时；不应自动删除测试或按失败概率取消构建。

来源：[Characterizing and Predicting the Longest CI Builds in Machine Learning Projects](https://arxiv.org/abs/2611.00667)

## Understanding GPU Megakernels: Why Residency Can Mislead
{: #reading-arxiv-2611.00495}

该 megakernel 研究用相同算子代码拆回独立 kernel，并控制启动、预取和内存次序。PDL 可使 TK decode step 快 5.7%；驻留 CTA 不等于瓶颈资源仍有可用重叠空间。

局限：主要针对两个实现与 H100；不能据此断言 megakernel 普遍更差，内存顺序不一致的比较无效。

来源：[Understanding GPU Megakernels: Why Residency Can Mislead](https://arxiv.org/abs/2611.00495)

## Weights That Stay: On-Chip Megakernels for Serial Heads in Speculative Decoding
{: #reading-arxiv-2611.00506}

Weights That Stay 在串行 draft walk 全程把投影权重分片留在片上，由 GPU 推进 token 与状态。head 最高加速 11.6 倍，但完整 SGLang 吞吐最高增益为 12.3%。

局限：B200 只测 head，端到端 serving 在 H100；不能把微 kernel 倍率当作整个模型的提升。

来源：[Weights That Stay: On-Chip Megakernels for Serial Heads in Speculative Decoding](https://arxiv.org/abs/2611.00506)

## Rethinking KV Cache Eviction for Agentic LLM Serving
{: #reading-arxiv-2611.00391}

Penelope 保留共享前缀和私有历史后缀，从中间缺失段重算，避免优先丢弃重算更贵的后部 token。它联合修改淘汰、重算与 GPU/CPU 管理，而非直接把缓存洞交给原有前缀逻辑。

局限：依赖配套正确性和索引实现；GPU-only 与两级缓存的最大收益采用不同条件，不能合并。

来源：[Rethinking KV Cache Eviction for Agentic LLM Serving](https://arxiv.org/abs/2611.00391)

## Fairway: Load-Aware KV Cache Reuse for LLM Prefill Scheduling
{: #reading-arxiv-2611.02082}

Fairway 在虚拟 Fast/Fair 双通道中按 KV 复用与相对等待时间调整顺序，短队列优先廉价命中，拥塞时保护昂贵请求。它把低中位 TTFT 与防饥饿作为联合目标。

局限：实验每请求只生成一个 token，隔离 prefill；尾延迟倍率不能推广为完整多轮 agent 完成速度。

来源：[Fairway: Load-Aware KV Cache Reuse for LLM Prefill Scheduling](https://arxiv.org/abs/2611.02082)

## LADS: Lease-Aware Delivery Scheduling of Tool Results for Language Model Agents
{: #reading-arxiv-2611.00881}

LADS 根据 prefix lease 归属和恢复延迟安排工具结果回传，让已恢复请求及时释放额外缓存保护额度。受限回传通道的突发负载中，它减少完整工作流等待。

局限：依赖回传带宽、并发与 cache lease 条件；不能将人工突发和 web replay 的收益推断到所有 agent 网络。

来源：[LADS: Lease-Aware Delivery Scheduling of Tool Results for Language Model Agents](https://arxiv.org/abs/2611.00881)

## When Shards Fly: Cross-Tensor In-Flight Conversion for Low-Latency, Low-Memory Weight Updates in Disaggregated RL
{: #reading-arxiv-2611.00646}

ShardFly 编译跨 tensor 分片计划，在 persistent kernel 中融合布局转换、量化、传输和原位写入，并在副本间转发转换后的字节。更新阶段最高倍率很大，完整 GRPO 响应吞吐增益为 5.49%–6.71%。

局限：主要是同步原位更新，稳定配置复用计划；不能把更新阶段最高 27.92 倍当作训练加速。

来源：[When Shards Fly: Cross-Tensor In-Flight Conversion for Low-Latency, Low-Memory Weight Updates in Disaggregated RL](https://arxiv.org/abs/2611.00646)

## Introducing Cluster Efficiency to LLM Serving: Pooling Economical Accelerators over Fast Interconnects
{: #reading-arxiv-2611.02975}

该研究把经济型加速器的计算与内存优势放到集群层评估：高速互联使 Blackhole Galaxy 在三年购置加电费模型下达到对照的 1.07–2.24 倍 token/美元；较慢通信仿真消除优势。

局限：成本模型不是完整 TCO，且 TCP 级通信为仿真；吞吐优势需与延迟、精度和软件覆盖一起解释。

来源：[Introducing Cluster Efficiency to LLM Serving: Pooling Economical Accelerators over Fast Interconnects](https://arxiv.org/abs/2611.02975)

## LoRAForge: Co-Designing Post-Hoc Compression and Execution for Efficient Multi-LoRA Serving
{: #reading-arxiv-2611.01256}

LoRAForge 用批量因子构建和显式保留 rank 的专用执行连接压缩与 serving。85 个 adapter 的谱分配配置保留约 7.7% 参数，平均分数损失不超过 1.2 分。

局限：压缩有损，平均损失掩盖单 adapter 退化；因子构建、后端收益与压缩策略收益需分开核算。

来源：[LoRAForge: Co-Designing Post-Hoc Compression and Execution for Efficient Multi-LoRA Serving](https://arxiv.org/abs/2611.01256)

## Scute: Exact Batched Serving for PEFT Adapters Beyond LoRA
{: #reading-arxiv-2611.01089}

Scute 用统一六槽正规形式把 DoRA、IA3、VeRA、OFT 等接入修改后的 batched LoRA kernel，避免先近似转换成 LoRA。不同方法可在同一 batch 中执行。

局限：数学表示精确不等于浮点逐位一致；实测误差以 adapter 效应归一化，混合方法相对纯 LoRA 仍有开销。

来源：[Scute: Exact Batched Serving for PEFT Adapters Beyond LoRA](https://arxiv.org/abs/2611.01089)

## Inference First, Training Underneath: Layer-Granular LoRA Co-Serving with LayerLoom
{: #reading-arxiv-2611.00652}

LayerLoom 把 LoRA backward 拆到层级，依据推理剩余延迟预算附着执行，以错层 microbatch 波前保持可用任务，并把激活状态卸载到主机。它让突发推理优先于后台训练。

局限：仅一张 4090、一个模型及 down_proj rank-16 设置；SLO 达标点数变化依赖指定阈值，不是通用延迟倍率。

来源：[Inference First, Training Underneath: Layer-Granular LoRA Co-Serving with LayerLoom](https://arxiv.org/abs/2611.00652)

## Jet-QSparse: Accelerating Agentic LLM Inference with 4-Bit Sparse Attention
{: #reading-arxiv-2611.01022}

Jet-QSparse 用 FP4 扫描全 key 历史，选块后以更高精度聚合 value。必须区分 128-block 的质量测试与 64-block 的最高 1.94 倍 decode 加速，二者不是同一工作点。

局限：没有检测到质量损失不等于无损；较小预算已有退化，依赖 Blackwell 和特定模型/context。

来源：[Jet-QSparse: Accelerating Agentic LLM Inference with 4-Bit Sparse Attention](https://arxiv.org/abs/2611.01022)

## PagedMoE: Cross-Precision Expert Caching for Token-Level Dynamic Precision in SSD-Resident MoE Inference
{: #reading-arxiv-2611.03173}

PagedMoE 把各精度表示做成同一专家状态的可扩展 bitplane 前缀，升精度时只补缺失部分，直接执行紧凑表示。专家在 CPU 执行；相同动态精度请求下共享缓存比独立对象快 1.33 倍。

局限：2.5-bit 是平均专家精度且有损；接近 INT4 的质量并非所有任务等价，不能误写成 GPU 专家执行。

来源：[PagedMoE: Cross-Precision Expert Caching for Token-Level Dynamic Precision in SSD-Resident MoE Inference](https://arxiv.org/abs/2611.03173)

## Apto: Self-Adaptive CPU-GPU Hybrid MoE Inference on Shared PCs
{: #reading-arxiv-2611.01859}

Apto 让 CPU/GPU 从双端队列分别领取专家，以实际进度自适应分工，并用亲和排序和可取消尾部竞争处理拖尾。它针对共享 PC 的动态 CPU 争用，而非固定离线切分。

局限：收益取决于争用类型、核心限制和模型；并发负载下更大倍率不意味着每台 PC 都有同等独立性能。

来源：[Apto: Self-Adaptive CPU-GPU Hybrid MoE Inference on Shared PCs](https://arxiv.org/abs/2611.01859)

## Layer-wise CPU-GPU Scheduling for LLM Inference on Memory-Limited Consumer GPUs
{: #reading-arxiv-2611.01393}

该调度方法在部分层由 CPU 计算时异步传下一层 GPU 权重，利用 CPU 计算短于 PCIe 搬运的情况隐藏传输。消费桌面 OPT-30B 测试相对 Accelerate 和 ZeRO-Inference 明显加速。

局限：输出仅 32 token，主要评估性能；不用压缩不等于已验证 CPU/GPU 浮点路径完全一致，不能声称质量已充分检验。

来源：[Layer-wise CPU-GPU Scheduling for LLM Inference on Memory-Limited Consumer GPUs](https://arxiv.org/abs/2611.01393)

## Accelerating LLM Decoding with In-DRAM Parallelism
{: #reading-arxiv-2611.02401}

PUD-LLM 用残差状态改写投影，将跨层工作打包，改善 DRAM 内 SIMD/MIMD 利用率，并以减少 bit-serial 步数近似修正。性能仿真最高为 PUD 基线的 1.41 倍。

局限：并非实体芯片端到端实测；近似修正有质量—效率折中，不能宣称无损替代 GPU。

来源：[Accelerating LLM Decoding with In-DRAM Parallelism](https://arxiv.org/abs/2611.02401)

## RankLane: Efficient MoE Prefill on Accelerators with Ranked Expert Capacities
{: #reading-arxiv-2611.00421}

RankLane 根据当前专家负载排序，把专家分配到固定容量 lane，保持编译形状与设备归属不变；溢出 chunk 以完整容量重跑。它在静态执行加速器上减少 MoE padding。

局限：结果针对一张四 SoC 卡的 batch-1 prefill；需要校准与恢复支持，不能将 prefill 倍率推广到 decode。

来源：[RankLane: Efficient MoE Prefill on Accelerators with Ranked Expert Capacities](https://arxiv.org/abs/2611.00421)

## Sonar-MoE: In-Backward Expert Updates for Memory-Efficient Mixture-of-Experts Training
{: #reading-arxiv-2611.03577}

Sonar-MoE 在 backward 完成一个专家 tensor 后立即更新并释放梯度，峰值内存降低 19%–22%。批量 tensor 更新避免逐专家 hook 的额外开销。

局限：逐位一致仅相对不裁剪专家梯度的基线；全局梯度裁剪与多步梯度累积不能直接保持原语义。

来源：[Sonar-MoE: In-Backward Expert Updates for Memory-Efficient Mixture-of-Experts Training](https://arxiv.org/abs/2611.03577)

## Accelerating LLM Pretraining with Zeroth-Order Curvature on Idle Serving Compute
{: #reading-arxiv-2611.02688}

ZO-Curv 将空闲 forward-only 设备用于估计曲率，辅助一阶预训练，而不直接依赖高噪声零阶梯度。770M 实验到达 AdamW 指定验证 loss 的时间从 7.5 小时降为 3.9 小时。

局限：使用额外设备计算，不能视为同资源成本减半；模型规模和空闲时段假设限制生产外推。

来源：[Accelerating LLM Pretraining with Zeroth-Order Curvature on Idle Serving Compute](https://arxiv.org/abs/2611.02688)

## FlyWheel: Attention Kernels Built for the TPU
{: #reading-arxiv-2611.01426}

FlyWheel 面向 TPU 重构 softmax 与线性 attention，减少向量工作、复用矩阵操作数并重叠独立计算。kernel 最大倍率明显高于接入 vLLM 后最高 1.56 倍的 prefill 吞吐收益。

局限：v6e/v7x 的 chip 与 TensorCore 计数不同；不是全部请求端到端同倍加速，近似数值路径仍需质量检查。

来源：[FlyWheel: Attention Kernels Built for the TPU](https://arxiv.org/abs/2611.01426)

## Multi-Turn Semantic Caching for Low-Cost LLM Serving
{: #reading-arxiv-2611.01077}

该多轮语义缓存方法从 judge 反馈学习复用风险，把省下的生成成本与不可接受回答代价一起优化。结构化辅导和订票对话中收益明显，但开放聊天可安全复用的后续轮仅约 1%–2%。

局限：判断依赖 judge 与状态复现假设；延迟改善是估算，不能外推到所有开放对话或将语义相似当作有效复用。

来源：[Multi-Turn Semantic Caching for Low-Cost LLM Serving](https://arxiv.org/abs/2611.01077)

## Seeing What Matters, Verifying What Pays: Load-Adaptive Speculative Decoding for Vision-Language Models
{: #reading-arxiv-2611.01617}

Uni-LaSpec 用上轮 verifier attention 选择少量视觉 token，并按 GPU 负载切换树验证与截短线性验证。八个视觉 token 保留至少 98.6% 全图草稿接受量，是接受率指标而非图像质量分数。

局限：123/144 配置达到最佳固定策略仍有例外；峰值吞吐来自 greedy/单并发，不能与突发延迟结果合并。

来源：[Seeing What Matters, Verifying What Pays: Load-Adaptive Speculative Decoding for Vision-Language Models](https://arxiv.org/abs/2611.01617)

## FactorSpec: Serving Exact Relational Constraints as Speculative Drafts
{: #reading-arxiv-2611.02297}

FactorSpec 把 JSON Schema 和字段关系编译为可精确检查的因子图，将约束唯一确定的 token 作为草稿，并异步计算 mask。它同时优化解码与有效记录产率。

局限：最高 13.9 倍指有效记录/GPU秒，纯解码最高为 1.43 倍；保证仅覆盖可表达关系和实现的约束模型。

来源：[FactorSpec: Serving Exact Relational Constraints as Speculative Drafts](https://arxiv.org/abs/2611.02297)

## Who Schedules Agent Memory? A Sidecar Approach to Long-Horizon Tasks
{: #reading-arxiv-2611.00779}

MemSidecar 提供事件触发直接注入的 Hooks，以及独立预测、并行检索的 Foresight，让主 agent 少花时间安排记忆访问。预取结果须匹配实际请求且仍有效才交付。

局限：额外预测模型也有成本；两个模式、两个基准需分别比较，预测命中不保证记忆内容正确。

来源：[Who Schedules Agent Memory? A Sidecar Approach to Long-Horizon Tasks](https://arxiv.org/abs/2611.00779)

## Capacity Planning for Resource-Constrained Clinical LLM Serving
{: #reading-arxiv-2611.01152}

该四 GPU 对照研究固定硬件与工作流，改变大小模型配比和路由。配置组成对延迟与长上下文覆盖的观测影响大于所测路由变化；容量感知路由只能在既有资源内缓解瓶颈。

局限：是 24 配置的描述性系统结果；长上下文覆盖不是临床正确性，也不足以指导实际临床使用。

来源：[Capacity Planning for Resource-Constrained Clinical LLM Serving](https://arxiv.org/abs/2611.01152)

## TRIAGE: Reliability- and Load-Conditioned Escalation for Two-Tier LLM Serving with a Semantic Evidence Judge
{: #reading-arxiv-2611.01174}

此 TRIAGE 研究保留失败主张：预注册可靠性状态检测损坏证据仅 AUROC .571，语义 judge 的改善是事后分析。实际 7B→32B 质量差距很小，分配器最终拒绝升级，是主要负面结果。

局限：与已刊 miniTE 的同名训练控制不同；API 成本收益取决于价格比，不能套用到开放模型对或当作预注册结论。

来源：[TRIAGE: Reliability- and Load-Conditioned Escalation for Two-Tier LLM Serving with a Semantic Evidence Judge](https://arxiv.org/abs/2611.01174)

## STLT: A Novel System for Energy-Aware Distributed Inference in the Edge-Cloud-Space Continuum
{: #reading-arxiv-2611.01233}

STLT 先离线筛选 DNN 的有利切分点，再按卫星能量与环境状态轻量选择星地分工。它把计算与下传能耗一起考虑，避免每轮搜索全部切分。

局限：真实遥测数据不等于在轨执行验证；决策模块能耗下降与总系统能耗下降采用不同口径。

来源：[STLT: A Novel System for Energy-Aware Distributed Inference in the Edge-Cloud-Space Continuum](https://arxiv.org/abs/2611.01233)

## Parallelism-Aligned Pruning and Round-Aware Context Reuse for On-Device Multimodal Agents
{: #reading-arxiv-2611.02601}

PARC 将 attention head 数剪到七核可整分的形状，再按生命周期分离持久文本与临时图像 KV。参数量匹配对照表明主要速度收益来自核对齐，而非仅减少参数。

局限：需要任务恢复训练，图像历史被移出持久缓存；2062 动作无回退不能证明所有依赖旧图的任务都保持语义。

来源：[Parallelism-Aligned Pruning and Round-Aware Context Reuse for On-Device Multimodal Agents](https://arxiv.org/abs/2611.02601)

## A Self-Exploring and Self-Evolving Paradigm for Adaptive Edge AI Development
{: #reading-arxiv-2611.01377}

SE2 让 agent 在检索、推理、编码与测试四种操作间动态选择，并持续调整模型。除扩展 IoTBench 外，作者在笔记本、Jetson Nano 和树莓派部署生成程序，分析缺失模态等变化。

局限：代码 embedding 相似度不代表功能正确；模型调优与工作流变化混合，所测案例不能证明任意未知边缘任务都适用。

来源：[A Self-Exploring and Self-Evolving Paradigm for Adaptive Edge AI Development](https://arxiv.org/abs/2611.01377)

## Action Verification through Conjecture and Refutation for Language Model Agents
{: #reading-arxiv-2611.02950}

BlackSwan 在写操作前先预测效果、提出可检验的反例怀疑，再用已有观察或只读动作反驳，仍有怀疑就不执行。AppWorld 与 WebShop 实验显示该流程可减少误行动。

局限：没有发现反例不等于证明安全；额外测试有成本，模拟应用与购物环境不能覆盖真实系统的所有副作用。

来源：[Action Verification through Conjecture and Refutation for Language Model Agents](https://arxiv.org/abs/2611.02950)

## When AI Agents Act on Our Behalf: A Taxonomy of Human-Agent Interaction Failure
{: #reading-arxiv-2611.00291}

该研究从两个公开库的 695 条事件提炼 12 种交互失败，分析用户何时能看见、阻止和撤销 agent 行为。所有模式在高低自主性都出现，自主性改变的是失败呈现与干预窗口。

局限：公开事件有报告与选择偏差，不能推断发生率或证明配置比模型能力更重要的普遍因果关系。

来源：[When AI Agents Act on Our Behalf: A Taxonomy of Human-Agent Interaction Failure](https://arxiv.org/abs/2611.00291)

## CUA-Master: Scaling Computer-use Agents through Open-World Recursive Improvements
{: #reading-arxiv-2611.03126}

CUA-Master 从教学视频挖真实流程，再转成可复用任务原语，通过模型弱点反馈扩展数据；snapshot rollback 减少失败重采成本。它将开放世界来源与受控任务生成连接。

局限：递归训练和 VM 基础设施成本较大；OSWorld-Verified 与 2.0 分数口径不同，不可用单一排行榜数字概括泛化。

来源：[CUA-Master: Scaling Computer-use Agents through Open-World Recursive Improvements](https://arxiv.org/abs/2611.03126)

## NorthCUA Technical Report: Turbocharging Computer-Use Agents through Experience at Scale
{: #reading-arxiv-2611.02102}

NorthCUA 将任务生成、执行记录、证据化结果检查与分阶段学习连成循环；未完成任务保留已验证里程碑。数据筛选的 agent judge 可检查实际工作区，正式基准则使用独立 scorer。

局限：开放内容 judge 仍依赖校准与判据覆盖；新软件和界面变化仍困难，示例证据链不是整体错误率的验证。

来源：[NorthCUA Technical Report: Turbocharging Computer-Use Agents through Experience at Scale](https://arxiv.org/abs/2611.02102)

## MemU-Bench: Benchmarking GUI Agents on Long-Horizon User Interactions
{: #reading-arxiv-2611.00191}

MemU-Bench 以 29 条用户历史构造 118 个模糊移动任务，要求恢复省略上下文，并用 SPL 区分记忆命中与遍历搜索。AppMem 的 GPT 配置 SPL 从 15.7% 升至 66.9%，是增加 51.2 个百分点。

局限：仅 44.9% 任务完全规则评分，其余需要 LLM judge；低温度不保证判断正确，也不是纯后端确定性验证。

来源：[MemU-Bench: Benchmarking GUI Agents on Long-Horizon User Interactions](https://arxiv.org/abs/2611.00191)

## Coati: Host-Grounded Execution for Installable Mobile GUI Agents
{: #reading-arxiv-2611.02644}

Coati 在手机宿主记录动作效果与跨 app 状态，VerifyLoop 将无法审计的完成声明标为未验证。AndroidWorld 的同模型对比成功率为 86.5%，另有真实手机快速执行实验。

局限：AndroidWorld 使用 Android 13 模拟器，不能写成 116 项均在真实手机测试；较少推理调用不等于本地模型无网络依赖。

来源：[Coati: Host-Grounded Execution for Installable Mobile GUI Agents](https://arxiv.org/abs/2611.02644)

## Optimize the Harness, Not the Model: Fitting a Minimal Agent to a Self-Hostable LLM for Investigative Analysis
{: #reading-arxiv-2611.03434}

CLEO 从小型 harness 开始，仅保留对专家验证数据有帮助的工具、guardrail 与记忆策略。单个调查分析域中，held-out 通过率 83.8%，接近最强现成 SDK 对照。

局限：评分由仅抽查而未系统验证的 LLM judge 完成；代码少百倍不等于攻击风险或维护成本同比下降。

来源：[Optimize the Harness, Not the Model: Fitting a Minimal Agent to a Self-Hostable LLM for Investigative Analysis](https://arxiv.org/abs/2611.03434)

## Latent Harness: Compiling Agent Behaviors into Post-Block Activation Shifts
{: #reading-arxiv-2611.01415}

Latent Harness 把外部行为条件蒸馏成冻结模型各 decoder block 后的低秩激活偏移，推理不再重复输入 harness 文本，并可调强度、阶段及混合。十个预注册设置中八个恢复原收益。

局限：仍需训练并运行额外参数，非免费编译；跨任务仅五组正向，不能替代动态工具权限或任意 harness 控制。

来源：[Latent Harness: Compiling Agent Behaviors into Post-Block Activation Shifts](https://arxiv.org/abs/2611.01415)

## Causality-Based Fault Localization
{: #reading-arxiv-2611.01292}

SoftReX 用实际因果责任和修改距离排序故障位置，并惩罚破坏通过测试的候选。同一 mutant 集下排名改善与结构化搜索减少 mutant 数量，是两个独立贡献。

局限：因果结论相对于程序模型、测试和可用变异；定位高分不是自动正确修复，2.6 倍不是完整调试耗时倍率。

来源：[Causality-Based Fault Localization](https://arxiv.org/abs/2611.01292)

## VerusWeave: A Benchmark for Proof Repair in Concurrent Verus Programs
{: #reading-arxiv-2611.00287}

VerusWeave 从四个项目移除证明标注，保留可执行代码与规格，用 Verus 和改动检查器验证修复。局部 75 题成功率 75%–85%，17 个整模块变体降至 29%–47%。

局限：小样本、已有证明衍生任务；不能当成从零证明任意并发程序，验证器与规格仍是信任边界。

来源：[VerusWeave: A Benchmark for Proof Repair in Concurrent Verus Programs](https://arxiv.org/abs/2611.00287)

## Stop Handcrafting Your Engine! GenDB-V: Towards AI-Generated and Formally Verified Database Systems
{: #reading-arxiv-2611.02779}

GenDB-V 先确定实现无关 SQLSpec 目标，再联合搜索执行代码与证明，并在隔离流程检查。模板专用实现与可接收受支持 SQL 子集的通用引擎分别评估，后者加速为 1.27–3.4 倍。

局限：模板的 22–61.3 倍不能当作完整数据库倍率；保证取决于 SQLSpec、验证链和支持子集，不覆盖所有 SQL 语义及数据库功能。

来源：[Stop Handcrafting Your Engine! GenDB-V: Towards AI-Generated and Formally Verified Database Systems](https://arxiv.org/abs/2611.02779)

## AdapBench: Adaptive Early-Stopping and Prioritization for Efficient Microbenchmarking in Cloud-based CI/CD
{: #reading-arxiv-2611.01255}

AdapBench 根据接近统计判定的程度优先运行微基准，并在证据足够时提前停止。记录数据回放中，Java 在匹配检测率和假阳性条件下节省 42% 总时长，Go 节省 85%。

局限：原型回放不是新线上 CI 部署；Go 的零观测假阳性不等于零风险，匹配 90% 检出率仍保留漏检。

来源：[AdapBench: Adaptive Early-Stopping and Prioritization for Efficient Microbenchmarking in Cloud-based CI/CD](https://arxiv.org/abs/2611.01255)

## FlashProve：模型来源证明的性能与信任边界
{: #reading-anthropic-provable-inference}

FlashProve 的问题是“哪个承诺的模型执行了这次计算”，而不是回答是否正确。提供者先对权重做隐藏承诺，再为请求生成 zkSNARK，持有承诺、输入和结果的人无需取得权重即可检查。系统隐藏权重与专家选择，但不以隐藏架构为目标；证明实际服务了获准模型，也不证明服务器没有同时执行其他工作。

实现采用事后证明：先完成文本，再按类似 prefill 的并行路径重算，被使用的 MoE 专家决定主要证明工作。权重分段从主机流入，允许单 H100 配合大量主机内存运行。测试采用 4-bit Llama 4 Maverick 与整数算术；每个请求含 1024-token 窗口，但每份证明只检查一个 token。24 个请求证明耗时约 223 秒，所谓 110 token/s 是上下文处理吞吐，不能写成每秒证明 110 个新生成 token。单份证明约 18.78MB，24 线程 CPU 检查约 17 秒；离线承诺还需约 39 分钟，并有可服务请求数上限。

可信边界同样重要。Lean 中形式化了随机 oracle 模型下的顶层性质，并提供有 soundness 联系的可执行 Lean verifier。日常 C++ verifier 只在测试中与其一致，本身没有该形式化保证；证明器代码与形式协议的对应关系仍需审计，尤其涉及零知识。顶层形式陈述是否符合意图也必须由人检查。

作者相对 FP8 vLLM 报告约 72–94 倍 GPU 时间开销。这不是零开销在线签名，也不是相同数值格式的纯 kernel 对比。适合继续研究的方向是低比例事后抽查、模型承诺生命周期，以及证明延迟与不可逆外部动作之间的时间窗口。代码库明确标为研究产物且不维护；这里没有运行证明、检查 Lean 构建或独立审核密码协议。

局限：证明只涉及声明的量化、算术和协议，不保证原始浮点模型、事实正确性或整段响应的未抽查 token；高开销、事后延迟和实现对应关系仍是部署限制。

来源：[Progress on provable inference for large language models](https://www.anthropic.com/research/provable-inference)

实现与说明：[FlashProve](https://github.com/anthropics/FlashProve).

## Honeycomb AI SRE：证据、假设与操作权限
{: #reading-honeycomb-ai-sre-agents}

Honeycomb 区分个人辅助与团队目标 agent，要求发现关联到 query、trace 或 deploy，并标记已确认与假设。个人 agent 操作需明确指示，团队自主权限由团队设定。

局限：发布稿未给出诊断准确率或事故恢复效果，调查比例也缺完整方法；不能把能力说明当作已验证 SRE 成果。

来源：[Honeycomb Introduces AI SRE Agents That Go Beyond Incidents](https://honeycomb.io/blog/honeycomb-introduces-ai-sre-agents)

## FastVideo Pika H3：核对资源与精度后的加速
{: #reading-haoailab-pika-h3-flex}

FastVideo 优化 Pika H3 Flex 的 attention、融合小操作与 VAE 解码，并提供 NVFP4 QAD。标题七倍比较四 GPU 优化路径与一 GPU 官方路径；同四 GPU 对照最高为 4.58 倍。

局限：采用常驻模型的 warm median，不含加载；精度与 decoder 也变化，接近实时的 480p 配置不能推广至更高分辨率。

来源：[Pika H3 Flex in FastVideo: 7x Faster, and Near Real Time in 4-bit](https://haoailab.com/blogs/pika-h3-flex/)

## TensorRT 全局调优：构建路线与准确率约束
{: #reading-nvidia-tensorrt-global-performance-tuner-1}

TensorRT Global Performance Tuner 将图变换、融合、kernel、布局与量化视为相互作用的构建路线，按端到端准确率约束搜索可接受引擎，而非逐个算子挑最快实现。

局限：Part 1 主要建立概念框架，未在本次验证 tuner 收益；候选空间与准确率检查的覆盖决定优化边界。

来源：[Scaling NVIDIA TensorRT Performance Optimization Beyond a Single Build Route with the Global Performance Tuner, Part 1](https://developer.nvidia.com/blog/scaling-nvidia-tensorrt-performance-optimization-beyond-a-single-build-route-with-the-global-performance-tuner-part-1/)

## 开放 megakernel 复现：同时运行与强基线
{: #reading-github-open-flapping-airplanes}

open-flapping-airplanes 从演示视频独立重建持续 GPU kernel，让训练、serving 与 Doom 共用设备。B200 上 162.4M 模型训练为 48.1 秒，快于 eager 对照，却慢于 CUDA Graph Megatron 的 43.1 秒。

局限：不是原项目代码复现或大模型生产验证；各 workload 分配固定 SM，不能把并行演示当作免费共享资源。

来源：[open-flapping-airplanes: reproducing the flapping airplanes megakernel](https://github.com/Bobliuuu/open-flapping-airplanes)

## 权重空间编程：修复循环与负面对照
{: #reading-weight-space-programming}

Weight-Space Programming 的 Qwen3.5-0.8B 案例编辑约 0.016% 权重，缓解 reasoning loop，MATH-500 从 7.9% 升至 48.1%。关键解释是解除已有能力的输出障碍：不循环的 Gemma 对照没有建立数学增益。

局限：仍使用受控 forward 反馈，非普遍零数据优化；只看原始权重识别迎合行为的实验失败，未来能力主张不应当作结果。

来源：[Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights](https://rikiyat.github.io/blog/weight-space-programming/)

## F3 Lightning：独立发布与共享执行
{: #reading-meta-f3-lightning}

F3 Lightning 将独立 feature 发布与共享执行图解耦，避免一个无效定义阻塞全部更新，再以稳定计算 ID、共享执行计划和缓冲区保留公共计算。Meta 报告可比 feature 约快 3.6 倍进入生产。

局限：3.6 倍是发布周期而非推理吞吐；无额外基础设施计算是特定比较，不代表无开发成本或所有 feature 完全隔离。

来源：[F3 Lightning: How Meta Accelerates Ads ML Features to Production at Scale](https://engineering.fb.com/2026/11/03/ml-applications/f3-lightning-how-meta-accelerates-ads-ml-features-to-production/)

## Trace linkage：具体 SQL 执行与查询上下文
{: #reading-grafana-trace-linkage}

Grafana trace linkage 先用 sqlcommenter 的 trace/span ID 匹配具体 SQL 样本，未命中时按规范化查询文本等信息关联历史。后者提供同类 query 上下文，并非该次执行的确定记录。

局限：Alloy 轮询可能漏掉短查询，精确匹配也尽力而为；SQL comment 对数据库缓存的影响需评估，相关不等于根因。

来源：[Trace linkage: connect the dots between your app traces and database queries](https://grafana.com/blog/trace-linkage-connect-the-dots-between-your-app-traces-and-database-queries/)

## AI Guard：agent 运行时检查与证据边界
{: #reading-datadog-runtime-security-ai-agents}

Datadog AI Guard 将检查放入 agent loop 的 prompt、输出和工具边界，结合会话、服务依赖与组织策略阻断或清理内容，并把安全信号关联到 traces 以复盘。

局限：文章没有给出攻击检出率、假阳性或 inline 开销；“及时阻断”是能力描述，不能替代独立对抗评估。

来源：[Agents make decisions at runtime—your security controls should too](https://www.datadoghq.com/blog/runtime-security-for-ai-agents/)
