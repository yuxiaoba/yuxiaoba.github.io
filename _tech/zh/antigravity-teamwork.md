---
id: antigravity-teamwork
title: 2026年11月15日｜Antigravity /teamwork：长任务如何组织独立验证
date: '2026-11-15'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- multi-agent
- agent-reliability
- systems-reliability
summary: 从干净上下文、依赖驱动重写与保留原测试，理解 Google 长任务 Agent 的验证机制及生产收益边界。
translation_source: assistant-authored bilingual content
long_read: true
source_url: https://research.google/blog/advancing-science-engineering-with-antigravitys-teamwork-feature/
permalink: /tech/zh/antigravity-teamwork/
published_at: '2026-11-15T15:30:22.801784+08:00'
updated_at: '2026-11-15T15:30:22.801784+08:00'
---
长时间运行的 Agent 系统，不能只依靠更多并行尝试。候选方案需要能被反驳的检查，已经完成的工作需要能被下一位执行者接续，测试本身也不能随着补丁一起被改到失去约束。Google 这篇报告最值得关注的，是将这些要求组织成不同的 /teamwork 工作流，并给出代码迁移、系统优化与生产调度案例。

原文：[Advancing science & engineering with Antigravity’s /teamwork](https://research.google/blog/advancing-science-engineering-with-antigravitys-teamwork-feature/) · Vahab Mirrokni · Google Research · 2026-11-13

## 用独立检查约束并行探索

报告把长任务的困难分成两类。第一类是单次生成不稳定：多开几个 Agent 可以增加找到方案的机会，却也可能同时产生多个看似合理的错误。/teamwork 将探索与专门的 falsifier 配对，例如 Lean 证明检查器、未修改的软件测试、执行模拟器和硬件计数器。候选是否可接受，取决于领域内可执行的检查，而不只是生成者对自己答案的评价。

这些检查器提供的保证并不相同。Lean 能检查形式化命题的证明关系，软件测试只能覆盖其测试条件，硬件计时验证的是给定工作负载上的表现。文章也指出，数学家仍需确认形式化命题与原问题相符。因此，独立验证的意义在于明确证据来自哪里、能排除什么错误，不能把工具通过统一解释成整个项目已正确。

第二类困难是持续多天的上下文漂移。报告的做法是按步骤限制 Agent 所接收的文件与工具，由协调者把任务交给新的接班者，并让 critic 和 auditor 在不携带原生产者推理的干净上下文里检查结果。它试图减少冗长历史对判断的干扰，但干净上下文仍需要足够的任务约束与产物。这里是工作流设计说明，文章没有提供单独隔离“干净上下文”收益的消融实验。

## 重写任务先保住依赖和原测试

代码迁移是检验这套设计的具体例子。Agent 可能用 stub 替代难处理的依赖，或者改测试让错误实现通过。报告描述的 rewrite pattern 按依赖顺序调度模块：只有依赖可编译后，才开始后续模块；叶子模块连接原始、未修改的测试套件。这样，调度顺序和验收条件共同约束生成过程，避免多个模块各自“完成”却无法组合。

Google 报告称，在已有约 25% Zircon 移植的基础上，一次两周任务将剩余 C++ 重写为约 80 万行 safe Rust，通过全部内核单元测试并在 arm64 硬件启动。libgav1 视频解码器则被重写为约 17 万行 Rust，在广泛的一致性测试中达到逐位相同输出。最初 Rust 版本慢约四倍，之后给 Agent profiling 工具和样例视频优化目标，报告称最终在 x86_64 与 ARM 上比原 C++ 及手工优化汇编快 20–30%。

这些是厂商报告的项目结果，测试通过、可启动与逐位一致分别对应不同验收范围。文章没有列出完整测试矩阵、硬件配置和所有视频分布，因此不能推导为 Rust 重写普遍能加速。它更具体的启发是：先锁住可检查的行为，再将性能优化接在功能验证之后。报告还称 rewrite pattern 即将提供，不能把所有展示案例都当成当日已开放的产品功能。

## 串行修订与快速评测各有位置

/teamwork 以声明式自然语言 pattern 表达工作流，并将请求路由到相应模式。对于耦合紧密的代码，报告称对历史轨迹的分析促使 /boost 采用紧密衔接的串行实现与修订阶段。这说明并行度不是唯一的优化轴：如果分工边界不稳定，顺序迭代可能更适合维持一致的实现状态。文章没有给出这项调整的定量对照，适合视作工程经验。

对于评测昂贵的 kernel 搜索，DuoDiscover 则让四个并行 Agent 创建快速 yardstick，再用完整硬件测试持续校验候选排序。报告中的 Argon 设置在 17 个 JAXBench kernel 上相对参考实现达到 4.09× 几何平均加速，在七个已手工优化的 vLLM TPU Pallas kernel 上达到 2.99×。这两个数字属于博客描述的设置；论文主实验使用不同 backbone，报告 4.62×／2.68×，不能拼成同一次实验或混用基线。

原文给出完整评测耗时 7–32 分钟、快速评测约 23 秒的例子。关键不是小测试天然代表真实系统，而是周期性回到真实评测检查排序是否失真。这与重写任务保留原测试是一致的工程原则：生成者可以改变实现，接受变更的证据需要另有约束。

## 从生产收益看证据边界

报告称，Borg 调度工作流落地了两项变更，使某些硬件类型的 TPU 工作负载抢占减少 24%，同时保持 SLO 和集群利用率。其范围是特定硬件上的抢占事件，不能改写成整个 Borg 集群吞吐提高 24%。内存部分则描述了从全局指标与既有优化案例识别节省机会，以及带人工环节的监测 Agent；“识别机会”也不能等同于全部已兑现的实际节省。

对 AgentOps，值得带走的是三个具体控制点：以领域检查器筛选候选，以依赖和交接管理长任务，以原有测试和生产指标约束最终变更。Google 的报告覆盖多个项目，提供了机制和实施案例，但缺少统一实验协议。适合将这些案例作为可迁移的工作流设计证据，而不是一项已证明对所有长任务有效的统一算法。原文没有可解释这些机制的静态架构图，本文保留文字说明。
