---
date: '2026-11-14'
published: true
layout: article
maintenance: daily-research
translation_source: assistant
authorship: assistant
id: rounding-ml-formulas
lang: zh
title: 2026年11月14日｜浮点公式：实数证明为什么挡不住梯度归零
source_type: tech
long_read: true
source_url: https://www.robertj1.com/ai4science/rounding-bugs-in-ml-formulas/
tags:
- systems-reliability
summary: 用 softmax 的具体反例解释浮点舍入、公式改写与证明边界。
permalink: /tech/zh/rounding-ml-formulas/
published_at: '2026-11-15T15:56:49.257918+08:00'
updated_at: '2026-11-15T15:56:49.257918+08:00'
---
公式在实数上正确，并不保证实现保留一个很小但可表示的梯度。Robert Joseph George 与 Sasha Rush 的文章从 TorchLean 自己的 softmax 问题出发，把执行所用的精度、运算次序和每一步舍入放回验证对象。它对 ML 基础设施的价值是解释为什么数学等价的改写可能显著改变数值行为，以及怎样为修复提供比几次随机测试更强的证据。

原文：[When Rounding Breaks Machine Learning](https://www.robertj1.com/ai4science/rounding-bugs-in-ml-formulas/) · Robert Joseph George、Sasha Rush · 2026-11

## 小数能表示，仍会在中间步骤消失

float32 在 1 上方相邻数之间的距离是 2 的负 23 次方。取可精确表示的小数 q=2 的负 25 次方，实数中的 (1+q)-1 等于 q，但先将 1+q 舍入到 float32，会得到 1，接着减 1 就变成 0。问题不在最终结果超出格式范围，而在与大数相加时被吞掉。

softmax 的例子把这个问题变成训练信号丢失。对 logits [9,-9,-9]，类别 0 为目标，减去最大值后，分母是 1 加两个 exp(-18)。每个小指数约为 1.52×10⁻⁸，加入 1 时被舍去，目标概率就变成恰好 1，损失与目标梯度均为 0。真实损失和梯度的幅值约为 3.046×10⁻⁸，float32 原本能保存。减最大值能防溢出，却没解决这里的消去问题。

## 修复依靠改变中间值，而非只提高输出精度

文章先独立保留非目标项的和 T，再计算：

$$L=\operatorname{log1p}(T),\qquad g_0=\operatorname{expm1}(-L).$$

log1p 专门计算 log(1+T)，避免先把小 T 加到 1 后舍掉；expm1 专门计算 exp(x)-1，避免先将 exp(x) 舍入为 1 再相减。它与原来的 p₀-1 在实数上等价，却保留了重要的小中间量。对该例，作者得到约 -3.046×10⁻⁸ 的非零梯度。

相同思路适用于其他公式。用 E[x²]-E[x]² 计算方差，会对两个接近的大数作减法；JAX 的例子中，[10001,10002,10003,10004] 的方差从真实 1.25 变为 0，文档已经提供 stable 算法选项。tanh 形式的 GELU 在负输入处也可能因为 1+tanh(z) 归零；改写为 x·sigmoid(2z) 保持同一近似函数，却改变舍入路径。这里必须区分已有文档说明的取舍与新缺陷，不能把所有数值差异都统称未报告 bug。

## FloatLib 证明什么，测量又证明什么

FloatLib 在 Lean 中显式建模格式与浮点运算；roundoff tactic 组合运算的舍入定理，构造带前提的前向误差界：

$$|\widehat y-y|\le r|y|+a.$$

相对项跟随结果大小，绝对项容纳下溢等效应。有限性、范围等前提仍要成立，最终证明由 Lean 内核检查。对实数公式的证明、对具体浮点程序的误差证明、跨库实测，三者的对象与覆盖范围不同。

当前原文列出 154 个 TorchLean 算子、含变体时 162 个条目，159 个有可执行 Lean 规则；跨库主比较约有 7.8 亿个输出。脚注进一步说明，137 个算子至少有一种计算生成了前向误差界，96 项计算未得到界。因此不能沿用输入摘要“152 个算子均有证书”的表述。CPU 与 GPU 结果也分开，因为输出标为 float32 不表示中间乘法一定采用同样精度，例如部分被测路径默认使用 TF32。

## 局部修复不能替代完整训练验证

作者用小型 transformer block 跟踪误差传播：修复损失公式之后，前面层中已有的舍入误差不会消失。部分极低精度格式中的真实结果本来就应舍为零，此时不能靠代数重排强行保留。某些超越函数近似也没有对应准确性定理，模型化算术与真实硬件仍需对齐。

这组工作提供了局部反例、修复公式和带条件证明，但不估计这些输入在实际训练中有多常见，也未证明整次训练质量会提高。原文主要使用交互式数值可视化，没有可直接采用的独立静态架构图；这里保留公式与反例，让“哪一步丢掉信息”成为阅读重点。
