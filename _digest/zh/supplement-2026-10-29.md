---
id: supplement-2026-10-29
title: 2026-10-29｜补读：论文与技术进展
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
translation_source: assistant-authored paired Chinese/English reading notes
source_type: paper
permalink: /digest/zh/supplement/2026-10-29/
summary: 44 条经原始来源核对的论文与技术补读。
tags:
- agent-reliability
- coding-agents
- observability
---

[返回当日论文集](/digest/zh/daily/2026-10-29/)

## safeL4: Rethinking Safe-Language-Based Single Address Space Microkernels
{: #reading-arxiv-2610.35999}

safeL4 用 Rust 对象能力统一暴露系统资源，以安全语言隔离减少地址空间和特权级切换。原文在 Raspberry Pi 3B+ 上比较 seL4、Redox 和 Linux，报告微内核原语平均约 1.9 倍性能。对系统设计的启示是把隔离边界与调用成本一起考虑。

局限：这不是整个应用统一加速 1.9 倍；可信基础仍包含 unsafe 代码、Rust 库和工具链假设，实验硬件范围有限。

来源：[safeL4: Rethinking Safe-Language-Based Single Address Space Microkernels](https://arxiv.org/abs/2610.35999)

## AgentBaton: Efficient Model Collaboration in Agentic Tasks
{: #reading-arxiv-2610.35959}

AgentBaton 研究同一长任务中的一次模型交接：先让强模型推进，再由便宜模型接续。11 组模型对、两个基准中，作者报告平均 API 成本降低 65.9%，准确率大体保持；反向交接通常更差。工作目录状态与历史传递方式也是设计变量。

局限：结果取决于模型对、任务和价格；最高准确率增益不是所有配置的保证，也未证明任意本地部署都节省端到端成本。

来源：[AgentBaton: Efficient Model Collaboration in Agentic Tasks](https://arxiv.org/abs/2610.35959)

## Distributed LLM Inference via Communication-Efficient Speculative Decoding
{: #reading-arxiv-2610.35957}

DISCO 在服务器再放一份草稿小模型，让拒绝采样需要的草稿分布就地计算，设备只传 token 索引和标量概率，从而减少词表规模的数据传输。原文同时评估带宽仿真和异构设备环境；其价值在于改变分布计算的位置，同时保留目标采样分布。

局限：服务器复制草稿模型有资源成本；主要评估单请求，多用户并发是未来工作，不能直接推导线上吞吐收益。

来源：[Distributed LLM Inference via Communication-Efficient Speculative Decoding](https://arxiv.org/abs/2610.35957)

## EdgePace: Deadline- and Freshness-Aware LLM Scheduling on Unified-Memory Platforms
{: #reading-arxiv-2610.37307}

EdgePace 在统一内存设备上监控前台内存压力，并在 prefill/decode 的安全暂停点调度 LLM，以兼顾截止期和输出新鲜度。手机及三种 Jetson 的两个工作负载中，前台超期减少 24.1%–96.1%，保留 64.9%–98.5% 的 LLM 吞吐。

局限：需要按平台和负载校准；实验输出较短，机器人案例使用 MuJoCo，LLM 输出没有改变跟踪动作，不能视为实机闭环安全保证。

来源：[EdgePace: Deadline- and Freshness-Aware LLM Scheduling on Unified-Memory Platforms](https://arxiv.org/abs/2610.37307)

## CRISP: Co-designing Pruning and Scheduling for Efficient MoE Inference on Edge Servers
{: #reading-arxiv-2610.37442}

CRISP 按专家组合的频率和角色分配执行宽度，并把专家加载与计算重叠。两个 MoE 模型在 Jetson 和 RTX 4090 测试中，同内存预算吞吐最高提高 2.1 倍，伴随最高 3.6% 的准确率损失。它把保留多少专家容量与如何调度作为同一个优化问题。

局限：并非无损加速；热组合统计、缓存容量限制和模型会影响收益，冷组合的质量下降更明显。

来源：[CRISP: Co-designing Pruning and Scheduling for Efficient MoE Inference on Edge Servers](https://arxiv.org/abs/2610.37442)

## Request-Adaptive Execution for Efficient Hybrid LLM Inference
{: #reading-arxiv-2610.37432}

该研究在 prefill 阶段为请求选择 Attention/SSM 分支，解码期间保持布局不变，再用选择性批处理和混合状态缓存处理请求间差异。作者在 H100 上报告最高 3.87 倍吞吐，说明自适应模型必须与执行和前缀复用一起设计。

局限：摘要称 Morph，正文称 Flex，原文命名不一致；需要相应模型结构及微调，最高收益不能推广至普通模型或任意请求。

来源：[Request-Adaptive Execution for Efficient Hybrid LLM Inference](https://arxiv.org/abs/2610.37432)

## JustGoal: With Only a Goal, the AI Baseline Is Above the Expert Kernels
{: #reading-arxiv-2610.36434}

JustGoal 只向通用 agent 给出目标和约束，由其建立优化循环。作者独立进行最终正确性和计时检查；B200 上 10 类算子有 8 类超过所选开源库，9 类可比较算子中 5 类超过公开专用 agent kernel。值得采用的是同模型、同范围的目标驱动基线。

局限：仅覆盖所测算子、形状、模型和硬件；计时排除 JIT，不能等同端到端开发成本或所有专家实现。

来源：[JustGoal: With Only a Goal, the AI Baseline Is Above the Expert Kernels](https://arxiv.org/abs/2610.36434)

## Less is more: learning what to profile for GPU kernel optimization
{: #reading-arxiv-2610.36576}

AutoProfiler 把 profiling 本身作为可学习策略：用优化反馈反复 REWRITE/SPLIT 决策树，为不同 kernel 选择不同硬件指标，最后只调用一次 LLM 重写。策略构建使用 CUDA-Agent-Ops-6K，测试使用独立 KernelBench；更多指标并不单调带来更好优化。

局限：独立任务划分降低直接重叠风险，但不是跨硬件和模型普适性的证明；策略构建成本也需计入使用成本。

来源：[Less is more: learning what to profile for GPU kernel optimization](https://arxiv.org/abs/2610.36576)

## God Does Not Play Dice: Enforcing Batch Invariance in Agentic Kernel Generation
{: #reading-arxiv-2610.36623}

BIEvolve 在性能测量前加入静态依赖检查与跨 batch 上下文的逐位一致性检查。作者在 83 个适用的公开产物中确认 19 个 batch invariance 违规；三个生成框架中通过率由 67.6% 升至 91.9%，保留基线几何平均加速收益的 91.8%。

局限：测试采用风险导向的紧凑任务集；动态通过不是对所有输入的形式化证明，也不能把残余失败忽略。

来源：[God Does Not Play Dice: Enforcing Batch Invariance in Agentic Kernel Generation](https://arxiv.org/abs/2610.36623)

## Kernel Performance Engineering under Physical Non-Idealities
{: #reading-arxiv-2610.37466}

该研究揭示 H100 的逻辑 SM 数量与可并发执行 cluster 的资源不同：132 个暴露 SM 并不意味着 cluster 可同时使用全部。按执行波次选择 cluster，Hopper FlashAttention 4 吞吐最高提高 5.30%；减少数据移动也可能腾出功耗预算，提高计算频率。

局限：具体 SM 上限和收益依赖硬件、功耗及启动形状，迁移时必须重新测量，不能按标称规格直接推断。

来源：[Kernel Performance Engineering under Physical Non-Idealities](https://arxiv.org/abs/2610.37466)

## DeepInfer-Mac: Running a 750B-Class MoE on a 24 GB Laptop
{: #reading-arxiv-2610.36564}

DeepInfer-Mac 通过 SSD 按需加载专家，让 24GB MacBook Air 执行 750B 级模型。作者实测仅 0.21–0.72 token/s，低比特模型占 SSD 338GiB；可运行与交互可用是不同目标。

局限：仅一台机器、一个转换模型和单序列；主机启用 swap，生成示例不是压缩质量基准。

来源：[DeepInfer-Mac: Running a 750B-Class MoE on a 24 GB Laptop](https://arxiv.org/abs/2610.36564)

## Folding Attention Biases into Keys Makes Compacted KV Caches Run on Standard Kernels
{: #reading-arxiv-2610.36520}

该工作沿每个 head 的拟合方向移动 key，把压缩 KV 所需的静态 attention bias 折叠进标准缓存，避免改写 query 路径。等预算下可经 KV connector 使用原生 vLLM kernel，13/14 项准确率与原方法差异在噪声内。

局限：不是精确等价；query 漂移会放大误差，原始非均匀预算下优势减弱，部分测试统计分辨率约五分。

来源：[Folding Attention Biases into Keys Makes Compacted KV Caches Run on Standard Kernels](https://arxiv.org/abs/2610.36520)

## DCKV: Learned Transform Coding of the Prompt KV Cache in Hybrid Language Models
{: #reading-arxiv-2610.36950}

DCKV 联合训练变换、量化器和熵模型，在冻结语言模型上权衡码长与输出偏差。Qwen3.5-2B 的三个长上下文基准中，压缩 token 字节数减少超过 55 倍，分数损失不超过 1.8 分。

局限：压缩 token 的字节比不等于整机显存或端到端加速；只测一个模型，KVTC 基线使用作者修订的公开实现。

来源：[DCKV: Learned Transform Coding of the Prompt KV Cache in Hybrid Language Models](https://arxiv.org/abs/2610.36950)

## INC-MoE: Overlapping In-Network Collectives and Expert Computation for Expert-Parallel Mixture-of-Experts Inference
{: #reading-arxiv-2610.36339}

INC-MoE 用网内 AllGather/ReduceScatter 加上分带 persistent kernel，重叠 dispatch、专家计算和 combine。四路专家并行的 OLMoE prefill 测试中，TTFT 最高降低 33%，吞吐最高增加 50%。

局限：网内交换机由第五个加速器仿真，不是商用交换机实测；输出余弦一致不应写成逐位相同。

来源：[INC-MoE: Overlapping In-Network Collectives and Expert Computation for Expert-Parallel Mixture-of-Experts Inference](https://arxiv.org/abs/2610.36339)

## Callosal: Rethinking the Kernel Page Cache for Disaggregated Storage and Memory
{: #reading-arxiv-2610.36347}

Callosal 把共享解耦内存作为集群 page cache，借助 RDMA 与可编程交换机提供接近本地文件系统的访问一致性。非极端竞争的混合读写中，作者报告平均吞吐约为 NFS 的 4.6 倍。

局限：完整 writeback 与持久性尚未实现，内存多为静态划分；不能把缓存一致性等同于完整崩溃恢复保证。

来源：[Callosal: Rethinking the Kernel Page Cache for Disaggregated Storage and Memory](https://arxiv.org/abs/2610.36347)

## WAKMan: Workload Aware KVCache Manager
{: #reading-arxiv-2610.36355}

WAKMan 根据流量回放在 LRU 与 S3FIFO 间选择，避免预先读取 prompt 或标注请求类型。20 种混合流量中，相对 LRU 平均命中率提高五个百分点；不同复用间隔会改变最佳策略。

局限：全部使用合成流量，仅两种候选策略；命中率收益不能直接当作等比例延迟收益。

来源：[WAKMan: Workload Aware KVCache Manager](https://arxiv.org/abs/2610.36355)

## PipeLink: Contract-Guided Linking of GPU Kernel Components
{: #reading-arxiv-2610.37200}

PipeLink 为独立编译的 GPU 组件携带资源契约，联合分配共享内存、barrier 等资源，再通过 LTO 链接。51 个配置中，链接性能与同源单编译单元相差约 0.2% 以内，便于跨库重组 kernel。

局限：契约只互相校验，并不证明组件遵守契约；数值检查与 sanitizer 仍必需，不能宣称形式化正确。

来源：[PipeLink: Contract-Guided Linking of GPU Kernel Components](https://arxiv.org/abs/2610.37200)

## EnvSched: Environment-Aware Scheduling for Rollout-Efficient Agent Reinforcement Learning
{: #reading-arxiv-2610.37609}

EnvSched 以环境—任务对为调度单位，用奖励方差和覆盖度分配 rollout。Qwen3-8B 在三个工具使用基准上，40 步训练的平均分 48.81，超过随机选择训练 120 步的最佳分数。

局限：训练步数不是端到端耗时；收益依赖图关系与环境覆盖，不能推断所有 RL 任务都提速三倍。

来源：[EnvSched: Environment-Aware Scheduling for Rollout-Efficient Agent Reinforcement Learning](https://arxiv.org/abs/2610.37609)

## Taming Multi-Dimensional Skew in Sparse Matrix Multiplication with Contention-Aware Scheduling [Technical Report]
{: #reading-arxiv-2610.36822}

AMS 用固定结果规模的 morsel 解耦 SpGEMM 的计算量、输出密度与局部性倾斜，再结合竞争感知调度、SMT 控制和混合累加器。其关键是负载均衡不能以加剧缓存竞争为代价。

局限：针对所测稀疏结构与硬件，不能把收益推广到所有矩阵或 GPU kernel。

来源：[Taming Multi-Dimensional Skew in Sparse Matrix Multiplication with Contention-Aware Scheduling [Technical Report]](https://arxiv.org/abs/2610.36822)

## IOSage: Detecting HPC I/O Bottleneck Patterns to Guide LLM Recommendations
{: #reading-arxiv-2610.36370}

IOSage 让训练好的分类器判断 Darshan 日志瓶颈，LLM 根据模式卡和配置给建议。无模式的 78 次测试中，建议修改从 LLM 单独判断的 64 次降至 9 次；实际修改由人应用，并用成对重复运行测时。

局限：新配置/作业的 Micro-F1 为 .832，低于总体 .929；不是无人值守自动修复，生产外部验证仅九条轨迹。

来源：[IOSage: Detecting HPC I/O Bottleneck Patterns to Guide LLM Recommendations](https://arxiv.org/abs/2610.36370)

## An Internet for the KV Cache: Rethinking Classical Infrastructure Boundaries in the LLM Inference Age
{: #reading-arxiv-2608.01526}

该观点论文把 KV cache 看成可跨存储层、区域和云分发的内容，用模型计算量、缓存大小、复用间隔及传输价格共同决定存储还是重算。10 月 LMCache 博客是对 8 月论文的改写，应作为同一来源链阅读。

局限：这是基础设施愿景和条件成本分析，不是已经部署的全球 KV 网络；示例没有涵盖全部存储和运营成本。

来源：[An Internet for the KV Cache: Rethinking Classical Infrastructure Boundaries in the LLM Inference Age](https://arxiv.org/abs/2608.01526)

## Who Convinced Whom? Tracing How LLMs Change Their Minds in Multi-Agent Systems
{: #reading-arxiv-2610.35930}

MAD Bench 对比多 agent 辩论与轮数匹配的独立反思。三个模型中，辩论可带来小幅准确率改善，却使一致错误率比反思高 3.1–7.4 个百分点；评估应同时报告准确率、错误相关性与全体一致错误。

局限：问题由单一模型构造，参考标签无独立人工标注；英语与文化覆盖有限，不能将数字外推到生产团队。

来源：[Who Convinced Whom? Tracing How LLMs Change Their Minds in Multi-Agent Systems](https://arxiv.org/abs/2610.35930)

## CASEL: Consequence-Aware Selective Execution for Reliable Long-Horizon Tool-Using Agents
{: #reading-arxiv-2610.36570}

CASEL 根据失败概率、后果、可逆性和证据新鲜度分配验证、沙箱或审批。在相同干预菜单和成本的模拟中，相比不确定性排序，有害轨迹比例由 14.75% 降至 7.02%；轨迹风险预算反而没有帮助。

局限：干预效果由模拟器设定，并非实际工具 agent 部署有效性的证据。

来源：[CASEL: Consequence-Aware Selective Execution for Reliable Long-Horizon Tool-Using Agents](https://arxiv.org/abs/2610.36570)

## CIVER: Causal Intervention Verification for Reliable Code Review
{: #reading-arxiv-2610.36010}

CIVER 用针对性修复、无关修改与语义保持变换检查代码评审结论：真正问题应对相关修复敏感，对无关变化稳定。SWE-Review-Bench 中作者报告通过针对性修复识别 77% 的真实缺陷。

局限：生成的干预与 verifier 本身也会出错；77% 不是对所有评审结果的精确率或因果正确性证明。

来源：[CIVER: Causal Intervention Verification for Reliable Code Review](https://arxiv.org/abs/2610.36010)

## Do Coding Agents Still Need a Debugger? Frontier-Model-Based Fault Localization at the Accuracy Ceiling
{: #reading-arxiv-2610.36015}

在短小且规格明确的 LeetCode 程序中，前沿 agent 静态定位单行注入故障已接近满分。鼓励调试可消除部分剩余错误，但 token 成本提高 14.7–27 倍，说明工具收益必须结合任务难度和成本解释。

局限：单行合成故障与短 Python 程序不能代表大型仓库、并发错误或多故障调试。

来源：[Do Coding Agents Still Need a Debugger? Frontier-Model-Based Fault Localization at the Accuracy Ceiling](https://arxiv.org/abs/2610.36015)

## PROBE: Frontier Coding Agents Find Different Bugs Than Maintainers Fix
{: #reading-arxiv-2610.35987}

PROBE 以 20 个仓库 18 个月中维护者修复的 2457 个 bug 评估主动发现。agent 对该参考集召回低于 21%、精确率低于 9%，但约 85% 发现被评为有效；发现的错误分布与维护者修复分布不同。

局限：参考集不完整；不能把低于 9% 的参考匹配精确率写成其余发现均为假阳性。

来源：[PROBE: Frontier Coding Agents Find Different Bugs Than Maintainers Fix](https://arxiv.org/abs/2610.35987)

## ProCerDCL: Query-Efficient Black-Box Probabilistic Verification of Deep Learning Compiler Optimization
{: #reading-arxiv-2610.36499}

ProCerDCL 用单个顺序检验输出接受、拒绝或不确定，控制指定分布下的违例概率错误。840 个输入—后端实例有 817 接受、19 不确定和 4 拒绝；相同数值参数下基线使用 3.6–4.2 倍独立样本。

局限：保证依赖独立采样、无状态 oracle 和指定输入分布；接受不等于全输入语义等价。

来源：[ProCerDCL: Query-Efficient Black-Box Probabilistic Verification of Deep Learning Compiler Optimization](https://arxiv.org/abs/2610.36499)

## kw-bench: Breaking Frontier Harnesses on Real-World Tasks
{: #reading-arxiv-2610.36405}

kw-bench 从跨代 SAP 原始导出重建五年 VAT 账目，用确定性答案评分，考验长任务中的证据关联和核对。实验提示 harness 配置会影响同一模型表现，但前沿模型又能显著改变难度。

局限：每个配置仅运行一次，首个任务族及两个模型不足以稳定排名；不能把供应商 harness 的一次失败推广为整体能力。

来源：[kw-bench: Breaking Frontier Harnesses on Real-World Tasks](https://arxiv.org/abs/2610.36405)

## Compatibility and future-proof testing for multi-agent systems
{: #reading-arxiv-2610.36289}

该理论工作区分“与种子 agent 兼容”和“与所有未来获准 agent 兼容”，以种子闭包刻画后者，并分析仅与种子交互的测试能力限制。单个合作测试通过不足以推出未来组合安全。

局限：是抽象理论，不是 LLM agent 部署实验；需要明确 agent 空间、结果规则和不可接受结果。

来源：[Compatibility and future-proof testing for multi-agent systems](https://arxiv.org/abs/2610.36289)

## Where Should the Evaluation Budget Go in LLM-Driven Agent Scaffold Evolution?
{: #reading-arxiv-2610.37276}

EvalAlloc 在搜索时使用稀疏反馈，先建立共享题目与固定评分参照，最后用成对 successive halving 确认候选。四个基准、两个演化框架中，约一半评估单元即可达到竞争性表现。

局限：评估单元减少不等于成本或耗时减半；题目选择和响应模型可能影响近似候选排序。

来源：[Where Should the Evaluation Budget Go in LLM-Driven Agent Scaffold Evolution?](https://arxiv.org/abs/2610.37276)

## When the Critic Falls Behind: Co-Evolving Rubrics and Harnesses for Continual Agent Self-Improvement
{: #reading-arxiv-2610.36826}

RuHarness 从执行轨迹更新行为 rubric，优先处理仍未解决的弱点，再修改 agent harness，同时保持任务目标和模型固定。其研究点是让改进依据随系统行为变化，而非长期使用静态批评规则。

局限：模型自身参与执行和演化，held-out 增益不代表外部 rubric 一定正确或长期改进不会过拟合。

来源：[When the Critic Falls Behind: Co-Evolving Rubrics and Harnesses for Continual Agent Self-Improvement](https://arxiv.org/abs/2610.36826)

## Meta Andromeda：融合执行与 GPU 共置的边界
{: #reading-meta-andromeda-ads-retrieval-gpu-co-design}

Meta Andromeda 把 embedding gather、MoE 交互和评分融合，避免中间张量落 HBM；再将索引匹配、评分和 top-K 放到同一 GPU 服务器，减少跨机候选传输。文章分别报告评分 kernel 超百亿广告/秒、完整流水线超十亿。

局限：均为厂商特定系统报告，kernel 与端到端口径不同；广告评分吞吐不能推广成通用 LLM 推理收益。

来源：[Meta Andromeda: Powering the Next Generation of Ads Retrieval Through Model-System Co-Design](https://engineering.fb.com/2026/10/28/ml-applications/meta-andromeda-next-gen-ads-retrieval-gpu-co-design/)

## PyTorch 2.15：分布式默认行为与故障诊断
{: #reading-pytorch-2-15-release-blog}

PyTorch 2.15 将重写的 NCCL 后端设为默认，并增加 hang 时的 flight recorder 与跨 rank 转储；提供旧后端回退路径。NIXL 单边传输及 FSDP2 精度、内存控制也改变分布式执行配置，升级应关注默认行为与故障诊断。

局限：多项 API 标为 unstable；这里只核对官方发布说明，未运行升级、性能或故障恢复测试。

来源：[PyTorch 2.15 Release Blog](https://pytorch.org/blog/pytorch-2-15-release-blog/)

## DGX Spark MoE 优化：实测收益与组合故障
{: #reading-nvidia-3-ways-boost-moe-inference-dgx-spark}

该 DGX Spark 实践组合 Humming、FP8 LM head 和 MTP；全 GSM8K 测试吞吐提高 42.5%、平均延迟降低 24.5%，远低于合成场景 185.1% 的吞吐增益。只共享权重而不共享完整 LM-head 模块会让组合优化反而退化。

局限：厂商报告限于 Ling 模型、单 batch 和给定采样；准确率无显著差异不是所有输出逐位等价。

来源：[3 Ways to Boost MoE Inference on NVIDIA DGX Spark](https://developer.nvidia.com/blog/3-ways-to-boost-moe-inference-on-nvidia-dgx-spark/)

## o11y-bench 1.1：可观测性任务的结果验证
{: #reading-grafana-o11y-bench-v1-1-fireworks}

o11y-bench 1.1 在运行中的 Grafana 栈执行 64 个任务，核对遥测事实、引用 trace 和持久化 dashboard 差异；无效标准查询视为评分错误。文章强调三次运行的一致性，且新版评分建立新基线。

局限：遥测为合成场景；1.1 与 1.0 不可直接比较，文章对 Pass^3 的定义应以实现核对，不能自行套用其他基准定义。

来源：[Evaluate AI models for observability: o11y-bench joins Fireworks' Specialized Intelligence Index and reaches v1.1](https://grafana.com/blog/evaluate-ai-models-for-observability-o11y-bench-joins-fireworks-specialized-intelligence-index-and-reaches-v1-1/)

## Miles：agent RL 的长尾、沙箱与资源上限
{: #reading-lmsys-miles-mi355x-agentic-rl-swe-agents}

Miles 的 MI355X 实践发现长尾轨迹、沙箱启动和固定并发上限比 GPU 更早限制 agent RL。文章区分单节点长度限制带来的约三倍步速与扩容加修复带来的约四倍 rollout 吞吐，并指出基础设施失败会被错误计为零奖励。

局限：四倍吞吐同时增加推理节点，非同资源比较；准确率仅 100 个分层抽样任务，不能写成完整 SWE-bench。

来源：[Training SWE agents with Miles on MI355X: taming long-tail trajectories and complex sandbox coordination](https://lmsys.org/blog/2026-10-22-miles-mi355x-agentic-rl)

## 网络中断复盘：共享物理依赖与故障域
{: #reading-cloudflare-q3-2026-internet-disruption-summary}

Cloudflare Radar 的第三季度记录有 49 次中断，其中 14 次与供电有关。洪都拉斯互联设施断电影响至少 11 家运营商，说明表面独立的网络服务可能共享物理故障域。

局限：是 Radar 观测和事件归因汇总，不是全球中断全量普查；流量下降不能直接换算成用户数量或应用停机。

来源：[What Took the Internet Offline in Q3 2026](https://blog.cloudflare.com/q3-2026-internet-disruption-summary/)

## GKE：高密度沙箱的网络身份瓶颈
{: #reading-google-gke-networking-dataplane-agentic-ai}

GKE 文章把高密度 agent 沙箱启动瓶颈定位到网络身份：每个 pod 的动态标签会生成独立身份。把不参与选择器的元数据放入 annotations，或精确排除不相关标签，可减少身份分配与 eBPF map 更新。

局限：过滤前需确认标签不承担网络策略语义；厂商不同沙箱/恢复基准不能合并为统一吞吐保证。

来源：[GKE networking dataplane for large agentic AI workloads](https://cloud.google.com/blog/products/networking/gke-networking-dataplane-for-large-agentic-ai-workloads)

## Volcano 1.16：事件驱动重试与资源公平
{: #reading-cncf-volcano-v1-16}

Volcano 1.16 引入 NamespaceQueue、历史用量 fairshare 和 HyperNode 反亲和。不可调度 Job 缓存按拒绝原因等待相关事件再重试，减少积压反复检查，并保留 watchdog 定期重试。

局限：缓存默认关闭，仅有安全事件提示的拒绝插件参与；发布说明不等同于本地性能或容灾验证。

来源：[Volcano v1.16 Released: NamespaceQueue, fairshare, and a broader HyperNode ecosystem](https://www.cncf.io/blog/2026/10/28/volcano-v1-16-released-namespacequeue-fairshare-and-a-broader-hypernode-ecosystem/)

## Foundry 长任务恢复：检查点与幂等边界
{: #reading-microsoft-copilot-harness-foundry}

Foundry 区分托管 Copilot harness 预览与 hosted agent 长任务恢复：平台检测中断并以原始输入重启，应用负责保存检查点和中间结果，并避免重复外部操作。仅有对话历史不足以恢复进行中的工作。

局限：这是官方能力和责任边界说明，没有给出可靠性或恢复延迟基准；恢复不保证外部操作 exactly-once。

来源：[Introducing the Microsoft Copilot harness in Foundry Agent Service](https://devblogs.microsoft.com/foundry/microsoft-copilot-harness-in-foundry/)

## Google Agent Skills：把指令更新作为行为发布
{: #reading-google-agent-skills-like-products}

Google 把 skill 指令改动视为行为发布：要求版本提升、比较评估报告、文件与链接校验，以及 AI 审阅后的人类专家批准。评估期望须拆成单一判据，确定性命令放入脚本，避免把复杂命令链全写入提示。

局限：流程经验不证明所有 skill 有正收益；仓库规模与 star 数不是质量指标，AI 审阅仍需独立验证。

来源：[Behind the scenes, two months later: How we ship Google Agent Skills like products](https://cloud.google.com/blog/topics/developers-practitioners/behind-the-scenes-two-months-later-how-we-ship-google-agent-skills-like-products)

## GKE Flow Logs：保留临时 pod 的网络归属
{: #reading-google-vpc-flow-logs-troubleshoot-gke}

VPC Flow Logs 在采样时把临时 pod IP 关联到工作负载、namespace 和 service，保留 pod 消失后的网络归属证据。文章用 Online Boutique 演示依赖映射与服务流量排查，适合补充 L3/L4 诊断。

局限：采样日志不是全流量或因果证明；intranode visibility 可能重启组件并增开销，分析桶升级有前置条件。

来源：[Using VPC Flow Logs to troubleshoot GKE workloads](https://cloud.google.com/blog/products/containers-kubernetes/using-vpc-flow-logs-to-troubleshoot-gke-workloads)

## @jiayq 手写长文：用 agent 集群优化 LLM 推理（DeepSeek 4.1 Flash serving 实践）
{: #reading-x-jiayq-2115490096049004765}

Yangqing Jia 的一线观察强调：超过一半有用优化无需新 kernel，配置、图和启动顺序同样重要；孤立 kernel 加速可能在完整 serving 中退化。数值、端到端质量、遥测与 A/B 测试决定 agent 能否持续探索。

局限：社交长文未给出完整复现实验；230 次提案和 94 次有效是作者统计，不能据此证明自动收敛或普遍提速。

来源：[@jiayq 手写长文：用 agent 集群优化 LLM 推理（DeepSeek 4.1 Flash serving 实践）](https://x.com/jiayq/status/2115490096049004765)

## @ekzhang1：agent 用 Resin 在 A100 上从零写小模型（Gemma E2B）推理 runner
{: #reading-x-ekzhang1-2115429450833699165}

Resin 作者补充 A100 小模型 runner 实验：低 batch 下融合小算子、调整 attention 规划，以及减少 assistant KV 开销。此前日报已介绍 Resin 调度与故障边界，本条只保留新增的模型/硬件优化观察。

局限：性能数值来自社交帖，未在本次运行复现；项目仍是实验库，不能当作生产性能优势。

来源：[@ekzhang1：agent 用 Resin 在 A100 上从零写小模型（Gemma E2B）推理 runner](https://x.com/ekzhang1/status/2115429450833699165)
