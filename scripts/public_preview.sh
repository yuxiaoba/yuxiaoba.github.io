#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
port="${1:-4001}"
python3 -u scripts/serve_preview.py --bind 0.0.0.0 --port "$port" --directory .preview/current 2>&1 | tee -a .preview/public-preview.log
