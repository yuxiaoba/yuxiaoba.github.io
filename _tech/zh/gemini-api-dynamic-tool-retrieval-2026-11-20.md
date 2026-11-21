---
id: gemini-api-dynamic-tool-retrieval-2026-11-20
title: 2026年11月21日｜Gemini 如何在一次请求内按需加载工具参数
date: '2026-11-21'
lang: zh
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
summary: 一个退款助手只需一次函数调用，却可能先把数百个无关工具的参数说明送进上下文。
translation_source: assistant
writing_source: assistant
long_read: true
source_url: https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-tool-retrieval/
permalink: /tech/zh/gemini-api-dynamic-tool-retrieval-2026-11-20/
published_at: '2026-11-21T08:47:17.687323+08:00'
updated_at: '2026-11-21T08:47:17.687323+08:00'
---
一个退款助手只需一次函数调用，却可能先把数百个无关工具的参数说明送进上下文。Google 在 Interactions API 预览中把两个问题拆开：模型先依据名称和描述决定需要哪种能力，决定之后才读取规定参数类型和必填字段的完整 schema。常用工具可以预先加载，长尾工具才走检索。

Lucia Loher, Nora Kassner · 2026-11-19 · [Introducing Tool Retrieval in the Gemini API](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-tool-retrieval/)

## 一次退款请求中的三条记录

服务端模式下，应用声明 tool_search，并在可延迟的函数上设置 defer_loading。以原文退款例子为例，模型看到退款工具的名称与描述，先按名检索；API 返回其参数定义后，模型发出带订单号和金额的 function_call。这三个步骤均在同一次 API 请求内发生，能在 interaction.steps 里分别看到搜索、结果和调用。真正执行退款以及返回执行结果仍由业务代码负责。排查选错工具时，这段记录能区分名称描述导致的选择问题和拿到参数定义之后的填参问题。

## 稳定前缀与持续计费

延迟加载让未用 schema 留在初始提示之外，后来需要的定义追加在对话后部，有利于保持跨轮缓存前缀。对远端 MCP 服务器，也可把整台服务器暴露的工具设为按需加载。费用上，搜索声明本身引入固定输入开销，已加载的 schema 在后续对话中继续按输入 token 收费。如果一次任务最终遍历了大部分工具，可省下的定义自然变少。官方给出了计费规则，未提供能普遍套用的延迟或选择准确率提升比例。

## 何时让客户端接管检索

若工具来自动态注册表，或不同用户看到的工具集合受权限约束，可把执行位置设为客户端，由应用自己的索引返回匹配 schema。这样可以在对话中途暴露新接入的工具，每次检索的代价是额外一次往返。与服务端按名查找不同，客户端可以决定查询参数和召回逻辑。原文列出的支持范围是 Interactions API 上的 Gemini 3.6 及后续模型；在比较两种接入方式时，工具库更新频率和权限过滤的位置，比工具总数更能说明这次额外往返是否值得。
