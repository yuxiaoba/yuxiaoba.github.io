---
id: phala-inference-exposure
title: 2026年11月23日｜Phala 为何把两天的金丝雀证据扩展为更长的通知窗口
date: '2026-11-23'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: 新 GPU 服务器已承接生产流量，安全加固却未完成。初步报告区分了请求发送、凭证被使用和隔离完成的时间。
long_read: true
source_url: https://phala.com/posts/phala-november-preliminary-incident-report
permalink: /tech/zh/phala-inference-exposure/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
Phala 在 11 月 10 日的初步报告中请用户检查一条具体路由：经 OpenRouter 发给 Phala 的 DeepSeek V4 Flash 0731。建议按暴露处理的请求从 10 月 21 日 00:00 UTC 延续到 11 月 8 日 05:35 UTC。已确认的金丝雀证据只对应其中两天。理解这个差距，要把请求发生的时间与后来发现数据被使用的时间分开。

## 生产流量先于加固就绪

Phala 称，一台尚未完成生产安全加固的新 GPU 服务器已经承接推理流量。推理虚拟机失陷后，处理中的请求内容对未经授权的一方可见；即使客户关注的是留存时长，运行当下的数据也有独立的暴露面。另有机密虚拟机（CVM）受到影响，已确认一个租户的部分应用凭证后来被滥用。Phala 根据活动和基础设施的重叠，初步将两起入侵归为同一事件。

## 为什么 11 月 6 日轮换根密钥仍不足以结案

团队在 11 月 5 日发现异常并处置未经授权的虚拟机，次日完成密钥管理系统根密钥轮换。直到 11 月 8 日 04:12 UTC，研究者提交的证据才把排查指向具体推理部署。团队随即将相关服务器和部署下线，05:35 完成隔离。两次处置针对不同资产。轮换根密钥也无法收回此前已经出现在请求内容里的第三方秘密。

## 两天的阳性样本怎样用于通知

研究者从 7 月 1 日到 11 月 7 日持续抽样，只有 10 月 21 日和 22 日发出请求中的金丝雀凭证随后出现滥用。检测依赖有人使用标记，无法看见只读取内容的行为，也覆盖不了未抽样请求。Phala 因此保留了更宽的预防窗口。报告还记录了 11 月 9 日对已取得数据的滥用；它可与公司所报的隔离后未观察到新的成功未授权访问同时成立。完整根因分析和修复验证在公告发布时仍在进行。

Phala · 2026-11-10 · [Phala November Preliminary Incident Report](https://phala.com/posts/phala-november-preliminary-incident-report)
