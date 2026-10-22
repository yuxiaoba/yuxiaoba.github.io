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

The daily server job still updates the local preview only. This workflow does not
commit or push incoming daily material automatically and does not change its timer.
