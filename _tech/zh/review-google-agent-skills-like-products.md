---
id: review-google-agent-skills-like-products
title: 2026-10-29｜Google Agent Skills：把指令更新作为行为发布
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://cloud.google.com/blog/topics/developers-practitioners/behind-the-scenes-two-months-later-how-we-ship-google-agent-skills-like-products
tags:
- agent-reliability
- coding-agents
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-google-agent-skills-like-products/
long_read: true
summary: "Google 如何将 skill 的版本、原子评测、脚本边界和最新提交证据纳入发布检查。"
---

## 指令修改为何需要行为回归

Google 的工程文章把 skill 视为会改变工具选择与执行路径的软件产物。一句措辞可能让 agent 使用错误参数或反复执行，因此 Markdown 格式通过不代表行为正确。团队要求行为变化显式提升版本，修改既有 skill 时与旧版比较，新 skill 则与不使用 skill 的 agent 比较。

CI 先执行目录、frontmatter、命名和版本等确定性检查，再运行昂贵评测与 AI 审阅。评测报告必须对应最新提交，避免修改后仍引用旧结果。版本字段必须是字符串，升级主版本或次版本时重置后续位数；这些规则服务于安装、锁定和比较，不意味着 agent 每次调用都联网自动更新。

## 单一判据与可执行步骤各归其位

文章用创建存储桶举例：地区、统一访问控制和生命周期规则若写成一个期望，漏掉其中一项时裁判评分容易不一致。拆成三个独立判据后，失败可定位到具体行为。检查还覆盖文件型测试提示是否存在且非空、重复提示、冲突期望以及报告是否过期。

另一个边界是确定性命令应放入脚本，判断任务留给指令。严格命令链、JSON 解析和部署步骤如果只写进提示，模型每次重新拼接就可能引入偏差。脚本需要非交互参数、结构化输出和可用错误信息；核心说明保持简短，详细参考通过单跳链接加载，避免 agent 在深层引用途中停止。

## 哪些流程经验可以借鉴

团队曾因路径匹配过宽挡住拼写修复，又漏掉深目录的新 skill，因此质量门槛本身也需要按文件操作和路径深度验证。索引由生成器维护，避免人工表格几天内漂移；AI 审阅检查设计问题，最终仍由领域专家批准。

我的理解是，真正可借鉴的是把“合法文件”“评测证据仍适用”和“行为值得发布”拆成不同检查。版本提升和三个标题一样，只是必要记录，不自动证明质量；本文没有证明所有 skill 都改善任务表现，也没有把 star 数作为质量证据。

来源：[原始工程文章](https://cloud.google.com/blog/topics/developers-practitioners/behind-the-scenes-two-months-later-how-we-ship-google-agent-skills-like-products)
