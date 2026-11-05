---
id: review-pytorch-2-15-release-blog
title: 2026-10-29｜PyTorch 2.15：分布式默认行为与故障诊断
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://pytorch.org/blog/pytorch-2-15-release-blog/
tags:
- agent-reliability
- coding-agents
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-pytorch-2-15-release-blog/
---

PyTorch 2.15 将重写的 NCCL 后端设为默认，并增加 hang 时的 flight recorder 与跨 rank 转储；提供旧后端回退路径。NIXL 单边传输及 FSDP2 精度、内存控制也改变分布式执行配置，升级应关注默认行为与故障诊断。

多项 API 标为 unstable；这里只核对官方发布说明，未运行升级、性能或故障恢复测试。

来源：[PyTorch 2.15 Release Blog](https://pytorch.org/blog/pytorch-2-15-release-blog/)

[PyTorch 2.15 Release Blog](https://pytorch.org/blog/pytorch-2-15-release-blog/)
