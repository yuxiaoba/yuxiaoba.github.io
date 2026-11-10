---
date: '2026-11-10'
published: true
layout: article
maintenance: daily-research
translation_source: assistant-authored paired Chinese/English research notes
authoring_source: assistant
editorial_status: source-checked
id: claude-fable-mythos-52
title: 2026年11月10日｜Claude Fable / Mythos 5.2：能力、推理成本与访问边界怎样一起变化
lang: zh
source_type: tech
source_url: https://www.anthropic.com/news/claude-fable-and-mythos-5-2
long_read: true
tags:
- coding-agents
- agent-reliability
summary: 官方发布中的速度与费用运行点、千 Agent 单次形式化案例，以及防护回退对 Agent 评测的影响。
permalink: /tech/zh/claude-fable-mythos-52/
published_at: '2026-11-10T09:37:04.860576+08:00'
updated_at: '2026-11-10T09:37:04.860576+08:00'
---
[Introducing Claude Fable 5.2 and Claude Mythos 5.2](https://www.anthropic.com/news/claude-fable-and-mythos-5-2) · Anthropic · 2026-11-09

Anthropic 的更新把开放式技术任务能力、生成速度和访问策略放在同一份发布说明中。Fable 5.2 与 Mythos 5.2 使用同一底座，但前者带更强的网络安全与生物学防护、面向广泛用户，后者通过相应 Verification Programs 开放。对 AgentOps 而言，这意味着模型名称之外，还需关心实际返回路径、推理档位和评测设置。

## 速度与能力应按同一运行点比较

官方称相对 5.1 生成速度最高增加 30%，标准输入/输出价格为每百万 token $8/$40；可选 fast mode 最高加速 2.5×，价格 $16/$80。这些是生成速度与 token 单价，不直接等于完整任务完成得更快或成本更低。工具等待、重复执行和输出量仍影响最终费用。

FrontierCode 2.0 的官方结果为 Fable 5.2 在 Xhigh effort 下 49.1%，5.1 为 32.4%，Opus 5.5 为 45.5%。同文还给出 Fable 5.2 High effort 的 45.3%，约以一半单任务费用接近 Opus 最高档位的成绩。比较中 effort 与实际任务成本是必要条件，不能只取最佳分数再配最低价格。

## 长时案例说明可行性，不代表稳定成功率

Fermat’s Last Theorem 形式化案例用了约一千个 Agent，30 小时完成，比较对象 Opus 5.5 采用相同千 Agent 配置。图注明确每模型一次运行，任务以中间定理陈述的加权完成比例记进度；不是一个 Agent 在普通会话中独立发现并证明新定理。

其他案例包括 Python→Rust 的生产服务迁移与三台电子设备设计。它们提供值得继续检查的工程线索，但宣传页并未给出足以估计跨项目可靠性的样本和对照，不能推广为任意迁移都能无人值守完成。对本网站关注的系统优化尤其要注意：官方称其训练中限制了部分直接加速 AI 研发的能力提升，accelerator kernel optimization 约处于 Opus 5.5 水平，通用编码分数上升不能替代 kernel 优化评测。

## 实际执行路径包含防护与回退

Fable 的特定网络安全或生物任务可能被防护分类器阻断并转给其他模型；官方也列出少数 AI 研发话题的透明回退。因此，同名产品的实际处理链可能不同，评估事故调查或安全工具时应记录所用端点、effort 和是否触发回退，而不是把所有响应都归于同一底座行为。

发布说明给出 Mythos 在约 1,900 个自动行为审计场景上的综合结果，并承认模型更频繁识别自己正被评估，会妨碍对真实部署行为的判断。这些是厂商预发布测量，不是生产故障率。本文保留与运行配置和证据解释直接相关的信息；原页主要用交互图表呈现结果，没有下载到适合复用的独立架构原图。

值得跟踪的是长任务能力提高能否在固定 harness、工具权限、时间与费用下持续兑现。官方自己仍建议多数日常编码和知识任务先使用 Opus 5.5；这是一条厂商定位，而非本篇对所有用户工作负载的实测推荐。
