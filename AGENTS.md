# Homepage development instructions

Read `.handoff/START_HERE.md`, `.handoff/STATUS.md`, and `.handoff/content/README.md` before editing. The accepted design is `.handoff/reference/approved-homepage.html`.

Continue this project on AgentBench in `/home/GB-Project/yuxiaoba.github.io`. Do not assume that local Mac paths or conversation history are accessible from the remote task.

## Think before coding

- State assumptions before implementing. Surface material ambiguity and tradeoffs.
- Prefer the smallest change that meets the confirmed requirements.
- Do not invent papers, news, personal information, food stories, or user-provided translations.

## Simplicity first

- Keep the Jekyll / GitHub Pages architecture and Markdown content.
- No database, separate CMS, speculative framework migration, or extra services.
- Do not add features beyond the agreed scope.

## Surgical changes

- Preserve existing user changes, especially the modified Mint PDF and deleted ChangeRCA PDF.
- Preserve all genuine publication records and profile content.
- Do not remove unrelated existing code simply because it is unused.
- Do not reset, clean, overwrite, or force-push user work.

## Verify completion

- Build the site and verify actual rendered pages, both languages, resource links, and responsive behavior.
- Test content-driven publishing, draft exclusion, and missing translations with temporary fixtures; do not publish fixtures.
- Report which checks passed, which were not run, and any remaining blockers.
- Record meaningful progress and the next actionable step in `.handoff/STATUS.md`.

Do not push, merge, deploy, schedule jobs, or send messages to other tasks without the user's authorization. Preparing this checkout does not mean a separate remote task has been started.

## Bilingual content updates (user-confirmed 2026-10-19)

- New or revised Paper Digest and Tech Notes content must be prepared and published locally in Chinese and English in the same batch. A Chinese-only update is not complete.
- Keep paired files under the same relative path in the zh/en collections. Translate titles, summaries, body text, figure captions/alt text, and table labels; preserve original paper/report titles, names, and factual results.
- Before switching the preview, check both language versions, reciprocal language links (including per-paper anchors for daily digests), language-specific lists and search, and responsive behavior.
- Record assistant-created translations as such in internal provenance; do not present them as translations supplied by the user.
- Keep draft exclusion and missing-translation fallback tests, but do not use fallback as a substitute for completing both languages for an actual content update.
- Publishing permission is separate from translation requirements; use the explicit daily-publishing authorization below for verified daily batches.

## Note topics and date filters (user-confirmed 2026-10-19)

- Keep Paper Digest / Tech Notes topics in the shared `_data/note_tags.yml` vocabulary: currently 8, never more than 10 without a new user decision.
- Use stable topic IDs in Markdown, with Chinese and English display labels. Do not introduce ad-hoc venue/year/framework tags into the user-facing filter list.
- Year/month filtering uses the published note or digest's date. Drafts and untranslated content must not leak into the other language's filters or search index.

## Life section (user-confirmed 2026-10-19)

- The former Kitchen section is now named Life / 生活, covering genuine travel, photographs, food and everyday notes.
- Navigation and collection entrances use /life/ and /zh/life/. Keep /kitchen/ and /zh/kitchen/ as compatibility redirects.
- Life is accessed through the top navigation only; do not restore a Life block on the homepage. Homepage order starts with the identity card, full About Me biography, academic News, then Recent Updates (user-confirmed 2026-10-21).
- Keep the existing _kitchen collection and article URLs for compatibility; do not invent personal stories or photographs to fill the empty section.

## Daily research task (user-authorized 2026-10-19)

