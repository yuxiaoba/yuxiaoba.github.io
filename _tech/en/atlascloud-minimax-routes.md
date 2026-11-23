---
id: atlascloud-minimax-routes
title: 2026-11-23 | Atlas Cloud ties MiniMax availability to the hosting path
date: '2026-11-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
summary: Atlas stopped forwarding to the official API, retained some hosting arrangements
  and described a separate model-by-model condition for returning to OpenRouter.
long_read: true
source_url: https://www.atlascloud.ai/blog/ai-updates/security-and-privacy-commitment
permalink: /tech/en/atlascloud-minimax-routes/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
The same MiniMax model name can correspond to different data processors on Atlas Cloud. Atlas based its availability decision on the hosting path. That explains how it could disable an upstream API while continuing to serve some models from the same family.

## Where researchers observed access

Atlas says a third party opened private links placed in test prompts sent through Atlas to the official MiniMax API, including M3 and M2.7 requests in Q3 and early Q4 2026. According to Atlas, the evidence available at publication pointed to access after the requests reached MiniMax. Atlas says it did not store those prompts or outputs. For other requests, the notice describes possible exposure. It cannot tell a customer whether the contents of an individual request were misused.

## Which hosting arrangements remained eligible

Atlas stopped sending requests to the official MiniMax API. It kept MiniMax models available where it hosted them itself or where the hosting provider confirmed the requests would bypass that API. The model name visible to the customer therefore identifies only part of the processing arrangement. Atlas also included M3.1 Flash in its precautionary guidance about secrets. The models expressly named in the link-access observations were M3 and M2.7.

## Four daily checks and a model-level return condition

Atlas says it chose to withdraw all its models from OpenRouter during testing and informed the platform in advance. Its stated return condition applies to each model individually. The researcher was testing the models Atlas serves four times a day. That cadence describes repeated sampling. The notice supplies no route-coverage figure, request denominator per run or sensitivity to passive reading. Atlas included other models in the checks even though it reported no problems with them at publication.

Atlas Cloud · 2026-11-22 · [Security notice: MiniMax's official API and how we protect your data](https://www.atlascloud.ai/blog/ai-updates/security-and-privacy-commitment)
