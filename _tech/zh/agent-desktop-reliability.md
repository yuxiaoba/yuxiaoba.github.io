---
id: agent-desktop-reliability
title: 2026年11月2日｜agent-desktop：让桌面动作携带身份与重试证据
date: '2026-11-02'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- observability
- systems-reliability
summary: 通过无障碍树、快照引用、送达状态与后置验证，理解桌面 Agent 工具如何处理状态变化和重复动作。
translation_source: assistant-authored Chinese and English paired content
long_read: true
source_url: https://github.com/vercel-labs/agent-desktop
permalink: /tech/zh/agent-desktop-reliability/
published_at: '2026-11-02T08:39:51.033336+08:00'
updated_at: '2026-11-02T08:39:51.033336+08:00'
---

桌面 Agent 最危险的失败，有时不是点不到按钮，而是窗口已经变了，却仍对旧目标执行；或者输入其实已经送达，超时重试又执行了一遍。Vercel Labs 的 agent-desktop 将这些问题放进工具接口：通过操作系统无障碍树观察控件，再用带身份信息的引用操作，并把动作送达、结果验证和重试安全性分别返回。

原始项目：[agent-desktop](https://github.com/vercel-labs/agent-desktop) · Vercel Labs；Chris Tate 于 [2026-10-31 发布介绍](https://x.com/ctatedev/status/2116323148706771302)。以下机制依据项目 2026-11-01 的文档快照，JSON 输出契约为 2.5。

## 无障碍树提供了什么

项目提供 Rust 实现的 CLI 和 C 库，覆盖 macOS、Windows 与 Linux。它读取应用暴露给操作系统的结构：窗口、控件角色、可访问名称、状态及可用动作，再返回 JSON 快照。Agent 选一个引用执行动作，随后重新观察；规划循环仍由上层 Agent 控制。

这条路径可以减少从像素推断按钮位置的需要，但它依赖应用实际暴露的无障碍信息。没有语义动作、读操作不完整或平台不支持的能力，都要作为接口边界处理。项目同时支持截图与显式物理输入，因此不应理解成所有软件都能完全摆脱坐标操作。

文档区分“已知没有”“已知有”和“未知”证据。读取失败不能被当成属性不存在，否则不完整快照可能被误判为完整，未知的控件能力也可能被错误授予。输出契约进一步要求检查 `data.complete`：预算耗尽的普通快照可以返回 `ok: true` 和部分树，同时标记 `complete: false`、`truncated: true`。外层只检查成功标志，会错把未观察到当成不存在。

## 引用绑定快照，不是永久控件编号

例如 `@s8f3k2p9:e8` 同时包含快照和元素身份；裸 `@e8` 会被拒绝。文档明确说，引用在同一快照中确定，但不保证跨 UI 变化稳定。每次动作前必须依据保存的身份信息重新寻找当前元素，缺失、过时或歧义都返回结构化错误，而不是挑一个最像的位置继续。

重新定位按层级使用路径、原生标识符、稳定文本和受限的几何证据。每一层只是找候选的方法，仍要核对身份；文本框当前值这类可变内容，不能单独充当稳定身份。窗口句柄也可能被操作系统复用，因此还要结合进程代际信息，避免旧句柄指向新窗口。

macOS 的命令宿主进一步保留原生无障碍对象，防止已删除的行悄悄解析成另一个拥有相同标识符的行。这些设计针对的是“观察之后、写入之前”状态变化的时间窗口。对上层调度器，`STALE_REF` 的合理恢复路径是重新观察并选择新引用，而不是无限重放旧命令。

## 后台语义动作与物理输入各有边界

默认 headless 引用操作走语义无障碍接口，不主动抢焦点或移动鼠标；语义路径不可用时，接口拒绝执行。`--headed` 才明确允许相应的物理输入。这里的后台执行不等于无图形会话的服务器环境：Linux 仍需要用户图形会话与 AT-SPI，X11 和 Wayland 的能力也不同。

动作前还有 actionability 检查，包括可见、稳定、启用、动作支持与策略等条件。默认有界等待为 5,000 ms，`type` 按字符增加预算；暂时不可见等条件可以等待，策略拒绝等终止条件则快速失败。等待结束后，共享输入的互斥租约在真正派发时生效，获得租约后还要重新解析之前观察到的对象。

这解释了为什么演示中的多个 Agent 光标不等于多个物理鼠标同时独立工作。光标是呈现层，底层仍需协调共享桌面输入。对物理输入，目标窗口与焦点在最后一步是否仍正确，和最初快照是否正确同样重要。

## 重试取决于送达证据

JSON 契约把 `delivery` 与 `retry` 放进 `disposition`。这比“成功／失败”多了一层关键语义：

| 返回状态 | 说明 | 自动重试判断 |
| --- | --- | --- |
| `not_delivered` | 未送达；部分操作也可表示目标状态已经满足 | `safe` |
| `delivered_unverified` | 已派发，但效果未得到独立确认 | `unsafe` |
| `delivered_verified` | 已回读并确认声明范围内的后置条件 | `unsafe` |
| `delivery_uncertain` / `unknown` | 送达不确定／未建立送达证据 | 不自动重试 |

最容易误解的是 `ok: true`。它可能只表示派发完成，并不代表应用已持久化数据。即使控件回读符合预期，也不等于远端服务已经保存。相反，动作失败后控件状态没变，也不能证明输入没有送达；盲目换一种点击或输入机制，可能造成重复副作用。

2.5 契约移除了那些每次成功调用都会返回、却没有独立证据的 `clicked`、`moved` 等标志，改为返回目标、步骤、送达状态与验证范围。窗口位置或尺寸的验证会注明范围、容差和单位。上层 Agent 可以据此区分“输入已发出”“目标控件状态已变化”和“业务目标完成”。最后一种仍需业务层证据。

## 值得跟踪的是接口契约，而非成功率口号

这些文档提供了可检查的设计，但没有给出相对截图 Agent 的统一任务成功率，因此不能据此声称全面更快或更可靠。平台适配也并不对称：例如 Windows 的严格 headless `type` 没有语义插入路径，`set-value` 才是对应的文本设置方式；Linux 某些窗口和鼠标操作依赖 X11。

对 AgentOps，最有价值的迁移是把观察完整性、身份有效性、派发结果与后置验证分开记录。这样，失败才可能被归因到看不全、找错对象、动作受限、结果未知或业务未完成，而不是统统记成“工具调用失败”。接入时应先读官方 [JSON 输出契约](https://github.com/vercel-labs/agent-desktop/blob/9eb9b296192fcb70bda25e918cd6dd66abfa3d0d/docs/json-output.md)，再读 [概念说明](https://github.com/vercel-labs/agent-desktop/blob/9eb9b296192fcb70bda25e918cd6dd66abfa3d0d/CONCEPTS.md) 中的引用、身份和动作可靠性部分。
