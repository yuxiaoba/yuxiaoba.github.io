import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import research_publish as p
import research_daily as d

class PublicationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.folder=Path(self.tmp.name);self.root=self.folder/'site';self.remote=self.folder/'remote.git'
  subprocess.run(['git','init','--bare','-q',str(self.remote)],check=True)
  subprocess.run(['git','init','-q','-b','work',str(self.root)],check=True)
  self.g('config','user.name','Test');self.g('config','user.email','test@example.org')
  (self.root/'.gitignore').write_text('.preview/\n.incoming/\n')
  (self.root/'keep.txt').write_text('original')
  self.g('add','.');self.g('commit','-qm','baseline');self.base=self.g('rev-parse','HEAD')
  self.g('remote','add','origin',str(self.remote));self.g('push','-q','origin','HEAD:master','HEAD:work')
  self.config={'enabled':True,'remote':'origin','remote_url':str(self.remote),'work_branch':'work','production_branch':'master','repository':'example/site','site_url':'https://example.org'}
  self.path=self.root/'.preview/research-jobs/runs/test/report.json';self.path.parent.mkdir(parents=True)
  self.report={'status':'completed','date':'2026-10-22','applied':True,'checks':{'build':{'indexed_pages':2},'browser':{'pages_at_widths':4}},'files':{},'publication':{'requested':True,'status':'pending'}}
  for lang in ['zh','en']:
   rel=f'_tech/{lang}/test.md';f=self.root/rel;f.parent.mkdir(parents=True);f.write_text('---\npublished: true\n---\nVerified note\n')
   self.report['files'][rel]=hashlib.sha256(f.read_bytes()).hexdigest()
  self.save()
 def g(self,*args):return p.git(self.root,*args)
 def save(self):self.path.write_text(json.dumps(self.report))
 def publish(self,status='published'):
  with patch.object(p,'deployment_status',return_value=(status,None)):
   return p.publish(self.root,self.path,self.config)
 def remote_head(self):return self.g('ls-remote','origin','refs/heads/master').split()[0]
 def test_exact_commit_atomic_push_and_idempotence(self):
  result=self.publish();self.assertEqual(result['status'],'published');commit=result['commit']
  self.assertEqual(self.remote_head(),commit);self.assertEqual(self.g('status','--porcelain'),'')
  self.assertEqual(set(self.g('diff','--name-only',self.base,commit).splitlines()),set(self.report['files']))
  self.assertEqual(self.publish()['commit'],commit);self.assertEqual(self.g('rev-list','--count','HEAD'),'2')
 def test_unrelated_local_change_blocks_and_preserves_it(self):
  (self.root/'keep.txt').write_text('user edit');self.assertEqual(self.publish()['status'],'blocked')
  self.assertEqual(self.remote_head(),self.base);self.assertEqual((self.root/'keep.txt').read_text(),'user edit')
 def test_unrelated_untracked_file_blocks(self):
  (self.root/'private.txt').write_text('do not upload');self.assertEqual(self.publish()['status'],'blocked');self.assertEqual(self.remote_head(),self.base)
 def test_existing_stage_blocks(self):
  self.g('add','_tech/zh/test.md');self.assertEqual(self.publish()['status'],'blocked');self.assertEqual(self.g('diff','--cached','--name-only'),'_tech/zh/test.md')
 def test_changed_output_blocks(self):
  (self.root/'_tech/zh/test.md').write_text('edited');self.assertEqual(self.publish()['status'],'blocked');self.assertEqual(self.remote_head(),self.base)
 def test_missing_translation_blocks(self):
  self.report['files'].pop('_tech/en/test.md');self.save();self.assertEqual(self.publish()['status'],'blocked')
 def test_unvalidated_or_draft_batch_blocks(self):
  self.report['status']='failed';self.save();self.assertEqual(self.publish()['status'],'blocked')
 def test_outside_manifest_scope_blocks(self):
  self.report['files']['keep.txt']=hashlib.sha256(b'original').hexdigest();self.save();self.assertEqual(self.publish()['status'],'blocked')
 def test_unpublished_local_commit_is_not_pushed(self):
  (self.root/'keep.txt').write_text('local code');self.g('add','keep.txt');self.g('commit','-qm','not approved')
  self.assertEqual(self.publish()['status'],'blocked');self.assertEqual(self.remote_head(),self.base)
 def test_remote_advance_blocks_without_merge(self):
  other=self.folder/'other';subprocess.run(['git','clone','-q','-b','master',str(self.remote),str(other)],check=True)
  p.git(other,'config','user.name','Test');p.git(other,'config','user.email','test@example.org');(other/'remote.txt').write_text('new');p.git(other,'add','.');p.git(other,'commit','-qm','remote');p.git(other,'push','-q','origin','master')
  expected=self.remote_head();self.assertEqual(self.publish()['status'],'blocked');self.assertEqual(self.remote_head(),expected);self.assertEqual(self.g('rev-parse','HEAD'),self.base)
 def test_network_failure_retries_same_commit(self):
  real=p.git
  def flaky(root,*args,**kw):
   if args[0]=='push':raise OSError('network unavailable')
   return real(root,*args,**kw)
  with patch.object(p,'git',side_effect=flaky):first=self.publish()
  self.assertEqual(first['status'],'blocked');self.assertEqual(self.remote_head(),self.base)
  second=self.publish();self.assertEqual(second['status'],'published');self.assertEqual(first['commit'],second['commit']);self.assertEqual(self.remote_head(),second['commit']);self.assertEqual(self.g('rev-list','--count','HEAD'),'2')
 def test_crash_after_commit_recovers_without_duplicate(self):
  self.report['publication'].update(base=self.base,status='prepared');self.save()
  self.g('add','_tech');self.g('commit','-qm','completed before crash');head=self.g('rev-parse','HEAD')
  self.assertEqual(self.publish()['commit'],head);self.assertEqual(self.g('rev-list','--count','HEAD'),'2')
 def test_push_is_not_deployment(self):
  self.assertEqual(self.publish('awaiting_deployment')['status'],'awaiting_deployment')
  self.assertEqual(self.publish('deployment_failed')['status'],'deployment_failed')
  self.assertEqual(self.publish()['status'],'published')
 def test_old_reports_not_enrolled(self):
  self.report.pop('publication');self.save();self.assertEqual(p.retry_pending(self.root,self.config),[]);self.assertEqual(self.remote_head(),self.base)
 def test_disabled_has_no_git_side_effects(self):
  self.config['enabled']=False;self.assertEqual(self.publish()['status'],'disabled');self.assertEqual(self.g('rev-parse','HEAD'),self.base)
 def test_pending_retry_does_not_invoke_writer_or_change_quota(self):
  state={'inputs':{},'daily_runs':{'2026-10-22':2}};state_path=self.root/'.preview/research-jobs/state.json';state_path.write_text(json.dumps(state))
  with patch.object(p,'deployment_status',return_value=('awaiting_deployment',None)),patch.object(d,'invoke_worker',side_effect=AssertionError('must not regenerate')):
   result=d.run(self.root,{'publication':self.config})
  self.assertEqual(result['status'],'publication_pending');self.assertEqual(json.loads(state_path.read_text()),state)
 def test_dry_run_never_retries_publication(self):
  state_path=self.root/'.preview/research-jobs/state.json';state_path.write_text(json.dumps({'inputs':{},'daily_runs':{}}));(self.root/'.incoming/research').mkdir(parents=True)
  with patch.object(p,'publish',side_effect=AssertionError('dry run must not publish')):
   d.run(self.root,{'publication':self.config,'start_date':'2026-10-19'},dry_run=True)
  self.assertEqual(self.remote_head(),self.base)

 def test_draft_manifest_blocks(self):
  f=self.root/'_tech/zh/test.md';f.write_text('---\npublished: false\n---\nDraft\n');self.report['files']['_tech/zh/test.md']=hashlib.sha256(f.read_bytes()).hexdigest();self.save()
  self.assertEqual(self.publish()['status'],'blocked');self.assertEqual(self.remote_head(),self.base)
 def test_symlink_output_blocks(self):
  f=self.root/'_tech/zh/test.md';raw=f.read_bytes();f.unlink();target=self.folder/'outside';target.write_bytes(raw);f.symlink_to(target)
  self.assertEqual(self.publish()['status'],'blocked');self.assertEqual(self.remote_head(),self.base)
 def test_completed_daily_run_enrolls_and_pushes(self):
  import research_backfill as backfill
  state_path=self.root/'.preview/research-jobs/state.json';state_path.write_text(json.dumps({'inputs':{},'daily_runs':{}}))
  inbox=self.root/'.incoming/research';inbox.mkdir(parents=True);source=inbox/'2026-10-22.yaml';source.write_text('frozen input')
  data={'date':'2026-10-22','items':[{'id':'example','type':'tech','url':'https://example.org/article'}]}
  work=self.root/'.preview/work';(work/'sources/x_exports').mkdir(parents=True);(work/'sources/x_exports/manifest.json').write_text('{}');(work/'events.jsonl').write_text('')
  files={name:(self.root/name).read_bytes() for name in self.report['files']};pairs=[('/tech/zh/test/','/tech/en/test/')]
  config={'publication':self.config,'max_model_runs_per_day':2,'max_items':{'tech':8}}
  self.path.unlink()  # Only the new successful run may be enrolled.
  selected=('2026-10-22',1,source,data,d.sha(source.read_bytes()),source.read_bytes())
  with patch.object(backfill,'select_approved',return_value=(None,[])),patch.object(d,'select_batch',return_value=(selected,[])),patch.object(d,'prepare_work',return_value=work),patch.object(d,'invoke_worker',return_value={'summary':'verified','deferred':[]}),patch.object(d,'validate_outputs',return_value=(files,pairs)),patch.object(backfill,'merge_digest',return_value=(files,pairs,{})),patch.object(d,'stamp_note_activity',side_effect=lambda root,files,stamp:files),patch.object(d,'build_candidate',return_value=(self.root,self.base,self.report['checks'])),patch.object(d,'apply_candidate',return_value='preview-release'),patch.object(p,'deployment_status',return_value=('published',None)):
   result=d.run(self.root,config)
  self.assertTrue(result['publication']['requested']);self.assertEqual(result['publication']['status'],'published');self.assertEqual(self.remote_head(),result['publication']['commit'])
 def test_live_commit_confirmation_and_failed_action(self):
  import io
  commit='a'*40
  with patch.object(p.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps({'commit':commit}).encode())):
   self.assertEqual(p.deployment_status(self.config,commit),('published',None))
  responses=[io.BytesIO(json.dumps({'commit':'b'*40}).encode()),io.BytesIO(json.dumps({'workflow_runs':[{'path':'.github/workflows/pages.yml','head_branch':'master','event':'push','status':'completed','conclusion':'failure','html_url':'https://example.org/run'}]}).encode())]
  with patch.object(p.urllib.request,'urlopen',side_effect=responses):
   self.assertEqual(p.deployment_status(self.config,commit),('deployment_failed','https://example.org/run'))
 def test_later_release_can_confirm_previous_batch(self):
  import io
  self.g('add','_tech');self.g('commit','-qm','daily');commit=self.g('rev-parse','HEAD')
  (self.root/'keep.txt').write_text('later approved edit');self.g('add','keep.txt');self.g('commit','-qm','later');live=self.g('rev-parse','HEAD')
  with patch.object(p.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps({'commit':live}).encode())):
   self.assertEqual(p.deployment_status(self.config,commit,self.root),('published',None))

 def test_atomic_push_race_does_not_advance_other_branch(self):
  real=p.git;advanced=[]
  def racing(root,*args,**kw):
   if args[0]=='push' and not advanced:
    tree=real(root,'rev-parse',self.base+'^{tree}')
    other=real(root,'commit-tree',tree,'-p',self.base,'-m','independent remote change')
    real(root,'push','origin',other+':refs/heads/master');advanced.append(other)
   return real(root,*args,**kw)
  with patch.object(p,'git',side_effect=racing):result=self.publish()
  self.assertEqual(result['status'],'blocked');self.assertEqual(self.remote_head(),advanced[0])
  self.assertEqual(self.g('ls-remote','origin','refs/heads/work').split()[0],self.base)

if __name__=='__main__':unittest.main()
