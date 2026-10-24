---
id: anthropic-formal-verification
title: 2026年10月23日｜把模糊测试变成证明：Claude 扩大二进制验证的规模
date: '2026-10-23'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- systems-reliability
summary: Anthropic 与 Theorem 将现有模糊测试转成二进制级规格，在 123 个库的 239 个入口上取得证明；理解其进展，需要同时看可信组件、修补约束和证明复用成本。
long_read: true
source_url: https://www.anthropic.com/research/formal-verification
permalink: /tech/zh/anthropic-formal-verification/
organization: Anthropic / Theorem
translation_source: assistant
editorial_status: source-checked
published_at: '2026-10-24T12:04:05.025845+08:00'
updated_at: '2026-10-24T12:04:05.025845+08:00'
---
让智能体生成代码之后，再提交机器可检查的证明，正在从小程序走向真实依赖库。Anthropic 与 Theorem 这次最值得关注的进展，是把已有模糊测试作为规格入口，让 Claude 围绕编译后的程序完成证明。它给系统可靠性带来的变化，是将部分“测试暂未发现问题”提升为有明确假设和范围的安全性质保证。

**原文：** [LLMs are making formal software verification feasible at a much larger scale](https://www.anthropic.com/research/formal-verification)  
**作者：** Keane Lucas、Aengus Lynch、Luna Tong 等；Anthropic Frontier Red Team 与 Theorem 合作。**首发：** 2026-10-22。

## 从测试入口得到可证明的目标

形式化验证的难点从规格开始：解析器尚可参照格式标准，但复杂应用很难一次写出完整的“正确行为”。这项工作利用 OSS-Fuzz 已有入口，把测试失败、断言失败和可检测的内存错误转成崩溃目标，再证明入口在规定输入范围内不会触发这些行为。维护者已经写进测试的领域知识因此可以进入定理。

流程先把库、测试驱动和 AddressSanitizer（ASan）编译成 RISC-V 可执行文件，再结合 Theorem 的指令与 Linux 进程语义生成规格。Claude 构造 Rocq 证明，由 Rocq 内核检查。与运行大量样本相比，证明量化了规定范围内的所有输入；最终保证仍以机器模型、定理陈述和检查器正确为前提。

<a class="note-image-link" href="/assets/images/tech/anthropic-formal-verification/pipeline.png" target="_blank" rel="noopener" aria-label="从测试源码到 Rocq 检查的二进制证明流程 · 查看原图 ↗"><img src="/assets/images/tech/anthropic-formal-verification/pipeline.png" alt="源码编译为 RISC-V 程序，机器语义与目标性质生成规格，Claude 写证明，Rocq 内核检查；蓝框标示可信组件，绿框标示条件成立的证明结果" loading="lazy"><span class="note-image-action">查看原图 ↗</span></a>

*沿箭头看编译、规格生成与证明检查；底部蓝框决定绿色结论成立的前提。图中 MB 是原图标记，技术附录将输入界限明确为小于 64 MiB。*

选择二进制级验证可以直接讨论编译产物，避免另写源码解释器引入一层行为差异；代价是证明也要处理运行时、分配器和测试驱动。作者报告，数周内在修补发现的问题后，为 123 个库的 239 个入口取得证明，通过检查的 Rocq 代码约 1.8 亿行。这说明了完成规模，不能直接当作整个 OSS-Fuzz 的成功率。

## ASan 版本通过，还需要连接普通程序

[技术附录](https://www-cdn.anthropic.com/files/4zrzovbb/website/6867eadf760258fa8b42a504600cd3c036d16358.pdf)进一步解释了保证如何从插桩版本连接到普通版本。作者分别证明两个二进制都不会出现故障、abort 或未建模行为，并证明它们在所有小于 64 MiB 的输入、所有内存布局下，具有相同的读写事件序列、退出行为和最终文件系统状态。

单独证明行为等价还不够：这里的轨迹定义允许一次崩溃与静默无限循环留下同样的有限轨迹，因此普通版本也需要独立的不崩溃证明。由此不能把“不崩溃”进一步理解为普遍的终止保证，更不能推导性能相同。这个细节体现了规格设计的价值：同一个“安全”词语，必须拆成检查器真正检验的命题。

## 证明受阻也能发现测试漏掉的问题

证明过程要处理任意满足前提的输入，因而可能碰到随机变异难以到达的条件。作者举出的例子包括：某解压代码在约 20 MB、具有罕见布局的输入下计数器下溢，造成越界写；另一图像解码器的问题需要 64 MB 输入和超过 2 GB 内存。原文指出模糊测试输入通常限制在 1 MB，这解释了为何测试运行很久仍可能遗漏这些情况。

智能体可以修补程序，再针对新二进制重新生成规格并证明。但修补也改变了被验证对象：把功能删掉可能更容易满足“不崩溃”。团队因此对补丁施加惩罚，鼓励证明补丁改变哪些输入的行为，并记录、审计修改。对编码智能体而言，这提示验收条件需要同时约束安全性质与功能保持，证明检查器本身不会判断改动是否符合产品意图。

保证还可以超出内存错误。例如，若测试把编码再解码的结果检查写成断言，证明断言不可达就能承载相应功能性质；具体覆盖什么，仍取决于入口实际表达的检查。

## 扩大规模的成本在生成，也在复用

附录指出，整个尝试过程产生了约十亿行 Rocq，其中约 1.8 亿行属于成功证明。典型成品约 60 万行，超过一半由智能体编写的工具自动产生；单份证明的检查需要 30 分钟至数小时 CPU 时间。证明行数不能等同于模型直接写出的推理量，也不能替代计算成本。

作者用 36 个缩小任务比较模型：输入上限降到 64 字节，替换大部分运行时，并使用简化的 mini-ASan；程序只有 283–2,491 条指令。每题有三次独立单智能体尝试，每次预算 500 万 token，以首次完成计成功。作者报告，完成一半任务时，Opus 5.5 比 Opus 5 少用约 40% token。这是缩小任务上的生成效率证据，不能直接外推为真实依赖库的成本降幅。

<a class="note-image-link" href="/assets/images/tech/anthropic-formal-verification/token-budget.png" target="_blank" rel="noopener" aria-label="36 个缩小验证任务的 token 预算与完成比例 · 查看原图 ↗"><img src="/assets/images/tech/anthropic-formal-verification/token-budget.png" alt="横轴为每个智能体的 token 预算，纵轴为 36 个任务的完成比例；曲线比较 Opus 5.5、Fable 5.1 与 Opus 5" loading="lazy"><span class="note-image-action">查看原图 ↗</span></a>

*在同一完成比例处比较横向预算；这里衡量生成证明所需的 token，不是程序执行性能，也不是完整库的平均验证费用。*

共享工作区实验还报告节约 17% token。其工程动机很清楚：不同程序都带有启动代码、ASan 等公共部分，复用证明可以减少重复劳动。不过专家评阅指出，现有证明仍大量展开寄存器、地址和分支细节，更复杂程序可能需要函数契约、内存抽象等模块化结构，单纯堆叠长证明未必能继续扩展。

## 最值得追踪的是保证如何接近部署环境

当前主要结果限定在固定内存预算、单线程、静态链接 musl 的 RISC-V Linux 二进制。它不能直接覆盖常见的 x86／ARM、动态链接 glibc 或并发运行；ASan 也不捕获所有内存安全问题，已证明的入口并未覆盖整个库，调用者误用仍可能出错。

这项工作推进了真实代码上机器可检查保证的规模，但落地价值还取决于规格是否抓住需求、补丁是否保留功能，以及机器模型与部署环境的距离。建议优先读原文的流程与局限，再读附录的等价定义和专家评阅；[公开证明库](https://github.com/theorem-labs/oss-verify-proofs)可帮助理解交付物形态。下一步值得关注的，是更准确的部署语义、可组合的证明组件，以及代码更新后维护证明的成本。
