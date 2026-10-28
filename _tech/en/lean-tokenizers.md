---
date: '2026-10-28'
published: true
layout: article
maintenance: daily-research
authoring_source: assistant
translation_source: assistant
id: lean-tokenizers
title: '2026-10-28 | A Lean tokenizer prototype: make token preservation explicit'
lang: en
source_type: tech
long_read: true
source_url: https://srush.github.io/verified-tokenizer/
tags:
- agent-reliability
- systems-reliability
summary: Why messages, bytes, and tokens are not interchangeable, and what extracted
  Rust proofs can guarantee.
permalink: /tech/en/lean-tokenizers/
published_at: '2026-10-28T15:24:19.938525+08:00'
updated_at: '2026-10-28T15:24:19.938525+08:00'
---
When an agent feeds tool results back into a conversation and later trains on that trajectory, decoding and re-encoding can preserve text while changing token IDs. Sasha Rush’s prototype verifies tokenization together with message rendering, making consistency more precise than textual similarity.

Original: [Lean Verified Tokenizers](https://srush.github.io/verified-tokenizer/) · Sasha Rush; [publicly introduced by the author](https://x.com/srush_nlp/status/2115197402525434242) on 2026-10-27.

### Prove a specified implementation

Rust code is extracted into Lean through Aeneas. The BPE specification selects the lowest-ranked eligible adjacent merge, breaking ties at the leftmost position. The implementation–specification theorem assumes valid merge rules and trusts the extraction process.

Message rendering uses fixed Qwen-style delimiters and escaping. Proven properties include recovering message roles and content after rendering/parsing, and preserving existing bytes when appending a message. They do not cover arbitrary Jinja templates that rewrite earlier history.

<a class="note-image-link" href="/assets/images/tech/lean-tokenizers/tito-append.png" target="_blank" rel="noopener" aria-label="Append-only growth of message, byte, and token representations · View original image ↗"><img src="/assets/images/tech/lean-tokenizers/tito-append.png" alt="Append-only growth of message, byte, and token representations" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*New content extends the right side while existing messages, bytes, and token IDs remain prefixes. Generated tokens are not re-encoded.*

### Preserve generated tokens instead of retokenizing

The application follows Tokens In, Tokens Out. Generated tokens remain intact; new tool messages contribute newly encoded bytes and tokens. Message, byte, and token representations extend together. This preserves retained IDs rather than asserting that BPE naturally commutes with arbitrary string concatenation.

The prototype also explores inserting a past message while retaining surrounding token IDs, under its fixed renderer, validity, and size assumptions. That can support rescoring under edited contexts but is not a general guarantee for every tokenizer and edit.

The useful contribution is an explicit verification boundary. Proven operations under stated assumptions do not prove an entire RL stack correct. The implementation is limited by Aeneas’ Rust subset, lacks threaded tokenization, and provides no complete-training or throughput result. It is a concrete example of a checkable contract for an agent infrastructure component.
