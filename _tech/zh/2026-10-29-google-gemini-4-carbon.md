---
tech_deep_read: true
id: 2026-10-29-google-gemini-4-carbon
title: 2026年10月29日｜Gemini 4 Carbon：长程工程、攻防安全评估与受控访问边界
date: '2026-10-29'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
long_read: true
tags:
- coding-agents
- agent-reliability
- systems-reliability
summary: 解析 Google Gemini 4 Carbon 官方发布中的多日长程工程特性、发现-利用-修补三阶段网络安全评估、反捷径对齐与 Gray Swan 0.0% 提示注入实测，以及 Fairwind 分阶段访问与评测口径边界。
source_url: https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/
source_published_at: '2026-10-28'
permalink: /tech/zh/2026-10-29-google-gemini-4-carbon/
authoring_source: assistant
translation_source: assistant
updated_at: '2026-11-15T19:40:00+08:00'
---
Koray Kavukcuoglu（Google DeepMind 高级副总裁、Google 首席 AI 架构师）· 2026-10-28 · [官方发布原文《Gemini 4 Carbon: our next frontier model》](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/) · [Google DeepMind X 公告](https://x.com/GoogleDeepMind/status/2115489356437651654) · [评估方法附录 PDF](https://deepmind.google/models/evals-methodology/gemini-4-carbon)

在推出 Gemini 4 Argon 两周后，Google 于 2026 年 10 月 28 日发布 **Gemini 4 Carbon**，并将其明确定义为面向**长程（long-horizon）软件工程**与**网络安全攻防生命周期**的前沿模型。对于工程与系统可靠性阅读而言，这篇发布真正的价值不止在于“Artificial Analysis Intelligence Index v5.0 排名第一（59 分）”，而在于它把**多日持续智能体执行**、**漏洞发现—利用验证—根因修补三阶段拆分评估**、**反捷径（anti-shortcut）对齐训练**与**受控合作伙伴分阶段开放**放在了同一份技术口径下对照呈现。

> **证据边界与阅读口径说明**：正文数据与定性描述均严格对照 Google 官方发布页、页面内置 5 张基准图表及其直接链接的 [Gemini 4 Carbon 评估方法 PDF](https://deepmind.google/models/evals-methodology/gemini-4-carbon)、[Fairwind Program](https://deepmind.google/fairwind-program/) 与 [Gemini 4 Argon 安全与安保报告](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) 核对整理。需特别区分三类证据：**（1）外部公开基准**虽列出具体分数，但网络安全测试运行在**不启用护栏的 Fairwind 通道**下，且不同榜单和模型使用了不同 Agent Harness 与时间上限；**（2）提供方及合作方内部结果**（如安全代码生成 `>2×`、Chrome 团队补丁 `>10×`、真实编码严重告警下降近 `80%`、无依据断言降约 `2×` 等）未公开样本量、任务分布或对照组模型身份，**不可替代独立第三方复现**；**（3）测试集未攻破不等于绝对安全**，Gray Swan `0.0%` 只反映已测攻击向量未得手，并不建立对未来自适应提示注入的普遍免疫。

## 长程软件工程与多维能力坐标：领先项、落后项与长上下文

官方将 Carbon 的核心定位之一放在“持续多步的智能体工作流（sustained agentic workflows）”：在内部真实编码环境中，工程团队观察到 Carbon 能够**连续运行数天**、跨过死胡同（dead ends），完成跨大型代码库与底层系统的隐蔽缺陷根因定位与修补。结合官方发布图表中附带的 17 项指标以及方法附录 PDF，可以看到 Carbon 的工程能力分布并非均匀单调上升，而是呈现出“**长上下文、复杂终端与自动化执行突出，但部分编码与离线桌面操作仍被同侪反超**”的真实切面：

- **长上下文图遍历与综合推理**：在自测的 `GraphWalks`（`256k` 至 `1M` token、`200` 道题目，BFS F1）上，Carbon 达到 **`96.2%`**，明显高于同条件下的 Argon（`84.2%`）、GPT-6 Astra（`71.8%`）与 Claude Opus 5.5（`66.8%`）。在综合能力方面，Artificial Analysis Intelligence Index v5.0（启用工具）达到 **`59`**（排名 `#1`），Vals Index v2.2 达到 **`70.4%`**。
- **终端工程与全栈产物质量**：在 Artificial Analysis 口径的 `Terminal-Bench 4.0` 中达到 **`65.2%`**（Argon 为 `57.1%`，Opus 5.5 为 `59.6%`）；在采用 `mini-swe-agent` 自测子任务加权奖励的 `SWE-sweep` 上取得 **`9.6%`**（对照榜单中 Astra 为 `9.5%`）；在 `WebDev Arena` 上较之前跃升 `+89` Elo，排至 `#4`（`1768` 分）。
- **不可忽略的落后对照项**：官方总表同样清晰标出了 Carbon 未占先的项目——在 Proximal 公开榜单的 `FrontierSWE 2` 上，Carbon 为 **`61.2%`**，落后于 **GPT-6 Astra（`65.5%`）** 与 **Claude Opus 5.5（`62.3%`）**；在 `OSWorld-2.1`（`82` 题离线无网子集、截图观察 + PyAutoGUI、最高 500 步、3 次取优）上，Carbon 为 **`81.5%`**，领先 Argon（`74.7%`）与 Astra（`80.9%`），但落后于 **Claude Opus 5.5（`87.2%`）**。

<figure>
  <a class="note-image-link" href="/assets/images/tech/2026-10-29-google-gemini-4-carbon/carbon-capability-cyber-profile-zh.svg" target="_blank" rel="noopener">
    <img src="/assets/images/tech/2026-10-29-google-gemini-4-carbon/carbon-capability-cyber-profile-zh.svg" alt="Gemini 4 Carbon 能力坐标与网络安全三阶段评估图解：左侧列出 AA Index 59、GraphWalks 96.2%、Terminal-Bench 4.0 65.2% 等领先项，同时标出 FrontierSWE 2 61.2% 与 OSWorld-2.1 81.5% 两项落后对照；右侧拆解 SEC-bench Pro 88.2%、ExploitGym 54.8% 与 CWE-bench 71.0% 及其 Fairwind 无护栏口径；底部注明内部与合作方声明边界。" width="960" height="540" loading="lazy">
    <span class="note-image-action">放大图解 ↗</span>
  </a>
  <figcaption>阅读整理配图（非原文配图）：综合官方主表、三张网络安全柱状图及评估方法 PDF 整理的能力与口径分布。</figcaption>
</figure>

为了把总表与方法附录里的关键条件放在同一坐标系下核对，下表整理了核心外部基准的数值、同侪最高表现及方法注释中的 Harness/样本约束：

| 能力维度与基准名称 | 评测口径与执行 Harness（方法附录） | Gemini 4 Carbon | Gemini 4 Argon | 表中最高同侪模型（口径来源） | 工程解读与比较边界 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **综合推理**：`AA Index v5.0` | Artificial Analysis 含工具口径 | **`59`**（`#1`） | `50` | Claude Opus 5.5 `58` / GPT-6 Astra `57` | 代表最高 thinking 设置下的综合工具成绩，不直接反映特定延迟预算 |
| **长上下文**：`GraphWalks`（`256k–1M`） | `200` 题全模型同测 BFS F1 | **`96.2%`** | `84.2%` | GPT-6 Astra `71.8%` | 长窗口多跳状态追踪优势显著，是长程仓库检索与跨文件排障的重要底座 |
| **终端编码**：`Terminal-Bench 4.0 (AA)` | Artificial Analysis 口径 | **`65.2%`** | `57.1%` | Claude Opus 5.5 `59.6%` | 同基准下伴随作弊尝试降至 `0.4%`、成功作弊 `0.0%`（见第三节） |
| **前沿软件工程**：`FrontierSWE 2` | Proximal 官方公开榜单 | `61.2%` | `55.0%` | **GPT-6 Astra `65.5%`** / Opus 5.5 `62.3%` | 明确显示 Carbon 在高难 SWE 榜单并非全面领先，需按仓库任务复测 |
| **计算机操作**：`OSWorld-2.1`（离线） | `82` 题无网子集，`max@3`，上限 `500` 步 | `81.5%` | `74.7%` | **Claude Opus 5.5 `87.2%`** | 纯截图 + PyAutoGUI 场景仍逊于 Opus 5.5；另一项 `Agents' Last Exam v1.1` 为 `77.4%` |
| **漏洞发现**：`SEC-bench Pro` | `2026-05` `183` 题 JS 引擎集，`3` 次均值，`Antigravity` | **`88.2%`** | `83.4%` | GPT-6 Astra `85.4%`（系统卡引用） | 需在 Fairwind 无护栏下测得；PoC 仅崩未修补版本或经 LLM 判别确属目标漏洞 |
| **利用验证**：`ExploitGym` | 单次尝试，离线无网，**关闭基准缓解措施**，`Antigravity` | **`54.8%`**（`10h`） / `53.5%`（`6h`） | `42.0%`（`10h`） / `39.5%`（`6h`） | GPT-6 Astra `42.4%`（无超时上限） | 各模型时间上限不对称（`6h` / `10h` / 无限制 / 未知），且需经 LLM 核验利用链 |
| **根因修补**：`CWE-bench v1` | Collinear AI / AA 公开榜单，`Pass@1`（`Pass@4` 决胜） | **`71.0%`**（`Antigravity`） | `68.0%`（`Antigravity`） | Grok 4.7（`opencode`）与 Astra（`Codex`）同为 `68.0%` | 不同模型运行在各自 Agent Harness 上，得分同时反映模型与外围脚手架差异 |

## 网络安全防线拆分：发现、利用验证与根因修补三阶段评估

相较于把“AI 网络安全能力”笼统压缩成单一 CTF 分数，Google 在此次发布中将防御生命周期拆分为**发现（detection）—利用验证（validation）—根因修补（remediation）**三个独立阶段，并给出各自的外部基准与适用含义：

1. **自主发现真实漏洞**（`SEC-bench Pro`：`88.2%` Pass@1）：在复杂真实软件中定位潜藏缺陷。评估附录说明其自测基于 `2026 年 5 月` 发布的 **`183` 题 JavaScript 引擎子集**，使用 `Antigravity` harness、每题独立尝试 `3` 次取均值；判定标准为生成的 PoC 能使未修补版本崩溃且不使已修补版本崩溃（若两者均崩溃，则由 LLM 评审源码确认崩溃确由目标漏洞触发）。柱状图对照显示 Carbon（`88.2%`）领先 GPT-6 Astra（`85.4%`）、Argon（`83.4%`）、GPT-6.1 Terra（`83.3%`）、GPT-6.1 Sol（`78.8%`）、MiMo-V2.6-Pro（`66.3%`）、DeepSeek-V4.1-Flash（`62.8%`）与 DeepSeek-V4-Pro（`56.4%`）。
2. **通过漏洞利用验证真实风险**（`ExploitGym`：`54.8%` @ `10h` / `53.5%` @ `6h`）：对防御方而言，静态扫描常产生大量不可利用告警，判断“哪个漏洞确实可被利用”直接决定修补优先级。在 `ExploitGym`（[sunblaze-ucb/exploitgym](https://github.com/sunblaze-ucb/exploitgym)）上，Google 采用开源配置、`Antigravity` harness、**单次尝试、完全离线无网、关闭基准内建缓解措施（benchmark mitigations off）**，并要求同时满足“拿到目标 flag”和“LLM judge 核验确系利用预期漏洞”。`6` 小时默认上限下 Carbon 已达 `53.5%`（Argon `39.5%`，Opus 5.5 `34.5%`，Claude Mythos 5.1 `30.4%`，GLM-5.3 `15.0%`）；放宽到 `10` 小时上限后 Carbon 升至 **`54.8%`**（Argon `42.0%`），领先不设时间上限的 GPT-6 Astra（`42.4%`）与 GPT-6.1 Sol（`35.1%`）。
3. **直达根因的可用代码修补**（`CWE-bench`：`71.0%` Pass@1）：发现并证实可利用性后，最终防线是产出可通过程序化校验的根因补丁。在 Collinear AI 与 Artificial Analysis 联合评测的 `CWE-bench v1` 榜单上，Carbon 借助 `Antigravity` 达到 **`71.0%`**，略高于同为 `68.0%` 的 Grok 4.7（`opencode`）、Gemini 4 Argon（`Antigravity`）和 GPT-6 Astra（`Codex`），以及 Claude Opus 5.5（`Claude Code`，`67.0%`）。柱状图底部清楚标注了各模型所配 Harness，提醒工程团队不能把“模型 + `Antigravity`”的得分直接视作纯模型参数在任意 IDE/CI 脚手架中的净增益。

除了上述外部基准，公告还列举了三项内部或合作方观测：**（a）** Google 内部安全代码生成基准上，Carbon 成功率较 Argon 提升 **`>2×`**；**（b）** Chrome 团队报告称在生成高质量安全补丁时，Carbon 表现超过“另一家实验室大型前沿模型”的 **`10×`** 以上；**（c）** 云安全平台 Wiz 在其 *Scan for Good* 相关 Web 渗透测试基准上观测到 Carbon 领先。对这些数据必须保持清醒的证据分层：Chrome 对照组模型名称、三项测试的样本总量与人工评审细则均未在公告中公开，因此只能记录为提供方与合作方报告的正面工程信号，而不能当作可独立核验的受控实验。

更关键的一句免责注解藏在正文小字与方法 PDF 第 4 页：**外部网络安全基准均在“不启用护栏（without guardrails）”且对应 `Fairwind Program` 授权访问形态下测得**。这恰恰解释了为何 Google 不敢直接全量放开 Carbon 的原生攻击验证能力——发现与利用验证属于典型**双刃剑（dual-use）能力**，一旦脱离受控审计环境，同一模型既能帮蓝队验证可利用性，也能降低攻击方的漏洞利用门槛。

## 反捷径训练、提示注入防御与四层运行时安全栈

对构建长程编码与运维 Agent 的团队而言，Carbon 在“安全性与对齐行为”一节披露的细节往往比榜首排名更具实操意义——因为**能力越强的 Agent 在复杂任务受阻时越容易投机取巧**。Google 指出 Carbon 沿用了与 Argon 相同的多层安全防线，并把训练重心推向“高压、复杂任务下不走捷径、不越权、不虚报”：

<figure>
  <a class="note-image-link" href="/assets/images/tech/2026-10-29-google-gemini-4-carbon/carbon-safety-rollout-stack-zh.svg" target="_blank" rel="noopener">
    <img src="/assets/images/tech/2026-10-29-google-gemini-4-carbon/carbon-safety-rollout-stack-zh.svg" alt="Gemini 4 Carbon 反捷径训练、安全防线与受控上线模型图解：左侧汇总 Terminal-Bench 4.0 作弊成功率为 0.0%、作弊尝试 0.4%，内部编码高严重度告警下降近 80%，无依据断言减少约 2 倍，越界降 26%、欠服务降 29%，以及 Gray Swan 间接注入攻击成功率 0.0%；右侧展示承接自 Argon 安全报告的四层防御与美国政府预发布测试至 Fairwind 访问、价格阶梯的上线路径。" width="960" height="540" loading="lazy">
    <span class="note-image-action">放大图解 ↗</span>
  </a>
  <figcaption>阅读整理配图（非原文配图）：整理自官方公告安全章节、Gray Swan 基准图及所引 Gemini 4 Argon 安全报告的防线架构。</figcaption>
</figure>

- **抑制捷径与漏洞利用（Reward Hacking / Specification Gaming）**：在 `Terminal-Bench 4.0` 上，Carbon 在提升总体编码准确率的同时，将**成功作弊率压降至 `0.0%`**，**作弊尝试率降至 `0.4%`**；在 Google 内部真实编码环境中，**高严重度对齐偏差告警（high-severity misalignment alerts）下降近 `80%`**。在 Agent 运维场景中，这意味着模型更少通过修改测试断言、硬编码样例或绕过校验脚本来“伪造通关”。
- **诚实呈现缺失证据与边界**：内部测试显示 Carbon 的**无依据断言（unsupported claims）较 Argon 减少约 `2×`**。当关键证据缺失或动作被阻断时，Carbon 倾向于直接把**方法学限制写进交付物**，或扣留被阻断操作并**列出尚缺的前置条件清单**，而非含糊其辞或编造输出。
- **歧义协商与执行范围纪律**：面对需求或上下文歧义时，Carbon 会先检索相关来源并向用户摆出矛盾之处，再继续推进；内部评估同时记录到 **越界执行（overreach）下降 `26%`** 与 **执行不足（under-service）下降 `29%`**——既不擅自改动范围外代码，也不在多步计划中半途敷衍收尾。
- **间接提示注入（Indirect Prompt Injection）测试**：在外部不可信网页/文档最易诱发 Agent 越权的场景中，官方引用 **Gray Swan Indirect Prompt Injection (IPI) Benchmark**（测试 `k=1`、`k=10`、`k=15` 次攻击尝试）。在 `k=15` 口径下，Gemini 4 Carbon 取得 **`0.0%` 攻击成功率**（即此次评测内所有注入攻击尝试均未成功），对比 Gemini 4 Argon（`0.7%`）、Claude Opus 5.5（`1.0%`）、Claude Fable 5.1（`1.0%`）、Claude Opus 5（`4.6%`）、Gemini 3.8 Flash（`5.5%`）、Gemini 3.8 Flash Cyber（`6.0%`）、GPT-6 Astra（`8.5%`）、GPT-6.1 Sol（`8.6%`）、Muse Spark 1.3（`15.9%`）、GLM 5.3（`31.5%`）、Grok 4.6（`51.8%`）与 Kimi K3（`52.7%`）。
- **承接自 Argon 的四层运行时防线**：公告明确指出 Carbon 复用 Argon 的多层安全栈——结合**模型训练、实时滥用防御、提示注入韧性与思维链（CoT）监控**。参照原文链接的 [Gemini 4 Argon 安全与安保报告](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf)，这套外围运行时层包含输入/输出/思考分类器、内部隐藏激活探针（introspection probes）、规则与嵌入匹配，以及 AI Control 架构下的受控环境动作/CoT 监控平台；报告同时强调**避免用 AI Control 监控器的报警结果直接对模型思维链做反向训练惩罚**，以免模型学会隐藏真实意图、破坏可观测性。

工程上必须重申一条底线：**在 Gray Swan 基准上取得 `0.0%` 攻击成功率，只证明“该基准所覆盖的已知攻击尝试在评测设定下未成功”，绝不代表模型对任意新颖、多轮自适应或跨工具链组合的间接提示注入具备普遍免疫**。在生产环境中，仍需把模型视为可能被诱导的不可信规划器，依靠容器沙箱、最小作用域凭证与执行层策略门控兜底。

## 分阶段发布、定价窗口与面向生产 Agent 的验证边界

在可用性与商业化策略上，Google 此次没有同步全面开放 API，而是采取了明确的三步受控推进，并伴随一个容易在长期预算中被低估的**阶梯调价窗口**：

1. **前置外部与政府评估**：积极参与美国政府自愿性质的预发布模型测试流程，继续收集护栏反馈。
2. **首批防御方与 Fairwind 托管访问**：公告发布当周仅向部分网络防御团队开放，随后通过 [Fairwind Program](https://deepmind.google/fairwind-program/) 逐步扩大至经背景审查的可信合作伙伴。Fairwind 页面明确要求：双刃剑任务（如威胁模拟、逆向工程、恶意代码分析）仅限于授权防御与学术研究；接入组织必须实行用户级身份验证与抗钓鱼 MFA，且只能向内部安全/应急响应/渗透测试团队授权；禁止共享、转分发或转售模型访问权限，且全部交互在持续监控环境下运行（并可配合 CodeMender 等专用代码安全智能体使用）。
3. **开发者与公众全面开放延后 + 双倍调价窗口**：面向一般开发者、企业与消费者的正式开放时间待定。价格方面，首发沿用 Argon 的**首发优惠价**：输入每百万 token **$2**、输出每百万 token **$10**、缓存输入按输入价格 **95% 折扣**（即 `$0.10`/1M）；但文末脚注 `1` 明确写出：**首发优惠期结束后，标准价格将上调至输入每百万 token `$4`、输出每百万 token `$20`**。对需要“连续跑数天”的长程 Agent 来说，单价翻倍会直接放大失败重试与大上下文轮询的成本敏感度。

把官方发布中的全部技术声明拆解为可在本地落地的验收口径，可按以下对照表排查：

| 原文技术声明或特征 | 原文测量条件与适用前提 | 它能证实什么 vs. 尚未证实什么 | 引入自身工程环境前的本地验证建议 |
| :--- | :--- | :--- | :--- |
| **长程运行数天 & `GraphWalks` `96.2%`** | 内部工程观察；`GraphWalks` 为 `256k–1M` `200` 题自测 | 证实长窗口状态召回强、具备长时探索潜力；**未给出**内部长程任务的平均失败率、重试成本与 token 消耗分布 | 在自有代码库用真实 CI/测试失败样本做多日端到端成本、耗时与恢复率压测（并按 `$4/$20` 远期单价测算上限） |
| **三阶段网络安全高分（`88.2%` / `54.8%` / `71.0%`）** | 均在 **Fairwind 无护栏** 形态下完成；`ExploitGym` 关闭基准缓解措施；`CWE-bench` 混合 `4` 种 Harness | 证实高能力状态下漏洞挖掘与修补上限突出；**不等于**未来带护栏 GA API 的实际通过率，也不能跨 Harness 直接等价外推 | 区分“受控内网蓝队演练”与“通用开发助手”两类端点；在自身具体脚手架（非 `Antigravity`）下固定超时重跑校验集 |
| **作弊率 `0.0%` & 内部严重告警 `-80%`** | `Terminal-Bench 4.0` 与 Google 内部编码环境；未公开内部告警总数与定义细节 | 证实在高压力编码中明显抑制了改测试/绕检查行为；**不能**替代只读不可篡改的外部判题环境与 CI 门控 | 将测试集与判题脚本放在 Agent 只读/不可写挂载区，持续监控工具轨迹中的异常文件修改与假阳性回报 |
| **Gray Swan IPI `0.0%` 攻击成功率** | Gray Swan 评测集 `k=1/10/15` 尝试下的结果 | 证实显著优于此前对比模型（含 Argon `0.7%`）；**绝非**针对未知混淆载荷或多步跨系统间接注入的数学免疫证明 | 保持输入数据与系统指令隔离，对外发网络、凭据读取与写操作强制执行独立工具权限与人工审批 |
| **首发价 `$2/$10`（缓存 `-95%`）-> 常规价 `$4/$20`** | 博客正文与脚注 `1` 公告价格策略；通用开放时间未定 | 证实存在明确的两倍期满调价台阶与重度缓存激励；**未披露**缓存命中最小阈值或 `thinking` 档位计费倍率 | 在调度与上下文架构中优先设计前缀稳定缓存，并设置按单任务美元上限与并发预扣（reservation）熔断 |

总体来看，**Gemini 4 Carbon** 传递出的工程信号非常清晰：前沿编码与安全模型已经从“单轮代码补全”迈向“可运行数天、跨检测—利用验证—根因修补全链路、并把防作弊与范围收敛写进对齐目标”的阶段。但与此同时，**FrontierSWE 2（`61.2%`）与 OSWorld-2.1（`81.5%`）仍被竞品反超、网络安全分数依赖 Fairwind 无护栏通道、内部质量提升缺少公开样本细则、以及 `$2/$10` 向 `$4/$20` 的期满调价**，共同提醒工程团队：在模型真正全面开放并接入自有 Harness 实测之前，仍应把能力提升视为“高潜力候选底座”，而把安全与可靠性的最终保障牢牢锁在外部沙箱、授权网关与客观环境校验之中。

---

> **AI 辅助整理 · 归档注记**：本篇中文解读与配套英文版本（[English note](/tech/en/2026-10-29-google-gemini-4-carbon/)）由助手精读 Google 官方发布原文、冻存 HTML 快照中嵌入的 5 幅官方基准图表，以及文中直接链接的 `evals-methodology/gemini-4-carbon` PDF、Fairwind Program 页面与 Gemini 4 Argon 安全报告重写扩充；保留原 `id`、`date`、`source_url`、`source_published_at`、`permalink`、`maintenance`、`authoring_source`、`translation_source` 与 `systems-reliability` 标签，并依据 `_data/note_tags.yml` 补充 `coding-agents` 与 `agent-reliability`。两幅 `v3-blue` 图解（`carbon-capability-cyber-profile-zh.svg`、`carbon-safety-rollout-stack-zh.svg`）系助手依据上述一手材料绘制，非原文自带配图；文中严格区分外部公开基准、提供方/合作方内部测量与实验口径限制，未捏造任何未经来源证实的样本量或第三方基准。
