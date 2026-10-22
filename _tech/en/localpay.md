---
id: localpay
title: '2026-10-21 | LocalPay: Making Payment Failures Repeatable Locally'
date: '2026-10-21'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
- observability
summary: How state machines, an event log, an injectable clock, and webhook faults
  work together, with the limits of compatibility not yet validated against real recordings.
long_read: true
source_url: https://github.com/karthikrshet/localpay
permalink: /tech/en/localpay/
authorship: assistant
translation_source: assistant
published_at: "2026-10-21T13:08:08.256303+08:00"
updated_at: "2026-10-21T13:08:08.256303+08:00"
---
Karthik Rajesh Shet (karthikrshet) · Repository created 2026-10-19; author announcement 2026-10-20  
Primary source: [LocalPay](https://github.com/karthikrshet/localpay) · [Compatibility matrix](https://github.com/karthikrshet/localpay/blob/main/docs/compat.md)

The hardest payment paths to test often involve bank failures, authorization arriving after a timeout, and duplicated or reordered webhooks rather than a successful order. Waiting for these events in an external environment is slow and difficult to reproduce. LocalPay turns them into controlled local inputs: an application calls Razorpay-shaped APIs, the emulator drives payment state, and signed events reach a local business endpoint.

Its value is a shorter feedback loop for failures, not a real payment network. The repository is pre-1.0. Its compatibility matrix explicitly says no fixtures have yet been recorded from a real test account, so API and event behavior remains partial. It is useful as an example of combining local emulation with fault injection, not as a verified gateway-equivalent implementation.

## One state engine connects APIs, UI, and events

Commands drive state machines for orders, payments, refunds, subscriptions, and related objects. Changes append to an event log. The REST provider handles validation, response shapes, and signature conventions; the webhook dispatcher translates events into notifications; the dashboard displays the same state. Persistence and replay also use the log instead of allowing several modules to maintain independent versions of reality.

A typical interaction creates an order, opens a test checkout, and selects a successful or failed scenario. Payments move through applicable created, authorized, captured, refunded, or failed states and produce callbacks and webhooks. A successful browser popup and server-side confirmation are different events; the emulator makes that distinction testable.

An injectable clock controls refund processing, link expiry, subscription renewal, and settlement. Advancing time triggers due events without waiting days. Seeded IDs and fixed inputs help make expectations repeatable. This is appropriate for state transitions and ordering, rather than a realistic latency model for a distributed payment service.

## Inject faults at consumer boundaries

The webhook layer supports duplicates, reordering, delay, missing signatures, retries, delivery logs, and replay. The REST layer can inject rate limits, server errors, and API delay. These exercise separate responsibilities: event consumers handle repeated or stale notifications, while request senders decide how to interpret failures and retry.

<a class="note-image-link" href="/assets/images/tech/localpay/webhooks.png" target="_blank" rel="noopener" aria-label="The official dashboard expands a webhook with its content and delivery history, alongside controls for replay, duplicate delivery, and sending without a signature. · View original image ↗"><img src="/assets/images/tech/localpay/webhooks.png" alt="The official dashboard expands a webhook with its content and delivery history, alongside controls for replay, duplicate delivery, and sending without a signature." loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*The official dashboard expands a webhook with its content and delivery history, alongside controls for replay, duplicate delivery, and sending without a signature.*

For example, after payment.captured causes a business action, receiving it again should ordinarily avoid repeating that effect. An older event should not casually roll back newer local state. These are test goals one can construct with the emulator, not properties the README proves for every application. Missing signatures provide a specific rejection case for checking that consumers actually verify notifications.

Late UPI authorization is particularly useful: a client timeout does not necessarily end the payment lifecycle. If the application immediately creates another payment, a later success exposes the need to correlate orders and payments. LocalPay supplies a controlled scenario, but production gateway behavior for competing payments must be checked independently rather than inferred from emulator rules.

## Turn manual scenarios into regression cases

The repository includes 15 YAML scenarios covering timeout/retry, authorization without capture, partial refunds, failed renewals, and late authorization. They can assert event presence and payment counts by state. Recorded webhook sessions can also be replayed after handler changes.

Useful system assertions concern business invariants: one payment should not trigger duplicate fulfillment, refunds should not exceed paid amounts, and invalid transitions should not silently succeed. The project uses property tests for related monetary-state constraints. Keeping rapid local tests separate from real-environment contract fixtures avoids a closed loop in which emulator and tests share the same mistake.

Node.js uses a shim to redirect the SDK; Python exposes a base_url option. The matrix marks connection integration for Node 2.9.8 and Python 2.0.1 as supported, while PHP, Java, and Go remain unchecked. SDK connection support does not upgrade all API fields or webhook semantics from partial to supported.

## Concrete differences matter more than coverage alone

The emulator retries webhooks five times: immediately, after 5 seconds, 30 seconds, 2 minutes, and 10 minutes. The real gateway retries longer. first_payment_min_amount is accepted but not enforced, some expand parameters are ignored, and subscription pause/resume is missing. Actual rate-limit quotas are not modeled; 429 responses are fault-driven. Tests should account for the specific interfaces they use.

The README reports more than 500 unit, contract, and property tests and approximately 98.7% line coverage for core and provider code. Those describe project self-testing, not compatibility established with real recordings, which the matrix explicitly says are absent. No controlled result establishes a reduction in production incidents, so feature availability should not be converted into a reliability percentage.

## Distinguish a failure from a repeated observation

An event log clarifies three different records: a payment-state change, a notification delivery attempt, and a business side effect. One captured event may be delivered repeatedly, with different HTTP outcomes. The consumer's idempotency rules determine whether an action should occur. Merely asserting an HTTP 200 can miss both duplicate fulfillment and an acknowledged event that never updates the order.

A local tool can replay different delivery orders from the same initial state. For example, deliver success, replay an older message, and compare final order state and side-effect counts. This is a test-design inference from the provided replay feature, not an author-reported experiment. Change delivery while holding payment facts fixed to distinguish handling a new state from reacting repeatedly to the same fact.

This also explains why real fixtures are a substantive next step. The local state machine supplies controlled causal sequences; recordings supply external protocol details. Connecting them prevents broad failure coverage from concealing semantic incompatibility.

Localhost-only defaults, rejection of live keys, and a checkout without real card-entry fields reduce confusion between emulation and production. A useful workflow places repeatable failures in regression tests and confirms critical contracts in the real test environment. The development worth following is the combination of state machines, events, virtual time, and consumer-side faults in one lightweight tool. Real fixtures and documented semantic differences are more meaningful next steps than simply expanding the feature list.
