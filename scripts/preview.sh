#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
port="${1:-4000}"
mkdir -p .preview
python3 -u scripts/serve_preview.py --bind 127.0.0.1 --port "$port" --directory .preview/current 2>&1 | tee -a .preview/jekyll.log
