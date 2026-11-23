---
id: together-prompt-samples
title: 2026年11月23日｜Together 复盘：一次代码提交如何暴露提示词样本
date: '2026-11-23'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- coding-agents
summary: 测试样本保存在私有库中，但仓库凭证进入了公开提交。扫描发现凭证时，下载已经发生。
long_read: true
source_url: https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026
permalink: /tech/zh/together-prompt-samples/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
Together AI 的复盘从推理结束后留下的一份副本开始。一批获准用于软件测试的提示词样本存放在私有 Hugging Face 仓库中。后来发生的下载，把生产推理、离线测试和编码智能体这三项往往分开管理的工作连在了一起。

## 从推理请求到测试样本

公司将事件范围限定在 2026 年 6 月和 7 月的部分 serverless 请求，涉及 MiniMax M3、GLM-5.2 和 Kimi K2.6，样本主要来自 6 月 24 日、7 月 4 日、8 日和 14 日。请求结束后，用于测试的副本仍可通过仓库凭证读取。对客户而言，核对模型和日期能缩小排查范围，但不能单凭命中日期认定某次请求已被取样。

## 扫描发现了提交，下载已在暴露窗口内发生

据 Together 说明，编码智能体在开发公开代码库时提交了一项能访问私有样本库的凭证。自动扫描发现了它，团队随后回退提交。未经授权的一方已在此期间取得凭证并下载样本。对方后来测试了样本中包含的其他服务凭证，其中五个属于 Dragos 的金丝雀实验。这个数字说明已经有人使用下载内容中的信息，不能用来估算有多少客户受影响。

## 三处改动分别作用在哪里

Together 将所有拉取请求纳入凭证检查，并更新了编码智能体的开发流程。限制凭证作用域、缩短有效期以及在适用场景采用无密钥访问，针对的是暴露后还能访问多少资源。新账户默认开启 ZDR 则更靠前，改变提示词能否留作样本。公告发布时，公司正与外部取证机构及执法部门合作，仍在检查样本内有哪些客户数据；其调查当时没有发现这起事件之外的其他提示词泄漏证据。

Vipul Ved Prakash · 2026-11-21 · [Security event: Prompt leakage for requests in June and July of 2026](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026)
