---
title:          "Graph based Incident Extraction and Diagnosis in Large-Scale Online Systems"
date:           2022-07-19 00:00:00 +0800
selected:       true
pub:            >-
                In 37th IEEE/ACM International Conference on Automated Software Engineering
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ASE'22 (CCF A)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  With the ever increasing scale and complexity of online systems, incidents are gradually becoming commonplace. Without appropriate handling, they can seriously harm the system availability. However, in large-scale online systems, these incidents are usually drowning in a slew of issues (i.e., something abnormal, while not necessarily an incident), rendering them difficult to handle. Typically, these issues will result in a cascading effect across the system, and a proper management of the incidents depends heavily on a thorough analysis of this effect. Therefore, in this paper, we propose a method to automatically analyze the cascading effect of availability issues in online systems and extract the corresponding graph based issue representations incorporating both of the issue symptoms and affected service attributes. With the extracted representations, we train and utilize a graph neural networks based model to perform incident detection. Then, for the detected incident, we leverage the PageRank algorithm with a flexible transition matrix design to locate its root cause. We evaluate our approach using real-world data collected from the WeChat ® online service system, the largest instant message system in China. The results confirm the effectiveness of our approach. Moreover, our approach is successfully deployed in the company and eases the burden of operators in the face of a flood of issues and related alert signals.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Zilong He
  - Pengfei Chen†
  - Yu Luo
  - Qiuyu Yan
  - Hongyang Chen
  - Guangba Yu
  - Fangyuan Li
links:
  Paper: https://yuxiaoba.github.io/files/ASE22/gied.pdf
  Project: https://github.com/IntelligentDDS/GIED
  DOI: https://doi.org/10.1145/3551349.3556904
  BibTex: https://yuxiaoba.github.io/files/ASE22/gied-bibtex.txt
  # Arxiv:
---
