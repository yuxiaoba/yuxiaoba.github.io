---
id: together-prompt-samples
title: 2026-11-23 | How a code commit exposed Together’s stored prompt samples
date: '2026-11-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- coding-agents
summary: Together traces a download of private test samples to a credential committed
  by a coding agent, and describes controls at three points in the data lifecycle.
long_read: true
source_url: https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026
permalink: /tech/en/together-prompt-samples/
translation_source: assistant-authored bilingual notes
published_at: '2026-11-23T08:36:00.662216+08:00'
updated_at: '2026-11-23T08:36:00.662216+08:00'
---
Together AI’s account begins with a copy that outlived inference. The company stored prompt samples authorized for software testing in a private Hugging Face repository. A subsequent download connected three workflows often managed separately: production inference, offline testing and agent-assisted software development.

## From a served request to a persistent sample

Together scoped the incident to a subset of serverless requests in June and July 2026 involving MiniMax M3, GLM-5.2 and Kimi K2.6. The samples came primarily from June 24 and July 4, 8 and 14. Once a request had finished, a repository credential still granted access to the test copy. Model and date can narrow a customer’s investigation, though a matching date alone cannot establish that a particular prompt was sampled.

## Detection and download occurred within the same exposure window

Together says a coding agent committed a credential for the private sample store during work on a public code repository. Automated scanning detected the credential and the team reverted the commit. During the exposure window, an unauthorized party obtained the credential and downloaded the samples. The party subsequently tested credentials found inside them, including five canaries from the Dragos experiment. Those five establish downstream use of information in the samples. They supply no estimate of the number of affected customers.

## Where each change takes effect

Together now checks all pull requests for credentials and has revised its coding-agent development process. Scoped or short-lived credentials and keyless access where supported limit what an exposed credential can reach. Default ZDR for new accounts acts earlier, at the point where prompt data might be retained. Together worked with external forensic investigators and law enforcement. At publication it was still examining the contents for customer impact and had found no evidence of additional prompt leakage beyond this incident.

Vipul Ved Prakash · 2026-11-21 · [Security event: Prompt leakage for requests in June and July of 2026](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026)
