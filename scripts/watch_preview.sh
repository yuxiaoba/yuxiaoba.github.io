#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -u scripts/watch_site.py 2>&1 | tee -a .preview/build.log
