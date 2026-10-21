import argparse,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from obsidian.transaction import pull,activate
from obsidian.exporter import ExportError
from run_obsidian_sync import run
class TransactionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.repo=self.root/'repo';self.repo.mkdir();self.site=self.root/'site';self.site.mkdir()
  self.git('init','-b','main');self.git('config','user.email','fixture@example.invalid');self.git('config','user.name','Local test fixture')
  (self.repo/'Paper').mkdir();(self.repo/'Tech Report').mkdir();(self.repo/'Tech Report/.gitkeep').touch()
  self.note=self.repo/'Paper/note.md';self.note.write_text('---\ntitle: Committed test\nid: committed\npublish: true\ndate: 2026-10-11\npaper_url: https://example.org/paper\n---\nPublic test content\n')
  self.commit('Initial real test commit')
  self.args=argparse.Namespace(site=self.site,source_repo=self.repo,branch='main',pull=False,dry_run=False,image_reviews=None)
 def tearDown(self):self.tmp.cleanup()
 def git(self,*args):return subprocess.run(['git','-C',str(self.repo),*args],check=True,capture_output=True,text=True).stdout.strip()
 def commit(self,message):self.git('add','-A');self.git('commit','-m',message)
 def fake_build(self,source,destination):
  destination.mkdir();(destination/'pagefind').mkdir();(destination/'pagefind/status.json').write_text('{"total":1}')
  (destination/'index.html').write_text('Valid complete test output');return {'indexed_pages':1}
 def test_failure_retains_last_release_and_managed_sources(self):
  with patch('run_obsidian_sync.build',side_effect=self.fake_build):first=run(self.args)
  self.assertTrue(first['success'],first);before=(self.site/'.preview/current').resolve();managed=self.site/'_digest/zh/obsidian/daily-2026-10-11.md';old=managed.read_bytes()
  self.note.write_text(self.note.read_text().replace('Public test content','Changed source'));self.commit('Change publication')
  with patch('run_obsidian_sync.build',side_effect=RuntimeError('deliberate build failure')):second=run(self.args)
  self.assertFalse(second['success']);self.assertEqual((self.site/'.preview/current').resolve(),before);self.assertEqual(managed.read_bytes(),old)
 def test_identical_run_and_unpublish_only_owned_content(self):
  with patch('run_obsidian_sync.build',side_effect=self.fake_build) as builder:
   self.assertTrue(run(self.args)['success']);second=run(self.args);self.assertTrue(second['unchanged']);self.assertEqual(builder.call_count,1)
   manual=self.site/'_digest/zh/manual.md';manual.write_text('Handwritten note')
   self.note.write_text(self.note.read_text().replace('publish: true','publish: false'));self.commit('Withdraw note')
   self.assertTrue(run(self.args)['success']);self.assertFalse((self.site/'_digest/zh/obsidian/daily-2026-10-11.md').exists());self.assertEqual(manual.read_text(),'Handwritten note')
 def test_dirty_source_never_pulled(self):
  self.note.write_text('Uncommitted source edits')
  result=run(self.args);self.assertFalse(result['success']);self.assertIn('local changes',result['error']);self.assertEqual(self.note.read_text(),'Uncommitted source edits')
 def test_source_rename_keeps_id(self):
  with patch('run_obsidian_sync.build',side_effect=self.fake_build):
   run(self.args);self.note.rename(self.repo/'Paper/renamed.md');self.commit('Move source file');result=run(self.args)
  self.assertTrue(result['success']);self.assertEqual(len(list((self.site/'_digest').rglob('*.md'))),1)
 def test_divergence_preserves_both_histories(self):
  remote=self.root/'remote.git';subprocess.run(['git','clone','--bare',str(self.repo),str(remote)],check=True,capture_output=True)
  self.git('remote','add','origin',str(remote))
  peer=self.root/'peer';subprocess.run(['git','clone',str(remote),str(peer)],check=True,capture_output=True)
  for k,v in [('user.email','fixture@example.invalid'),('user.name','Peer')]:subprocess.run(['git','-C',str(peer),'config',k,v],check=True)
  (peer/'remote.txt').write_text('remote');subprocess.run(['git','-C',str(peer),'add','.'],check=True);subprocess.run(['git','-C',str(peer),'commit','-m','Remote test commit'],check=True,capture_output=True);subprocess.run(['git','-C',str(peer),'push','origin','main'],check=True,capture_output=True)
  (self.repo/'local.txt').write_text('local');self.commit('Local divergent test commit');head=self.git('rev-parse','HEAD')
  with self.assertRaises(ExportError):pull(self.repo,update=True)
  self.assertEqual(self.git('rev-parse','HEAD'),head);self.assertEqual((self.repo/'local.txt').read_text(),'local')
if __name__=='__main__':unittest.main()
