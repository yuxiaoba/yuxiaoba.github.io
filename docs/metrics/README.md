# Private readership metrics

The public site remains on GitHub Pages. Only published Digest issues and Tech Notes
load `assets/js/reading-metrics.js`. The script sends one asynchronous JSON request to
`https://111.119.236.134/api/count` when a page becomes visible. It sends the canonical
article path and a random event ID, never query parameters, anchors, search text,
bookmarks, excerpts or a persistent browser identifier. Reloads count as new views;
retrying the same event ID does not. Metrics failure does not block article rendering.

`reading_metrics.enabled` in `_config.yml` controls inclusion. The script additionally
requires the exact production HTTPS origin and skips automation, embedded pages,
DNT/GPC and the local `gy-reading-metrics-disabled` preference. The bilingual
`/privacy/` and `/zh/privacy/` pages let any reader opt out; the owner can use the same
switch to exclude their own browser. No public visitor counter is displayed.

## Metric definitions and limits

Reports are per Shanghai calendar day. A keyed digest of date, network address and
browser User-Agent estimates daily unique visitors. Raw addresses and User-Agent
strings are processed in memory but are not persisted. The secret is private, no
identity is inferred, and identifiers differ across dates. Shared networks and
browsers can merge people; device/network changes can split one person. Daily UVs
must not be summed and called cross-day unique people. Pageviews do not imply a
completed read. Collection starts when enabled; historical counts cannot be inferred.

The intake allowlist is `reading-metrics.json`, generated only from published reading
pages during the normal build. Removed pages, search, bookmarks and arbitrary paths
cannot be counted. CORS is restricted to the production origin; this is not an
authentication or anti-forgery guarantee for a public counter. Basic bot screening,
120 requests/minute per address and a 50,000 event/day storage guard bound simple
abuse. Malicious clients can still forge plausible requests. No statistics are used
to automatically delete or rank research content.

Daily JSON aggregates, visitor digests and hashed event IDs are stored under
`/var/lib/homepage-reading-metrics/live` by a systemd DynamicUser. Atomic replacement,
file locks and fsync protect concurrent updates. No database is installed. Files are
retained for owner-controlled backup/export; backing up this directory needs root.
Invalid/corrupt storage fails closed rather than overwriting the last file. At higher
traffic volumes this file-based storage should be reassessed before raising guards.

## Private access and service

The dashboard is `https://111.119.236.134/admin`; `/api/stats?date=YYYY-MM-DD` returns
only aggregate counts. Both require the owner credentials, use HTTPS, disable caching
and have no cross-origin read permission. No public report API or write-admin API is
provided. Credentials are generated once by `scripts/setup_reading_metrics.py`, and
the login information is kept in `.metrics/admin-access.json` (mode 0600). Do not put
that file or its contents in Git, page templates, URLs or public logs. The settings
file contains a hash of the random password and a separate visitor-HMAC key.

The service loads settings and TLS keys through systemd credentials; its worker is
not root. The project contains code and dependencies, while systemd maintains private
runtime state. There is no public filesystem-serving route. Gunicorn access logs and
its control socket are disabled. The private directory `.metrics/`, build tools and
maintenance documentation are excluded from Jekyll output and snapshots.

Dependencies are installed in `.preview/metrics-venv`, with pip cache in
`.preview/pip-cache`. The locked server packages are in `requirements-server.txt`;
Certbot is pinned separately in `requirements-acme.txt`. CI runs backend tests but
does not install host services or obtain certificates.

The installed units are copied from this directory:

- `homepage-reading-metrics.service`: HTTPS on the checked-free port 443.
- `homepage-reading-metrics-renew.service`: Certbot renewal using the project-local
  ACME directories; its deploy hook restarts only this metrics service so systemd
  reloads certificate credentials.
- `homepage-reading-metrics-renew.timer`: checks twice daily, with a short randomized
  delay. It is separate from the unchanged research-writing timer.

The IP certificate requires public port 80 for the brief standalone ACME challenge.
Its lifetime is about six days, making renewal essential. Do not stop another service
if that port becomes occupied; inspect the conflict and switch to an appropriate
challenge arrangement. CA account and private keys remain in `.metrics/acme`.
See the [Let's Encrypt IP certificate guide](https://letsencrypt.org/2026/03/11/shorter-certs-certbot).

Useful owner commands:

```sh
sudo systemctl status homepage-reading-metrics.service
sudo systemctl list-timers homepage-reading-metrics-renew.timer
sudo journalctl -u homepage-reading-metrics.service
```

Changing the private settings or certificates requires restarting this service;
changing public article content does not, because the catalog follows the existing
atomic preview-release symlink. Credentials must never be passed as command-line URL
parameters. No password is stored in the public frontend.

## Verification and activation

`tests/metrics` covers counting/deduplication, concurrent persistence, daily rotation,
allowed paths/origins, privacy/bot exclusion, authentication, injection, rate limits,
corrupt files and private report dates. `scripts/check_reading_metrics_browser.py`
uses real IP HTTPS and a locally rendered production-origin fixture; it refuses to
write unless the service uses the separate `validation` directory. Browser tests
cover real preflight, counting, opt-out, previews, privacy signals, hidden tabs,
network failure, dashboard authentication and mobile layout. It does not write to
real visitor data.

After tests, change only the private settings' `directory` to
`/var/lib/homepage-reading-metrics/live` and restart the service. Retain validation
data separately; do not copy it into live. Confirm the live report is initially empty
before publishing the frontend. Production checks then use authenticated GETs and
automated/blocked requests that do not increment live counters. Never erase live
files to make a test pass.

To pause future collection, disable `reading_metrics.enabled`, build and publish.
The private historical files remain available. Stopping the metrics service only
affects counts; the GitHub Pages reading site continues to work.
