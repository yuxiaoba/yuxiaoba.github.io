---
id: cloudflare-ddos-q3-2026
title: 2026年10月30日｜短促高频攻击增加：Cloudflare 的季度 DDoS 观察
date: '2026-10-30'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
summary: Cloudflare 的第三季度数据提醒运维团队，攻击风险不只来自极端峰值：大量短促攻击可能在人工响应之前结束，也可能反复影响服务。
long_read: true
source_url: https://blog.cloudflare.com/ddos-threat-report-2026-q3/
permalink: /tech/zh/cloudflare-ddos-q3-2026/
translation_source: assistant-authored paired Chinese/English reading notes
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-10-30T10:31:20.339125+08:00'
---
Cloudflare 的第三季度数据提醒运维团队，攻击风险不只来自极端峰值：大量短促攻击可能在人工响应之前结束，也可能反复影响服务。

**来源：** Cloudforce One，[Cloudflare DDoS Threat Report 2026 Q3: More swarms, fewer giants](https://blog.cloudflare.com/ddos-threat-report-2026-q3/)，2026 年 10 月 29 日。

Cloudflare 称其网络在 2026 年第三季度缓解了 1820 万次网络层 DDoS 攻击，平均每小时约 8226 次；其中 96% 少于 10 分钟，98% 低于 1 Gbps。超过 1 Tbps 的攻击从第二季度的 805 次降至 251 次；报告提到执法行动与之同时发生，但不足以证明因果关系。

攻击向量也发生变化：CLDAP 反射攻击占比降至 0.05%，DNS 放大攻击环比增长 215%，其他 UDP flood 的占比由 14.06% 升至 31.31%。反射攻击利用伪造源地址，让开放服务向受害者发送放大的响应；原始 UDP flood 则以大量数据包消耗目标网络与计算资源。

这些统计来自 Cloudflare 自身网络和检测口径，不能直接视为整个互联网的无偏样本。对可靠性工作的启示是同时观察频率、持续时间和协议构成，而非只关注最大带宽。
