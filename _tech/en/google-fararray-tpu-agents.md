---
tech_deep_read: true
id: google-fararray-tpu-agents
title: '2026-10-30 | FarArray and Pallas TPU Kernels: Systems Co-Design with Gemini 4 Argon Agents'
date: '2026-10-30'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
long_read: true
tags:
- multi-agent
- systems-reliability
- coding-agents
- agent-reliability
summary: 'A deep systems breakdown of how Google Graph Mining and Graph Learning teams used Gemini 4 Argon agents to build FarArray (a kernel-bypass RDMA PGAS engine for trillion-edge graphs) and custom Pallas TPU v6e sparse kernels (streaming COO blocks through SMEM into 122 MiB VMEM with zero-float-residual VJP), plus Zero-Facade verification and vendor benchmark boundaries.'
source_url: https://antigravity.google/blog/gemini-4-argon-trillion-edge-graphs-and-tpu-kernels
permalink: /tech/en/google-fararray-tpu-agents/
authoring_source: assistant
translation_source: assistant
published_at: '2026-10-30T10:31:20.339125+08:00'
updated_at: '2026-11-16T12:05:00+08:00'
---
The Antigravity & Google Research Team · 2026-10-26 · [Original Google Antigravity Blog: "How Gemini 4 Argon Upleveled Agents on Antigravity: Trillion-Edge Graphs and Custom TPU Kernels"](https://antigravity.google/blog/gemini-4-argon-trillion-edge-graphs-and-tpu-kernels)

While our companion note on [Antigravity /teamwork](/tech/en/antigravity-teamwork/) examines Google's general declarative workflow patterns (clean contexts, dependency-ordered Rust rewrites, cheap proxy yardsticks, and Borg preemption), this earlier October 26 case study dives directly into **low-level hardware datapath and memory-hierarchy co-design**. Inside Google's internal [Distributed Graph Flow (DGF)](https://dgf.readthedocs.io/en/latest/) stack, researchers used [Gemini 4 Argon](https://antigravity.google/blog/gemini-4-argon-in-google-antigravity) inside [Teamwork](https://antigravity.google/blog/teamwork-when-ai-becomes-a-research-partner) to implement two foundational systems while keeping humans in charge of interfaces, memory layouts, and zero-mock verification harnesses: **FarArray** for trillion-edge distributed graphs over RDMA, and **custom O(N)-memory Pallas TPU kernels** for sparse GNNs.

> **Evidence & scope boundary**: Every throughput ratio, wall-clock speedup, memory footprint, and the claim of "compressing an estimated one-year distributed systems roadmap into a 5-hour gated engineering sprint" comes from Google's internal engineering report published October 26, 2026. Neither FarArray nor the Pallas TPU kernels or benchmark suites are open-sourced with the post. Throughout this note, reported mechanisms and numbers are explicitly separated from our systems derivations and scaling boundary observations.

## FarArray Architecture: Eliminating the Distributed Graph Key-Value Tax via Kernel-Bypass RDMA

On a single server, shared-memory multicore libraries such as Google's open-source [Graph Based Benchmark Suite (GBBS)](https://github.com/ParAlg/gbbs) process billions of edges in seconds using lock-free atomic operations on dense flat arrays—right up to the point where the graph outgrows single-host RAM. Scaling past one machine traditionally forces pipelines onto distributed batch engines like [MapReduce](https://research.google/pubs/connected-components-in-mapreduce-and-beyond/), often paired with low-latency Remote Key-Value (RKV) services such as [CliqueMap](https://research.google/pubs/cliquemap-productionizing-an-rma-based-distributed-caching-system/) or TCP key-value stores—triggering what the authors term the **"Distributed Graph Tax"**:

1. **Per-key metadata and serialization inflation**: Generic key-value stores wrap every vertex state in heavy per-key metadata, hash table structures, and serialization framing, multiplying cluster DRAM demand at billion- and trillion-edge scale.
2. **OS kernel network interrupts and saturated server CPUs**: Fine-grained remote lookups and mutations flood host kernels with network interrupts and RPC handling. Under comparison benchmarks, the post reports TCP key-value server CPUs saturating at **100%**.
3. **Write-once stage overhead in iterative embeddings**: For Personalized PageRank embeddings ([InstantEmbedding](https://arxiv.org/abs/2010.06992)), tandem MapReduce and Remote KV servers serialize states across write-once batch stages rather than updating compact mutable arrays in place, inflating peak concurrent and cumulative memory.

To remove this tax, the team designed **FarArray**: a low-latency, kernel-bypass Partitioned Global Address Space (PGAS) inspired by the [SNAP microkernel](https://research.google/pubs/snap-a-microkernel-approach-to-host-networking/) that exposes pinned cluster DRAM as a flat, hardware-addressable global array without per-key KV headers or hash buckets.

<figure class="note-figure">
  <a class="note-image-link" href="/assets/images/tech/google-fararray-tpu-agents/fararray-tpu-architecture-en.svg" target="_blank" rel="noopener">
    <img src="/assets/images/tech/google-fararray-tpu-agents/fararray-tpu-architecture-en.svg" alt="Dual systems datapath diagram for FarArray RDMA PGAS and Pallas TPU sparse kernels: top track contrasts TCP key-value and shuffle baselines experiencing 100% server CPU saturation and 4.0 TB ClueWeb memory against FarArray's worker-local LCA pruning filtering 97% to 99.9% of redundant edges, batched PCIe MMIO doorbells, and SmartNIC one-sided DMA and 64-bit CAS directly on pinned remote DRAM; bottom track contrasts native JAX segment_sum materializing an O(|E| times D) tensor of 20.2 GiB HBM at 20M edges against Pallas streaming 4,096-edge COO blocks via SMEM into 122 MiB VMEM with (8, 128) 3D VREG register forwarding and zero-float-residual custom_vjp holding HBM flat at 111.5 MiB." width="960" height="540" loading="lazy">
    <span class="note-image-action">Expand diagram ↗</span>
  </a>
  <figcaption>Assistant diagram (not an original figure): Comparing the two low-level datapaths described in the Google Antigravity post—FarArray kernel-bypass RDMA over pinned DRAM (top) and Pallas on-chip TPU v6e sparse SpMM execution (bottom).</figcaption>
</figure>

Three coordinated mechanisms make FarArray's datapath behave like single-machine shared memory across a cluster:

- **Pluggable transports and dual cluster topologies**: Teamwork agents implemented backends across **SmartNIC RDMA**, **Linux `io_uring`**, and **POSIX shared memory**. FarArray supports both **Symmetric PGAS** (where worker nodes also host globally addressable pinned DRAM) and **Dedicated Worker/Server** topologies (where dedicated memory targets can run custom native extensions to execute hardware-accelerated logic and minimize network hops).
- **Batched PCIe MMIO doorbells and zero remote CPU interrupts**: On RDMA-capable SmartNICs, application threads post Work Queue Elements (`WQEs`) via **PCIe MMIO doorbells** (batched in the pipeline) directly to the local NIC. The SmartNIC executes one-sided DMA reads, writes, and **64-bit atomic `CompareAndSwap` (`CAS`)** directly in NIC hardware via **PCIe AtomicOps** against pinned remote DRAM in **microseconds**—with **zero remote CPU interrupts**, leaving target host application CPUs idle.
- **Algorithmic co-design via thread-local LCA pruning**: Even microsecond-scale RDMA NICs suffer tail-latency contention if every redundant edge hits the fabric. FarArray pairs hardware atomics with thread-local **Lowest Common Ancestor (LCA) early-exit pruning**, resolving **`97%–99.9%` of redundant graph edges** in local worker RAM before touching the network. (**Engineering interpretation**: in union-find / pointer-jumping connected components, discarding intra-component edges locally slashes remote RDMA CAS traffic by 1–3 orders of magnitude; even with that pruning, heavy fan-in still triggered tail spikes during benchmarking until Teamwork analyzed hardware telemetry and cut maximum read latency spikes by 89%.)

## Pallas TPU Sparse Kernels: Eliminating Edge-Sized HBM Intermediates in SMEM and VMEM

While FarArray attacks inter-node DRAM and CPU bottlenecks, Google's Graph Learning team faced an orthogonal hardware mismatch on [Google Cloud TPUs](https://cloud.google.com/tpu), which are engineered for dense Matrix Multiply Unit (MXU) operations and contiguous memory layouts.

GNN message passing (`Y = A @ X`) aggregates node features across sparse, irregular edge tuples (`row_ids`, `col_ids`). In standard [JAX](https://docs.jax.dev/en/latest/) (`jax.ops.segment_sum`), gathering source node embeddings onto edges materializes an **`O(|E| × D)` intermediate tensor** in **High-Bandwidth Memory (HBM)** before segment reduction. Across a progressive sweep (**50K nodes, 256-dimensional features, 214K to 20.97M edges**), native JAX temporary HBM scales linearly to **20.2 GiB** at **20M (`20.97M`) edges**, exhausting a single **TPU v6e** device.

Co-designed through an iterative Teamwork kernel-design and verification loop, the custom **Pallas SpMM TPU kernel** removes edge-sized HBM intermediates using three hardware-specific techniques:

1. **Streaming raw COO edge blocks through SMEM into expanded VMEM**: Instead of converting sparse graphs to CSR on the host CPU, the kernel streams raw Coordinate (`COO`) `(row_ids, col_ids)` blocks (**4,096 edges/block**) directly through **TPU Scalar Memory (SMEM)** while expanding XLA's scoped **Vector Memory (VMEM)** allocation from **`16 MiB` to `122 MiB`**. Dense node feature tables and accumulators reside wholly on-chip, eliminating edge-sized HBM materialization. (**Systems boundary observation**: 50K nodes × 256D features fits inside the 122 MiB on-chip VMEM window; graphs whose node-feature footprint exceeds VMEM capacity would require node-partition tiling or multi-chip sharding, which the post does not evaluate beyond 50K nodes.)
2. **Hardware-aligned `(8, 128)` 3D VREG tiling and register forwarding**: To keep vector units saturated on TPU v6e, the kernel reshapes 2D node embeddings into hardware-aligned **`(8, 128)` 3D vector register (`VREG`) tiles** and applies **4-way loop unrolling with software store-to-load register forwarding**, avoiding VMEM pipeline stalls when consecutive COO edges update duplicate destination nodes.
3. **Zero-float-residual backpropagation (`custom_vjp`)**: For backward message passing (`dX = A^T @ dY`), the custom VJP retains **zero floating-point activation residuals** from the forward pass—storing only integer edge indices and swapping `row_ids` and `col_ids` to preserve strict **`O(N)` HBM scaling** throughout training.

The table below compiles every reported benchmark separately by workload, scale, and baseline so distinct comparisons are never collapsed into one misleading number:

| System & Workload | Evaluated Scale & Setup | Baseline Compared | Vendor-Reported Outcome |
| :--- | :--- | :--- | :--- |
| **FarArray Connected Components** (ClueWeb12 & HyperLink 2012) | Up to **3.56B** vertices, **113.6B–128.7B** edges | TCP key-value stores & distributed shuffle pipelines | **60× & 90× higher throughput**, **40× (ClueWeb12) & 180× (HyperLink 2012) faster wall-clock time**, **6×–22× less RAM** vs. TCP KV; **over 100× less DRAM** vs. shuffle (**`28.5 GB` vs. `4.0 TB`**); **100% exact partition parity** vs. single-machine GBBS |
| **FarArray Planet-Scale Connected Components** | **18.0B** vertices, **1.14T unique** (**2.27T symmetric**) edges | `>1 TiB` TCP KV &amp; `>20 TB` shuffle (reported infeasible) | Finished in **148 GB total pinned DRAM** across **64 targets** (**2.31 GB/node**), **0 OOMs** |
| **FarArray Distributed [InstantEmbedding](https://arxiv.org/abs/2010.06992)** (Personalized PageRank) | **955M–3.56B** vertices, up to **98.0B** directed edges (ClueWeb12 / Hyperlink 2012) | MapReduce + Remote KV tandem servers | Holding quantized mutable embeddings in PGAS reduced **peak concurrent RAM by 8.7–13.9×** (`8.69×` / `13.85×` in caption), **cumulative memory by up to 55.9×** (`55.87×`), **per-hop latency by 12.90×–30.26×**, and **8-hop wall time by 11.3–26.5×** (`11.29×–26.46×`) |
| **Pallas TPU v6e Sparse Kernels** (SpMM / GIN / GCN) | **50K** nodes, **256D** features, **214K–20.97M** edges; GIN (`SUM` / `MEAN`) &amp; 1-/4-layer GCN | Native JAX (`jax.ops.segment_sum`) on TPU v6e | **111.5 MiB constant HLO temporary memory** vs. **20.2 GiB** in JAX at 20.97M edges (**up to 185.8× reduction**); **10.5×–14.7×** faster forward (`10.45×–14.66×`) and **8×–12×** faster backward / forward+backward (`7.96×–11.98×`) with **strict floating-point numerical parity** |

## Human-Specified Invariants, Autonomous Execution: Zero-Facade Gates and Telemetry Loops

A central systems lesson from the report is the strict division of authority between human engineers and Gemini 4 Argon sub-agents. Equipped with Argon's **1-million-token context window**, tunable reasoning, and native sub-agent orchestration, specialized Teamwork agents covered C++ RDMA verbs, Linux `io_uring`, lock-free graph algorithms, and Pallas/XLA lowering—yet **humans controlled the architectural contract throughout**: engineers specified system interfaces, memory layouts, mathematical invariants, and zero-mock verification harnesses before agents implemented, tested, and tuned.

<figure class="note-figure">
  <a class="note-image-link" href="/assets/images/tech/google-fararray-tpu-agents/argon-verification-boundaries-en.svg" target="_blank" rel="noopener">
    <img src="/assets/images/tech/google-fararray-tpu-agents/argon-verification-boundaries-en.svg" alt="Diagram of human-controlled contracts, Zero-Facade verification gates, and evidence boundaries for Gemini 4 Argon: top three columns depict human specifications for PGAS and SMEM/VMEM memory layouts plus zero-mock invariants, Teamwork execution across the 5-milestone FarArray pipeline and hardware telemetry tuning cutting max read tail latency by 89%, and an independent adversarial auditor enforcing Zero-Facade 4-tier tests alongside JAX and GBBS parity; bottom three boxes highlight non-collapsible baselines, undisclosed code and hardware counts, and project-estimate caveats on time compression." width="960" height="540" loading="lazy">
    <span class="note-image-action">Expand diagram ↗</span>
  </a>
  <figcaption>Assistant diagram (not an original figure): Mapping human architectural boundaries, Teamwork's Zero-Facade verification loop, and external evidence limits from the Google Antigravity report.</figcaption>
</figure>

Three concrete verification mechanisms anchored execution:

- **Five-milestone gated pipeline**: FarArray progressed strictly through **`Transport Abstraction → Core Pinned Arena → Batched Doorbells → Distributed Algorithms → Live Audit`**, preventing agents from skipping low-level memory and transport contracts straight to high-level graph demos.
- **Independent auditor and the "Zero-Facade" gate**: Adversarial verification sat in an independent auditor agent enforcing a **"Zero-Facade" rule**—forbidding mocks or simplified stubs—and requiring reviewable change lists to pass **four end-to-end test tiers**: functional, scale, stress, and failure-recovery.
- **Hardware telemetry closed-loop debugging**: Rather than relying on static analysis or synthetic simulations, Teamwork read real cluster telemetry when heavy fan-in exposed tail-latency spikes on FarArray, diagnosing and tuning the datapath to cut **maximum read latency spikes by 89%**. On TPU v6e, the kernel loop verified both single- and four-layer GIN (`SUM` / `MEAN`) and GCN layers directly on hardware against native JAX outputs.

## Evidence Boundaries of Vendor-Reported Gains and Takeaways for AgentOps

Because both systems sit inside Google's internal stack, reading these numbers responsibly requires tracking four distinct **independent verification boundaries**:

1. **Baselines are task-specific and cannot be merged**: `40×–180×` runtime and `6×–22×` RAM compare connected components against TCP KV; `over 100×` DRAM (`28.5 GB` vs. `4.0 TB`) compares against distributed shuffle; `11.3–26.5×` 8-hop speedups compare InstantEmbedding against MapReduce + Remote KV; and the `1.14T` unique-edge run (`148 GB` across 64 targets, `0 OOMs`) demonstrates feasibility where `>1 TiB` TCP KV and `>20 TB` shuffle baselines are infeasible rather than giving a direct runtime ratio.
2. **Artifacts and cluster parameters remain private**: Neither FarArray's C++/RDMA implementation nor the Pallas SpMM kernels or benchmark scripts are public. The post also omits NIC hardware models, network fabric specs, node counts for the ClueWeb12/HyperLink 2012 runs, and the exact floating-point precision (`bf16` vs. `fp32`) or tolerance threshold underlying "strict floating-point numerical parity."
3. **On-chip VMEM scaling assumes fitting node features inside 122 MiB**: Expanding scoped VMEM from `16 MiB` to `122 MiB` keeps the evaluated `50K × 256D` node feature and accumulator tables on-chip; workloads whose vertex tables exceed VMEM would need outer node tiling or cross-chip partitioning not benchmarked here.
4. **"Months into hours" rests on project estimates and prior infrastructure**: Compressing a "one-year roadmap into a 5-hour sprint" compares measured sprint duration against an internal roadmap estimate, relies on pre-existing `DGF`, `SNAP`, `CliqueMap`, `GBBS`, and `Pallas` infrastructure plus human-authored invariants and non-mock test harnesses, and provides no ablation isolating Gemini 4 Argon from Teamwork's pipeline gates.

| Systems Layer | Primary Evidence Reported | Undisclosed or Non-Extrapolable Boundary | Reusable Principle for AgentOps |
| :--- | :--- | :--- | :--- |
| **FarArray (RDMA / PGAS)** | Dual PGAS topologies, batched PCIe MMIO doorbells, hardware 64-bit `CAS`, `97%–99.9%` local LCA pruning, 3 benchmark families, and 100% GBBS parity | Source code, SmartNIC models, fabric bandwidth, and cluster sizes for ClueWeb/HyperLink runs undisclosed; RDMA vs. LCA shares not ablated | Lock down memory ownership, lock-free atomics, and traffic-pruning contracts before letting coding agents generate transport code |
| **Pallas TPU Sparse Kernels** | `4,096`-edge COO streaming via SMEM, `16→122 MiB` VMEM, `(8, 128)` 3D VREG unroll + forwarding, zero-float-residual `custom_vjp`, 214K–20.97M sweep | Kernel source, dtype (`bf16`/`fp32`), and parity tolerance unstated; scaling evaluated up to 50K nodes × 256D without cross-chip VMEM spill tests | Convert physical bottlenecks (HBM edge-tensor bytes, on-chip VMEM ceiling, saved backward bytes) into hard acceptance gates |
| **Teamwork / Argon Loop** | 5-milestone pipeline, independent auditor enforcing Zero-Facade (no mocks), 4-tier e2e tests, and telemetry loop (-89% max read tail) | "1 year to 5 hours" uses internal estimates atop existing DGF/GBBS/SNAP foundations; no Argon vs. gating ablation | Separate code synthesis from an adversarial Zero-Facade verifier, and wire real hardware telemetry directly into the revision loop |
| **Relation to `antigravity-teamwork`** | This Oct 26 note details RDMA PGAS and TPU on-chip memory/register co-design; our Nov 15 [Antigravity /teamwork note](/tech/en/antigravity-teamwork/) covers declarative patterns, Rust rewrites, proxy yardsticks, and Borg | Separate internal campaigns and metrics; never merge JAXBench or Rust rewrite outcomes into FarArray or Pallas benchmarks | Pair general multi-agent orchestration patterns with hardware-specific physical invariants and non-mock verification |

For engineering teams adopting coding agents on systems and ML infrastructure, the transferable insight is not prompt craftsmanship—it is **translating physical system laws (zero kernel interrupts, on-chip VMEM budgets, zero saved float residuals, and real-hardware stress tests) into unyielding contracts enforced by an independent Zero-Facade verifier**.

---

> **Provenance**: Rewritten and expanded by the assistant from the frozen primary HTML of Google Antigravity's October 26, 2026 blog post ([中文笔记](/tech/zh/google-fararray-tpu-agents/), `authoring_source: assistant`, `translation_source: assistant`), preserving the original `id`, `date`, `permalink`, `published_at`, and `source_url`, and tagging strictly within the site's `_data/note_tags.yml` vocabulary (`multi-agent`, `systems-reliability`, `coding-agents`, `agent-reliability`). Both `v3-blue` diagrams (`fararray-tpu-architecture-en.svg`, `argon-verification-boundaries-en.svg`) are assistant-authored summaries grounded solely in the frozen source without fabricated benchmarks.
