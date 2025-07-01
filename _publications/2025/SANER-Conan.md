---
title:          "Conan: Uncover Consensus Issues in Distributed Databases Using Fuzzing-driven Fault Injection"
date:           2025-01-10 00:00:00 +0800
selected:       false
pub:            >-
                In IEEE International Conference on Software Analysis, Evolution and Reengineering
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">SANER'25 (CCF B)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    Consensus is critical for distributed databases as it ensures the consistency of states across nodes, reinforcing the robustness of the overall system. However, faults related to the consensus protocols such as Paxos can lead to serious issues in distributed databases. Such consensus issues impact the correctness and availability of these databases. Therefore, to automatically uncover consensus issues in distributed databases, we propose Conan, a framework designed with fuzzing-driven fault injection. Conan applies a state-guided fuzzing algorithm to effectively explore the fault search space. Moreover, Conan employs hybrid fault sequences that combines fine-grained message-level faults and coarse-grained system-level faults to enhance fault injection. We implement and evaluate Conan on 3 widely-used distributed databases, including etcd, rqlite and openGauss. Finally, Conan has successfully uncovered previously unknown consensus issues, some of which are not detected by existing approaches.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Haojia Huang
  - Pengfei Chen†
  - Guangba Yu
  - Haiyu Huang
  - Jia Chang
  - Jun Li
  - Jian Han

links:
  Paper: https://yuxiaoba.github.io/files/Saner25/conan.pdf
  Project: https://github.com/huanghj78/conan
  DOI: https://doi.org/10.1109/SANER64311.2025.00073
  BibTex: https://yuxiaoba.github.io/files/Saner25/conan-bibtex.txt
---