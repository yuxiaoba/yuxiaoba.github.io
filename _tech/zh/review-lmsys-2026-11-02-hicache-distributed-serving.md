---
id: review-lmsys-2026-11-02-hicache-distributed-serving
title: 2026-11-03｜HiCache：并行缓存复用的正确性条件
date: '2026-11-03'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://lmsys.org/blog/2026-11-02-hicache-distributed-serving
tags:
- agent-reliability
- observability
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-lmsys-2026-11-02-hicache-distributed-serving/
---

HiCache 文章把并行缓存正确性拆为多个不变量：CP 保持页归属，PP 各阶段对命中前缀达成一致，投机解码恢复 drafter 状态，P/D 只传缺失后缀。缓存命中必须同时与执行拓扑兼容。

跨拓扑复用需要布局兼容；生产命中率与 TTFT 是团队报告，不是所有并行组合的独立测试。

来源：[HiCache Across Multi-Parallelism and Distributed Serving](https://lmsys.org/blog/2026-11-02-hicache-distributed-serving)

[HiCache Across Multi-Parallelism and Distributed Serving](https://lmsys.org/blog/2026-11-02-hicache-distributed-serving)
