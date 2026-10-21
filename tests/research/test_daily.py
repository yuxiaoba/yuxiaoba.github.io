import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import research_daily as d
import yaml

class DailyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  (self.root/'.incoming/research').mkdir(parents=True);(self.root/'_data').mkdir()
  (self.root/'_data/note_tags.yml').write_text('- id: inference-serving\n')
  self.config={'start_date':'2026-10-19','max_attempts_per_input':2,'max_model_runs_per_day':2,'max_items':{'paper':12,'tech':4,'social':8}}
 def batch(self,day='2026-10-19',revision=1):
  data={'schema_version':1,'date':day,'revision':revision,'timezone':'Asia/Shanghai','status':'ready','items':[{'id':'arxiv-2610.22863','type':'paper','title':'Real source','url':'https://arxiv.org/abs/2610.22863v1'}]}
  p=self.root/'.incoming/research'/(day+('' if revision==1 else f'.r{revision:03d}')+'.yaml');p.write_text(yaml.safe_dump(data));return p,data
 def select(self,state=None):return d.select_batch(self.root,state or {'inputs':{}},self.config,'2026-10-19')
 def test_valid_batch_and_hash(self):
  p,data=self.batch();got,h,raw=d.read_batch(p);self.assertEqual(got,data);self.assertEqual(h,d.sha(raw))
 def test_duplicate_yaml_key(self):
  p,_=self.batch();p.write_text(p.read_text()+'revision: 1\n')
  with self.assertRaises(d.IntakeError):d.read_batch(p)
 def test_not_ready(self):
  p,_=self.batch();p.write_text(p.read_text().replace('ready','draft'))
  with self.assertRaises(d.IntakeError):d.read_batch(p)
 def test_filename_mismatch(self):
  p,_=self.batch();p.write_text(p.read_text().replace('2026-10-19','2026-10-20'))
  with self.assertRaises(d.IntakeError):d.read_batch(p)
 def test_arxiv_mismatch(self):
  p,_=self.batch();p.write_text(p.read_text().replace('arxiv-2610.22863','arxiv-2610.11111'))
  with self.assertRaises(d.IntakeError):d.read_batch(p)
 def test_duplicate_item(self):
  p,data=self.batch();data['items']*=2;p.write_text(yaml.safe_dump(data))
  with self.assertRaises(d.IntakeError):d.read_batch(p)
 def test_explicit_history_selection_does_not_change_schedule(self):
  p,_=self.batch('2026-10-18');_,h,_=d.read_batch(p);state={'inputs':{h:{'status':'deferred_history','attempts':0}}}
  chosen,_=d.select_manual_batch(self.root,state,self.config,'2026-10-19',p.name)
  self.assertEqual(chosen[2],p);self.assertIsNone(d.select_batch(self.root,state,self.config,'2026-10-19')[0]);self.assertEqual(state['inputs'][h]['status'],'deferred_history')
 def test_manual_completed_batch_rejected(self):
  p,_=self.batch();_,h,_=d.read_batch(p)
  with self.assertRaises(d.IntakeError):d.select_manual_batch(self.root,{'inputs':{h:{'status':'completed'}}},self.config,'2026-10-19',p.name)
 def test_manual_old_revision_rejected(self):
  p,_=self.batch();self.batch(revision=2)
  with self.assertRaises(d.IntakeError):d.select_manual_batch(self.root,{'inputs':{}},self.config,'2026-10-19',p.name)
 def test_manual_path_escape_rejected(self):
  with self.assertRaises(d.IntakeError):d.select_manual_batch(self.root,{'inputs':{}},self.config,'2026-10-19','../../elsewhere.yaml')
 def test_partial_ignored(self):
  (self.root/'.incoming/research/partial.part').write_text('broken YAML [');self.assertEqual(self.select(),(None,[]))
 def test_history_and_future_not_selected(self):
  self.batch('2026-10-18');self.batch('2026-10-20');self.assertIsNone(self.select()[0])
 def test_latest_revision_selected(self):
  self.batch();p,_=self.batch(revision=2);self.assertEqual(self.select()[0][2],p)
 def test_completed_new_revision_never_falls_back(self):
  self.batch();p,_=self.batch(revision=2);_,h,_=d.read_batch(p)
  self.assertIsNone(self.select({'inputs':{h:{'status':'completed'}}})[0])
 def test_retry_exhaustion_reported(self):
  p,_=self.batch();_,h,_=d.read_batch(p);selected,errors=self.select({'inputs':{h:{'status':'failed','attempts':2}}})
  self.assertIsNone(selected);self.assertIn('Attempt limit',errors[0]['error'])
 def test_initialize_preserves_historical_files(self):
  p,_=self.batch('2026-10-18');raw=p.read_bytes();r=d.initialize(self.root,self.config);self.assertEqual(r['historical_batches_deferred'],1);self.assertEqual(raw,p.read_bytes())
  with self.assertRaises(d.IntakeError):d.initialize(self.root,self.config)
 def test_path_escape_and_symlink(self):
  with self.assertRaises(d.IntakeError):d.safe_path(self.root,'../outside')
  (self.root/'link').symlink_to('/tmp')
  with self.assertRaises(d.IntakeError):d.safe_path(self.root,'link/a')
 def test_canonical_arxiv_versions(self):self.assertEqual(d.source_key('https://arxiv.org/abs/2610.22863v2'),d.source_key('https://arxiv.org/pdf/2610.22863v1'))
 def test_authenticated_url_rejected(self):
  with self.assertRaises(d.IntakeError):d.source_key('https://user:pass@example.org/paper')
 def fixture_output(self):
  _,data=self.batch();data['items'][0]['type']='tech';data['items'][0]['id']='test-tech'
  work=self.root/'work';(work/'output').mkdir(parents=True);(work/'sources').mkdir();(work/'sources/article.txt').write_text('Verified source evidence')
  result={'summary':'Test','articles':[{'kind':'tech','source_ids':['test-tech'],'zh_path':'_tech/zh/test-tech.md','en_path':'_tech/en/test-tech.md'}],'deferred':[],'images':[],'evidence':[{'source_id':'test-tech','url':data['items'][0]['url'],'local_file':'sources/article.txt','sha256':d.sha((work/'sources/article.txt').read_bytes()),'review_notes':'Test fixture evidence, never published'}]}
  for lang in ['zh','en']:
   path=work/f'output/_tech/{lang}/test-tech.md';path.parent.mkdir(parents=True)
   meta={'id':'test-tech','title':('2026年10月19日｜测试' if lang=='zh' else '2026-10-19 | Test'),'date':'2026-10-19','lang':lang,'published':True,'layout':'article','source_type':'tech','maintenance':'daily-research','tags':['inference-serving'],'summary':'Summary','long_read':True,'source_url':data['items'][0]['url'],'permalink':f'/tech/{lang}/test-tech/'}
   path.write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True)+'---\n'+'Fixture text only. '*60)
  return work,data,result
 def test_valid_pair(self):
  work,data,result=self.fixture_output();files,pairs=d.validate_outputs(self.root,work,data,result);self.assertEqual(len(files),2);self.assertEqual(len(pairs),1)
 def test_social_longform_requires_explicit_source_format(self):
  work,data,result=self.fixture_output();data['items'][0]['type']='social'
  with self.assertRaises(d.IntakeError):d.validate_outputs(self.root,work,data,result)
  for lang in ['zh','en']:
   p=work/f'output/_tech/{lang}/test-tech.md';p.write_text(p.read_text().replace('long_read: true','long_read: true\nsource_format: x-article'))
  files,pairs=d.validate_outputs(self.root,work,data,result);self.assertEqual(len(files),2)
 def test_missing_translation(self):
  work,data,result=self.fixture_output();(work/'output/_tech/en/test-tech.md').unlink()
  with self.assertRaises(FileNotFoundError):d.validate_outputs(self.root,work,data,result)
 def test_evidence_hash_required(self):
  work,data,result=self.fixture_output();result['evidence'][0]['sha256']='wrong'
  with self.assertRaises(d.IntakeError):d.validate_outputs(self.root,work,data,result)
 def test_unmanifested_file_rejected(self):
  work,data,result=self.fixture_output();(work/'output/script.js').write_text('bad')
  with self.assertRaises(d.IntakeError):d.validate_outputs(self.root,work,data,result)
 def test_missing_item_disposition(self):
  work,data,result=self.fixture_output();data['items'].append({'id':'missing','type':'tech'})
  with self.assertRaises(d.IntakeError):d.validate_outputs(self.root,work,data,result)
 def test_existing_manual_file_cannot_be_overwritten(self):
  work,data,result=self.fixture_output();files,pairs=d.validate_outputs(self.root,work,data,result)
  p=self.root/'_tech/zh/test-tech.md';p.parent.mkdir(parents=True);p.write_text('Manual content')
  with self.assertRaises(d.IntakeError):d.build_candidate(self.root,self.root/'job',files,pairs)
  self.assertEqual(p.read_text(),'Manual content')
 def test_failed_activation_rolls_back_only_new_files(self):
  site=self.root/'candidate';site.mkdir();(self.root/'.preview/releases').mkdir(parents=True)
  with patch.object(d,'fingerprint',return_value='before'),patch.object(d,'activate',side_effect=RuntimeError('activation failure')):
   with self.assertRaises(RuntimeError):d.apply_candidate(self.root,site,{'_tech/zh/new.md':b'new'},'before',{})
  self.assertFalse((self.root/'_tech/zh/new.md').exists())
 def test_successful_apply_switches_preview_and_keeps_old_release(self):
  old=self.root/'.preview/releases/old';(old/'pagefind').mkdir(parents=True);(old/'pagefind/status.json').write_text('{}');d.activate(self.root,old)
  site=self.root/'candidate';(site/'pagefind').mkdir(parents=True);(site/'pagefind/status.json').write_text('{}')
  with patch.object(d,'fingerprint',return_value='before'):
   release=d.apply_candidate(self.root,site,{'_tech/zh/new.md':b'new'},'before',{})
  self.assertEqual((self.root/'.preview/current').resolve(),Path(release));self.assertTrue(old.is_dir());self.assertEqual((self.root/'_tech/zh/new.md').read_bytes(),b'new')
 def test_no_new_input_avoids_model(self):
  self.batch('2026-10-18');d.initialize(self.root,self.config)
  with patch.object(d,'today',return_value='2026-10-19'),patch.object(d,'invoke_worker',side_effect=AssertionError('must not run')):
   self.assertEqual(d.run(self.root,self.config)['status'],'no_new_batch')
 def test_budget_avoids_model(self):
  d.initialize(self.root,self.config);self.batch();p=self.root/'.preview/research-jobs/state.json';state=json.loads(p.read_text());state['daily_runs']={'2026-10-19':2};p.write_text(json.dumps(state))
  with patch.object(d,'today',return_value='2026-10-19'),patch.object(d,'invoke_worker',side_effect=AssertionError('must not run')):
   self.assertEqual(d.run(self.root,self.config)['status'],'daily_budget_reached')
if __name__=='__main__':unittest.main()
