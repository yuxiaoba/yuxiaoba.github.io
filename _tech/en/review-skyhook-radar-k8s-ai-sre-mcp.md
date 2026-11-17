---
id: review-skyhook-radar-k8s-ai-sre-mcp
title: '2026-10-31 | Radar: Kubernetes Informer State Graph, Event Deduplication, and Constrained MCP Diagnostics'
date: '2026-10-31'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://github.com/skyhook-io/radar
tags:
- agent-reliability
- observability
- systems-reliability
permalink: /tech/en/review-skyhook-radar-k8s-ai-sre-mcp/
long_read: true
authorship: assistant
authoring_source: assistant
translation_source: assistant
updated_at: '2026-11-16T12:00:00+08:00'
summary: "Dissecting Radar's client-go informer cache, topology graph, event deduplication, noise-stripped diffs, and /mcp-readonly boundaries versus unconstrained kubectl loops."
---

Skyhook · Apache-2.0 single Go binary · [GitHub Repository & README](https://github.com/skyhook-io/radar) · [SREGym Benchmark Page (radarhq.io/benchmark)](https://radarhq.io/benchmark)

When an AI coding or SRE agent investigates a broken Kubernetes cluster through raw `kubectl`, the primary bottleneck is rarely reasoning syntax alone—it is context bloat and serial discovery round trips. **Radar**, an open-source single Go binary from Skyhook (running locally against your kubeconfig or in-cluster via Helm, listening on port `9280` by default), puts its web UI and built-in Model Context Protocol (MCP) server on top of one shared `client-go` informer state graph, deduplicated event feed, and stripped diff timeline.

> **Evidence & sibling-note boundary**: Architectural mechanisms and benchmark measurements in this note are grounded strictly in the frozen `skyhook-io/radar` repository README (`4.0k` stars / `268` forks at snapshot time), official MCP documentation (`docs/mcp.md`), and the three author-run SREGym benchmark studies on `radarhq.io/benchmark` (3-node Amazon EKS cluster scored by Claude Opus 5 on SREGym's rubric, **where fault sets, dates, and cluster loads differ across studies so arms are comparable within a study only**). Tool names, CLI flags, and study numbers are directly observed source facts; engineering trade-off analyses around context economics, local neighborhood traversal, and host-vs-endpoint isolation are assistant interpretations built on that evidence. For Radar's later November 5 SREGym end-to-end repair leaderboard (`90` faults / `270` runs / `95.2%` joint success with `kubectl` and `kubeconfig` removed), see the companion note [Radar on SREGym: connecting diagnosis and repair through structured context](/tech/en/radar-sregym-leaderboard/); this October 31 note focuses deeply on **Radar's internal state-graph cache, event/diff preprocessing, read-only MCP tool surface, and deployment boundaries**.

## Informer State Cache, Topology Linking, and the Shared UI/MCP Model

Stateless `kubectl` troubleshooting burns turns because Kubernetes splits causal chains across loosely coupled primitives. A stalled rollout can span a `Deployment`, `ReplicaSet`, `Pod`, `Service`, `EndpointSlice`, `ConfigMap`, `Ingress` or `HTTPRoute`, and GitOps reconcilers like Argo CD or Flux. Every `kubectl get`, `describe`, `events`, and `logs` invocation triggers a new API query and asks the LLM to rebuild `OwnerReferences` and label-selector edges inside its conversation history.

Radar replaces repeated discovery queries with `client-go` **Shared Informers** inside its single Go binary (`internal/k8s/`), maintaining an in-memory resource and relationship cache (`internal/k8s/cache.go`). Two structural properties follow from that choice. First, Radar needs **no cluster-side agents or custom CRDs**: locally it authenticates with `~/.kube/config`, while in-cluster Helm deployments enforce per-user Kubernetes RBAC via OIDC or auth-proxy impersonation. Second, one deterministic graph links built-in workloads, networking, storage, Helm releases, GitOps objects (Argo CD `Application`/`ApplicationSet`/`AppProject` and Flux `GitRepository`/`OCIRepository`/`HelmRepository`/`Kustomization`/`HelmRelease`), and auto-discovered CRDs (covering Karpenter, Gateway API, Knative, CloudNativePG, GPU/inference stacks, and more when served).

<figure class="note-figure">
  <a class="note-image-link" href="/assets/images/tech/review-skyhook-radar-k8s-ai-sre-mcp/radar-informer-topology-en.svg" target="_blank" rel="noopener">
    <img src="/assets/images/tech/review-skyhook-radar-k8s-ai-sre-mcp/radar-informer-topology-en.svg" alt="Radar architecture diagram: left column shows Kubernetes API Server streaming via client-go Shared Informers plus optional telemetry sources; center column shows Radar's internal/k8s memory core handling Topology and Ownership mapping, Event Dedup and ranked Issues, and Stripped Diff Timeline; right column shows dual Web UI (SSE and ELK.js) and MCP Server (/mcp-readonly vs /mcp) outputs; bottom strip highlights Secret .data withholding, regex scrubbing limits, cloud LLM provider egress, and local shell isolation." width="960" height="540" loading="lazy">
    <span class="note-image-action">Expand diagram ↗</span>
  </a>
  <figcaption>Assistant diagram (not an original figure): Radar's client-go informer cache, topology/timeline core, shared UI and MCP surfaces, and security boundaries.</figcaption>
</figure>

The central design thesis is **one shared cluster model** for both operators and agents. The React UI (updated over Server-Sent Events `SSE`, laid out via `@xyflow/react` and ELK.js, and paired with `44` cached Cluster Audit checks) reads the exact same health evaluations, owner links, and recent deltas exposed over MCP. When an engineer spots a failing workload in `Issues` and opens `Investigate`, the agent does not restart cluster discovery from raw manifests—it begins on the identical dependency slice.

## Event Deduplication, Noise-Stripped Diffs, and Timeline Retention

Graph connectivity solves spatial discovery, but incident debugging also fails along two temporal noise axes:

- **Warning storms and short native Event retention**: Pods stuck in `CrashLoopBackOff` or `ImagePullBackOff` repeatedly emit near-identical `Warning` events, while native Kubernetes `Event` objects typically expire after a default 1-hour TTL. Feeding raw event lists to an LLM fills prompt windows with duplicates, yet waiting too long after a failure or process restart erases native evidence entirely.
- **Server-assigned YAML bookkeeping hiding actual edits**: Raw `kubectl get -o yaml` comparisons bury genuine mutations—such as image tag bumps, replica changes, or GitOps drift—beneath bulky `metadata.managedFields`, `metadata.resourceVersion`, and `kubectl.kubernetes.io/last-applied-configuration` blocks alongside verbose status conditions.

Radar splits temporal cleanup across two complementary mechanisms. First, **event deduplication (`dedup`) and ranked `Issues`** fold repetitive warnings and surface concrete failures (crash loops, image pull errors, unschedulable pods, dangling service references, and failing Argo CD/Flux conditions) into severity-ordered summaries via `issues` and `get_events`. Second, **noise-stripped diffs and configurable timeline retention** (`get_changes` and Compare) strip `managedFields`, `resourceVersion`, and last-applied boilerplate so diffs isolate behavioral changes (while still allowing internal cues such as `managed_fields_mtime` without dumping full field-manager trees). By default, change history lives in memory (`--timeline-storage=memory`), but `--timeline-storage=sqlite` (with `--timeline-db` and `--timeline-max-size`) or `postgres` persists events and deltas across restarts and past Kubernetes's 1-hour event TTL.

As an observability trade-off, an informer-backed control-plane model surfaces **Kubernetes resource symptoms and spec drift**, not missing application-internal metrics or host-level failures—which explains why the remaining failures in the [November 6 SREGym leaderboard follow-up](/tech/en/radar-sregym-leaderboard/) clustered around Kafka internals and node/kubelet faults. Radar supplements control-plane state with optional Prometheus integration (`--prometheus-url`), Hubble/Istio/Caretta/Beyla traffic views, and explicit single-Pod evidence collection for RabbitMQ, NATS, and Vault—explicitly documented as point-in-time single-Pod snapshots requiring operator approval rather than automatic `Issues` triggers.

## Read-Only MCP Tool Surface vs. Unconstrained kubectl Context Economics

Rather than exposing `kubectl` inside an unrestricted `run_shell` wrapper, Radar structures its `internal/mcp/` interface into roughly 30 narrow, intent-scoped tools served over HTTP on port `9280`. The table below contrasts how raw `kubectl` discovery interacts with LLM context windows against Radar's `/mcp-readonly` surface:

| Diagnostic Stage | Unconstrained `kubectl` Loop | Radar Read-Only MCP (`/mcp-readonly`) | Impact on Context & Turns |
| :--- | :--- | :--- | :--- |
| **Fault Entry Point** | Repeated `get pods` / `get deploy` scans across namespaces to spot unhealthy states | `issues` or `get_dashboard` returns a ranked queue of broken workloads | Eliminates cluster-wide listing turns; enters directly at failing resources |
| **Dependency Traversal** | Serial `describe`, `get rs`, `get svc`, `get endpoints` calls stitched manually | `get_topology` or BFS-bounded `get_neighborhood` around a target object | Supplies upstream/downstream links without dumping unrelated cluster YAML |
| **Events & Warning Storms** | `get events` pulls un-deduplicated warnings limited by ~1h native TTL | `get_events` returns deduplicated events backed by persistent timeline storage | Stops crash-loop warning spam from crowding out earlier root-cause history |
| **Change & Drift Inspection** | Full `-o yaml` comparisons polluted by `managedFields` & `resourceVersion` | `get_changes` emits noise-stripped field diffs (replicas, images, config) | Focuses model attention on actionable spec drift instead of server metadata |
| **Logs & Secret Guardrails** | Raw `logs` tails; naive manifest reads risk leaking base64 Secret payloads | `get_pod_logs` supports error filtering/`grep`; Secret reads omit `.data`/`.stringData` | Trims log noise and withholds Secret fields before entering model prompts |
| **Bundled Evidence Capture** | 4–6 sequential CLI round trips replaying growing YAML context per turn | Single `diagnose` call bundles matching objects, neighborhood, events & logs | Compresses multi-turn context assembly (probe Pod creation disabled read-only) |

To measure the latency and accuracy impact of structured context, `radarhq.io/benchmark` publishes three author-run **SREGym** studies conducted on a **3-node Amazon EKS cluster** and scored uniformly by **Claude Opus 5** on SREGym's rubric (per-fault JSON datasets are downloadable):

<figure class="note-figure">
  <a class="note-image-link" href="/assets/images/tech/review-skyhook-radar-k8s-ai-sre-mcp/radar-mcp-context-budget-en.svg" target="_blank" rel="noopener">
    <img src="/assets/images/tech/review-skyhook-radar-k8s-ai-sre-mcp/radar-mcp-context-budget-en.svg" alt="Context economics and SREGym benchmark comparison diagram: top left illustrates Path A raw kubectl multi-turn polling with managedFields, resourceVersion, un-deduped events, and raw logs taking 191s mean in Study 01 and 249s in Study 02; top right illustrates Path B Radar /mcp-readonly using issues, get_neighborhood, get_changes, and get_pod_logs taking 64s mean (about 3x faster, 86% within 2 minutes) in Study 01 and 57s in Study 02; bottom panel summarizes Study 01, Study 02, and Study 03 metrics with an explicit warning against cross-study ranking and a pointer to the Nov 6 90-fault/270-run leaderboard note." width="960" height="540" loading="lazy">
    <span class="note-image-action">Expand diagram ↗</span>
  </a>
  <figcaption>Assistant diagram (not an original figure): Contrast between serial raw kubectl loops and Radar's graph-scoped MCP surface alongside the three SREGym study metrics.</figcaption>
</figure>

| Study & Question | Scope & Controlled Variables | Reported Measurements (Within-Study Only) | Methodological Scope & Caveats |
| :--- | :--- | :--- | :--- |
| **Study 01 · Tool Control** | `50` SREGym faults; **same agent and same model** swapping only Radar MCP vs. raw `kubectl` | Mean time to diagnosis **64s vs. 191s** (~3x faster); diagnosed correctly within two minutes **86% vs. 60%** | Timing averages **all submitted answers (right or wrong)**—it is not mean time to repair |
| **Study 02 · 6-Arm MCP Speed** | `25` faults; one agent driving 5 Kubernetes MCP servers and raw `kubectl` | Radar **57s** vs. Flux159 **135s** (2.3x faster than next-best), `containers/kubernetes-mcp-server` 149s, `k8sgpt` 174s, `kubectl` 249s, Amazon EKS MCP 321s | Across the **14 faults** every arm solved, Radar took **33s vs. 58s** for next-fastest |
| **Study 03 · 6 AI SRE Tools** | `50` faults; Claude Code + Radar MCP vs. 5 full products (all using Claude Sonnet 5 via Bedrock except AWS DevOps Agent's proprietary stack) | Claude Code + Radar MCP **44/50 (88%), 79s, `$0.27`/fault**; `kubectl-ai` 41/50 (82%, 288s, `$1.67`); HolmesGPT/OpenSRE/kagent 38/50 (76%, 151–181s, `$0.37`–`$2.26`); AWS DevOps Agent 33/50 (66%, 123s, `$1.27`) | Compares **complete agent harnesses, prompts, and tools together**; cannot isolate MCP alone |

Comparing Study 01 and Study 03 clarifies the attribution picture: holding agent and model fixed in Study 01 isolates a threefold reduction in average time to answer (`191s` down to `64s`) from pre-correlated context alone, whereas Study 03 bundles Claude Code's harness with Radar MCP against independent products. Because fault subsets, dates, and cluster background loads differ across the three studies, the authors explicitly warn against ranking numbers across tables—and faster answers still differ from authorized, verified recovery, which is tested separately in the [November 6 SREGym 90-fault / 270-run repair study](/tech/en/radar-sregym-leaderboard/).

## Read-Only Boundaries, Secret Scrubbing, and Agent Isolation Pitfalls

Running an MCP server inside a local dashboard on port `9280` creates subtle operational gaps if teams confuse **"connecting to `/mcp-readonly`"** with **"full process sandboxing."** Checking Radar's startup flags and MCP security notes highlights four boundaries that require explicit enforcement:

1. **Dual default endpoints vs. server-wide read-only locks**: Both `/mcp-readonly` and the full `/mcp` endpoint (which adds `patch_resource`, `apply_resource`, restart, scale, rollback, GitOps sync, node drain marked destructive, and `diagnose` in-cluster probe Pods) are enabled by default. Passing `--mcp-read-only` (or `RADAR_MCP_READ_ONLY=1` / `"mcpReadOnly": true`) shuts off `/mcp` (`404` response) and blocks applying fixes from AI investigations; `--no-mcp` disables MCP and AI investigations altogether. Crucially, the README explicitly notes that **neither flag blocks ordinary UI writes**.
2. **Endpoint `/mcp-readonly` does not disable an agent's shell or sibling MCPs**: Pointing an MCP client at `http://localhost:9280/mcp-readonly` restricts only Radar's tools—not an agent's local `shell`, `kubectl`, or other configured MCP servers. Radar's built-in `AI investigations` (`radar diagnose deploy/checkout -n shop --json > conclusion.json`) therefore distinguish two execution modes: **mode `Radar safeguards`** (Claude Code and Codex) disables the agent's other MCP servers and write access during investigation, whereas **mode `Your agent setup`** (the only mode for Cursor and OpenCode) runs the agent with its normal tools and MCP servers—where Cursor and OpenCode **auto-approve tool requests without asking** and Radar cannot constrain them. Built-in investigations also require MCP enabled and authentication disabled, so in-cluster deployments do not run them.
3. **Secret withholding vs. incomplete pattern scrubbing**: Structured `Secret` reads never include `.data` or `.stringData` (exposing names only), and environment variables, Helm values, and logs are scrubbed for known secret patterns. Pattern matching lowers exposure risk without guaranteeing every custom token is caught, and the opt-in `exec_pod` tool (controllable via `--disable-exec`) returns raw command output.
4. **"Local binary" does not mean "zero external model egress"**: Radar itself stores cluster state locally and sends nothing to Skyhook (anonymous usage telemetry is opt-in only and excludes resource payloads). Yet **any cloud LLM agent connected over MCP receives every minified topology slice, diff, and scrubbed log it queries and transmits those payloads to its own model provider**. In regulated or air-gapped environments, pairing Radar with local/private model endpoints, `--namespace-scope`, and least-privilege `kubeconfig` or RBAC impersonation is what actually enforces the data perimeter.

---

> **Provenance**: Rewritten and expanded by the assistant from frozen `skyhook-io/radar` repository documentation, `radarhq.io/benchmark` evidence, and `docs/mcp.md` (`authoring_source: assistant`, `translation_source: assistant`), retaining original `id`, `date`, `permalink`, and topic tags (`agent-reliability`, `observability`, `systems-reliability`). Both figures (`radar-informer-topology-en.svg` and `radar-mcp-context-budget-en.svg`) are assistant-authored `v3-blue` diagrams summarizing source mechanisms and author-reported benchmark numbers without inventing unmeasured token percentages.
