---
id: novita-forwarding-scope
title: 2026年11月23日｜Novita 的客户专用转发规则为何影响了更多请求
date: '2026-11-23'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Novita 确认一条例外路由扩大了适用范围。测试链接被访问，访问目的和上游是否留存仍待核实。
long_read: true
source_url: https://novita.ai/blog/minimax-requests-privacy-notice/
permalink: /tech/zh/novita-forwarding-scope/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
选择 Novita 托管的模型，实际计算却可能发生在 MiniMax 官方 API。Novita 对部分请求确认了这一偏差。事故的关键在于谁被纳入一条本应只对特定客户生效的转发规则，这一判断直接影响谁能看到提示词。

## 配置作用域决定数据经过谁

Novita 将原因归于路由配置：原为特定客户设置的 API 转发路径被更广泛地应用。部分请求因此离开 Novita 自有推理基础设施。公告将可能受影响的范围定为 2026 年 5 月 28 日至 11 月 11 日期间经 Novita 使用 MiniMax 模型的请求，既包括直连客户，也包括经 OpenRouter 接入的客户。日期和入口可用于筛查，但公告没有披露具体转发比例。

## 链接访问和凭证使用给出不同证据

研究者看到了测试请求中嵌入的 URL 和主机名被访问，没有观察到 AWS 测试密钥标记被使用。前者说明请求中的信息引发了可观测的外部访问，后者限定了观察到的行为种类。Novita 据访问模式推测可能存在自动内容审查，仍在向 MiniMax 核实；仅靠这些信号无法确定访问目的、数据保留了多久，或是否有人阅读了完整提示词。

## 暂停端点后仍需查清的数据去向

Novita 表示已暂停受影响模型，正在核验处理路径，并与 MiniMax 跟进是否有数据被保留及其删除情况。公司称自己不留存客户提示词和输出，也不将其用于训练。对被转发的请求，上游的留存与删除情况仍需单独确认。它计划改进 Partner API 标识，以及相关供应商的留存条款与服务条款披露，使客户能在选择端点时看见这一差别。

Novita AI · 2026-11-22 · [Privacy Notice Regarding MiniMax Requests on Novita](https://novita.ai/blog/minimax-requests-privacy-notice/)
