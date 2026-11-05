---
id: review-lmsys-miles-mi355x-agentic-rl-swe-agents
title: 2026-10-29｜Miles：agent RL 的长尾、沙箱与资源上限
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://lmsys.org/blog/2026-10-22-miles-mi355x-agentic-rl
tags:
- agent-reliability
- coding-agents
- observability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-lmsys-miles-mi355x-agentic-rl-swe-agents/
---

Miles 的 MI355X 实践发现长尾轨迹、沙箱启动和固定并发上限比 GPU 更早限制 agent RL。文章区分单节点长度限制带来的约三倍步速与扩容加修复带来的约四倍 rollout 吞吐，并指出基础设施失败会被错误计为零奖励。

四倍吞吐同时增加推理节点，非同资源比较；准确率仅 100 个分层抽样任务，不能写成完整 SWE-bench。

来源：[Training SWE agents with Miles on MI355X: taming long-tail trajectories and complex sandbox coordination](https://lmsys.org/blog/2026-10-22-miles-mi355x-agentic-rl)

[Training SWE agents with Miles on MI355X: taming long-tail trajectories and complex sandbox coordination](https://lmsys.org/blog/2026-10-22-miles-mi355x-agentic-rl)
