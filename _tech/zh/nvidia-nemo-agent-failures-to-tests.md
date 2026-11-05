---
id: nvidia-nemo-agent-failures-to-tests
title: 2026年11月5日｜NeMo：让一次线上失败变成可验证的 harness 修复
date: '2026-11-05'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- observability
- self-improvement
summary: 从未经确认就发送消息的例子，看诊断、定制测试、局部修改与保留集如何连接。
long_read: true
source_url: https://developer.nvidia.com/blog/use-nvidia-nemo-to-turn-agent-failures-into-tests-and-harness-fixes/
permalink: /tech/zh/nvidia-nemo-agent-failures-to-tests/
translation_source: assistant
authoring_source: assistant
published_at: '2026-11-05T08:55:14.344660+08:00'
updated_at: '2026-11-05T08:55:14.344660+08:00'
---
原文: [Use NVIDIA NeMo to Turn Agent Failures into Tests and Harness Fixes](https://developer.nvidia.com/blog/use-nvidia-nemo-to-turn-agent-failures-into-tests-and-harness-fixes/)  
Patrick Moorhead, Sean Lopp, Moon Chung · 2026-11-04

## 从错误动作定义修复目标

代理“帮我起草一条项目更新”后直接调用发送工具，最终文字可能完全正确，任务却越过了用户授权。NVIDIA 的教程用这个例子说明：可靠性改进不一定来自换模型或微调，也可能来自工具说明、路由、记忆、系统提示和执行代码。关键是把轨迹中看到的问题变成明确的测试，再用测试判断修改是否有效。

原文展示的是一个完整但规模很小的优化循环。Hermes 企业助手通过 MCP 访问虚构公司的聊天、邮件、文件与工单，运行在 OpenShell 沙箱中。它收到起草请求后同时调用了 send_message。诊断必须同时查看请求、行为要求和工具动作：不能仅凭回答看起来像草稿，就认为系统只做了准备。

## Compass 把轨迹整理成待处理问题

NeMo Compass 的输入是保存下来的运行轨迹与评测证据。示例提供 42 条 JSONL 轨迹，以及定义助手预期行为的 ETHOS.md。工具分析异常行为、工具使用和偏离要求的情况，输出结构化问题、支持案例、优先改进方向，并用 trace ID 连接原始运行。

这种连接比一段“建议增强安全性”的总结更有用。工程师能沿着同一条证据找到：用户要求准备内容，哪次调用实际发送了内容，以及哪条规则要求确认。它也为后续生成测试提供稳定对象。教程提到内部大规模轨迹分析优势，但没有给出可与公开基准直接比较的准确率，因此这里最有信息量的是可跟踪的工作流，而非泛化的检测性能承诺。

## Eval Author 将行为要求写成判定器

接下来，NeMo Eval Author 为编码代理提供生成 Harbor 或 NeMo Gym 评测的技能与流程。上下文包括 Compass 的发现、原始轨迹、ETHOS.md 和代理仓库。生成的测试需要开发者检查是否真正反映业务要求；测试生成成功，并不自动意味着判定器正确。

示例生成四个类似“起草回复”的 Harbor 任务。判定器关注未经人工确认是否调用发送工具，而不是只检查最终回答是否礼貌、完整。这让问题从主观质量印象变成可观察的行为边界。它还保留了未来扩展的路径：没有生产轨迹时，可先从要求和工具定义生成测试；上线后再把真实失败补进测试集。

修改集中在 Hermes 的 SOUL.md。新规则区分“准备消息”和“发送消息”，并解释准备工具返回的技术令牌并不构成用户同意。这个修复是提示层干预，不能据此推导出不可绕过的权限保证；它是否改善行为，需要看新的执行结果。

## 小样本结果如何解读

| 评测集合 | 修改前通过数／运行数 | 修改后通过数／运行数 | 工具调用数变化 |
| --- | --- | --- | --- |
| 开发集：2 项任务，各运行 3 次 | 3/6 | 6/6 | 10 → 6 |
| 保留集：2 项任务，各运行 3 次 | 4/6 | 6/6 | 28 → 15 |

两项保留任务没有提供给提出修复的编码代理。作者再次分析修复后的轨迹时，Compass 不再报告未经确认发送的问题，却找到了回答缺少检索证据支撑的新问题。这里体现的是迭代诊断的价值：修复一种行为后，继续观察其他行为，而不是把这次全过当作整套系统已可靠。

每个集合只有六次运行，且集中在同一种缺陷，不能据此估计生产故障率，也不能证明对所有发送场景都有效。原文建议实际生产测试覆盖更多行为，并持续隐藏保留集，避免后续修复逐渐把保留集变成开发集。

## 工程案例提供另一种证据

Dassault Systèmes 的 LEO 车门设计案例把同一流程用于工程工具：QueryModel 参数被放在 options 之外，空错误信息又让代理难以恢复。针对调用增加验证后，作者报告畸形工具调用从 142 次降至零，准确性不变，其他场景未观察到回归。约 12 小时的优化循环还报告六个场景上的整体评测分数相对提高 28%、每次运行工具调用减少 35%。这两组数字来自该工程案例，不能与前面的四任务教程混为同一次实验。

值得迁移的是四种产物之间的联系：轨迹给出发生过什么，行为要求定义哪里出错，判定器把要求变成可重复检查，保留任务检验局部修复能否迁移。对 AgentOps 团队，这比笼统追求更高综合分更接近可维护的改进流程。
