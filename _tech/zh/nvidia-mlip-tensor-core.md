---
id: nvidia-mlip-tensor-core
title: 2026年10月30日｜用 Tensor Core 加速原子势计算，同时检查物理稳定性
date: '2026-10-30'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
summary: NVIDIA 用多项低精度乘积逼近 FP32，并在轨迹和结构优化中检查误差。
long_read: true
source_url: https://developer.nvidia.com/blog/unlocking-tensor-core-performance-for-machine-learning-interatomic-potentials/
permalink: /tech/zh/nvidia-mlip-tensor-core/
translation_source: assistant-authored paired Chinese/English reading notes
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-10-30T10:31:20.339125+08:00'
---
NVIDIA 针对 Point Edge Transformer 原子间势模型探索 Tensor Core 加速，重点不仅是矩阵乘法速度，还包括力误差、能量守恒和结构优化是否仍可信。

**来源：** Anoushka Bhutani、Atul Thakur、Erica Tsai、Kristopher Keipert、Michele Ceriotti，[Unlocking Tensor Core Performance for Machine Learning Interatomic Potentials](https://developer.nvidia.com/blog/unlocking-tensor-core-performance-for-machine-learning-interatomic-potentials/)，2026 年 10 月 29 日。

BF16x9 将每个 FP32 操作数拆成三个带缩放的 BF16 分量，计算九个乘积并以 FP32 累加。TF32x3 则把操作数分为主分量和残差，计算主项及两个交叉项，省去残差相乘。前者在 Blackwell 上的 17,280 原子任务中使大型 GEMM 快 2.2–2.5 倍；后者在 A100 上使主要 GEMM 快 1.7–1.9 倍，较大系统的完整分子动力学步快 1.5 倍。小系统的收益较小，因为非 GEMM 工作和启动开销占比更高。

单点误差不足以衡量长期数值行为。作者在 192 原子水盒的 30 ps NVE 轨迹中观察到 TF32x3 与 FP32 的能量波动相近，而单次 TF32 有更明显漂移。在 539 原子合金结构优化中，TF32x3 的三次实验用 218–222 步达到力阈值；单次 TF32 在 1000 步后仍未达到。结论限于所测模型与任务，但展示了可迁移的性能评估原则：同时检查端到端收益和应用需要的数值不变量。
