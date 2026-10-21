#!/usr/bin/env python3
"""Single scheduled/manual sync transaction; scheduling is configured separately."""
import argparse,json,shutil,sys,tempfile,time
from pathlib import Path
from obsidian.exporter import Exporter,ExportError,apply_files,plan_changes,digest
from obsidian.transaction import locked,pull,source_snapshot,fingerprint,commit_release,atomic_json
from obsidian_sync import snapshot
from build_site import build
ROOT=Path(__file__).resolve().parents[1]
def run(args):
 site=args.site.resolve();report={'started':time.strftime('%Y-%m-%dT%H:%M:%S'),'success':False,'applied':False}
 exporter=None
 try:
  with locked(site):
   repo=args.source_repo.resolve()
   if repo==Path('/home/Obsidian').resolve():raise ExportError('Use the dedicated source checkout; /home/Obsidian is protected')
   sha=pull(repo,args.branch,update=args.pull and not args.dry_run);report['source_commit']=sha
   jobs=site/'.preview/jobs';jobs.mkdir(parents=True,exist_ok=True)
   with tempfile.TemporaryDirectory(prefix='sync-',dir=jobs) as tmp:
    job=Path(tmp);vault=job/'vault';source_snapshot(repo,sha,vault)
    exporter=Exporter(vault,args.image_reviews)
    files=exporter.run();old,new,changes=plan_changes(site,files)
    sources={f'{n.collection}/{n.data["lang"]}/{n.data["id"]}':digest(n.path.read_bytes()) for n in exporter.notes if n.public}
    report.update(exporter.report());report['changes']=changes
    if args.dry_run:report.update(success=True,dry_run=True);return report
    if any(not a['reviewed'] for a in exporter.assets.values()):raise ExportError('New/changed images require visual review; see asset hashes in the report')
    before=fingerprint(site)
    last=site/'.sync-state/last-success.json'
    if last.exists():
     previous=json.loads(last.read_text())
     if previous.get('digest_grouping')=='daily-v1' and previous.get('fingerprint')==before and previous.get('source_commit')==sha and old.get('sources',{})==sources and not changes['write'] and not changes['remove']:
      report.update(success=True,unchanged=True);return report
    candidate=job/'source';snapshot(site,candidate);apply_files(candidate,files)
    output=job/'site';report['build']=build(candidate,output)
    report.update(commit_release(site,output,files,sources,report,before))
    report.update(success=True,applied=True)
    atomic_json(last,{'digest_grouping':'daily-v1','fingerprint':fingerprint(site),'source_commit':sha,'release':report['release']})
 except Exception as exc:
  if exporter:report.update(exporter.report())
  report['error']=str(exc)
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source-repo',type=Path,default=Path('/home/Obsidian-sync'));p.add_argument('--site',type=Path,default=ROOT);p.add_argument('--branch',default='main');p.add_argument('--pull',action='store_true');p.add_argument('--dry-run',action='store_true');p.add_argument('--image-reviews',type=Path,default=ROOT/'docs/obsidian/image-reviews.json');p.add_argument('--report',type=Path,default=ROOT/'.preview/obsidian-last-run.json')
 args=p.parse_args();result=run(args);atomic_json(args.report,result);print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(0 if result['success'] else 1)
