---
title:          "Network shortcut in data plane of service mesh with eBPF"
date:           2023-12-12 00:00:00 +0800
selected:       false
pub:            >-
                In Journal of Network and Computer Applications
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-info">JNCA (CCF C)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  In recent years, the adoption of the service mesh as a dedicated infrastructure layer to support cloud-native systems has gained significant popularity. Service meshes involve the incorporation of proxies to handle communication between microservices, thereby speeding up the development and deployment of microservice applications. However, the use of service meshes also increases the request latency because they elongate the packet transmission between services. After investigating the transmission path of packets in a representative service mesh Istio, we observed that the service mesh dedicates approximately 25% of its time to packet transmission in the Linux kernel network stack. To shorten this process, we propose a non-intrusive solution that enables packets to bypass the kernel network stack through the implementation of socket redirection and tc (traffic control) redirection with eBPF (extended Berkeley Packet Filter). We also conduct comprehensive experiments on the widely-used Istio. The evaluation results show that our approach can significantly reduce the request latency by up to 21%. Furthermore, our approach decreases CPU usage by 1.73% and reduces memory consumption by approximately 0.98% when compared to the original service mesh implementation.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Wanqi Yang
  - Pengfei Chen
  - Guangba Yu
  - Haibin Zhang
  - Huxing Zhang
  
links:
  Paper: https://yuxiaoba.github.io/files/JNCA/servicemesh.pdf
  Project: https://github.com/IntelligentDDS/ServiceMeshRedirect
  DOI: https://doi.org/10.1016/j.jnca.2023.103805
  BibTex: https://yuxiaoba.github.io/files/TSC/faasdeliver-bibtex.txt
  # Arxiv:
---
