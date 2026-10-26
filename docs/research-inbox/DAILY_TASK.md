# 每日研究资讯任务

用户于 2026-10-19 授权启用每日处理；Grok 通常在上海时间 08:00 完成上传。计划 08:30 首次运行，12:00 补查。安装与实测结果以 `.handoff/STATUS.md` 和 systemd 状态为准。

## 处理流程

`homepage-research-daily.timer` → `homepage-research-daily.service` → `scripts/research_daily.py run`

1. 校验 `.incoming/research/*.yaml`，忽略 `.part`；优先当天最高 revision，之后按日期补其他待处理批次。最高 revision 校验失败时不回退旧版。
   来源 `published_at` 支持 YYYY-MM、YYYY-MM-DD 或带时区时间；月份精度原样传给写作任务，不能补造具体日期，原始文件和哈希保持。批次 `date` 仍要求完整日期。
2. 根据原始 URL／arXiv ID 去重，跳过网站已经引用的来源。初始化时保留历史批次；用户随后批准的 10 月 1—18 日队列在没有新日更可处理时补写。
3. 在 `.preview/research-jobs/runs/<run>/work/` 启动独立 Codex 任务，使用现有登录和模型配置。允许工作目录写入与读取网络原文，不给原网站额外写权限，不使用 bypass／danger-full-access。
4. 输出双语 Markdown、原图、原文证据与结构化结果。外层校验路径、图片来源、真实文件哈希、条目去向、分类、日期和语言配对。
   X 原帖导出在准备阶段从同日最高 revision JSON 中关联并冻结，详见 X_EXPORTS.md。完整原创技术长文可写独立 Tech Notes；短帖、宣传及缺失全文不自动扩写成长文。每次报告包含实际采用的导出／附件哈希与警告。
5. 在当前网站的隔离副本中构建 Jekyll、KaTeX、Pagefind；检查新页面资源、章节、语言切换、图片解码和 390／1440px 排版。
6. 构建成功且网站源码未并发变化时，添加新文件并原子切换 4000/4001 共用的预览指针。现有文件或 URL 冲突进入待处理，永不覆盖人工稿；失败保留上次正常预览。
7. 正常日更按2026-10-22持续授权，由外层发布器仅暂存报告列出的双语Markdown和配图，逐文件核对哈希。确认本地和远端基线一致、没有无关改动后提交，并原子快进开发分支及master；GitHub Actions再次验证后部署官网。失败保留上次线上版本。
8. 推送与上线分开记录。下次触发先重试未完成发布或检查正式build-info；重用原提交、不重复写作、不消耗调用次数。未解决的冲突／构建失败保留在报告，阻止继续叠加新批次。历史报告和显式手动／一次性补更不自动追溯纳入。

只新增完整中英文内容。修订不会自动删除文章或替换已有页面；目前同名修订会产生候选／失败报告，需人工合并。无新论文不强造空日报，无法核验的来源明确列入 deferred。

## 范围与限额

配置：`docs/research-inbox/daily-config.json`。

- 从 2026-10-19 起接收正常日更；之前日期仅通过用户明确批准的历史队列或显式 --batch 处理。
- 每次定时触发最多处理一批；每日最多启动 2 次写作任务，每个输入哈希最多尝试 2 次。
- 单次写作最长 60 分钟；整个服务最长 75 分钟。失败后等下一次定时触发再试，不在一轮内无限重跑。
- 每批最多24篇论文、8条社交消息，超过仍转待审。2026-10-26用户调整技术资讯规则：最多生成10篇Tech Notes，超过10条输入时由编辑按研究相关性、实质技术贡献和一手证据筛选，未入选记录具体deferred原因；不静默截断或必须凑满。select_important_tech启用此规则，外层再次校验成文篇数；所有输入仍须有明确去向。每日最多两次、每输入两次尝试和单次60分钟不变。
- 这是任务次数和时间上限，不是精确的 token／费用硬上限。模型使用量受当前账号额度约束；登录失效、限额或网络问题会记录失败，不自动切换账号。
- 无邮件／Slack／Grok 主动通知；结果写本地日志和回执。Grok 可只读查看，但不能把输入文件还在视为失败。
- 外层发布器仅对通过验证的正常日更执行Git commit/push，Pages部署由CI控制；写作子进程仍无Git／部署权限。不更新原笔记库，也不安装论文中的系统。

## 观察与手动操作

用户于2026-10-22确认：每日上传无需逐次确认，消费者自行校验、核对来源、生成双语并在构建／页面检查通过后更新本机预览。原有08:30／12:00时间、调用预算和既有文章保护保持。

条目ID中的ASCII大小写和首尾空白可在内存中自动规范化。原始YAML字节与SHA-256保持，隔离任务保留原件，worker读取规范化后的input.json；dry-run、运行报告及处理状态记录intake_corrections。大小写规范化后重名、危险路径字符、来源缺失等仍会拦截，不猜测内容。不修改网址路径或作者名称的大小写。

来源去重识别已核实的vLLM博客域名变体和Techstrong视频的www／非www地址；文章中仍保留原始来源链接。历史未核验材料、冲突或失败有明确回执，保留上次正常预览；只有无法自行解决的内容歧义／需求冲突才需要用户介入，不将普通格式问题变成发布确认。

```bash
systemctl status homepage-research-daily.timer homepage-research-daily.service
systemctl list-timers homepage-research-daily.timer
journalctl -u homepage-research-daily.service -n 80 --no-pager
python3 scripts/research_daily.py run --dry-run
python3 scripts/research_daily.py status
```

