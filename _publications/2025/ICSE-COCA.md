---
title:          "COCA: Generative Root Cause Analysis for
Distributed Systems with Code Knowledge"
date:           2025-01-20 00:00:00 +0800
selected:       true
pub:            >-
                In 47th IEEE/ACM International Conference on Software Engineering
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ICSE'25 (CCF A)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    Runtime failures are commonplace in modern distributed systems. When such issues arise, users often turn to platforms such as Github or JIRA to report them and request assistance. Automatically identifying the root cause of these failures is critical for ensuring high reliability and availability. However, prevailing automatic root cause analysis (RCA) approaches rely significantly on comprehensive runtime monitoring data, which is often not fully available in issue platforms. Recent methods leverage large language models (LLMs) to analyze issue reports, but their effectiveness is limited by incomplete or ambiguous user-provided information. To obtain more accurate and comprehensive RCA results, the core idea of this work is to extract additional diagnostic clues from code to supplement data-limited issue reports. Specifically, we propose COCA, a \underline{co}de knowledge enhanced root \underline{c}ause \underline{a}nalysis approach for issue reports. Based on the data within issue reports, COCA intelligently extracts relevant code snippets and reconstructs execution paths, providing a comprehensive execution context for further RCA. Subsequently,  COCA constructs a prompt combining historical issue reports along with profiled code knowledge, enabling the LLMs to generate detailed root cause summaries and localize responsible components. Our evaluation on datasets from five real-world distributed systems demonstrates that COCA significantly outperforms existing methods, achieving a 28.3\% improvement in root cause localization and a 22.0\% improvement in root cause summarization. Furthermore, COCA's performance consistency across various LLMs underscores its robust generalizability. 
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Yichen Li
  - Yulun Wu 
  - Jinyang Liu
  - Zhihan Jiang
  - Zhuangbin Chen
  - Guangba Yu*
  - Michael Lyu

links:
  Paper: 
  Project: 
  DOI: 
  BibTex: 
  Arxiv: 
---