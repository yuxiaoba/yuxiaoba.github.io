# 实施与验收记录

日期：2026-10-15（Asia/Shanghai）。全部工作在 AgentBench 的 `/home/GB-Project/yuxiaoba.github.io` 完成，未 push、合并或部署。

## 已实现

- Jekyll 双语首页、完整论文库、Paper Digest、厨房手记及文章阅读页。英文根路径 `/`，中文 `/zh/`，旧 `/publications.html` 保留。
- 复用确认稿的暖纸色、字体、留白、拱形真实头像及响应式断点；保留完整简介、单位、邮箱、联系方式、两条研究主线、教育、五项获奖和学术服务。
- 全部 41 篇论文保留，标题、作者顺序和来源原文经逐条检查。旧字段与新模板共存；资源键兼容、空链接不显示。
- 英文 12 条 News 全部保留；中文仅使用确认稿已有的两条译文，可用 `title_zh` 补充后续译文。
- Digest / Kitchen 根据语言目录推导语言，按相同相对文件名配对；按日期更新列表、首页入口和归档，草稿无正式输出，缺译文返回目标栏目并显示本地化提示。
- 没有发布示例文章或示例食物照片。当前真实 Digest / Kitchen 内容为空，使用空状态。
- 内容维护文档及五份模板见 [content/README.md](content/README.md)。

## 验证结果

| 检查 | 结果 |
| --- | --- |
| `bundle3.2 exec jekyll build --strict_front_matter` | 通过 |
| `bundle3.2 exec jekyll build --safe --strict_front_matter --destination .preview/safe-site` | 通过，中文论文页仍为 41 篇 |
| `python3 scripts/verify_site.py` | 784 项通过：双语路由、资料和论文原文、本地资源与锚点、发布和草稿、缺译、嵌套配对、厨房正文图片、排除文件、PDF 哈希 |
| `python3 scripts/check_browser.py` | 180 组通过：真实页面和隔离文章样例 × 10 个宽度，另含导航、语言切换、缺译提示、键盘、触屏目标、字体和控制台检查 |
| `python3 scripts/verify_preview.py` | 19 项通过：实际 HTTP 页面、实际下载 PDF、404 排除规则、tmux 存活及回环监听 |
| `python3 scripts/check_external_links.py` | 60 个外部资源链接，46 个可访问，其余 14 个返回 HTTP 403 |
| `git diff --check` | 通过 |

浏览器：Chromium。宽度：320、390、600、601、768、820、821、1024、1440、1920px。已查看桌面、手机、论文页及文章布局截图，未发现横向溢出或损坏图片。Manrope、Noto Serif SC 的实际文字字体加载检查通过。没有测试 Safari、Firefox 或真实手机硬件。

测试文章只写入临时目录的仓库副本，构建结果在 `.preview/fixture-site/`；不进入内容目录或实际预览。测试报告和截图位于 `.preview/`，不提交也不发布。实际预览输出为 `.preview/site/`，不会覆盖仓库历史上跟踪的 `_site/`。浏览器运行文件在 `.preview/browsers/`，Ruby gems 在 `vendor/bundle/`。

## 已处理与保留的历史问题

- TopoMAD 的 PDF / BibTeX 路径从误拼的 `topomd` 修为仓库实际存在的 `topomad`。
- ServiceMesh 原 BibTeX 链接实际指向 FaaSDeliver，已清空并加注释，未编造替代引用。
- T-Rank 的 PDF / BibTeX、ServiceMesh 的 PDF 在原仓库缺失，下载入口不显示，DOI 及其他资源保留；需要用户后续提供文件才能补齐。
- ChangeRCA PDF 保持用户删除状态，不显示对应下载入口，DOI / 项目 / 幻灯片 / BibTeX 保留。
- 14 个出版社链接返回 403，无法从本环境确认最终页面内容；未将访问限制当作链接失效或删除依据。
- Mint 原修改保持不变，SHA-256：`689902a7753a9fa3c9ba031e3be338c6d7e120a1399c4f600c67caf6427f4c03`；通过 HTTP 下载得到相同哈希。

## 运行中预览

- 地址：`http://127.0.0.1:4000/`；中文：`http://127.0.0.1:4000/zh/`。
- tmux：`homepage-preview:jekyll`；查看：`tmux attach -t homepage-preview`。已在 tmux 中时用 `tmux switch-client -t homepage-preview`。
- 日志：`.preview/jekyll.log`；状态：`.preview/preview.json`。
- 脱离窗口：`Ctrl-b`，再按 `d`。预览继续运行；服务器重启不会自动恢复，未设置系统服务或定时任务。
- 启动脚本：`python3 scripts/start_preview.py`。4000 已占用时会另选端口，不停止现有服务；不要为查看当前预览重复启动。

在你的电脑上使用实际 AgentBench SSH 地址：

```bash
ssh -N -L 4000:127.0.0.1:4000 <你的 AgentBench SSH 地址>
```

随后打开 `http://127.0.0.1:4000/zh/`。若电脑本地 4000 被占用，可将 `-L` 的第一个端口改成 4001，再打开本地 4001。

## 2026-10-15：用户授权公网预览

