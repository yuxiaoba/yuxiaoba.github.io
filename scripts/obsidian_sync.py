#!/usr/bin/env python3
"""Preflight or export into a new isolated candidate; never write back to a vault."""
import argparse,json,shutil,sys
from pathlib import Path
from obsidian.exporter import Exporter,ExportError,apply_files,plan_changes
ROOT=Path(__file__).resolve().parents[1]
IGNORE=shutil.ignore_patterns('.*','node_modules','vendor','_site','__pycache__','.bundle','.sass-cache')
def snapshot(site,destination):
 shutil.copytree(site,destination,ignore=IGNORE)
 manifest=site/'.sync-state/manifest.json'
 if manifest.exists():
  dest=destination/'.sync-state/manifest.json';dest.parent.mkdir(parents=True);shutil.copy2(manifest,dest)
def main():
 p=argparse.ArgumentParser();p.add_argument('--vault',type=Path,required=True);p.add_argument('--site',type=Path,default=ROOT);p.add_argument('--dry-run',action='store_true');p.add_argument('--output',type=Path);p.add_argument('--report',type=Path);p.add_argument('--image-reviews',type=Path)
 a=p.parse_args();exporter=Exporter(a.vault,a.image_reviews)
 try:
  files=exporter.run();_,_,changes=plan_changes(a.site,files);report={**exporter.report(),'changes':changes}
  if not a.dry_run:
   if not a.output:raise ExportError('--output is required; use the runner for transactional application')
   if a.output.exists():raise ExportError('Isolated output must not already exist')
   if a.output.resolve().is_relative_to(a.vault.resolve()):raise ExportError('Output must not be inside the vault')
   if a.output.resolve().is_relative_to(a.site.resolve()) and not a.output.resolve().is_relative_to(a.site.resolve()/'.preview'):raise ExportError('Nested candidate output must be inside excluded .preview')
   snapshot(a.site,a.output);apply_files(a.output,files)
  code=0
 except Exception as exc:
  report={**exporter.report(),'fatal':str(exc),'changes_applied':False};code=1
 if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps(report,ensure_ascii=False,indent=2));return code
if __name__=='__main__':sys.exit(main())
