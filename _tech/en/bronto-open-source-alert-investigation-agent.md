---
id: bronto-open-source-alert-investigation-agent
title: '2026-10-27 | Bronto: Bound the Scope and Budget of an Alert Investigator'
date: '2026-10-27'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- observability
summary: The open-source investigator separates alert confirmation, deterministic
  context, bounded log queries, and reporting, with concrete call-budget and persistence
  limits.
long_read: true
source_url: https://bronto.io/blog/introducing-brontos-open-source-alert-investigation-agent
permalink: /tech/en/bronto-open-source-alert-investigation-agent/
translation_source: assistant-authored Chinese and English; English translation by
  assistant
published_at: '2026-10-27T08:49:56.503057+08:00'
updated_at: '2026-10-27T08:49:56.503057+08:00'
---
An AI SRE system is useful when it turns an alert into traceable evidence, rather than merely a plausible root-cause narrative. Bronto’s open-source Alert Investigation Agent separates identification, context generation, investigation, and reporting. The interesting details are the constraints between those stages: which fields come from service APIs, which questions require confirmation, which logs the model can query, and how a budget-limited investigation ends.

Original: [Introducing Bronto’s Open-Source Alert Investigation Agent](https://bronto.io/blog/introducing-brontos-open-source-alert-investigation-agent)  
Nikolai Gladychev · Bronto · 2026-10-21 · [Project and README](https://github.com/bronto-community/bronto-alert-investigation-agent)

## Establish which alert is being investigated

A natural-language description does not uniquely identify an event. “More gateway 500s” may match several monitors and time windows. Interactive mode searches audit logs, asks the user to confirm the alert, and offers an optional playbook. Confirmation is implemented as a tool call, with middleware interrupting execution until a choice arrives. An unconfirmed target routes to a give-up branch, avoiding a polished report about an unidentified incident.

Confirmation is not mandatory for every entry point. A webhook carries a known alert, so it proceeds directly to context and investigation without asking questions. The design places interaction where the input is ambiguous; it does not mean that every automatic investigation receives human approval. Generating an investigation report and authorizing a remediation action are also separate matters. This workflow produces reports and recommendations.

<a class="note-image-link" href="/assets/images/tech/bronto-open-source-alert-investigation-agent/graph.png" target="_blank" rel="noopener" aria-label="Bronto identification, context, investigation, and reporting graph · View original image ↗"><img src="/assets/images/tech/bronto-open-source-alert-investigation-agent/graph.png" alt="Bronto identification, context, investigation, and reporting graph" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Interactive input starts with identification; a known alert can enter context directly. Unconfirmed input takes give_up, while the other path investigates and reports before ending.*

## Let deterministic logic establish the time window

The context stage uses SDK REST lookups to retrieve the monitor, its backing queries, and datasets, then computes a pre-trigger time series and an absolute investigation window. With a playbook, a model can help identify relevant datasets. Core event identity and time boundaries are not left to unconstrained model inference. This gives later reasoning an explainable search scope.

Investigation binds a limited tool set including `get_keys`, `get_key_values`, `search_logs`, and `timeseries`, with concurrent queries supported. Middleware removes `time_range` from the model-visible schema and supplies absolute boundaries from the alert context. Failed calls use backoff retries. Moving this error-prone parameter choice into program logic also prevents historical alerts from silently becoming searches over a default recent interval.

A correct window does not guarantee that the cause lies inside it. A deployment may predate the window, or a dependency may be absent from the selected logs. The engineering trade-off is greater control at the potential expense of evidence coverage. An extension should specify when to widen the interval or add a data source and retain the reason. That is a recommendation derived from the implementation, not an already demonstrated project capability.

## Five calls bound investigation, not the whole task’s cost

The README defaults to five model calls for investigation. `--max-model-calls` controls only that stage. Context and report generation can each make another model call, while identification has a separate budget mechanism. Setting the parameter to five therefore does not imply five calls for the complete session or a fixed total cost.

On the last investigation turn, search tools are removed and only the structured findings tool remains. It produces root cause, evidence, remediation, and confidence fields. This is easier for the reporting stage to consume than an abruptly truncated conversation. It guarantees an output form and a stopping path, however, not sufficient evidence. A model-written confidence value is not automatically a calibrated probability.

Tool result size is also unbounded. Even with few calls, one broad log search can expand the context rapidly. The article emphasizes targeted queries over relevant logs rather than sampling; this does not mean that every relevant fact reaches the model. Query expressions, dataset selection, and result volume still determine visibility. Limiting calls, limiting data volume, and establishing evidence sufficiency are different budget problems.

## Separate report speed from diagnostic quality

The official article describes reports arriving in roughly one minute with Claude Sonnet 5 and default settings. This is a vendor usage description without an accompanying incident distribution, labeled root causes, or accuracy comparison. It supports the positioning of rapid investigation material, not a demonstrated reduction in production incident recovery time.

The final report turns structured findings into an account of the event, impact, likely causes, and next steps. A more useful operational check is whether each important conclusion leads back to a query, time interval, and concrete evidence, and whether missing evidence changes the recommendation. OpenTelemetry tracing helps inspect the call path. Trace completeness must still be reconciled with actual tool results; the model’s explanation alone cannot replace execution facts.

Another useful distinction is between a failed query and an absence of evidence. “No anomaly found” after a timeout is different from an empty result from a completed query. Evaluation should record failed calls, the datasets and intervals actually covered, and whether the report preserves those gaps. This helps distinguish a faster investigation from a report that conceals unfinished retrieval.

## Automatic triggers introduce lifecycle constraints

The current README gives concrete limits for automation. Webhook mode defaults to three concurrent investigations, deduplicates by monitor ID and window start, and returns 503 when busy so the caller can retry. Both active runs and deduplication state live in memory. It calls for one instance that remains running between requests. Interactive Slack investigations likewise do not survive restart, and an unanswered question ends its run after 15 minutes.

Adding replicas is consequently more than a throughput change: it changes the scope of deduplication, while restarts change whether an alert can enter investigation again. This follows directly from the storage boundary. Process-local deduplication is not exactly-once handling across restarts. Teams needing stronger reliability should first define acceptable duplicate reports, retry costs, and recovery ownership before extending persistence and queueing.

The implementation is a useful, inspectable AI SRE reference because it places search scope, confirmation, model budgets, and report production into explicit stages. Start with those four stages, then inspect budget semantics and deployment limits. It supplies a foundation for turning alerts into evidence reports; remediation effectiveness, diagnostic accuracy, and behavior during large alert storms still require separate evaluation.
