---
id: review-github-open-flapping-airplanes
title: 2026-11-04｜开放 megakernel 复现：同时运行与强基线
date: '2026-11-04'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://github.com/Bobliuuu/open-flapping-airplanes
tags:
- agent-reliability
- self-improvement
- observability
- inference-serving
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/zh/review-github-open-flapping-airplanes/
---

open-flapping-airplanes 从演示视频独立重建持续 GPU kernel，让训练、serving 与 Doom 共用设备。B200 上 162.4M 模型训练为 48.1 秒，快于 eager 对照，却慢于 CUDA Graph Megatron 的 43.1 秒。

不是原项目代码复现或大模型生产验证；各 workload 分配固定 SM，不能把并行演示当作免费共享资源。

来源：[open-flapping-airplanes: reproducing the flapping airplanes megakernel](https://github.com/Bobliuuu/open-flapping-airplanes)

[open-flapping-airplanes: reproducing the flapping airplanes megakernel](https://github.com/Bobliuuu/open-flapping-airplanes)
