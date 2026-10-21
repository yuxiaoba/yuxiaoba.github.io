# 根据 GB-Resume 更新主页与论文库

完成日期：2026-10-15。范围由用户确认：个人资料和论文库，首页保持简洁；不增加项目、教学或专利栏目。

## 来源与合并规则

只读参考 `/home/GB-Project/GB-Resume/build.py`、`guangba.bib`、`cv-A.html`、`cv-A-zh.html`，并从 `cv-en.html` 补齐两项科技奖的已有英文名称。没有运行简历生成器，没有修改该目录，也没有发布简历源文件或 PDF。

- 个人资料：博士后起始时间采用较新的 2024.07；补齐本科、导师及精确教育日期；保留原个人故事、单位、联系方式和两条研究主线。
- 获奖：中英文各 11 项，包含国家奖学金和腾讯犀牛鸟项目／特别奖学金。之前只查看新 A 版而误认为两项科技奖没有英文名称，已依据 `cv-en.html` 纠正。
- 学术服务：同步 FSE 2027、FSE 2026 IVR、ICSME 2026 等，保留原有有效服务信息。Sub-reviewer 按用户要求隐藏，资料保存在数据文件中。
- 论文：保留原 41 条，新增 18 条，共 59 条；其中 3 条在来源中属于 arXiv 预印本，未把它们计作正式论文。CV 未列出的 Kmon 原记录仍保留。
- 更新已有论文的明确题名、作者、年份与奖项信息；原文件路径、摘要原文和全部原资源链接保留。旧通讯标记不因简历未标注而删除；只补充简历明确的本人通讯信息，页面仍只对 Guangba Yu 显示信封标记。
- 出版年份优先 `year`，不伪造精确发表／录用日期，不生成 acceptance News。

## 按后续反馈统一论文格式

1. 左侧显示会议／期刊简称与年份；有来源的 CCF 等级独立下一行且不拆行。
2. 所有 59 条记录均在作者下方显示完整发表来源；新增记录补齐 `pub`，原有记录保留原文。
3. 不展示摘要，不显示额外的 Preprint 标签；arXiv 来源及数据状态保留。
4. 右侧年份导航、中文话题和 CUHK 紫金配色保持。

## 验证

- 标准 Jekyll 构建与 `git diff --check` 通过。
- `python3 scripts/verify_site.py`：1178 项通过，含双语页面、全部论文、原文姓名顺序、资源、草稿、缺译及临时新增内容。
- `python3 scripts/verify_resume_sync.py`：553 项通过，核对简历源哈希、论文与来源一致性、原摘要／资源不丢失、11 项获奖、奖学金、隐藏服务项、59 条完整来源行。
- `python3 scripts/check_publications_browser.py`：40 组通过，覆盖 10 个宽度 × 中英文 × 真实及临时论文库，包含年份、CCF 独立行、完整发表来源、导航和无横向溢出。
- 首页实际浏览器检查：12 组通过，覆盖 320、390、768、821、1024、1440px × 中英文；3 段教育、11 项获奖、3 组可见学术服务、奖学金、无 Sub-reviewer、无 JS 错误。桌面及手机截图已查看。
- 运行中预览 19 项检查通过，Mint HTTP 下载哈希仍与用户文件一致，私有文件及测试内容不可访问。
- 公网英文论文页确认 59 篇、59 个完整发表来源、59 个左侧年份，没有摘要或多余 Preprint 标签。
- 新增外链 19 个，16 个可访问；2 个 DOI 最终返回 403，1 个 DBLP BibTeX 返回 429，按源链接保留，未当作错误删除。未重查无改动的旧外链，也未测试 Safari / Firefox 或真实手机硬件。

## 资料与产物

- 逐条来源、修改前后值及简历源哈希：[resume-sync-data.json](resume-sync-data.json)。
- 报告和截图：`.preview/resume-sync-checks.json`、`.preview/resume-home-browser.json`、`.preview/publication-browser-checks.json`、`.preview/resume-external-links.json`，以及 `.preview/resume-home-*.png`、`.preview/publications-refined-*.png`。
- 维护方式：[content/README.md](content/README.md)。复核简历同步的脚本依赖本次本地 `.preview/resume-sync-baseline.json` 和原 GB-Resume 目录。
- 原 PDF 修改保留，未 push、未部署、未停止既有服务。公网预览仍为 `http://111.119.236.134:4001/`，中文 `/zh/`，英文论文 `/publications/`，中文论文 `/zh/publications/`。

下一步：用户在公网预览检查简历同步和统一后的论文格式；缺少下载资源的新增论文可继续补充真实链接。
