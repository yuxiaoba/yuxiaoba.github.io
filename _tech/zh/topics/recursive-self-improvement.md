---
id: topic-recursive-self-improvement
title: '递归自我改进：Agent 如何修改自己的执行系统'
date: '2026-11-11'
updated_at: '2026-11-11'
lang: zh
published: true
layout: article
topic_guide: true
long_read: true
tags: [self-improvement, agent-reliability]
authoring_source: assistant
translation_source: assistant
permalink: /tech/zh/topics/recursive-self-improvement/
summary: 从 InfraRSI、BOXBOX 到 JoMoHa，比较改进对象、反馈闭环和验证边界，判断“自我改进”究竟发生在哪里。
---

RSI（Recursive Self-Improvement，递归自我改进）正在被用来描述多种不同的系统：有的优化训练集群，有的在长任务中重写工具，有的联合训练模型与执行框架。它们都让前一轮的经验影响后一轮，但**改了什么、反馈从哪里来、错误会传到哪里**，并不相同。

这个专题按问题组织阅读：先辨认改进对象，再比较闭环和证据。新增工作时，先看它是否改变了这张路线图，再决定放到哪一条线上。

## 先分清：谁在改，改的又是谁？

Harness 是模型外部组织执行的那层系统：工具接口、上下文管理、任务循环、错误恢复和评测流程等。换提示、改可执行代码、训练模型权重，是不同层面的变化；“能自动搜索更快配置”也不等于“Agent 已能递归升级自身全部能力”。

| 工作 | 主要改进对象 | 改进发生在哪里 | 反馈与验证 |
| --- | --- | --- | --- |
| [InfraRSI](https://arxiv.org/pdf/2611.11558) | 分布式训练的启动配置和代码补丁 | 训练优化试验之间；经验跨环境积累 | 固定训练契约，测量时间与内存，复测候选 |
| [BOXBOX](https://arxiv.org/pdf/2611.09218) | Agent 当前使用的可执行 harness | 同一个长任务的运行过程中 | 性能任务反馈；独立 kernel 检查并激活新版本 |
| [JoMoHa](https://arxiv.org/pdf/2611.11499) | 生成 harness 的 Engineer 策略和执行任务的 Solver 策略 | 联合强化学习训练过程中 | 用实际执行轨迹协调两个策略的更新 |

表里三行不是递进的“能力等级”。选择路线要先看问题：你是在找训练系统的更好设置、修补正在执行的 Agent，还是训练更能协同的模型与 harness？

## InfraRSI：先保证优化前后还是同一份工作

InfraRSI 先锁定训练负载、loss 与计时不变量，再结合 profiling、配置搜索、代码修改和重新测量。其关键不是只记住一次最快结果，而是检查提速有没有偷换计算任务，并把失败试验纳入搜索经验。[原论文](https://arxiv.org/pdf/2611.11558)

这条路线最适合带着一个验证问题来读：**改完有效 batch、精度或计时范围后，那个更短的时间还有没有可比性？** 经验迁移也要检查模型、硬件和通信拓扑。局部数值检查不能替代完整训练收敛验证。

→ [当日解读：InfraRSI 的任务契约与验证流程](/digest/zh/daily/2026-11-11/#paper-arxiv-2611.11558)

## BOXBOX：长任务暴露了问题，能否不中断地改 harness？

BOXBOX 让 Agent 在任务中调用审阅入口；独立 kernel 暂停执行、保存上下文、检查新 harness 并热加载，激活失败时回退。改进对象是当前任务的执行系统，并不是在线更新基础模型权重。[原论文](https://arxiv.org/pdf/2611.09218)

这让阅读重点从“新配置能否在下一个任务上奏效”转向**状态能否跨版本保留**：未完成的工具动作如何处理，旧记录还能否被新版本理解，回退是否会重复外部副作用？这些是需要额外检查的工程问题，不能仅从支持热加载推断已经解决。

→ [当日解读：BOXBOX 的运行时修订与实验条件](/digest/zh/daily/2026-11-10/#paper-arxiv-2611.09218)

## JoMoHa：改了 harness，模型是否还能配合？

JoMoHa 把可执行 harness 的生成者 Engineer 和任务执行者 Solver 都作为学习策略。论文关注的是：两者各自变好，却可能越来越不兼容；因此使用共享任务执行经验协调联合训练。[原论文](https://arxiv.org/pdf/2611.11499)

这里需要区分**模型能力下降**和**模型与旧 harness 不再匹配**。比较保存下来的模型、固定 harness 和不同组合，比只看联合系统总分更能定位退化。论文在 ALFWorld、WebShop 和 DBBench 上评估，不能将其结果直接视为真实生产系统的长期自治能力。

## 三种收益不能直接排成一张榜

训练吞吐、被优化程序的加速比、Agent 的任务成功率，回答的是不同问题。即使都说“提升”，也不能把它们当成同一种能力。

| 阅读时要问 | 为什么影响结论 |
| --- | --- |
| 优化对象和正确性要求固定了吗？ | 改了任务本身，可能得到不可比的“收益” |
| 搜索、失败和验证花费算进去了没？ | 推理阶段更便宜，不代表完整优化过程更便宜 |
| 评估的是当前任务，还是没见过的任务？ | 任务内适应和跨任务泛化需要不同证据 |
| 谁判定可以采用新版本？ | 生成者自评、隐藏测试和独立复核提供不同保证 |
| 如何保存状态和回退？ | 代码能恢复，不代表外部动作也能撤销 |
| 权限与安全约束能被修改吗？ | 更会完成任务，不等于获得更广的授权 |

## 接下来值得跟踪什么？

我会优先跟踪三个问题：**验证成本是否随改进复杂度上升；经验能否迁移而不污染评测；长期改动是否仍遵守原来的权限与任务语义。** 这是跨工作阅读后的判断，不是三篇论文共同证明的结论。

新的论文如果只在既有路线内换一个搜索器，适合放进日更；如果改变了反馈来源、状态管理或验证方法，就值得更新这个专题。后续阅读可以沿“固定任务 → 修改执行系统 → 协调模型与执行系统”展开，而不是把所有带 RSI 的标题放进同一类。

## 原文阅读

- [InfraRSI: Harnessing Recursive Self-Improvement for Training Infrastructure](https://arxiv.org/pdf/2611.11558)
- [BOXBOX: Recursive Harness Self-Improvement for Long-Running Performance Optimization](https://arxiv.org/pdf/2611.09218)
- [JoMoHa: Joint Model–Harness Optimization with Reinforcement Learning](https://arxiv.org/pdf/2611.11499)
