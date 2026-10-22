---
id: torchtpu
title: '2026-10-21 | TorchTPU: Compilation and Communication Behind Native PyTorch
  APIs'
date: '2026-10-21'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- inference-serving
- systems-reliability
summary: How eager execution, DeferAndFuse, and distributed collectives connect PyTorch
  semantics to TPU execution.
long_read: true
source_url: https://pytorch.org/blog/introducing-torchtpu/
permalink: /tech/en/torchtpu/
authorship: assistant
translation_source: assistant
published_at: "2026-10-21T13:08:08.256303+08:00"
updated_at: "2026-10-21T13:08:08.256303+08:00"
---
The TorchTPU Team · PyTorch · 2026-10-20  
Original: [Introducing TorchTPU](https://pytorch.org/blog/introducing-torchtpu/)

TorchTPU's central change is a native backend for PyTorch programs on TPUs, with eager execution, torch.compile, and distributed APIs treated as design priorities. The entry point becomes more familiar, but compilation latency, tensor shapes, communication semantics, and precision still determine practical behavior. Changing cuda to tpu starts compatibility work; it does not finish performance tuning.

## Familiar APIs still reach the TPU compiler stack

The backend registers through PyTorch's PrivateUse1 dispatcher path and supplies device-specific tensor storage. High-level operations lower to StableHLO; custom Pallas kernels can enter through Mosaic. OpenXLA generates TPU executables, while PjRT handles compilation, dispatch, and movement. The standard backend runtime does not require JAX; authoring optional kernels through JAX/Pallas is a separate path, so these statements are compatible.

<a class="note-image-link" href="/assets/images/tech/torchtpu/stack.png" target="_blank" rel="noopener" aria-label="PyTorch and JAX independently enter StableHLO, while custom kernels enter Mosaic. The paths converge inside OpenXLA before producing a TPU executable. · View original image ↗"><img src="/assets/images/tech/torchtpu/stack.png" alt="PyTorch and JAX independently enter StableHLO, while custom kernels enter Mosaic. The paths converge inside OpenXLA before producing a TPU executable." loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*PyTorch and JAX independently enter StableHLO, while custom kernels enter Mosaic. The paths converge inside OpenXLA before producing a TPU executable.*

This translation reconciles mutable PyTorch views with StableHLO's single-assignment semantics. The article describes view decomposition and inversion to implement familiar in-place behavior. Shapes are generally known at compile time, with bounded dynamic dimensions under development. Beyond successful execution, users should examine whether shape changes trigger recompilation and whether view updates add work.

## Eager execution has more than one dispatch policy

Strict mode submits operations individually and asynchronously. Debug mode synchronizes each operation, exchanging speed for diagnosis. DeferAndFuse records operations until a materialization point, such as retrieving a CPU value, then analyzes live values, constructs a graph, checks the compilation cache, and dispatches it. Brief deferral enables fusion and can reduce temporary HBM storage.

The trade-off is compilation now versus reuse later. With a warm cache, CPU tracing and dispatch can stay ahead of device computation. Cold starts or changing graphs may not amortize compilation. Collectives have side effects and cannot simply be eliminated as dead operations; their order must also survive. First execution, steady iteration, and shape changes therefore deserve separate measurements.

The reported FLUX optimization sequence illustrates this distinction. Step time starts at 11.49 seconds in eager mode, reaches 9.95 with DeferAndFuse, 6.52 after SimpleFSDP, 5.55 after Pallas attention, 3.02 with full compilation, and 2.78 after model-specific rewrites. Several improvements accumulate. The entire 11.49-to-2.78-second change cannot be credited to one switch and is not a direct comparison with an arbitrary GPU.

## Distributed compatibility is harder than changing a device name

TorchTPU uses one process per device and integrates collectives through Process Group. TPU communication compilation needs consistency across ranks, while rank-dependent branches or uneven DTensor splits can produce different modules. Default Skinny Collectives compile each communication operation separately to avoid mismatched synchronization flags and buffer offsets, but reduce compute–communication overlap.

The authors give examples of approximately 30–40% end-to-end penalties, illustrating the cost of conservative compatibility. Known-SPMD regions can use spmd_safe annotations to widen optimization, but an incorrect annotation is brittle. A compilation handshake comparing graphs across replicas offers another direction; developing mechanisms should not be treated as default guarantees for every case.

Physical topology also matters. Communication-heavy tensor, context, and expert dimensions should preferentially use fast intra-slice ICI, while slower inter-slice DCN suits less frequent traffic. DeviceMesh expresses logical relationships, but incorrect rank-to-device mapping can still misroute custom distributed kernels. The discussion of logical addressing and ProcessGroup mapping is particularly useful for multi-device users.

## Interpret precision and coverage per workload

Default medium matmul precision uses BF16 inputs with FP32 accumulation. High and highest use multi-pass algorithms, with approximately threefold and sixfold MXU compute cost respectively. These are neither free accuracy upgrades nor predictions that an entire model slows by those factors. Sensitive layers need convergence or output-error checks alongside throughput.

The team reports support for approximately 450 ATen operations and validates out-of-box execution on the 5,000 most downloaded Hugging Face models. That is coverage evidence, not uniform performance. One training example runs BF16 Llama 3 405B across 1,024 v7x chips with 8K context, reporting 500 tokens/s/chip and more than 50% MFU. Those conditions belong with the numbers. A TPU's restriction to one user process also complicates colocated RL training and sampling.

## Evaluate a complete workload lifecycle

The announcement addresses both training and inference, where the same optimization can have different value. Long training runs amortize compilation over many iterations; short jobs and frequent scaling care more about time to readiness. Training needs coordination of saved activations and backward computation, while inference changes batch and sequence shapes. Supporting both through one backend is progress in interface unification, not evidence that their bottlenecks are identical.

The mechanisms suggest three separate performance questions. First, can graphs be reused consistently, limiting compilation? Second, how much temporary memory, padding, and serial small-operation work remains on the device? Third, can communication overlap computation under the required graph consistency and topology? Looking only at a final step-time measurement can omit preparation and memory costs.

SimpleFSDP in the TorchTitan case illustrates the third question. Expressing collectives as ordinary graph operations gives the compiler opportunities to place them and overlap SparseCore work with matrix computation. It does not eliminate communication; it exposes more information to scheduling. Similarly, activation offloading frees HBM but adds host transfers whose value depends on pressure, bandwidth, and overlap.

The article's value extends beyond a support list to the construction of a TPU backend for PyTorch semantics. Ecosystem reuse reduces duplicate implementation, while hardware-specific tuning still needs explicit accounting. Separating these benefits helps identify when easier use becomes more efficient execution.

Code reuse also separates operator semantics from performance implementation. A general path starts more models; specialized attention, sparse-expert execution, and memory layouts determine whether hotspots exploit the device. Presenting both shows why coverage and optimization should be reported separately: one reduces migration friction, while the other establishes performance for a particular workload.

The development to watch is lower ecosystem migration cost and broader compiler control over communication, memory, and compute. The article offers substantial implementation detail and selected cases, not a uniform cross-model, cross-hardware, price-controlled evaluation. Start with the eager/compiled boundary and collective correctness, then assess whether model shapes, precision needs, and cold-start conditions match the reported strengths.
