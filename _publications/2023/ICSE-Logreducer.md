---
title:          "LogReducer: Identify and Reduce Log Hotspots in Kernel on the Fly"
date:           2022-12-09 00:00:00 +0800
selected:       true
pub:            >-
                In 45th IEEE/ACM International Conference on Software Engineering
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ICSE'23 (CCF A)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Modern systems generate a massive amount of logs to detect and diagnose system faults, which incurs expensive storage cost and runtime overhead. After investigating real-world production logs, we observe that most of the logging overhead is due to a small number of log templates, referred to as log hotspots. Therefore, we conduct a systematical study about log hotspots in an industrial system WeChat, which motivates us to identify log hotspots and reduce them on the fly. In this paper, we propose LogReducer, a non-intrusive and language-independent log reduction framework based on eBPF (Extended Berkeley Packet Filter), consisting of both online and offline processes. After two months of serving the offline process of LogReducer in WeChat, the log storage overhead has dropped from 19.7 PB per day to 12.0 PB (i.e., about a 39.08% decrease). Practical implementation and experimental evaluations in the test environment demonstrate that the online process of LogReducer can control the logging overhead of hotspots while preserving logging effectiveness. Moreover, the log hotspot handling time can be reduced from average 9 days in production to 10 minutes in the test with the help of LogReducer.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Guangba Yu
  - Pengfei Chen†
  - Pairui Li
  - Tianjun Weng
  - Haibing Zheng
  - Yuetang Deng
  - Zibin Zheng
links:
  Paper: https://yuxiaoba.github.io/files/ICSE23/logreducer.pdf
  Project: https://github.com/IntelligentDDS/Logreducer
  Slides: https://yuxiaoba.github.io/files/ICSE23/logreducer-slides.pdf
  DOI: https://doi.org/10.1109/ICSE48619.2023.00151
  BibTex: https://yuxiaoba.github.io/files/ICSE23/logreducer-bibtex.txt
  # Arxiv:
---
