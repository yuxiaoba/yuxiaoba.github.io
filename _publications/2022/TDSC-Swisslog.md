---
title:          "SwissLog: Robust Anomaly Detection and Localization for Interleaved Unstructured Logs"
date:           2022-03-11 00:00:00 +0800
selected:       true
pub:            >-
                In IEEE Transactions on Dependable and Secure Computing
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-info">TDSC (CCF A)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Modern distributed systems generate interleaved logs when running in parallel. Identifiers (ID) are always attached to them to trace running instances or entities in logs. Therefore, log messages can be grouped by the same IDs to help anomaly detection and localization. The existing approaches to achieve this still fall short meeting these challenges, 1) Log is solely processed in single components without mining log dependencies, 2) Log formats are continually changing in modern software systems, 3) It is challenging to detect latent performance issues non-intrusively by trivial monitoring tools. To remedy the above shortcomings, we propose SwissLog, a robust anomaly detection and localization tool for interleaved unstructured logs. \textcolor{black}{SwissLog focuses on log sequential anomalies and tries to dig  out possible performance issues. SwissLog constructs ID relation graphs across distributed components and groups log messages by IDs. Moreover, we propose an online data-driven log parser without parameter tuning.} The grouped log messages are parsed via the novel log parser and transformed with semantic and temporal embedding. Finally, SwissLog utilizes an attention-based Bi-LSTM model and a heuristic searching algorithm to detect and localize anomalies in instance-granularity, respectively. The experiments on real-world and synthetic datasets confirm the effectiveness, efficiency, and robustness of SwissLog. 
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Xiaoyun Li
  - Pengfei Chen†
  - Linxiao Jing
  - Zilong He
  - Guangba Yu
  
links:
  Paper: https://yuxiaoba.github.io/files/TDSC/swisslog.pdf
  Project: https://github.com/IntelligentDDS/SwissLog
  DOI: https://doi.org/10.1109/TDSC.2022.3162857
  BibTex: https://yuxiaoba.github.io/files/TDSC/swisslog-bibtex.txt
  # Arxiv:
---