- Grok normally finishes uploads at 08:00 Asia/Shanghai. The authorized server workflow runs at 08:30 with a 12:00 catch-up, consuming new ready YAML batches from `.incoming/research/`.
- On 2026-10-22 the user confirmed standing authorization: daily uploads do not need another confirmation. Automatically validate, repair unambiguous formatting, verify sources, prepare both languages, build, and update the local preview after checks pass. Preserve original input bytes and record every normalization. Ask only about genuinely unresolved ambiguity or conflicting requirements; the subsequent daily-publishing authorization below extends this to verified daily commits and production publication.
- Prefer the current day's newest valid revision before older pending daily batches. A malformed newest revision must not silently fall back to an older one. Normalize ASCII item-ID case and surrounding whitespace only; reject collisions and unsafe IDs, and retain the last good preview on failure.
- Generate in an isolated job directory, verify sources and paired Chinese/English output, then build and check the candidate before updating the local preview. Only the outer publisher may commit and publish verified daily batches under the authorization below; the isolated writing task cannot push.
- Initial timer setup deferred historical files. The user subsequently explicitly authorized the full 2026-10-01–2026-10-18 backfill. Consume only the approved hash-pinned backfill queue after new daily inputs, within the unchanged shared daily/attempt/time limits.
- On 2026-10-20 the user superseded that shared-budget ordering for the remaining October 3–15 batches: prioritize these 13 exact approved input hashes and account for their calls separately from the normal daily quota. Keep attempt/time limits and the single consumer; let an already-running daily task finish. This exemption does not alter account/platform usage limits or authorize other historical inputs.
- Existing manual articles remain protected. The approved October 11 merge may only append new readings to both language versions, preserving original body bytes, anchors and metadata identity under an expected-hash check; no arbitrary rewrites or deletions.
- Enforce a single consumer, bounded run time and retry count, preserve the last good preview on failure, and record results under `.preview/research-jobs/`.
- On 2026-10-27 the user rejected count-based curation. Curate papers, tech and social every day by substantive contribution, relevance, primary evidence and genuine novelty, without publication-count limits or forced rejection ratios. Distinguish deep reads, briefs, evidence-based exclusions, unverified sources and unfinished work; never label missing evidence or runtime limits as low value. Keep a complete internal selection audit and identical bilingual selections. Preserve file-size/daily/attempt/time safeguards, existing content and month-precision source dates. The owner-feedback/deletion interface is deferred; do not add it or retroactively withdraw notes.
- The user subsequently approved the specific existing-content audit on 2026-10-27. Apply only its confirmed withdrawals/merges, preserving bilingual source drafts and recovery history. `docs/research-inbox/curation-exclusions.json` prevents exact withdrawn sources from being reintroduced; it is not a domain/topic ban or permission for further automatic withdrawals. Do not build the deferred owner-feedback service.

## Daily production publishing (user-authorized 2026-10-22)

- The user explicitly authorized daily commit, push and production publication after validation, without per-day confirmation. The existing 08:30/12:00 timer and writing quotas remain unchanged.
- The outer publisher may commit only the successful daily report's hash-verified bilingual Markdown and images, then atomically fast-forward the development branch and master. GitHub Actions must pass before deploying; do not include unrelated edits or unpushed local code, force-push, reset, stash or auto-merge conflicts.
- A failed push is retried using the same recorded commit on the next timer invocation, before generating more content. Confirm deployment using the production build-info, rather than treating a push as proof of publication. Preserve the previous live site on build failure and record blocked work locally.
- Existing historical reports are not retroactively enrolled. Explicit manual/one-off backfills keep their existing publication scope. Raw inboxes and private evidence stay excluded; the isolated writer still has no Git or deployment authority.

## Visual direction (user-authorized 2026-10-19)

- The user superseded the purple/gold UI on 2026-10-21: use the original site's Lato typography, Chinese sans-serif, neutral dark text, light-gray outer background, white content and blue links. `assets/css/editorial.css` remains the final visual layer. The bilingual research illustrations also use the blue-gray palette (v3-blue), as confirmed on 2026-10-21.
- Preserve the homepage sequence and all genuine profile content. Use the compact mobile identity/portrait layout, highlighted latest digest and adjacent Tech Notes. After the identity card, use About Me → News → Recent Updates; Life remains navigation-only.
- Publication years are on the left on desktop and above the list on mobile. Keep CCF on its own line, original author/venue records and the owner's correspondence marks.
- Search refinements use native details/summary with an active-filter count. Keep keyword search directly visible, paired language indexing, and the existing eight-topic vocabulary.

## News and portrait consistency (user correction 2026-10-19)

- Keep academic News aligned across Chinese and English: translate every published English record using `title_zh` or `_data/news_zh.yml`, preserving dates, venue links and claims. New or revised News needs both languages.
- Use a single portrait frame aligned with the introduction's top edge; do not restore the offset decorative outline.

## Private readership metrics (user-authorized 2026-10-28)

- The user authorized a small self-hosted HTTPS counting service on the existing server, compatible with GitHub Pages and without a database. This is an exception to the earlier no-extra-services rule only for article metrics; the owner-feedback/removal interface remains deferred.
- Count published Digest issues and Tech Notes only. Keep the dashboard owner-authenticated. Never put credentials, certificate keys, visitor digests or raw metrics into Git or static output. `.metrics/` is private; persistent runtime data uses the dedicated systemd state directory.
- Use project-local dependencies, a non-root runtime, automatic IP-certificate renewal and isolated validation storage. Keep the research timer and existing preview services intact. Exclude previews, automation, search, bookmarks and reader opt-outs; do not infer completed reading or use popularity to withdraw research.
