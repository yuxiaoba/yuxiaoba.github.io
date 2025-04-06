---
title:          "Take Kernel Stack Overhead Out: eBPF-Enhanced Network  Acceleration for Distributed Training within Ethernet"
date:           2025-03-31 00:00:00 +0800
selected:       false
pub:            >-
                In 16th International Conference on Internetware.
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">Internetware'25 (CCF C)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    As deep neural networks (DNN) continue to scale up in size to achieve greater capabilities, distributed training (DT) has become the prevailing approach to accelerate the training process. However, according to our observation on the network communication overheads in DT within Ethernet, the Linux kernel network stack accounts for 30% to 40% of the total communication time, posing a significant bottleneck to training efficiency. To mitigate the overhead introduced by the kernel network stack, we propose eRAR, an eBPF-based gradient aggregation over Ring-AR for DT tasks in commodity data centers. eRAR exploits Ring-AR's topology for in-kernel gradient aggregation using eBPF, enabling packet-level parallelism and avoiding the overhead of network stack. It ensures reliability through ring-based retransmission and accelerates computations via SIMD-enabled kfuncs. eRAR has the advantages of hardware-agnostic, network-topology-independent, and resource-efficient. Our experimental results on four popular DNN models demonstrate that, compared to aggregation based on TCP/IP network stack, eRAR improves the gradient aggregation throughput by 77.2%. Furthermore, eRAR reduces the communication time by up to 37.4% compared to existing systems.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Zhenyu Zhang 
  - Pengfei Chen
  - Guangba Yu†
  - Zilong He
  - Xiaoyun Li

links:
  Paper: 
  DOI: 
  BibTex: 
  Arxiv: 
---