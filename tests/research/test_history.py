import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import research_daily as d
import research_history as h
import research_publish as publication


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        (self.root/'.incoming/research').mkdir(parents=True);(self.root/'_data').mkdir()
        (self.root/'_data/note_tags.yml').write_text('- id: systems-reliability\n')
        self.config={'start_date':'2026-10-19','max_attempts_per_input':2,'max_model_runs_per_day':2,'max_items':{'paper':None,'tech':None,'social':None},'curate_by_value':True}
        self.state={'inputs':{},'daily_runs':{}}
    def batch(self,day='2026-08-01',revision=1):
        data={'schema_version':1,'date':day,'revision':revision,'timezone':'Asia/Shanghai','status':'ready','items':[{'id':'tech-test','type':'tech','title':'Source','url':'https://example.org/source'}]}
        path=self.root/'.incoming/research'/(day+('' if revision==1 else f'.r{revision:03d}')+'.yaml');path.write_text(yaml.safe_dump(data));return path,data,d.sha(path.read_bytes())
    def approve(self,path,digest):
        queue=self.root/h.QUEUE;queue.parent.mkdir(parents=True,exist_ok=True)
        queue.write_text(json.dumps({'version':1,'enabled':True,'range':h.BOUNDS,'quota_exempt':True,'publication_authorized':True,'entries':[{'file':path.name,'sha256':digest}]}))
    def test_no_approval_no_history(self):
        self.batch();self.assertEqual(h.select_history(self.root,self.state,self.config,'2026-10-28'),(None,[]))
    def test_exact_hash_and_scope_are_required(self):
        path,data,digest=self.batch();self.approve(path,digest)
        selected,errors=h.select_history(self.root,self.state,self.config,'2026-10-28');self.assertEqual(selected[4],digest);self.assertFalse(errors)
        path.write_text(path.read_text()+'# change\n');selected,errors=h.select_history(self.root,self.state,self.config,'2026-10-28');self.assertIsNone(selected);self.assertIn('changed',errors[0]['error'])
    def test_latest_revision_requires_new_hash_approval(self):
        path,_,digest=self.batch();self.approve(path,digest);self.batch(revision=2)
        selected,errors=h.select_history(self.root,self.state,self.config,'2026-10-28');self.assertIsNone(selected);self.assertIn('Newer',errors[0]['error'])
    def test_no_other_months_or_publication_without_authorization(self):
        path,_,digest=self.batch('2026-07-31');self.approve(path,digest)
        self.assertIn('outside',h.select_history(self.root,self.state,self.config,'2026-10-28')[1][0]['error'])
        queue=self.root/h.QUEUE;value=json.loads(queue.read_text());value['publication_authorized']=False;queue.write_text(json.dumps(value))
        with self.assertRaises(d.IntakeError):h.load_queue(self.root)
    def test_today_first_but_history_does_not_spend_daily_quota(self):
        path,_,digest=self.batch();self.approve(path,digest);normal,_,_=self.batch('2026-10-28')
        with patch.object(h,'daily_due',return_value=True):
            selected,_,origin=h.select_next(self.root,self.state,self.config,'2026-10-28');self.assertEqual(selected[2],normal);self.assertEqual(origin,'daily')
            self.state['daily_runs']['2026-10-28']=2
            selected,_,origin=h.select_next(self.root,self.state,self.config,'2026-10-28');self.assertEqual(selected[2],path);self.assertEqual(origin,'approved_history')
    def test_no_early_daily_trigger(self):
        path,_,digest=self.batch();self.approve(path,digest);self.batch('2026-10-28')
        with patch.object(h,'daily_due',return_value=False):
            selected,_,origin=h.select_next(self.root,self.state,self.config,'2026-10-28');self.assertEqual(selected[2],path);self.assertEqual(origin,'approved_history')
    def test_broken_today_is_not_hidden_by_backfill(self):
        path,_,digest=self.batch();self.approve(path,digest);normal,data,_=self.batch('2026-10-28')
        data['items'][0]['title']='';normal.write_text(yaml.safe_dump(data))
        with patch.object(h,'daily_due',return_value=True):
            selected,errors,origin=h.select_next(self.root,self.state,self.config,'2026-10-28')
        self.assertIsNone(selected);self.assertEqual(origin,'daily');self.assertEqual(errors[0]['file'],normal.name)
    def test_attempt_limit_and_completed_status(self):
        path,_,digest=self.batch();self.approve(path,digest)
        for status in ['completed','completed_with_deferred','needs_review','editorially_excluded']:
            self.state['inputs'][digest]={'status':status};self.assertIsNone(h.select_history(self.root,self.state,self.config,'2026-10-28')[0])
        self.state['inputs'][digest]={'status':'failed','attempts':2}
        self.assertIn('attempt',h.select_history(self.root,self.state,self.config,'2026-10-28')[1][0]['error'].lower())
    def test_daily_windows_reserved(self):
        for hour,minute,expected in [(7,14,False),(7,15,True),(8,29,True),(8,30,False),(10,44,False),(10,45,True),(11,59,True),(12,0,False)]:
            self.assertEqual(h.reserve_daily_window(dt.datetime(2026,10,28,hour,minute)),expected)
    def test_real_run_history_ledger_and_publication_enrollment(self):
        path,data,digest=self.batch();self.approve(path,digest);folder=self.root/'.preview/research-jobs'
        self.state['daily_runs']['2026-10-28']=2;(folder/'state.json').write_text(json.dumps(self.state));self.config['publication']={'enabled':True}
        def prepare(root,job,worker_data):
            work=job/'work';(work/'sources/x_exports').mkdir(parents=True);(work/'sources/x_exports/manifest.json').write_text('{}');(work/'events.jsonl').write_text('');return work
        def write(root,work,config):
            evidence=work/'sources/original.txt';evidence.write_text('Fixture source, not a published document')
            article={'kind':'tech','source_ids':['tech-test']}
            for lang in ['zh','en']:
                rel=f'_tech/{lang}/history-fixture.md';p=work/'output'/rel;p.parent.mkdir(parents=True)
                meta={'id':'history-fixture','title':'2026年8月1日｜测试' if lang=='zh' else '2026-08-01 | Fixture','date':'2026-08-01','lang':lang,'published':True,'layout':'article','maintenance':'daily-research','source_type':'tech','tags':['systems-reliability'],'summary':'Fixture','long_read':True,'source_url':'https://example.org/source','permalink':f'/tech/{lang}/history-fixture/'}
                p.write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True)+'---\n'+'Fixture only. '*70);article[lang+'_path']=rel
            return {'summary':'Fixture','articles':[article],'deferred':[],'images':[],'evidence':[{'source_id':'tech-test','url':'https://example.org/source','local_file':'sources/original.txt','sha256':d.sha(evidence.read_bytes()),'review_notes':'Fixture source checked'}],'selection':[{'id':'tech-test','decision':'deep_read','relevance':'System reliability','contribution':'Test mechanism','evidence_status':'verified','reason':'Fixture selection'}]}
        with patch.object(d,'today',return_value='2026-10-28'),patch.object(h,'daily_due',return_value=True),patch.object(d,'prepare_work',side_effect=prepare),patch.object(d,'invoke_worker',side_effect=write),patch.object(d,'build_candidate',return_value=(self.root/'candidate','fingerprint',{'build':{'ok':True},'browser':{'ok':True}})),patch.object(d,'apply_candidate',return_value='fixture-release'),patch.object(publication,'retry_pending',return_value=[]),patch.object(publication,'publish',return_value={'status':'awaiting_deployment'}) as publish:
            report=d.run(self.root,self.config,history=True)
        state=json.loads((folder/'state.json').read_text());self.assertEqual(state['daily_runs']['2026-10-28'],2);self.assertEqual(state['history_runs']['2026-10-28'],1)
        self.assertEqual(report['origin'],'approved_history');self.assertTrue(report['daily_quota_exempt']);publish.assert_called_once()
        stored=json.loads((self.root/report['job']/'report.json').read_text());self.assertTrue(stored['publication']['requested'])
        self.assertEqual(d.sha(path.read_bytes()),digest)


if __name__=='__main__':unittest.main()
