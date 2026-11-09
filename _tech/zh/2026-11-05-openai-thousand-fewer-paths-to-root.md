---
id: 2026-11-05-openai-thousand-fewer-paths-to-root
title: 2026年11月5日｜技术阅读：A thousand fewer paths to root
date: '2026-11-05'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://openai.com/index/a-thousand-fewer-paths-to-root
source_published_at: '2026-11-05T00:00:00+08:00'
tags:
- systems-reliability
authoring_source: assistant
translation_source: assistant
permalink: /tech/zh/2026-11-05-openai-thousand-fewer-paths-to-root/
long_read: true
summary: 区分候选、动态复现、提权验证与补丁审查，理解自动化内核漏洞研究的证据链。
---

自动扫描能快速产生大量候选，真正限制修复速度的却是判断哪些问题可复现、会跨越什么权限边界，以及补丁是否适合合入。OpenAI 的 [Linux 内核研究报告](https://openai.com/index/a-thousand-fewer-paths-to-root/)把这几步分开记录。

## 从代码发现到动态证据

流水线先选择安全相关的内核路径，再由审查智能体产生候选。动态验证在隔离环境中尝试复现并保存运行时证据；之后单独评估信息泄露或本地提权等后果。这意味着，发现可疑代码、触发崩溃、证明安全影响，是三种不同的证据。

对维护者而言，值得复用的是这种分阶段交接：静态解释可以指导测试，但不应替代可重复的触发条件。复现失败也不证明代码安全，可能只是目标环境或触发条件不匹配。

## 2308、1724 和 948 分别是什么

报告的这次运行得到 2,308 个候选、1,724 个动态复现的问题，以及 948 个本地提权验证结果。三者的分母和通过条件不同；948 不是已被维护者接受或合入的修复数。作者还报告了约 121 万美元的 API 开销，这是该模型、环境和工作流的一次运行成本，不是所有内核扫描的单位价格，也不是实际赏金收入。

如果将流水线迁移到其他项目，我会先看候选去重、复现率和专家复核成本，再考虑扩大扫描范围。只看发现数量会把后段验证和人工审查的积压隐藏起来。

## 补丁是交付给维护者的候选

系统为问题整理根因、最小触发证据和候选补丁，安全研究人员审查后再向维护者报告。可用的交付包能缩短追问，但最终是否正确、是否破坏兼容性、是否值得合入，仍是独立的工程判断。

这篇报告最值得关注的是把“发现漏洞”变成一条带有逐步证据的修复流程。适用性仍受目标版本、威胁模型、隔离环境和维护团队审查能力约束；一轮内核实验不能直接推出其他项目的发现率或修复速度。
