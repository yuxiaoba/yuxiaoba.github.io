#!/usr/bin/env python3
"""Build current website edits into immutable releases, retaining the last good one."""
import argparse,json,shutil,tempfile,time,uuid
from pathlib import Path
from build_site import build,ROOT
from obsidian_sync import snapshot
from obsidian.transaction import locked,fingerprint,activate,atomic_json

def build_preview(root):
 with locked(root):
  before=fingerprint(root);jobs=root/'.preview/jobs';jobs.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='preview-',dir=jobs) as name:
   job=Path(name);source=job/'source';snapshot(root,source);output=job/'site';result=build(source,output)
   if fingerprint(root)!=before:raise RuntimeError('Source changed while building; retaining previous preview')
   release=root/'.preview/releases'/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]);release.parent.mkdir(parents=True,exist_ok=True)
   shutil.move(str(output),release);atomic_json(root/'.preview/release-meta'/f'{release.name}.json',{'kind':'website-preview','fingerprint':before,'build':result});activate(root,release)
   print('Activated '+str(release),flush=True)
   return before
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--once',action='store_true');p.add_argument('--site',type=Path,default=ROOT);p.add_argument('--interval',type=float,default=3);a=p.parse_args();previous=None
 while True:
  try:
   current=fingerprint(a.site)
   if current!=previous:previous=build_preview(a.site)
  except Exception as e:
   print('Build failed; previous preview retained: '+str(e),flush=True)
   if a.once:raise
   # Wait for another source change instead of rebuilding a broken version endlessly.
   previous=current if 'current' in locals() else None
  if a.once:break
  time.sleep(a.interval)
