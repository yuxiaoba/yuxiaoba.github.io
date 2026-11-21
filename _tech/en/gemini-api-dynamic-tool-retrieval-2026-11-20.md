---
id: gemini-api-dynamic-tool-retrieval-2026-11-20
title: 2026-11-21 | How Gemini loads tool schemas on demand within one request
date: '2026-11-21'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
summary: A refund assistant may need one function yet start by sending parameter schemas
  for hundreds of unrelated tools.
translation_source: assistant
writing_source: assistant
long_read: true
source_url: https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-tool-retrieval/
permalink: /tech/en/gemini-api-dynamic-tool-retrieval-2026-11-20/
published_at: '2026-11-21T08:47:17.687323+08:00'
updated_at: '2026-11-21T08:47:17.687323+08:00'
---
A refund assistant may need one function yet start by sending parameter schemas for hundreds of unrelated tools. Google’s Interactions API preview separates choosing a capability by name and description from loading its argument types and required fields. Frequent tools can stay loaded while the long tail is deferred.

Lucia Loher, Nora Kassner · 2026-11-19 · [Introducing Tool Retrieval in the Gemini API](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-tool-retrieval/)

## Three records in one refund request

In server-side mode the application declares tool_search and marks eligible functions with defer_loading. In Google’s refund example, the model sees the function name and description, searches for it by name, receives its schema and emits a function_call with the order identifier and amount. Search, result and call all appear in interaction.steps inside one API request. Application code executes the refund and returns the result. The trace distinguishes a naming or selection problem from an argument error after schema retrieval.

## Stable prefixes and continuing charges

Unused definitions stay out of the initial prompt. A schema loaded later appears further along in the conversation, helping the cached prefix remain stable across turns. A remote MCP server can also expose its tools on demand. The search declaration adds a fixed input overhead, and loaded schemas continue to count as input for the rest of the conversation. A task that eventually touches most of the catalog saves less. Google documents the billing behavior without supplying a universal latency or selection-accuracy gain.

## When the client owns retrieval

A dynamic registry or per-user permission filter may favor client-side execution. The application can query its own index and return matching schemas, including tools connected mid-conversation. Each lookup adds a round trip. In exchange, the client controls the query parameters and selection logic. The article lists Gemini 3.6 and later in the Interactions API. Registry changes and where permissions are enforced help determine whether an extra round trip buys something the server-side name lookup cannot supply.