- 在保留原 `127.0.0.1:4000` Jekyll 预览的同时，新增仅提供 `.preview/site/` 的静态预览，监听 `0.0.0.0:4001`。
- 公网入口：`http://111.119.236.134:4001/zh/`（中文）及 `/`（英文）。主机网卡为 `192.168.0.205`，公网出口经直连检查为上述 IP。
- tmux 窗口：`homepage-preview:public`；日志：`.preview/public-preview.log`；启动命令：`bash scripts/public_preview.sh 4001`。原 `homepage-preview:jekyll` 窗口继续构建与监听 4000，生成页面的更新也会反映在公网预览。
- 本机通过公网 IP 和内网 IP 访问均返回 HTTP 200；两种语言的 8 个栏目页面均通过，Mint 下载哈希正确，源代码/交接/测试路径为 404，共 15 项公网入口内容检查通过。独立外部浏览器检查工具不支持此地址，尚未获得异地网络访问证据。
- 已确认两个 tmux 窗口均存活，未停止已有服务，未修改主机防火墙、路由或 GitHub 部署配置，未 push。
- 公网预览状态及验证范围保存于 `.preview/public-preview.json`。下一步由用户从自己的网络直接打开公网链接；如其网络无法访问，再检查上游安全组/端口映射，当前本机公网回环检查成功。

## 2026-10-15：论文页面持续优化

- 根据用户反馈将年份导航移到桌面右侧，采用 sticky 定位；滚动时高亮当前年份，点击保留可分享的年份锚点。<=820px 转为顶部换行导航，触屏区域至少 44px。
- 通讯作者的 `†` / `#` / `✉️` 在页面统一为 `✉️`，含中英文无障碍说明；共同第一作者 `*` 保留。仅更改渲染，原作者记录未改。
- 已查明旧话题缺失原因：真实论文没有 `topics` 字段，确认稿四条话题未迁移。现把 L4、COCA、AlertGuardian、ChangeRCA 的确认标签及译文恢复到 `_data/publication_topics.yml`，新记录显式填写的 `topics` 优先；没有依据的其余历史话题未猜填。
- `python3 scripts/verify_site.py`：962 项通过，含原作者姓名与顺序、通讯标记、四篇话题、临时新增话题、草稿和缺译回归。
- `python3 scripts/check_publications_browser.py`：40 组通过（10 个宽度 × 中英文 × 真实/临时论文库），验证侧栏位置、滚动停留、高亮、年份跳转、旧链接深链接、长标题、无横向溢出和无 JS 错误。桌面和手机截图已人工查看。
- 公网 `/zh/publications/` 实际响应已确认包含 41 篇论文、7 个侧栏年份、信封标记和四组已确认话题。普通构建及 `git diff --check` 通过。未重新检查无改动的外部资源或其他浏览器。
- Mint 哈希及 ChangeRCA 删除状态保持不变；未 push、未部署、未停止任何已有预览。
- 下一步：用户刷新 `http://111.119.236.134:4001/zh/publications/` 或英文 `/publications/` 查看；如需扩展其他论文话题，再按确认分类维护数据。

## 2026-10-15：配色改为白底蓝色

- 用户最新要求替代最初暖纸色方案：参考 https://pinjiahe.github.io/ 的实际样式和浏览器截图，采用纯白 `#fff` 背景、正文 `#282d34`、次要文字 `#57616d`、分隔线 `#e3e8ed`、强调蓝 `#2265aa`、选中浅蓝 `#edf4fb`。本轮更改全站配色，原排版、字体、头像与年份侧栏保留。原确认稿作为历史参考不覆盖。
- 中文话题已核对：L4 为“大模型训练、故障诊断、日志分析”，其他已确认话题也有中文；英文页显示对应英文，论文标题保留原文。话题数据无需修改。
- 标准 Jekyll 构建及 `git diff --check` 通过。临时浏览器检查覆盖 8 个双语栏目路由 × 320/390/1440px，共 24 组，验证实际背景、正文和强调色、无横向溢出、无 JS 错误及话题中英切换。已人工查看参考站及新版桌面/手机截图。报告 `.preview/palette-checks.json`，截图 `.preview/white-blue-*.png`。
- 公网 CSS 实际响应已验证新配色，不含旧奶油底色。仅样式变更，未重跑内容发布临时样例和未变更的外链检查。
- Mint 哈希和 ChangeRCA 删除状态保持不变；未 push、未部署、未停止现有服务。下一步：用户刷新公网首页或论文页验收配色。

## 2026-10-15：采用 CUHK 紫金配色

- 用户不喜欢蓝色，最新配色改为 CUHK 紫与金。紫色 `#750f6d`、金色 `#dda300` 来自 CUHK 官方校徽指南 RGB（117,15,109 / 221,163,0），来源：https://www.iso.cuhk.edu.hk/english/documents/resource/cuhk-emblem/emblem-guideline.pdf 。校色说明：https://cuhk.edu.hk/chinese/aboutus/mission.html 。这是个人站配色调整，未添加校徽或官方身份声明。
- 保留纯白背景，正文 `#2c2630`，次要文字 `#655e69`，分隔线 `#e7e1e9`，淡紫选中背景 `#f6eff7`；链接和姓名标识用紫色，金色只用于导航下划线和年份选中边线，正文不使用金色。
- Jekyll 构建和 `git diff --check` 通过；24 组浏览器检查（8 个双语路由 × 320/390/1440px）通过，验证真实配色、话题译文、无横向溢出和无 JS 错误。已查看新版截图；报告 `.preview/cuhk-palette-checks.json`，截图 `.preview/cuhk-purple-gold-*.png`。
- 公网 CSS 已确认新配色并移除蓝色强调值。本轮未改正文和发布逻辑，未重跑临时内容全套或外链检查。原 PDF 状态未变；未 push、未部署，两个 tmux 预览继续运行。
- 下一步：用户刷新公网首页验收 CUHK 配色；本条为当前配色决定，取代之前暖纸色与白底蓝色。