程序日志：`.preview/research-jobs/latest-run.json`；状态／历史基线：`state.json`；每次任务有输入快照、work/events.jsonl、work/stderr.log、work/result.json、原文和候选构建。`consumer.lock` 防止并发消费，已有 `build.lock` 防止与预览监听器同时提交构建。

容量超限会在 state 与报告中保留 counts、limits 和 review_reason。若没有可运行输入但仍有待审条目，返回 awaiting_review 并附 pending_reviews，不再用 no_new_batch 掩盖待审积压。修正容量或来源后，只能在核对具体输入哈希与原尝试记录后恢复该项，不清空历史状态或重置调用额度。

初始化命令 `python3 scripts/research_daily.py initialize` 只能执行一次，已有状态时拒绝覆盖。dry-run 不调用模型、不写处理状态。不要删除 state.json 来“重试”，那会丢失去重和重试信息；需要人工检查具体失败或准备更高 revision。

若需要暂停，使用 `systemctl disable --now homepage-research-daily.timer`；该命令暂停未来触发，不取消已在执行的 service。只有用户要求中断当前任务时再停止 service。定时器使用 Persistent=true，服务器错过触发后恢复运行会补一次检查。

## 质量保证的边界

自动结构／浏览器检查不能证明所有论文事实或图解都正确。写作任务必须实际下载和阅读原文、检查图片、记录数字条件，证据不足应延期；用户仍可通过预览审阅内容。测试稿只在隔离候选中构建，不进入真实网站或搜索。

## 按用户要求补指定历史批次

已接收但处于 deferred_history 的资料不会因为定时器启用而自动发表。用户要求补更时，可以显式指定一个完整文件名：

```bash
python3 scripts/research_daily.py run --batch 2026-10-16.yaml --dry-run
python3 scripts/research_daily.py run --batch 2026-10-16.yaml
```

该入口允许被指定的历史日期进入同一写作、校验和预览流程，不改变 start_date，也不批量解除其他历史清单的待办状态。仍遵守每日调用与重试限额、使用最新 revision、拒绝已处理输入和覆盖已有文章。定时 service 不传 --batch，正常日更规则保持。

## 已授权的 10 月 1—18 日补更队列

用户在确认“整段日期尚未发布的内容逐日补齐”后，明确授权此范围；这取代初始化时仅搁置历史清单的处理方式。批准清单位于 `.preview/research-jobs/backfill-queue.json`，逐文件固定 SHA-256，不通过降低 start_date 将任意历史输入一起放行。

原 08:30／12:00 service 不变：先处理正常新日期输入，当前没有新批次可处理时才取历史队列的最早待办。二者共享每天最多 2 次写作、每输入最多 2 次尝试及原时间限额。通常上午完成新日更，中午补一日历史；若新日更重试或迟到资料占用额度，历史顺延。没有新增模型通道、调用额度、定时器或并行消费者。

- 10/1 与 10/16 已有内容去重保留。
- 10/2—10/15 按日期补齐，10/11 使用专门的追加合并。
- 10/11：先写出新论文的双语补充稿，再校验批准时原文件哈希；保留原正文为完全相同的字节子串，保留旧标题／链接／原章节，增加补充正文、目录、数量及标签。原稿若被手工修改，转待审，不覆盖。失败时恢复旧文件和旧预览。
- 10/17 官方内容已发布；其他条目及 10/18 的二手周报／社交线索有明确延期记录，不假称已生成原始论文或技术报告。

整段进度见 `.preview/research-jobs/backfill-progress.json`。`queued` 表示还未写完，`completed` 才表示本批完成；`completed_with_deferred` 与 `needs_review` 不等同于全部条目已发布。队列哈希变化或新 revision 出现时先待审，不擅自扩大批准范围。

## 2026-10-20 一次性优先补更授权

用户明确授权优先完成余下 10/3—10/15 共 13 个日期，免计入项目的每日 2 次写作限额。仅 backfill-queue.json 的 one_off.input_sha256 所列清单享受豁免；清单变更或更高 revision 必须重新核验。正常 daily_runs 与单独 one_off_runs 记账，每输入最多两次尝试及写作时限不变；平台账号本身的使用限制仍适用。

`scripts/research_one_off.py` 串行消费这一固定列表，可在独立 tmux 窗口运行。与定时任务共享消费者锁，等待已经运行的日更完成，不中断它；此后优先补更。列表处理完即退出，不消费其他日期，也不新增定时器。失败或延期在进度和任务报告中如实记录。

## 自动提交与正式发布

配置项 `publication.enabled` 已按用户持续授权启用；不用逐日确认。分支、远端URL与正式域名固定在daily-config.json。

每次生成报告的 `publication` 记录原基线、唯一提交号、状态与错误：`blocked` 为本地修改／冲突／网络问题，`awaiting_deployment` 表示已推送但尚未确认上线，`deployment_failed` 表示GitHub构建／部署失败，`published` 才表示正式站确认包含该提交。不会发送邮件或其他任务消息。

下次08:30／12:00运行优先重试。网络恢复后沿用同一提交；遇到无关已暂存／未提交文件、远端独立变更或构建失败时不会reset、stash、强推或自动合并。原始YAML、证据、缓存和用户其他编辑不会进入提交。处理冲突后再次执行正常run即可重试；dry-run不会推送或改变报告。

关闭自动发布可将 `publication.enabled` 改为false；已生成内容、待办回执、当前官网与定时器保持。写作流程继续使用现有额度和本机预览。详细发布与回退方式见 ../content/DEPLOYMENT.md。
