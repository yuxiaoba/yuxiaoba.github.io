---
id: meta-jittesting
title: 2026年10月30日｜Meta 用两条测试生成路径捕获代码变更风险
date: '2026-10-30'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
- coding-agents
summary: Meta 将 Catching JiTTests 部署到生产流程：对高风险代码变更生成可执行测试，再筛掉不值得打扰工程师的失败。它提供的是可观察的行为差异，是否构成缺陷仍需结合变更意图判断。
long_read: true
source_url: https://engineering.fb.com/2026/10/29/security/catching-bugs-before-they-land-jittestings-human-on-the-loop-approach-at-full-scale/
permalink: /tech/zh/meta-jittesting/
translation_source: assistant-authored paired Chinese/English reading notes
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-10-30T10:31:20.339125+08:00'
---
Meta 将 Catching JiTTests 部署到生产流程：对高风险代码变更生成可执行测试，再筛掉不值得打扰工程师的失败。它提供的是可观察的行为差异，是否构成缺陷仍需结合变更意图判断。

**来源：** Sreeja Thummala、Sophie Zeng、Mark Harman、Weini Liu、Eric Liu，[Catching Bugs Before They Land: JiTTesting’s Human-on-the-Loop Approach at Full Scale](https://engineering.fb.com/2026/10/29/security/catching-bugs-before-they-land-jittestings-human-on-the-loop-approach-at-full-scale/)，2026 年 10 月 29 日。

## 从行为差异到候选缺陷

系统利用夜间空闲算力，优先处理前一天按历史变更风险模型选出的 diff。两条路径并行：dodgy diff 直接把变更当作变异体，生成能够区分新旧行为的测试；intent-aware 路径先根据代码、标题和摘要推断意图与风险，构造代表潜在错误的变异体，再生成区分变异体的测试并运行于真实 diff。测试在实际变更上失败后，成为待筛查的 weak catch，而不是自动认定的缺陷。

<a class="note-image-link" href="/assets/images/tech/meta-jittesting/workflows.png" target="_blank" rel="noopener" aria-label="查看 JiTTests 双路径流程原图"><img src="/assets/images/tech/meta-jittesting/workflows.png" alt="JiTTests 通过直接变异和意图推断两条路径生成测试，再筛选行为差异" loading="lazy"><span class="note-image-action">查看原图 ↗</span></a>

两条路径生成变异体和测试，只有通过旧版本并在变异体及目标变更上失败的测试才进入候选集合。

## 筛选与人的角色

多个 LLM 组成的评审集成会查看测试代码、执行结果、diff 和推断意图；规则系统 RubFake 补充可验证的确定性判断。两者共同排序，达到阈值才联系工程师。人的角色转向设定标准、审查整体效果及确认实际行为是否符合意图，减少逐条审阅负担。模型评审本身并非确定性的，因此规则和人工反馈仍有意义。

Meta 报告，589 名工程师参与反馈，占联系对象的 64%；报告的真阳性率为 60%。2026 年上半年，该系统帮助在代码变更阶段捕获 74 个严重隐私缺陷，公司报告同期隐私 SEV 总发生量下降 20%。这些是内部运营数据，文章没有提供足以单独估计因果效果的对照设计；不同代码库、风险筛选与审核策略也可能改变实际效果。
