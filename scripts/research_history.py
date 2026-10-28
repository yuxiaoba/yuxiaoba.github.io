"""Hash-pinned August/September 2026 queue, independently authorized by the owner."""
import argparse
import datetime as dt
import json
import time
from pathlib import Path

QUEUE = '.preview/research-jobs/aug-sep-2026-queue.json'
BOUNDS = ['2026-08-01', '2026-09-30']


def load_queue(root):
    from research_daily import require
    path=root/QUEUE
    if not path.exists():return {'enabled':False,'entries':[]}
    value=json.loads(path.read_text())
    require(value.get('version')==1 and value.get('range')==BOUNDS and isinstance(value.get('entries'),list),'Invalid August/September approval')
    require(value.get('quota_exempt') is True and value.get('publication_authorized') is True,'Historical queue requires quota and publication authorization')
    names=[entry['file'] for entry in value['entries']]
    require(len(names)==len(set(names)),'Duplicate history approval entry')
    return value


def require_approval(root, filename, digest):
    from research_daily import require, read_batch, safe_path
    queue=load_queue(root)
    require(queue.get('enabled') is True,'Historical publication approval disabled')
    entry=next((e for e in queue['entries'] if e['file']==filename and e['sha256']==digest),None)
    require(entry is not None,'History input is not hash-approved')
    path=safe_path(root/'.incoming/research',filename)
    require(path.parent==root/'.incoming/research','Historical input must be a filename')
    data,actual,raw=read_batch(path)
    require(actual==digest,'Approved historical input changed')
    require(BOUNDS[0]<=data['date']<=BOUNDS[1],'Historical input outside approved months')
    for other in path.parent.glob(data['date']+'*.yaml'):
        # Validate all revisions; never bypass a broken newer upload.
        newer,_,_=read_batch(other)
        require(newer['revision']<=data['revision'],'Newer history revision needs approval')
    return data,actual,raw


def select_history(root,state,config,day):
    from research_daily import TERMINAL
    queue=load_queue(root);errors=[]
    if queue.get('enabled') is not True:return None,errors
    for entry in sorted(queue['entries'],key=lambda e:e['file']):
        previous=state['inputs'].get(entry['sha256'],{})
        if previous.get('status') in TERMINAL-{'deferred_history'}:continue
        if previous.get('attempts',0)>=config['max_attempts_per_input']:
            errors.append({'file':entry['file'],'error':'History attempt limit reached; inspect report'});continue
        try:
            data,digest,raw=require_approval(root,entry['file'],entry['sha256'])
            if data['date']>day:continue
            return (data['date'],data['revision'],root/'.incoming/research'/entry['file'],data,digest,raw),errors
        except (OSError,ValueError,KeyError) as error:errors.append({'file':entry.get('file'),'error':str(error)})
    return None,errors


def daily_due():
    from research_daily import TZ
    return dt.datetime.now(TZ).time()>=dt.time(8,30)


def select_next(root,state,config,day):
    from research_daily import select_batch
    daily,errors=select_batch(root,state,config,day)
    today_errors=[error for error in errors if error.get('file','').startswith(day)]
    if today_errors and daily_due() and state['daily_runs'].get(day,0)<config['max_model_runs_per_day']:
        return None,today_errors,'daily'
    if daily and daily_due() and state['daily_runs'].get(day,0)<config['max_model_runs_per_day']:
        return daily,errors,'daily'
    selected,history_errors=select_history(root,state,config,day)
    return selected,errors+history_errors,'approved_history'


def reserve_daily_window(moment):
    """Avoid starting an hour-long job just before the existing daily triggers."""
    minute=moment.hour*60+moment.minute
    return 7*60+15<=minute<8*60+30 or 10*60+45<=minute<12*60


