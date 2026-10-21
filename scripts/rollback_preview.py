#!/usr/bin/env python3
"""Explicit preview-only rollback. Does not change source Markdown or Git."""
import argparse
from build_site import ROOT
from obsidian.transaction import activate,locked
p=argparse.ArgumentParser();p.add_argument('release',help='Existing release directory name');a=p.parse_args()
with locked(ROOT):activate(ROOT,ROOT/'.preview/releases'/a.release)
print('Preview switched to '+a.release+'; source files were not changed.')
