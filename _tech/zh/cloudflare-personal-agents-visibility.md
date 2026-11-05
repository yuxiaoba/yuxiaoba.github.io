---
id: cloudflare-personal-agents-visibility
title: 2026年11月5日｜个人代理流量：识别代理身份，还不能推断用户授权
date: '2026-11-05'
lang: zh
published: false
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- observability
summary: Cloudflare 将个人代理接入流量分析与访问策略，同时明确用户上下文仍是下一步。
long_read: true
source_url: https://blog.cloudflare.com/personal-agents-visibility-control/
permalink: /tech/zh/cloudflare-personal-agents-visibility/
translation_source: assistant
authoring_source: assistant
published_at: '2026-11-05T08:55:14.344660+08:00'
updated_at: '2026-11-05T08:55:14.344660+08:00'
---

原文: [See the agents, set the terms: new visibility and control for personal agents](https://blog.cloudflare.com/personal-agents-visibility-control/)<br>
Marina Elmore, Nicole Justus · Cloudflare · 2026-11-04

Cloudflare 把 Personal Assistants 加入 Security Analytics 的 Bot Analysis 分类，并提供按代理名称筛选的请求量、路径、状态码和网络信息。对站点来说，这让“有自动化访问”细化为“哪个代理访问了哪些业务路径、在哪里遇到错误”，可用于观察代理访问兼容性。

已接入早期开放的 Account Abuse Protection 的站点，还可在登录、注册及账户视图中关联代理活动。文章举例说明，可针对被滥用账户的 Hashed User ID 设置 WAF 规则，而不是阻断该代理的全部用户。访问设置也允许对支持的个人代理分别选择不阻断、只在有广告页面阻断或全部阻断。

其边界同样具体：识别了代理，不表示站点知道用户究竟授权了什么、是否订阅或拥有哪些权益。原文将携带用户上下文、声誉与责任归属列为后续方向。因此，这是面向 AgentOps 的观测与策略接口更新，不是完整的代理授权协议，也没有提供识别准确率的对照测量。值得关注的是站点开始把个人代理当成独立可观测的访问主体，同时仍需保留账户与用户意图的判断。
