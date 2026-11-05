---
id: review-microsoft-copilot-harness-foundry
title: 2026-10-29｜Foundry 长任务恢复：检查点与幂等边界
date: '2026-10-29'
lang: zh
published: false
layout: article
maintenance: daily-research
source_type: tech
source_url: https://devblogs.microsoft.com/foundry/microsoft-copilot-harness-in-foundry/
tags:
- agent-reliability
- coding-agents
- observability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-microsoft-copilot-harness-foundry/
---


Foundry 区分托管 Copilot harness 预览与 hosted agent 长任务恢复：平台检测中断并以原始输入重启，应用负责保存检查点和中间结果，并避免重复外部操作。仅有对话历史不足以恢复进行中的工作。

这是官方能力和责任边界说明，没有给出可靠性或恢复延迟基准；恢复不保证外部操作 exactly-once。

来源：[Introducing the Microsoft Copilot harness in Foundry Agent Service](https://devblogs.microsoft.com/foundry/microsoft-copilot-harness-in-foundry/)

[Introducing the Microsoft Copilot harness in Foundry Agent Service](https://devblogs.microsoft.com/foundry/microsoft-copilot-harness-in-foundry/)
