# Paper close readings / 论文精读

Use the existing `_digest/zh/` and `_digest/en/` collections for independent close readings. No new collection, navigation item, search type, scheduler, or topic vocabulary is introduced.

- Set `paper_deep_read: true` and `long_read: true`. The header, Paper Digest listing, and homepage recent entries display a localized close-reading label. The flag also opts into the existing sidebar reader; it does not make the article a topic guide.
- Keep the same relative filename in both languages, with paired `permalink` values. Prepare titles, summaries, text, tables, figure captions and images in both languages before local publication.
- Use the review date in `date`; record `published_at` for same-day ordering. The paper version and inspected code commit belong in the body/provenance, not as invented publication dates.
- Keep tags within `_data/note_tags.yml`. “Paper close reading” is a content label, not a ninth topic.
- Mark assistance explicitly and avoid attributing the paper to the site owner. Distinguish author-reported results, code inspection and analysis. Do not imply benchmark reproduction.
- Source prose is Markdown. Diagrams are local PNGs under `assets/images/digest/paper-close-readings/`, with accessible alternative text, captions and the existing image viewer. These are explanatory diagrams, not figures extracted from the paper.
- `provenance.json` records source versions/hashes, inspected code commits, assistant translations and diagram specifications. Diagrams were rendered from these specifications using the project-local, pinned `answer-me-with-html` renderer and Chromium; that temporary tooling is not a website runtime dependency.

Validation uses `scripts/verify_site.py` for ordinary publishing, close-reading fixtures, draft exclusion and missing translations. Browser checks must cover both languages, reciprocal links, sidebar/phone contents, image zoom, homepage/list labels, search and private bookmarks.

These manually prepared close readings are not enrolled in the automated daily publisher. Production publication requires explicit owner authorization; the owner authorized publication of this first pair on 2026-11-12.

Paper close readings are independent paper articles, not Tech Notes and not dated daily digests. Do not set `daily_digest`. Search uses the existing `paper` type. The initial Tech preview URLs remain as unindexed redirects.

## Keep follow-up work proportional

Start from the existing source manifest and article pair. Reuse verified evidence and diagrams; refresh sources when the version, status or claim needs checking. Patch the affected section in both languages rather than rewriting the full reading.

Group related changes into one validation batch. A table or bold-format fix needs source/rendered checks for the affected articles and the specific failure, including mobile behavior when relevant. A new article type, collection move, template change or search/filter change still needs the full applicable build, fixture and browser validation. Repeat previously passing checks only when a subsequent change can invalidate them.

Keep Markdown tables separated from preceding headings or prose by a blank line. Put a label's colon outside its bold markers. Check rendered text for unparsed Markdown before updating a preview.

Token estimates are planning ranges, not observed consumption. Distinguish a fresh paper-and-code review from adapting existing research, and specify whether translation, diagrams, reasoning tokens and repeated conversation history are included. No fixed token quota or new publishing authorization is introduced here.
