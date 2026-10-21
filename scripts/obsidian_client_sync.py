#!/usr/bin/env python3
"""Optional client command: commit only reading directories; no automatic configuration."""
import argparse,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vault',type=Path,required=True);p.add_argument('--asset-dir',action='append',default=[]);p.add_argument('--apply',action='store_true');p.add_argument('--push',action='store_true');a=p.parse_args()
root=a.vault.resolve()
def git(*args,check=True):return subprocess.run(['git','-C',str(root),*args],check=check,text=True,capture_output=True)
paths=['Paper','Tech Report']+a.asset_dir
for path in paths:
 if not (root/path).resolve().is_relative_to(root) or Path(path).is_absolute():raise SystemExit('Asset paths must stay inside the vault')
if git('diff','--cached','--quiet',check=False).returncode:raise SystemExit('Existing staged changes: refusing to include them in an automatic commit')
print(git('status','--short','--',*paths).stdout)
if not a.apply:raise SystemExit('Dry run only. Add --apply to commit scoped changes, and --push to send them.')
git('add','-A','--',*paths)
if git('diff','--cached','--quiet',check=False).returncode:
 git('commit','-m','Update published-reading sources')
if a.push:
 branch=git('branch','--show-current').stdout.strip()
 if not branch:raise SystemExit('Detached HEAD: refusing push')
 git('fetch','origin',branch)
 if git('merge-base','--is-ancestor','FETCH_HEAD','HEAD',check=False).returncode:
  raise SystemExit('Remote has changes requiring reconciliation; local commit kept, no merge/rebase/force-push attempted')
 git('push','origin',f'HEAD:{branch}')
print('Scoped client sync finished. Unrelated files were not staged.')
