# GitHub Pages publishing

The production site is https://yuxiaoba.github.io/. Pages must use **GitHub Actions**
as its publishing source (Settings → Pages → Build and deployment → Source).

`.github/workflows/pages.yml` builds commits on `master` and
`codex/warm-bilingual-homepage`, and pull requests targeting `master`.
Only successful builds of `master` can deploy. A failed build leaves the previous
published site intact. The workflow can also be started manually on `master`.

The pipeline installs the locked Ruby and npm dependencies and Python requirements,
tests the Obsidian and daily publishing rules, and runs `scripts/verify_site.py`.
This builds Jekyll, renders KaTeX, generates bilingual Pagefind indexes, checks local
resources, and tests draft exclusion and missing translations with isolated fixtures.
Only `.preview/content-test-site` is uploaded, never the fixture output, raw inbox,
local preview state, or historical tracked `_site` directory.

`/build-info.json` identifies the source commit actually served by Pages. After a
release, check it and the Chinese/English homepages, latest reading notes, search,
images, math, and mobile layout on the production domain.

Source development remains on the development branch. To release an approved
version, fetch remote changes, verify that `master` is an ancestor of the tested
commit, then fast-forward `master` without force-pushing. If histories diverge,
review and resolve the differences before publishing. For rollback, revert the
problematic change on `master` and let the same checks build the restored version;
do not rewrite branch history.

On 2026-10-22 the user authorized automatic production publication of validated
normal daily batches. `scripts/research_publish.py`, called by the existing daily
consumer, commits only the successful report's hashed bilingual notes and images.
It requires matching local/remote baselines and no unrelated work, then pushes both
development and production refs atomically without force. The Actions checks above
remain the production deployment gate. Private input and evidence are never staged.

Network failures retain the same commit for the next timer retry. Unrelated edits,
divergent refs, or altered output block publication without changing user files.
Pending publication is reconciled before another writing task; retries do not spend
writing quota. `publication.status` in each job report distinguishes `blocked`,
`awaiting_deployment`, `deployment_failed`, and `published`. A successful push is
not reported as live until production `/build-info.json` confirms that commit (or
a known descendant). A build failure leaves the previous production site intact.

Only newly completed normal daily jobs are enrolled. Previous reports and explicit
manual/one-off backfills are not retroactively pushed. Disable future automatic
publication with `publication.enabled: false` in daily-config.json; this leaves
pending reports and commits intact and does not disable local generation.
