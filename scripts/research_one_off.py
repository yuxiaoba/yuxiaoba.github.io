#!/usr/bin/env python3
"""Drain only an explicitly approved hash-pinned one-off queue; no scheduler changes."""
import json
import time
from research_daily import ROOT, IntakeError, run, now

def main():
    config = json.loads((ROOT / 'docs/research-inbox/daily-config.json').read_text())
    while True:
        try:
            report = run(ROOT, config, one_off=True)
        except IntakeError as error:
            if 'Another research consumer' not in str(error): raise
            print(json.dumps({'at': now(), 'status': 'waiting_for_consumer'}), flush=True)
            time.sleep(30)
            continue
        print(json.dumps(report, ensure_ascii=False), flush=True)
        if report['status'] in {'no_new_batch', 'input_errors', 'awaiting_review'}:
            return 1 if report['input_errors'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
