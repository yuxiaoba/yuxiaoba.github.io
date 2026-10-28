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
 def test_month_precision_preserves_source_value_and_raw_input(self):
  p,data=self.batch();data['items'][0]['published_at']='2026-08';p.write_text(yaml.safe_dump(data));original=p.read_bytes()
  got,h,raw=d.read_batch(p)
  self.assertEqual(got,data);self.assertEqual(got['items'][0]['published_at'],'2026-08')
  self.assertEqual(raw,original);self.assertEqual(p.read_bytes(),original);self.assertEqual(h,d.sha(original))
  selected,errors=self.select();self.assertEqual(selected[2],p);self.assertEqual(errors,[])
 def test_bad_source_months_and_unzoned_timestamps_still_rejected(self):
  for value in ['2026-00','2026-13','0000-08','2026-8','2026','2026-08-32','2026-08-01T12:00:00']:
   with self.subTest(value=value):
    p,data=self.batch();data['items'][0]['published_at']=value;p.write_text(yaml.safe_dump(data))
    with self.assertRaises(ValueError):d.read_batch(p)
 def test_full_source_dates_and_zoned_timestamps_preserved(self):
  for value in ['2026-08-01','2026-08-01T12:00:00Z','2026-08-01T12:00:00+08:00']:
   with self.subTest(value=value):
    p,data=self.batch();data['items'][0]['published_at']=value;p.write_text(yaml.safe_dump(data))
    self.assertEqual(d.read_batch(p)[0],data)
 def test_month_precision_only_applies_to_source_not_batch_date(self):
  p,data=self.batch();data['date']='2026-08';p.write_text(yaml.safe_dump(data))
  with self.assertRaises(d.IntakeError):d.read_batch(p)
 def test_duplicate_yaml_key(self):
  p,_=self.batch();p.write_text(p.read_text()+'revision: 1\n')
  with self.assertRaises(d.IntakeError):d.read_batch(p)
 def test_input_cannot_override_server_tech_limit(self):
  p,data=self.batch();data['_tech_article_limit']=999;p.write_text(yaml.safe_dump(data))
  with self.assertRaises(d.IntakeError):d.read_batch(p)
 def test_input_cannot_override_curation_policy(self):
  p,data=self.batch();data['_curation_policy']='disabled';p.write_text(yaml.safe_dump(data))
  with self.assertRaises(d.IntakeError):d.read_batch(p)
 def decision(self,ident,decision='deep_read',evidence='verified'):
  return {'id':ident,'decision':decision,'evidence_status':evidence,'relevance':'Explains a failure mode in agent systems','contribution':'Controlled evidence of the failure mechanism','reason':'Actionable mechanism and supported observations'}
 def test_value_selection_is_complete_and_consistent(self):
  work,data,result=self.fixture_output();data['_curation_policy']='evidence-and-value-v1'
  data['items'].append({'id':'unverified','type':'paper'})
  result['deferred']=[{'id':'unverified','reason':'Full text not available yet'}]
  result['selection']=[self.decision('test-tech'),self.decision('unverified','needs_evidence','unavailable')]
  files,pairs=d.validate_outputs(self.root,work,data,result);self.assertEqual(len(files),2);self.assertEqual(len(pairs),1)
  for mode in ['missing','duplicate','unknown','wrong_disposition','unverified_published','unavailable_rejected','blank_reason']:
   with self.subTest(mode=mode):
    bad=copy.deepcopy(result)
    if mode=='missing':bad.pop('selection')
    elif mode=='duplicate':bad['selection'].append(bad['selection'][0])
    elif mode=='unknown':bad['selection'][0]['id']='unknown'
    elif mode=='wrong_disposition':bad['selection'][0]['decision']='exclude'
    elif mode=='unverified_published':bad['selection'][0]['evidence_status']='partial'
    elif mode=='unavailable_rejected':bad['selection'][1]['decision']='exclude'
    elif mode=='blank_reason':bad['selection'][0]['reason']=' '
    with self.assertRaises(d.IntakeError):d.validate_outputs(self.root,work,data,bad)
 def test_no_count_limit_can_reject_eleven_valid_tech_articles(self):
  work,data,result=self.fixture_output();template=result['articles'][0];evidence=result['evidence'][0]
  originals={lang:d.frontmatter(work/'output'/template[lang+'_path']) for lang in ['zh','en']}
  # Replace the single fixture with eleven independently identified bilingual notes.
  for lang in ['zh','en']:(work/'output'/template[lang+'_path']).unlink()
  data['items']=[];data['_curation_policy']='evidence-and-value-v1';result['articles']=[];result['evidence']=[];result['selection']=[]
  for i in range(11):
   ident=f'tech-{i}';url=f'https://example.org/{ident}';data['items'].append({'id':ident,'type':'tech','title':ident,'url':url})
   article={'kind':'tech','source_ids':[ident]}
   for lang in ['zh','en']:
    meta,body=copy.deepcopy(originals[lang]);rel=f'_tech/{lang}/{ident}.md';meta.update(id=ident,source_url=url,permalink=f'/tech/{lang}/{ident}/');article[lang+'_path']=rel
    (work/'output'/rel).write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True)+'---'+body)
   result['articles'].append(article);result['evidence'].append({**evidence,'source_id':ident,'url':url});result['selection'].append(self.decision(ident))
  files,pairs=d.validate_outputs(self.root,work,data,result)
  self.assertEqual(len(pairs),11);self.assertEqual(len(files),22)
 def test_null_input_limits_allow_value_review_above_old_caps(self):
  p,data=self.batch();data['items']=[{'id':f'{kind}-{i}','type':kind,'title':'Source','url':f'https://example.org/{kind}/{i}'} for kind,n in [('paper',25),('tech',11),('social',9)] for i in range(n)]
  p.write_text(yaml.safe_dump(data));d.initialize(self.root,self.config);self.config.update(curate_by_value=True,select_important_tech=False,max_items={'paper':None,'tech':None,'social':None})
  def prepare(root,job,worker_data):
   self.assertEqual(len(worker_data['items']),45);self.assertEqual(worker_data['_curation_policy'],'evidence-and-value-v1');self.assertNotIn('_tech_article_limit',worker_data)
   work=job/'work';(work/'sources/x_exports').mkdir(parents=True);(work/'output').mkdir();(work/'sources/x_exports/manifest.json').write_text('{}');(work/'events.jsonl').write_text('');return work
  result={'summary':'Sources await verification','articles':[],'deferred':[{'id':i['id'],'reason':'Full source unavailable'} for i in data['items']],'images':[],'evidence':[],'selection':[self.decision(i['id'],'needs_evidence','unavailable') for i in data['items']]}
  with patch.object(d,'today',return_value='2026-10-19'),patch.object(d,'prepare_work',side_effect=prepare),patch.object(d,'invoke_worker',return_value=result) as worker:
   report=d.run(self.root,self.config)
  worker.assert_called_once();self.assertEqual(report['selection_counts'],{'needs_evidence':45});self.assertEqual(report['selection'],result['selection']);self.assertFalse(report['applied'])
  state=json.loads((self.root/'.preview/research-jobs/state.json').read_text());self.assertEqual(state['daily_runs']['2026-10-19'],1)
 def test_excess_tech_is_reviewed_without_silently_dropping_inputs(self):
  p,data=self.batch();data['items']=[{'id':f'tech-{i}','type':'tech','title':'Tech','url':f'https://example.org/{i}'} for i in range(11)];p.write_text(yaml.safe_dump(data))
  d.initialize(self.root,self.config);self.config['select_important_tech']=True;self.config['max_items']['tech']=10
  def prepare(root,job,worker_data):
   self.assertEqual(len(worker_data['items']),11);self.assertEqual(worker_data['_tech_article_limit'],10)
   work=job/'work';(work/'sources/x_exports').mkdir(parents=True);(work/'output').mkdir();(work/'sources/x_exports/manifest.json').write_text('{}');(work/'events.jsonl').write_text('');return work
  result={'summary':'Insufficient primary evidence','articles':[],'deferred':[{'id':i['id'],'reason':'Insufficient primary evidence'} for i in data['items']],'images':[],'evidence':[]}
  with patch.object(d,'today',return_value='2026-10-19'),patch.object(d,'prepare_work',side_effect=prepare),patch.object(d,'invoke_worker',return_value=result) as worker:
   report=d.run(self.root,self.config)
  worker.assert_called_once();self.assertEqual(len(report['deferred']),11);self.assertEqual(report['tech_selection'],{'article_limit':10,'input_count':11})
  self.assertNotEqual(report.get('reason'),'Batch exceeds configured item limits; no model call made')
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
 def test_id_case_and_outer_whitespace_are_repaired_without_editing_input(self):
  p,data=self.batch();data['items']=[{'id':'  x-ReignSwords-123  ','type':'social','title':'Original title','url':'https://x.com/ReignSwords/status/123'}];p.write_text(yaml.safe_dump(data));original=p.read_bytes()
  got,h,raw=d.read_batch(p)
  self.assertEqual(got['items'][0]['id'],'x-reignswords-123');self.assertEqual(got['items'][0]['url'],data['items'][0]['url'])
  self.assertEqual(got['_intake_corrections'][0]['before'],'  x-ReignSwords-123  ')
  self.assertEqual(raw,original);self.assertEqual(p.read_bytes(),original);self.assertEqual(h,d.sha(original))
 def test_normalized_id_collision_is_rejected(self):
  p,data=self.batch();data['items']=[{'id':ident,'type':'tech','title':'Title','url':f'https://example.org/{n}'} for n,ident in enumerate(['Foo','foo'])];p.write_text(yaml.safe_dump(data))
  with self.assertRaises(d.IntakeError):d.read_batch(p)
 def test_unsafe_ids_are_not_guessed(self):
  for ident in ['../foo','foo/bar','two words','foo_bar','ｆｏｏ']:
   with self.subTest(ident=ident):
    p,data=self.batch();data['items'][0]['id']=ident;p.write_text(yaml.safe_dump(data))
    with self.assertRaises(d.IntakeError):d.read_batch(p)
 def test_intake_correction_report_is_auditable_in_dry_run(self):
  d.initialize(self.root,self.config);p,data=self.batch();data['items'][0]['id']='ARXIV-2610.22863';p.write_text(yaml.safe_dump(data));state_path=self.root/'.preview/research-jobs/state.json';before=state_path.read_bytes()
  with patch.object(d,'today',return_value='2026-10-19'):
   result=d.run(self.root,self.config,dry_run=True)
  self.assertEqual(result['status'],'pending');self.assertEqual(result['intake_corrections'][0]['after'],'arxiv-2610.22863');self.assertEqual(state_path.read_bytes(),before)
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
 def test_limit_review_is_persistent_and_not_reported_as_no_new_input(self):
  p,data=self.batch();d.initialize(self.root,self.config)
  for i in range(12):data['items'].append({'id':f'extra-{i}','type':'paper','title':'Paper','url':f'https://example.org/{i}'})
  p.write_text(yaml.safe_dump(data))
  with patch.object(d,'today',return_value='2026-10-19'),patch.object(d,'invoke_worker',side_effect=AssertionError('over-limit batch must not call model')):
   first=d.run(self.root,self.config);second=d.run(self.root,self.config)
  self.assertEqual(first['status'],'needs_review');self.assertEqual(first['counts']['paper'],13)
  self.assertEqual(second['status'],'awaiting_review');self.assertEqual(second['pending_reviews'][0]['limits']['paper'],12)
  state=json.loads((self.root/'.preview/research-jobs/state.json').read_text());self.assertEqual(state['daily_runs'],{})
 def test_history_and_future_not_selected(self):
  self.batch('2026-10-18');self.batch('2026-10-20');self.assertIsNone(self.select()[0])
 def test_latest_revision_selected(self):
  self.batch();p,_=self.batch(revision=2);self.assertEqual(self.select()[0][2],p)
 def test_today_precedes_old_pending_batches_then_catches_up(self):
  old,_=self.batch('2026-10-19');current,_=self.batch('2026-10-22')
  state={'inputs':{}};selected,_=d.select_batch(self.root,state,self.config,'2026-10-22');self.assertEqual(selected[2],current)
  state['inputs'][selected[4]]={'status':'completed'};selected,_=d.select_batch(self.root,state,self.config,'2026-10-22');self.assertEqual(selected[2],old)
 def test_invalid_newest_revision_never_falls_back(self):
  self.batch();p,data=self.batch(revision=2);data['items'][0]['title']='';p.write_text(yaml.safe_dump(data))
  selected,errors=self.select();self.assertIsNone(selected);self.assertEqual(errors[0]['file'],p.name)
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
 def test_verified_aliases_deduplicate_without_merging_unrelated_paths(self):
  self.assertEqual(d.source_key('https://blog.vllm.ai/blog/a'),d.source_key('https://vllm.ai/blog/a'))
  self.assertEqual(d.source_key('https://techstrong.tv/videos/a'),d.source_key('https://www.techstrong.tv/videos/a'))
  self.assertNotEqual(d.source_key('https://blog.vllm.ai/other/a'),d.source_key('https://vllm.ai/other/a'))
  self.assertNotEqual(d.source_key('https://vllm.ai/blog/a?v=1'),d.source_key('https://vllm.ai/blog/a?v=2'))
 def test_authenticated_url_rejected(self):
  with self.assertRaises(d.IntakeError):d.source_key('https://user:pass@example.org/paper')
 def exclusion_rules(self,entries):
  path=self.root/'docs/research-inbox/curation-exclusions.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps({'version':1,'entries':entries}))
 def test_editorial_exclusion_is_source_specific_and_preserves_other_topics(self):
  self.exclusion_rules([{'url':'https://arxiv.org/abs/2610.22863','reason':'Owner-approved editorial withdrawal'}])
  items=[{'id':'old','url':'https://arxiv.org/pdf/2610.22863v2','title':'Paper'}, {'id':'new','url':'https://arxiv.org/abs/2610.22864','title':'Paper on the same topic'}]
  self.assertEqual(d.editorial_exclusions(self.root,items),{'old':'Owner-approved editorial withdrawal'})
 def test_shared_updates_page_matches_title_not_future_releases(self):
  self.exclusion_rules([{'url':'https://example.org/updates/','title':'Old release','reason':'Thin announcement'}])
  items=[{'id':'old','url':'https://example.org/updates','title':' old   RELEASE '},{'id':'new','url':'https://example.org/updates/','title':'New release'}]
  self.assertEqual(d.editorial_exclusions(self.root,items),{'old':'Thin announcement'})
 def test_excluded_batch_uses_no_writing_quota_and_records_reason(self):
  p,data=self.batch();self.exclusion_rules([{'url':data['items'][0]['url'],'reason':'Approved removal'}]);d.initialize(self.root,self.config);raw=p.read_bytes()
  with patch.object(d,'today',return_value='2026-10-19'),patch.object(d,'invoke_worker',side_effect=AssertionError('Excluded source must not reach writer')):
   report=d.run(self.root,self.config)
  self.assertEqual(report['status'],'editorially_excluded');self.assertEqual(report['editorially_excluded'][0]['reason'],'Approved removal');self.assertEqual(report['already_covered'],[])
  state=json.loads((self.root/'.preview/research-jobs/state.json').read_text());self.assertEqual(state['daily_runs'],{});self.assertEqual(p.read_bytes(),raw)
  self.assertIsNone(d.select_batch(self.root,state,self.config,'2026-10-19')[0])
 def test_invalid_editorial_rules_do_not_silently_disappear(self):
  self.exclusion_rules([{'url':'https://example.org/source','reason':''}])
  with self.assertRaises(d.IntakeError):d.editorial_exclusions(self.root,[])
 def fixture_output(self):
  _,data=self.batch();data['items'][0]['type']='tech';data['items'][0]['id']='test-tech'
  work=self.root/'work';(work/'output').mkdir(parents=True);(work/'sources').mkdir();(work/'sources/article.txt').write_text('Verified source evidence')
  result={'summary':'Test','articles':[{'kind':'tech','source_ids':['test-tech'],'zh_path':'_tech/zh/test-tech.md','en_path':'_tech/en/test-tech.md'}],'deferred':[],'images':[],'evidence':[{'source_id':'test-tech','url':data['items'][0]['url'],'local_file':'sources/article.txt','sha256':d.sha((work/'sources/article.txt').read_bytes()),'review_notes':'Test fixture evidence, never published'}]}
  for lang in ['zh','en']:
   path=work/f'output/_tech/{lang}/test-tech.md';path.parent.mkdir(parents=True)
   meta={'id':'test-tech','title':('2026年10月19日｜测试' if lang=='zh' else '2026-10-19 | Test'),'date':'2026-10-19','lang':lang,'published':True,'layout':'article','source_type':'tech','maintenance':'daily-research','tags':['inference-serving'],'summary':'Summary','long_read':True,'source_url':data['items'][0]['url'],'permalink':f'/tech/{lang}/test-tech/'}
   path.write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True)+'---\n'+'Fixture text only. '*60)
  return work,data,result
 def test_output_tech_limit_is_enforced(self):
  work,data,result=self.fixture_output()
  with self.assertRaisesRegex(d.IntakeError,'Tech selection exceeds article limit'):
   d.validate_outputs(self.root,work,data,result,tech_limit=0)
  files,pairs=d.validate_outputs(self.root,work,data,result,tech_limit=1)
  self.assertEqual(len(pairs),1)
 def test_valid_pair(self):
  work,data,result=self.fixture_output();files,pairs=d.validate_outputs(self.root,work,data,result);self.assertEqual(len(files),2);self.assertEqual(len(pairs),1)
 def test_bilingual_activity_stamps_preserve_reading_date_and_body(self):
  work,data,result=self.fixture_output();files,_=d.validate_outputs(self.root,work,data,result)
  at='2026-10-21T13:08:08+08:00';stamped=d.stamp_note_activity(self.root,files,at)
  for rel,raw in stamped.items():
   parts=raw.decode().split('---',2);meta=yaml.safe_load(parts[1]);self.assertEqual(meta['date'],'2026-10-19');self.assertEqual(meta['published_at'],at);self.assertEqual(meta['updated_at'],at);self.assertEqual(parts[2],files[rel].decode().split('---',2)[2])
 def test_update_keeps_original_publication_time(self):
  work,data,result=self.fixture_output();files,_=d.validate_outputs(self.root,work,data,result)
  old='2026-10-20T08:00:00+08:00';new='2026-10-20T16:00:00+08:00'
  first=d.stamp_note_activity(self.root,files,old)
  for rel,raw in first.items():p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  second=d.stamp_note_activity(self.root,files,new)
  for raw in second.values():
   meta=yaml.safe_load(raw.decode().split('---',2)[1]);self.assertEqual(meta['published_at'],old);self.assertEqual(meta['updated_at'],new)
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
