---
tech_deep_read: true
id: llamacpp-kv-fallback
title: '2026-11-04 | Silent CPU Fallback on Quantized KV Caches: Dispatch Root Cause, Benchmarks, and Gates in llama.cpp #28455'
date: '2026-11-04'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://github.com/ggml-org/llama.cpp/issues/28455
source_published_at: '2026-09-05'
long_read: true
tags:
- inference-serving
- systems-reliability
- observability
summary: 'Dissects llama.cpp Issue #28455 where FlashAttention (-fa on) with q5_1/q4_1 or mixed K/V caches silently falls back to CPU under default builds, bounding the RTX 4080 benchmark numbers, numerical-perplexity confounding, and observability gates.'
authoring_source: assistant
translation_source: assistant
permalink: /tech/en/llamacpp-kv-fallback/
updated_at: '2026-11-17T10:00:00+08:00'
---
Reporter: `AhBumm` · Opened 2026-09-05 (closed 2026-09-06) · [GitHub Issue #28455](https://github.com/ggml-org/llama.cpp/issues/28455) · Key thread comments: `@sinanezhadian` ([Comment #1](https://github.com/ggml-org/llama.cpp/issues/28455#issuecomment-5554868313)), `@JohannesGaessler` (maintainer, [Comment #2](https://github.com/ggml-org/llama.cpp/issues/28455#issuecomment-5558436618))

You launch `llama-server` with `-ngl 99 -fa on`, and `llama-bench` dutifully prints `fa=1 q5_1` in its results table—yet on a 3.6K-token prompt, time to first token (TTFT) stretches from roughly `3 s` to `~95 s`, GPU utilization drops to `0%` (`~62 W`), and host CPU usage spikes to `~930%`. This `ggml-org/llama.cpp` issue exposes a sharp gap between configuration surfaces and runtime reality: **CLI flags and benchmark headers document what you requested, not which device actually executed the attention operator**.

> **Evidence Boundary & Source Provenance**: This note is grounded strictly in the frozen capture of [GitHub Issue #28455](https://github.com/ggml-org/llama.cpp/issues/28455) (`bug-unconfirmed` label, `closed / completed`). Three scope constraints apply: **(1) Thread governance context**: the issue body is prefixed `(USER WAS BANNED FOR THIS POST)`, and on 2026-09-06 maintainer `@JohannesGaessler` banned the author and closed the ticket under llama.cpp's [AI usage policy](https://github.com/ggml-org/llama.cpp/blob/master/CONTRIBUTING.md#ai-usage-policy) prohibiting AI-authored posts—while simultaneously confirming **"This is a known issue."**, verifying the underlying fallback behavior as real; **(2) Single-machine empirical basis**: all `llama-bench`, `llama-server`, and `top`/`nvidia-smi` figures come from one Ubuntu 24.04 RTX 4080 machine (`0.3.0-dev` `b10791` / commit `95ef7fc16`, `27B` Q5_K model) across configurations and one rebuild rather than a multi-GPU suite (an inconsistent social post in the original raw inbox with different hardware and speedups remains omitted); and **(3) Unmeasured numerical delta**: `@sinanezhadian`'s perplexity-confounding warning and citation of [arXiv:2605.19537](https://arxiv.org/abs/2605.19537) isolate a valid mechanism, but no one executed `llama-perplexity` on the two `q5_1` builds in the thread.

## Dispatch Root Cause: Why Default CUDA Builds Silently Route Quantized KV Attention to CPU

Tracing `ggml/src/ggml-cuda/fattn.cu` on `0.3.0-dev` (`build 10791`, commit `95ef7fc16`—and reported as unchanged on `master` `6a1a922d2` / `b10819` at filing time), the issue attributes the collapse not to a single recent commit regression, but to the intersection of **default compile-time kernel exclusion** and **silent scheduler fallback**:

1. **Narrow default vec-kernel instantiation**: With `GGML_CUDA_FA_ALL_QUANTS=OFF` (the default build), `FATTN_VEC_CASES_ALL_D` in `fattn.cu` compiles FlashAttention vector kernels only for four homogeneous `(K, V)` pairs: `(GGML_TYPE_F16, GGML_TYPE_F16)`, `(GGML_TYPE_Q4_0, GGML_TYPE_Q4_0)`, `(GGML_TYPE_Q8_0, GGML_TYPE_Q8_0)`, and `(GGML_TYPE_BF16, GGML_TYPE_BF16)`.
2. **`supported()` and `get_best_fattn_kernel()` reject quantized and mixed pairs**: Unless `GGML_CUDA_FA_ALL_QUANTS` is defined, `ggml_cuda_fattn_kv_type_supported()` returns `false` for `Q4_1`, `Q5_0`, `Q5_1`, and unsupported mixed `K/V` pairs, causing `get_best_fattn_kernel()` to return `BEST_FATTN_KERNEL_NONE`. Meanwhile, the tile FlashAttention kernel reads `K/V` strictly as `half2`, so it cannot accept quantized KV caches either.
3. **Silent CPU assignment across every layer and step**: Once the CUDA backend rejects `GGML_OP_FLASH_ATTN_EXT`, the `ggml` scheduler assigns `GGML_OP_FLASH_ATTN_EXT` to the **CPU backend**—for every layer and every inference step—emitting **zero warnings and zero errors** in the console.
4. **Disabling FlashAttention (`-fa 0`) offers no GPU escape hatch for quantized `V`**: As the report notes, running `-fa 0` with quantized `V` fails outright because the non-FlashAttention path requires a transposeable `f16` `V` cache. Without rebuilding with `GGML_CUDA_FA_ALL_QUANTS=ON`, types such as `q5_1` `V` therefore have **no working GPU path at all**: `-fa 1` (`-fa on`) silently moves attention to CPU, while `-fa 0` errors out.

<figure class="note-figure">
  <a class="note-image-link" href="/assets/images/tech/llamacpp-kv-fallback/ggml-fa-quant-dispatch-fallback-en.svg" target="_blank" rel="noopener" aria-label="Enlarge llama.cpp quantized KV cache silent CPU fallback dispatch and K/V isolation diagram">
    <img src="/assets/images/tech/llamacpp-kv-fallback/ggml-fa-quant-dispatch-fallback-en.svg" alt="Assistant diagram of llama.cpp Issue 28455 dispatch and K/V isolation: top row traces -ngl 99 -fa on with q5_1 KV through fattn.cu default compile set (homogeneous F16, BF16, Q4_0, Q8_0 only) to CUDA rejection and silent ggml CPU scheduling (0 percent GPU, about 930 percent CPU, 38.4 t/s on 3.6K prompt), contrasted with GGML_CUDA_FA_ALL_QUANTS=ON recovery (1509.70 t/s pp512); bottom left explains why -fa 0 fails outright on quantized V (requires transposeable f16 V), and bottom right bars plot the six llama-bench pp512 K/V configurations showing every V=q5_1 row falling to 190 to 197 t/s." width="960" height="540" loading="lazy">
    <span class="note-image-action">Click to zoom ↗</span>
  </a>
  <figcaption>Assistant diagram (not an original figure): Tracing the fattn.cu compile guard, ggml silent CPU dispatch, blocked -fa 0 fallback, and six-way K/V isolation results from Issue #28455.</figcaption>
</figure>

This single dispatch gate also explains the cluster of related issues cross-referenced inside `#28455`: `#24403` previously consolidated the checks into `supported()`; `#27109` reported `q4_1` prefill collapse on `qwen35` hybrid (RTX 3090) while `q4_0` worked because `Q4_1` sits in the exact `return false` branch alongside `Q5_0`/`Q5_1`; `#20866` hit the same matrix for mixed `K/V` GPU offloading; `#27905` triggered fatal FlashAttention errors over RPC on those uncompiled types; and `#24485` (proposing `GGML_CUDA_FA_ALL_QUANTS` by default or a runtime warning) closed stale, leaving users exposed.

From a build-engineering standpoint (assistant architectural analysis rather than an empirical test in `#28455`), keeping `GGML_CUDA_FA_ALL_QUANTS=OFF` by default reflects a real compile-time and binary-size trade-off across combinatorial `(K, V)` types and head dimensions. The reliability failure is not that default builds omit niche kernels—it is that **the CLI help, parser, and docs advertise `-ctk`/`-ctv` formats that a default binary neither runs on GPU nor rejects loudly**.

## Benchmarks and Length Amplification: Isolating K/V Pairs, Rebuilds, and Context Scaling

To rule out the assumption that `q5_1` math is inherently slow, the reporter ran four measurements on the same Ubuntu 24.04 RTX 4080 (`CMAKE_CUDA_ARCHITECTURES=89`) workstation, separating build configuration, `K/V` asymmetry, and telemetry fingerprints:

- **K/V isolation matrix shows strong `V`-side sensitivity**: In `llama-bench` (`pp512`, `-ngl 99 -fa 1 -t 12`, `qwen35 27B Q5_K_XL`), homogeneous `q8_0 / q8_0` achieved `1511.92 t/s`. Every uncompiled `q5_1` or mixed combination dropped sharply, with a clear empirical split across the reported rows (assistant reading of the published matrix): whenever **`V` was `q5_1`** (`q8_0 / q5_1` at `197.05 t/s`, `q5_1 / q5_1` at `196.62 t/s`, `f16 / q5_1` at `190.36 t/s`), `pp512` clustered at `190–197 t/s` (`7.7×–7.9×` slower); whenever **`K` was `q5_1` with `V` in `q8_0` or `f16`**, throughput landed at `427.61 t/s` (`3.5×` slower) and `483.14 t/s` (`3.1×` slower). Throughout, `llama-bench` still printed `fa=1 q5_1` in its results table even while timing CPU attention plus host-device transfers.
- **Controlled rebuild restores `q5_1 / q5_1` to GPU parity**: On `llama-bench` (`qwen35 27B Q5_K - Medium`, concurrency `1`) holding model, GPU, and `q5_1 / q5_1` flags constant, the default build (`ALL_QUANTS=OFF`) produced `pp512 = 197.15 t/s` and `tg128 = 25.98 t/s`. Rebuilding with `-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89 -DGGML_CUDA_FA_ALL_QUANTS=ON` raised `pp512` to `1509.70 t/s` (~`7.66×` recovery, virtually matching `q8_0 / q8_0`'s `1511.92 t/s`) and `tg128` to `30.55 t/s`—while using ~`60%` less KV VRAM than `q8_0` per the reporter's estimate.
- **Hardware telemetry gives an unmistakable fingerprint**: During `pp512` with `q5_1` KV, `nvidia-smi` / `top` showed **`0%` GPU utilization** (`~62 W` GPU power) alongside **`~930%` CPU utilization** (saturating 9+ cores). An identical run with `q8_0` KV held GPU utilization at `≥ 30%` and single-digit CPU percentage—consistent with GPU-to-host KV copies feeding CPU attention.
- **Longer prompts amplify CPU attention into a `~30×–35×` `llama-server` collapse**: On a `3.6K`-token prompt (`128` generated tokens, `llama-server` launched with `-c 131072 -np 4 --spec-type draft-mtp --spec-draft-n-max 3`), default-build `q5_1` slowed to **`38.4 t/s`** prompt eval (`6.5 t/s` decode), inflating a `~3 s` TTFT to **`~95 s`**. On the same machine, default `q8_0` reached `1348 t/s` (`30.1 t/s` decode) and the `GGML_CUDA_FA_ALL_QUANTS=ON` `q5_1` rebuild reached `1162 t/s` (`38.5 t/s` decode). Because CPU attention cost grows with KV length, short `pp512` runs hide the worst of a regression that easily masquerades as "long context overwhelms my GPU" in production serving.

| Tool & Workload Setup | Build Flag & K/V Types | Reported Throughput & Telemetry | Relative Gap & Validity Boundary |
| :--- | :--- | :--- | :--- |
| **`llama-bench` `pp512` (`qwen35 27B Q5_K_XL`)** | Default `OFF` · `q8_0 / q8_0` | `1511.92 t/s`; GPU `≥30%`, CPU single-digit % | `1.0×` GPU FA baseline on reporter's RTX 4080 |
| **`llama-bench` `pp512` (`K=q5_1` mixed pairs)** | Default `OFF` · `q5_1 / f16` & `q5_1 / q8_0` | `483.14 t/s` & `427.61 t/s` | `3.1×` & `3.5×` slower; table still prints `fa=1` |
| **`llama-bench` `pp512` (`V=q5_1` trio)** | Default `OFF` · `q8_0/q5_1`, `q5_1/q5_1`, `f16/q5_1` | `197.05`, `196.62`, `190.36 t/s`; GPU `0%` (`~62 W`), CPU `~930%` | `7.7×–7.9×` slower across all `V=q5_1` configs |
| **`llama-bench` same-KV rebuild (`27B Q5_K - Medium`)** | Default `OFF` vs `ALL_QUANTS=ON` (`q5_1 / q5_1`) | `pp512`: `197.15` → `1509.70 t/s`; `tg128`: `25.98` → `30.55 t/s` | Pure backend swap with model, GPU & KV type fixed (~`7.66×` gain) |
| **`llama-server` long prompt (`3.6K` in, `128` gen)** | Default `OFF` `q5_1` vs `q8_0` vs Rebuild `ON` `q5_1` | Prompt `38.4` vs `1348` vs `1162 t/s`; decode `6.5` vs `30.1` vs `38.5 t/s` | `q5_1` default stretches TTFT from `~3 s` to `~95 s`; includes `-np 4` & `draft-mtp` |

Keep the validity boundary sharp: all five rows come from one RTX 4080 machine and one `27B` model, and the `llama-server` comparison spans both a KV change (`q5_1` vs `q8_0`) and a rebuild (`1162` vs `38.4 t/s`). Do not generalize `~30×–35×` as a universal multiplier across every GPU and context length; the transferable engineering behavior is that silent CPU fallback scales adversely with sequence length and masks itself behind GPU-looking flags.

## The Second-Order Hazard: Numerical Drift and Confounded KV-Quantization Benchmarks

While slowdowns eventually show up in latency histograms, `@sinanezhadian`'s [Comment #1](https://github.com/ggml-org/llama.cpp/issues/28455#issuecomment-5554868313) reveals a subtler second-order failure: **silent CPU fallback alters numerical outputs, not merely execution speed**.

That argument breaks into three distinct points:

- **Different reduction orders yield different logits**: CPU FlashAttention and CUDA FlashAttention kernels accumulate floating-point sums in different orders. Consequently, a default CUDA build running `-ctk q5_1 -ctv q5_1` produces **different logits** from the same binary at `q8_0` (or from a GPU-compiled `q5_1` build)—it is not just producing the same numbers more slowly.
- **KV quantization perplexity tables become confounded**: Any practitioner ranking KV cache formats (`q4_0`, `q4_1`, `q5_0`, `q5_1`, `q8_0`) by perplexity on a default CUDA build inadvertently ran `q4_0` and `q8_0` on the **CUDA GPU backend** while running `q4_1`, `q5_0`, and `q5_1` on the **CPU backend**. What looks like a pure measurement of *"how much quality does this KV bit-width cost?"* actually mixes **quantization error with a CPU-versus-CUDA backend swap**.
- **An ideal zero-confound control exists, though perplexity remains unrun**: `@sinanezhadian` observes that `#28455`'s two `q5_1 / q5_1` binaries (`GGML_CUDA_FA_ALL_QUANTS=OFF` at `197.15 t/s` vs `ON` at `1509.70 t/s`) hold model weights, GPU, and KV quantization format identical while changing **only** the attention backend—so running `llama-perplexity` on both binaries isolates pure backend divergence for free. Crucially, **no one posted `llama-perplexity` measurements before `#28455` was closed**, so the actual perplexity delta in `llama.cpp` remains an unexecuted empirical check.

To illustrate why unlogged backend switches deserve scrutiny, `@sinanezhadian` cites [arXiv:2605.19537](https://arxiv.org/abs/2605.19537) (*The Silent Hyperparameter: Quantifying the Impact of Inference Backends on LLM Reproducibility* by David Pape, Jonathan Evertz, and Lea Schönherr), where holding weights, decoding parameters, and hardware fixed across five inference engines shifted benchmark scores by **up to 16.6 points**. Following `@sinanezhadian`'s explicit disclaimer, that cross-engine figure operates at a different scale and **must be read as motivation to measure, not a prediction for `llama.cpp` `q5_1` perplexity**. Even so, because `llama-bench` prints `fa=1 q5_1` for both CPU fallback and GPU FA paths, it mislabels the **numerical configuration** as well as throughput—meaning warnings belong directly in result tables, not tucked solely behind `--verbose`.

## Observability and Engineering Gates: Catching Silent Backend Fallback Before Serving or Benchmarking

Synthesizing the three upstream fixes proposed in `#28455`, `@sinanezhadian`'s table-labeling critique, and practical inference-serving safeguards yields four defense-in-depth gates:

<figure class="note-figure">
  <a class="note-image-link" href="/assets/images/tech/llamacpp-kv-fallback/silent-fallback-diagnostic-gates-en.svg" target="_blank" rel="noopener" aria-label="Enlarge numerical confounding and four-layer silent-fallback gates diagram">
    <img src="/assets/images/tech/llamacpp-kv-fallback/silent-fallback-diagnostic-gates-en.svg" alt="Assistant diagram of numerical confounding and four-layer fallback gates: top left illustrates default CUDA builds running q4_0 and q8_0 on GPU while routing q4_1, q5_0, and q5_1 silently to CPU, confounding KV perplexity comparisons under identical fa=1 labels; top right maps Issue 28455's controlled q5_1 pair (unrun llama-perplexity check) and arXiv 2605.19537's up-to-16.6-point cross-engine shift; middle four cards detail build contract, loud fallback warnings, honest benchmark table output, and telemetry plus CI smoke gates; bottom bar records the 2026-09-06 issue closure and AI-policy ban." width="960" height="540" loading="lazy">
    <span class="note-image-action">Click to zoom ↗</span>
  </a>
  <figcaption>Assistant diagram (not an original figure): Connecting the thread's numerical-confounding critique and arXiv scale context to four engineering gates across build, runtime, evaluation, and CI.</figcaption>
</figure>

| Gate Layer & Stage | Failure Exposed by Silent Fallback | Source Attribution & Scope | Actionable Engineering Control |
| :--- | :--- | :--- | :--- |
| **1. Build & Flag Contract** | CLI help, docs, and parser accept `q4_1`/`q5_0`/`q5_1` & mixed `K/V`, yet default CUDA binary lacks kernels | `#28455` Fix 1 (align defaults with advertised flags) | Compile with `-DGGML_CUDA_FA_ALL_QUANTS=ON` when serving those KV types; if keeping `OFF` for binary size, reject uncompiled `-ctk`/`-ctv` flags explicitly |
| **2. Loud Runtime Placement** | CUDA rejects `GGML_OP_FLASH_ATTN_EXT`, scheduler routes to CPU with zero console error or warning | `#28455` Fix 2 + maintainer `"known issue"` confirmation | Emit an immediate startup/runtime warning whenever `-ngl` non-zero + `-fa on` falls back to CPU; provide a strict fail-fast serving mode that aborts on off-GPU attention |
| **3. Benchmark & Eval Integrity** | `llama-bench` displays `fa=1 q5_1` identically for CPU fallback and GPU FA, tainting latency & PPL tables | `@sinanezhadian` Comment #1 + `#28455` Fix 3 | Print an off-GPU placement flag directly inside `llama-bench` result rows (not only `--verbose`), and require GPU placement verification before logging perplexity runs |
| **4. Production Telemetry & CI** | Alerting solely on TTFT lets silent CPU fallback masquerade as context-length saturation | Assistant operational synthesis from `#28455` telemetry | Alert on correlated `high TTFT + 0% GPU / low W + multi-core CPU spike`; run CI `pp512` throughput & device-placement smoke assertions across shipped `-ctk/-ctv` pairs |

For teams running self-hosted `llama.cpp` servers, the operational takeaway is immediate: **whenever `-ngl 99 -fa on` exhibits sudden long-context TTFT spikes, check GPU compute utilization and host CPU core saturation alongside your CMake build flags and scheduler placement—never treat a printed `fa=1` flag as proof that attention stayed on the GPU**.

---

### Verified Primary References

- Frozen issue report: `AhBumm`, *[Misc. bug: quantized KV cache (q5_x, q4_x) with -fa on silently fallback CPU attn](https://github.com/ggml-org/llama.cpp/issues/28455)*, `ggml-org/llama.cpp` GitHub Issue #28455 (opened 2026-09-05, closed 2026-09-06; cross-referencing `#27109`, `#24485`, `#20866`, `#27905`, and `#24403`).
- Numerical equivalence & confounding critique: `@sinanezhadian`, [Issue #28455 Comment #1](https://github.com/ggml-org/llama.cpp/issues/28455#issuecomment-5554868313) (2026-09-05), citing David Pape, Jonathan Evertz, and Lea Schönherr, *[The Silent Hyperparameter: Quantifying the Impact of Inference Backends on LLM Reproducibility](https://arxiv.org/abs/2605.19537)*, arXiv:2605.19537.
- Maintainer confirmation & governance policy: `@JohannesGaessler`, [Issue #28455 Comment #2](https://github.com/ggml-org/llama.cpp/issues/28455#issuecomment-5558436618) (2026-09-06), referencing [llama.cpp CONTRIBUTING.md — AI usage policy](https://github.com/ggml-org/llama.cpp/blob/master/CONTRIBUTING.md#ai-usage-policy).

> **AI-Assisted Curation & Archival Note**: Both this English deep read and its paired Chinese version ([中文笔记](/tech/zh/llamacpp-kv-fallback/)) were rewritten and verified by the assistant against the frozen capture of GitHub Issue #28455, its two comments, and directly linked primary documents, preserving original `id: llamacpp-kv-fallback`, `date: '2026-11-04'`, `permalink`, `source_url`, and canonical tags (`inference-serving`, `systems-reliability`, `observability`). No official diagrams accompanied the source; both `v3-blue` diagrams (`ggml-fa-quant-dispatch-fallback-en.svg`, `silent-fallback-diagnostic-gates-en.svg`) were authored by the assistant from the reported dispatch path, single-machine measurements, and thread comments, without generalizing single-GPU ratios into universal constants or reintroducing conflicting social-post numbers omitted from the original curation.