def write_progress(root,state,config):
    from research_daily import TERMINAL, now
    from obsidian.transaction import atomic_json
    rows=[]
    for entry in load_queue(root)['entries']:
        saved=state['inputs'].get(entry['sha256'],{});status=saved.get('status','pending')
        if status=='deferred_history':status='pending'
        if saved.get('attempts',0)>=config['max_attempts_per_input'] and status=='failed':status='attempts_exhausted'
        row={**entry,'status':status,'attempts':saved.get('attempts',0),'job':saved.get('job')}
        if row['job']:
            path=root/row['job']/'report.json'
            if path.exists():
                report=json.loads(path.read_text())
                row.update(publication=report.get('publication',{}).get('status'),selection_counts=report.get('selection_counts'),deferred=report.get('deferred',[]),error=report.get('error'))
        rows.append(row)
    result={'range':BOUNDS,'updated_at':now(),'total':len(rows),'remaining':sum(r['status'] not in TERMINAL and r['status']!='attempts_exhausted' for r in rows),'rows':rows}
    atomic_json(root/'.preview/research-jobs/aug-sep-2026-progress.json',result)
    return result


def prepare_queue(root):
    from research_daily import read_batch, now, require, queue_lock
    from obsidian.transaction import atomic_json
    import collections
    with queue_lock(root/'.preview/research-jobs'):
        path=root/QUEUE;require(not path.exists(),'History approval already exists; do not overwrite it')
        newest={}
        for file in sorted((root/'.incoming/research').glob('2026-0[89]*.yaml')):
            data,digest,raw=read_batch(file)
            require(BOUNDS[0]<=data['date']<=BOUNDS[1],'Unexpected historical date')
            if data['date'] not in newest or data['revision']>newest[data['date']]['revision']:
                newest[data['date']]={'file':file.name,'date':data['date'],'revision':data['revision'],'sha256':digest,
                    'counts':dict(collections.Counter(i['type'] for i in data['items'])),'intake_corrections':data.get('_intake_corrections',[])}
        require(len(newest)==61,'Expected all 61 August/September dates; inspect missing uploads')
        approval={'version':1,'enabled':True,'range':BOUNDS,'approved_at':now(),'quota_exempt':True,'publication_authorized':True,
                  'approval':'User authorized reading and publishing August/September, a separate continuous queue exempt from two daily writing calls; normal daily work first; attempt/time limits retained.',
                  'entries':[newest[day] for day in sorted(newest)]}
        atomic_json(path,approval)
        return approval


def main():
    from research_daily import ROOT, IntakeError, run, now, TZ
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','run','status']);args=parser.parse_args()
    config=json.loads((ROOT/'docs/research-inbox/daily-config.json').read_text())
    if args.action=='prepare':
        queue=prepare_queue(ROOT);print(json.dumps({'approved_days':len(queue['entries']),'range':BOUNDS}));return 0
    if args.action=='status':
        print(json.dumps(write_progress(ROOT,json.loads((ROOT/'.preview/research-jobs/state.json').read_text()),config),ensure_ascii=False));return 0
    while True:
        if reserve_daily_window(dt.datetime.now(TZ)):
            print(json.dumps({'at':now(),'status':'reserving_normal_daily_window'}),flush=True);time.sleep(60);continue
        try:report=run(ROOT,config,history=True)
        except IntakeError as error:
            if 'Another research consumer' not in str(error):raise
            print(json.dumps({'at':now(),'status':'waiting_for_consumer'}),flush=True);time.sleep(60);continue
        print(json.dumps(report,ensure_ascii=False),flush=True)
        if report['status']=='publication_pending':
            last=report['publication_retries'][-1]
            if last['status'] in {'blocked','deployment_failed'}:return 1
            time.sleep(60);continue
        if report['status'] in {'no_new_batch','input_errors','awaiting_review'}:
            return 1 if report['input_errors'] else 0
        # An account/network/runtime failure must not consume every queued batch.
        if report['status']=='failed' and ('Codex exited' in report.get('error','') or 'time budget' in report.get('error','')):return 1
        time.sleep(2)


if __name__=='__main__':raise SystemExit(main())
