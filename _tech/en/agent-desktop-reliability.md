---
id: agent-desktop-reliability
title: '2026-11-02 | agent-desktop: Identity and Retry Evidence for Desktop Actions'
date: '2026-11-02'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- agent-reliability
- observability
- systems-reliability
summary: Accessibility trees, snapshot references, delivery states and postcondition
  checks make desktop-action uncertainty explicit.
translation_source: assistant-authored Chinese and English paired content
long_read: true
source_url: https://github.com/vercel-labs/agent-desktop
permalink: /tech/en/agent-desktop-reliability/
published_at: '2026-11-02T08:39:51.033336+08:00'
updated_at: '2026-11-02T08:39:51.033336+08:00'
---

A desktop agent can fail by acting on a target that changed after observation, or by retrying an input that already reached the application. Vercel Labs' agent-desktop makes these concerns part of the tool interface: observe through OS accessibility trees, act through identity-bearing references, and report delivery, verification and retry safety separately.

Original project: [agent-desktop](https://github.com/vercel-labs/agent-desktop) · Vercel Labs; introduced by Chris Tate on [2026-10-31](https://x.com/ctatedev/status/2116323148706771302). The mechanisms below follow the project's 2026-11-01 documentation snapshot and JSON output contract 2.5.

## What the accessibility tree supplies

The Rust CLI and C library support macOS, Windows and Linux. They read the structure applications expose to the OS: windows, roles, accessible names, states and available actions. An agent receives a JSON snapshot, selects a reference, acts and observes again. The planning loop remains in the calling agent.

This reduces the need to infer button positions from pixels, but depends on the application's actual accessibility evidence. Missing semantic actions, incomplete reads and platform limitations remain interface boundaries. Screenshots and explicitly authorized physical input are also supported; the project does not establish that every application can dispense with coordinates.

The concepts document distinguishes known absence, known presence and unknown evidence. A failed read must not become an absent property, or an incomplete observation could appear complete. The output contract requires checking `data.complete`: an ordinary snapshot that exhausts its budget may return `ok: true` with a partial tree, `complete: false` and `truncated: true`. A caller checking only the success flag could mistake unobserved content for absent content.

## References belong to snapshots

A reference such as `@s8f3k2p9:e8` identifies both a snapshot and an element; bare `@e8` is rejected. References are deterministic within a snapshot, not guaranteed stable across UI changes. Before acting, the tool re-identifies the live element using stored identity evidence. Missing, stale or ambiguous matches produce structured errors instead of a best guess.

Resolution uses a hierarchy of paths, native identifiers, stable text and restricted geometry. Each tier locates candidates rather than proving identity by itself. Mutable text-field values cannot independently identify a control. Window handles can also be recycled, so process-generation evidence helps prevent an old handle from resolving to a different window.

On macOS, a command host retains native accessibility objects to stop a deleted row from silently becoming another row with the same identifier. These designs address changes between observation and mutation. For a scheduler, a `STALE_REF` calls for fresh observation and a new reference, rather than repeated dispatch of the old command.

## Background semantics and physical input have boundaries

Default headless reference actions use semantic accessibility APIs without implicitly taking focus or moving the pointer. An unavailable semantic path fails closed. `--headed` explicitly permits the relevant physical-input behavior. Background operation does not mean a server without a graphical session: Linux still needs a user graphical session and AT-SPI, with differing X11 and Wayland capabilities.

Actionability checks cover visibility, stability, enabled state, supported actions and policy. Bounded waiting defaults to 5,000 ms, with a per-character addition for `type`. Temporary conditions can be polled, while terminal restrictions such as policy denial fail promptly. An interaction lease serializes shared input at dispatch, after waiting; targets observed before the lease are re-resolved once it is held.

Multiple agent cursors in a demonstration therefore do not imply independent simultaneous physical pointers. The cursor is presentation; shared desktop input still requires coordination. For physical actions, the final target window and focus matter as much as the initial snapshot.

## Retry follows delivery evidence

The JSON contract puts `delivery` and `retry` in `disposition`, adding essential semantics beyond a success flag:

| State | Meaning | Automatic retry |
| --- | --- | --- |
| `not_delivered` | Not delivered; for some operations, the desired state was already satisfied | `safe` |
| `delivered_unverified` | Dispatched without independent confirmation of effect | `unsafe` |
| `delivered_verified` | Readback confirmed the named postcondition scope | `unsafe` |
| `delivery_uncertain` / `unknown` | Uncertain delivery / no established delivery evidence | Do not retry automatically |

`ok: true` can mean dispatch completed, not that application data was persisted. Even a matching control readback does not prove that a remote service saved the change. Conversely, an unchanged control after an error does not prove non-delivery. Switching to another click or typing mechanism can duplicate side effects.

Contract 2.5 removes unconditional flags such as `clicked` and `moved`, replacing them with target, steps, disposition and verification scope. Window position and size checks identify their tolerance and units. A caller can distinguish sent input, verified control state and completed business goals. The last still needs application-level evidence.

## Follow the contract, not a success-rate slogan

The documentation offers an inspectable design, but no unified task-success comparison against screenshot agents. It therefore does not establish universal speed or reliability gains. Platform adapters are asymmetric: strict-headless `type` on Windows lacks a semantic insertion path, while `set-value` provides text assignment; some Linux window and mouse operations depend on X11.

For AgentOps, the transferable idea is to record observation completeness, identity validity, delivery and postcondition verification separately. Failures can then be attributed to incomplete observation, a changed target, a restricted action, an unknown result or an unfinished business operation, instead of one generic tool-failure category. Start with the official [JSON output contract](https://github.com/vercel-labs/agent-desktop/blob/9eb9b296192fcb70bda25e918cd6dd66abfa3d0d/docs/json-output.md), followed by references, identity and action reliability in [CONCEPTS.md](https://github.com/vercel-labs/agent-desktop/blob/9eb9b296192fcb70bda25e918cd6dd66abfa3d0d/CONCEPTS.md).
