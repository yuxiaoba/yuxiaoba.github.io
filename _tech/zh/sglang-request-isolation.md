---
date: '2026-10-28'
published: true
layout: article
maintenance: daily-research
authoring_source: assistant
translation_source: assistant
id: sglang-request-isolation
title: 2026年10月28日｜SGLang：请求结束后，KV 页面何时才真正可复用？
lang: zh
source_type: tech
long_read: true
source_url: https://www.lmsys.org/blog/2026-10-26-cf-security
tags:
- inference-serving
- systems-reliability
summary: 从异步 RDMA 写入解释延迟释放、排空确认与超时边界，并区分它们和准入拒绝修复。
permalink: /tech/zh/sglang-request-isolation/
published_at: '2026-10-28T15:24:19.938525+08:00'
updated_at: '2026-10-28T15:24:19.938525+08:00'
---
SGLang 这份报告最值得关注的，是一个容易被本地分配器隐藏的状态：请求已经结束，远端却仍在写它的 KV 页面。只把请求标为 aborted，无法撤销已经提交给传输引擎或网卡的操作。对分离 prefill/decode 的推理服务，页面的寿命必须长于所有可能触碰它的异步工作。

原文：[SGLang security update: improving request isolation](https://www.lmsys.org/blog/2026-10-26-cf-security) · LMSYS / SGLang · 2026-10-26。

### 两条失败路径要分开理解

与 Cloudflare 事故直接相关的路径是准入拒绝：超出 prefill KV 容量的请求被标为拒绝，却仍进入交接，decode 读到了未由当前请求填充的页面。修复需要让拒绝真正阻止交接。

报告进一步分析另一族竞态：A 在传输中途终止，decode 立即释放它的页面；分配器将页面交给 B；A 的在途写入随后到达，覆盖 B 的缓存。它不依赖同一个超长请求占位符缺陷，而依赖“释放、重用、迟到写入”的时间关系。长上下文增加在途数据和传输时长，内存压力又加快页面重用，二者会放大风险。

### 取消负责停止新工作，排空负责证明旧工作结束

路由器应将 prefill 和 decode 当作一对取消，避免一边结束、另一边继续。但配对取消仍不能召回网卡队列里的写入。引擎必须保留页面，并等待每个相关 prefill rank 证明它已提交的工作完成。

<a class="note-image-link" href="/assets/images/tech/sglang-request-isolation/deferred-release.png" target="_blank" rel="noopener" aria-label="请求终止后保留 KV 槽，直到所有 prefill rank 排空 · 查看原图 ↗"><img src="/assets/images/tech/sglang-request-isolation/deferred-release.png" alt="请求终止后保留 KV 槽，直到所有 prefill rank 排空" loading="lazy"><span class="note-image-action">查看原图 ↗</span></a>

*上方是 decode 的持有区间，下方是在途写入的排空；所有必要确认汇合后才能进入正常释放路径。超时释放仍依赖写入已停止的边界条件。*

延迟释放的流程是：decode 发出 ABORT；prefill 将请求标为失败、丢弃尚未发送的块，并追踪已启动工作；只有排空后才发送 ABORT_ACK；decode 收齐所需确认后才归还缓存槽、请求池行和元数据。后续消息增加代际标识，避免重用请求编号时错误消费旧确认。

失败的传输调用不能当作排空。Mooncake 的一次调用超时，底层写入仍可能继续重试；报告中的修复因此不再对失败发送发出“已排空”确认。这里的正确性来自写者生命周期，而非上层异常是否已处理。

### 超时是有条件的后备路径

如果确认丢失，系统会等待配置的超时。作者明确指出：时间到了本身不能证明远端停止写入。安全释放依赖保留时间覆盖取消传播、剩余分块和在途调用的尾部；有界传输批次用于约束这段尾部。异常路径越频繁、保留越久，占用的 KV 容量也越大。

可选的 PD checksum 在接收提交时检查 KV 完整性，能捕获该检查点之前的一部分污染。它会增加 GPU 读取和同步开销，也不能代替之后的内存生命周期保护，更不是每步 decode 都重新证明页面归属。

### 证据与运维含义

作者把复现分成两层：单个 P/D 对上的受控窗口用于证明页面重叠，错误输出通过模拟迟到写入展示；两个 prefill 共享 decode 的真实 RDMA 实验才验证实际迟到写入。修复后记录到 hold、drain-ack、release，输出恢复为基线内容。

性能报告在 2×H100、1P1D Mooncake、1,024 请求、并发 256 的 21 次运行中，三组每组七次，吞吐差异均在 ±2% 内，置信区间跨零。这说明所测正常路径未见明显吞吐损失，不代表取消风暴和显存紧张时没有成本。

对运维最有用的新信号，是释放究竟由 drained 还是 timeout 触发。超时占比高意味着确认路径或传输尾部值得调查。部署检查也应覆盖路由器配对取消、两侧版本兼容与后端能力。报告涉及多次补丁和不同后端，具体升级应按官方补丁表核对；一个笼统的“打开延迟释放”不能覆盖全部失败路径。
