import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import research_daily as d
import research_backfill as b

class BackfillTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  (self.root/'.incoming/research').mkdir(parents=True)
  self.config={'start_date':'2026-10-19','max_attempts_per_input':2,'max_model_runs_per_day':2,'max_items':{'paper':12,'tech':4,'social':8}}
 def batch(self,date='2026-10-11',rev=1):
  p=self.root/'.incoming/research'/(date+('' if rev==1 else f'.r{rev:03d}')+'.yaml')
  data={'schema_version':1,'date':date,'timezone':'Asia/Shanghai','revision':rev,'status':'ready','items':[]};p.write_text(yaml.safe_dump(data));return p,data,d.sha(p.read_bytes())
 def queue(self,entries):
  p=self.root/b.QUEUE;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'version':1,'enabled':True,'entries':entries,'range':['2026-10-01','2026-10-18']}))
 def test_no_approval_no_history_selection(self):
  self.batch();self.assertEqual(b.select_approved(self.root,{'inputs':{}},self.config,'2026-10-19'),(None,[]))
 def test_approved_deferred_history_selected(self):
  p,data,h=self.batch();self.queue([{'file':p.name,'sha256':h,'mode':'generate'}]);state={'inputs':{h:{'status':'deferred_history'}}}
  selected,errors=b.select_approved(self.root,state,self.config,'2026-10-19');self.assertEqual(selected[2],p);self.assertFalse(errors);self.assertEqual(self.config['start_date'],'2026-10-19')
 def test_changed_hash_is_not_auto_approved(self):
  p,data,h=self.batch();self.queue([{'file':p.name,'sha256':h,'mode':'generate'}]);p.write_text(p.read_text()+'# changed\n')
  selected,errors=b.select_approved(self.root,{'inputs':{}},self.config,'2026-10-19');self.assertIsNone(selected);self.assertIn('changed',errors[0]['error'])
 def test_new_revision_requires_review(self):
  p,data,h=self.batch();self.batch(rev=2);self.queue([{'file':p.name,'sha256':h,'mode':'generate'}])
  selected,errors=b.select_approved(self.root,{'inputs':{}},self.config,'2026-10-19');self.assertIsNone(selected);self.assertIn('revision',errors[0]['error'])
 def test_outside_approved_range_rejected(self):
  p,data,h=self.batch('2026-10-19');self.queue([{'file':p.name,'sha256':h,'mode':'generate'}])
  selected,errors=b.select_approved(self.root,{'inputs':{}},self.config,'2026-10-19');self.assertIsNone(selected);self.assertIn('outside',errors[0]['error'])
 def test_completed_skipped(self):
  p,data,h=self.batch();self.queue([{'file':p.name,'sha256':h,'mode':'generate'}])
  self.assertIsNone(b.select_approved(self.root,{'inputs':{h:{'status':'completed'}}},self.config,'2026-10-19')[0])
 def test_retry_limit_preserved(self):
  p,data,h=self.batch();self.queue([{'file':p.name,'sha256':h,'mode':'generate'}])
  selected,errors=b.select_approved(self.root,{'inputs':{h:{'status':'failed','attempts':2}}},self.config,'2026-10-19');self.assertIsNone(selected);self.assertTrue(errors)
 def test_new_daily_has_priority(self):
  d.initialize(self.root,self.config);p,_,h=self.batch();self.queue([{'file':p.name,'sha256':h,'mode':'generate'}]);new,_,_=self.batch('2026-10-19')
  with patch.object(d,'today',return_value='2026-10-19'):
   result=d.run(self.root,self.config,dry_run=True)
  self.assertEqual(result['input'],new.name);self.assertEqual(result['origin'],'daily')
 def test_shared_daily_budget_not_bypassed(self):
  d.initialize(self.root,self.config);p,_,h=self.batch();self.queue([{'file':p.name,'sha256':h,'mode':'generate'}]);sp=self.root/'.preview/research-jobs/state.json';state=json.loads(sp.read_text());state['daily_runs']={'2026-10-19':2};sp.write_text(json.dumps(state))
  with patch.object(d,'today',return_value='2026-10-19'),patch.object(d,'invoke_worker',side_effect=AssertionError('must not run')):
   result=d.run(self.root,self.config)
  self.assertEqual(result['status'],'daily_budget_reached');self.assertEqual(result['origin'],'approved_backfill')
 def exempt_queue(self):
  p,data,h=self.batch();self.queue([{'file':p.name,'sha256':h,'mode':'generate'}]);q=self.root/b.QUEUE;value=json.loads(q.read_text());value['one_off']={'enabled':True,'input_sha256':[h]};q.write_text(json.dumps(value));return p,data,h
 def test_one_off_prioritized_without_changing_normal_budget(self):
  d.initialize(self.root,self.config);p,_,h=self.exempt_queue();self.batch('2026-10-19')
  sp=self.root/'.preview/research-jobs/state.json';state=json.loads(sp.read_text());state['daily_runs']={'2026-10-19':2};sp.write_text(json.dumps(state))
  with patch.object(d,'today',return_value='2026-10-19'):
   result=d.run(self.root,self.config)
  self.assertEqual(result['input'],p.name);self.assertTrue(result['daily_quota_exempt']);self.assertEqual(result['status'],'already_covered');self.assertEqual(json.loads(sp.read_text())['daily_runs'],state['daily_runs'])
 def test_one_off_model_call_has_separate_ledger(self):
  d.initialize(self.root,self.config);p,data,h=self.exempt_queue()
  item={'id':'paper-test','type':'paper','title':'Test','url':'https://example.org/paper','published_at':'2026-10-11','priority':'normal'}
  selected=('2026-10-11',1,p,{**data,'items':[item]},h,p.read_bytes())
  with patch.object(b,'select_approved',return_value=(selected,[])),patch.object(d,'prepare_work',return_value=self.root),patch.object(d,'invoke_worker',side_effect=RuntimeError('simulated failure')):
   result=d.run(self.root,self.config,one_off=True)
  state=json.loads((self.root/'.preview/research-jobs/state.json').read_text())
  self.assertEqual(result['status'],'failed');self.assertEqual(state['daily_runs'],{});self.assertEqual(sum(state['one_off_runs'].values()),1);self.assertEqual(state['inputs'][h]['attempts'],1)
 def test_one_off_does_not_select_unlisted_hash_or_daily_input(self):
  d.initialize(self.root,self.config);self.batch('2026-10-19');p,data,h=self.exempt_queue()
  q=self.root/b.QUEUE;value=json.loads(q.read_text());value['one_off']['input_sha256']=[];q.write_text(json.dumps(value))
  with patch.object(d,'today',return_value='2026-10-19'):
   result=d.run(self.root,self.config,one_off=True)
  self.assertEqual(result['status'],'no_new_batch')
 def test_one_off_still_checks_hash_and_attempt_limit(self):
  p,data,h=self.exempt_queue();state={'inputs':{h:{'attempts':2,'status':'failed'}}}
  self.assertIsNone(b.select_approved(self.root,state,self.config,'2026-10-19',one_off=True)[0])
  p.write_text(p.read_text()+'# changed\n')
  selected,errors=b.select_approved(self.root,{'inputs':{}},self.config,'2026-10-19',one_off=True)
  self.assertIsNone(selected);self.assertIn('changed',errors[0]['error'])
 def test_one_off_completed_not_reprocessed(self):
  p,data,h=self.exempt_queue();self.assertIsNone(b.select_approved(self.root,{'inputs':{h:{'status':'completed'}}},self.config,'2026-10-19',one_off=True)[0])
 def merge_fixture(self):
  p,data,h=self.batch();spec={};files={};original={};pairs=[]
  for lang in ['zh','en']:
   rel=f'_digest/{lang}/obsidian/daily-2026-10-11.md';path=self.root/rel;path.parent.mkdir(parents=True)
   meta={'id':'daily-2026-10-11','date':'2026-10-11','lang':lang,'title':'Preserve title','summary':'Preserve summary','daily_digest':True,'paper_ids':['old'],'paper_count':1,'daily_papers':[{'id':'old','title':'Old'}],'tags':['agent-reliability'],'permalink':f'/digest/{lang}/daily/2026-10-11/','maintenance':'manual'}
   body='\nOriginal manually edited text must survive.\n<h2 id="paper-old">Old</h2>\n'
   path.write_text('---\n'+yaml.safe_dump(meta)+'---\n'+body);original[rel]=path.read_bytes();spec[lang]={'path':rel,'sha256':d.sha(path.read_bytes())}
   new={**meta,'paper_ids':['new'],'paper_count':1,'daily_papers':[{'id':'new','title':'New'}],'tags':['observability']}
   files[f'_digest/{lang}/daily-2026-10-11.md']=('---\n'+yaml.safe_dump(new)+'---\nNew supplement.\n<h2 id="paper-new">New</h2>\n').encode();pairs.append(meta['permalink'])
  self.queue([{'file':p.name,'sha256':h,'mode':'append_digest','originals':spec}]);return data,h,files,[tuple(pairs)],original
 def test_append_preserves_original_and_pairs(self):
  data,h,files,pairs,original=self.merge_fixture();merged,routes,replacements=b.merge_digest(self.root,data,h,files,pairs)
  for rel,old in original.items():
   self.assertEqual((self.root/rel).read_bytes(),old)
   oldmeta,body=d.frontmatter(self.root/rel);self.assertIn(body.encode(),merged[rel]);new=yaml.safe_load(merged[rel].decode().split('---',2)[1]);self.assertEqual(new['title'],oldmeta['title']);self.assertEqual(new['paper_ids'],['old','new']);self.assertEqual(new['paper_count'],2);self.assertEqual(new['maintenance'],'manual');self.assertEqual(replacements[rel],d.sha(old))
  self.assertEqual(routes,pairs)
 def test_manual_edit_after_approval_blocks_merge(self):
  data,h,files,pairs,original=self.merge_fixture();p=self.root/next(iter(original));p.write_bytes(p.read_bytes()+b'Manual new edit')
  with self.assertRaises(d.ReviewRequired):b.merge_digest(self.root,data,h,files,pairs)
  self.assertTrue(p.read_bytes().endswith(b'Manual new edit'))
 def test_duplicate_anchor_is_rejected(self):
  data,h,files,pairs,original=self.merge_fixture();files={k:v.replace(b'new',b'old') for k,v in files.items()}
  with self.assertRaises(d.IntakeError):b.merge_digest(self.root,data,h,files,pairs)
 def test_failed_merge_activation_restores_original_bytes(self):
  data,h,files,pairs,original=self.merge_fixture();merged,_,replacements=b.merge_digest(self.root,data,h,files,pairs);site=self.root/'candidate';site.mkdir()
  with patch.object(d,'fingerprint',return_value='before'),patch.object(d,'activate',side_effect=RuntimeError('failed')):
   with self.assertRaises(RuntimeError):d.apply_candidate(self.root,site,merged,'before',{},replacements)
  for rel,raw in original.items():self.assertEqual((self.root/rel).read_bytes(),raw)
 def test_successful_merge_keeps_old_release(self):
  data,h,files,pairs,original=self.merge_fixture();merged,_,replacements=b.merge_digest(self.root,data,h,files,pairs);site=self.root/'candidate';(site/'pagefind').mkdir(parents=True);(site/'pagefind/status.json').write_text('{}')
  old=self.root/'.preview/releases/old';(old/'pagefind').mkdir(parents=True);(old/'pagefind/status.json').write_text('{}');d.activate(self.root,old)
  with patch.object(d,'fingerprint',return_value='before'):release=d.apply_candidate(self.root,site,merged,'before',{},replacements)
  self.assertEqual((self.root/'.preview/current').resolve(),Path(release));self.assertTrue(old.exists())
  for rel,raw in merged.items():self.assertEqual((self.root/rel).read_bytes(),raw)
if __name__=='__main__':unittest.main()
