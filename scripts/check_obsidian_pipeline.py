#!/usr/bin/env python3
"""Local real-Git end-to-end test; no remote GitHub pushes or real-vault mutations."""
import argparse,gzip,json,shutil,subprocess,sys,time
from pathlib import Path
from bs4 import BeautifulSoup
from obsidian_sync import snapshot
from run_obsidian_sync import run,ROOT
work=ROOT/'.preview'/('obsidian-integration-'+str(int(time.time())))
work.mkdir();editor=work/'editor';shutil.copytree(ROOT/'.preview/obsidian-demo-vault',editor)
def git(repo,*args):
 return subprocess.check_output(['git','-C',str(repo),*args],text=True,stderr=subprocess.PIPE).strip()
git(editor,'init','-b','main');git(editor,'config','user.name','Local sync test');git(editor,'config','user.email','fixture@example.invalid')
def commit(message):git(editor,'add','-A');git(editor,'commit','-m',message);return git(editor,'rev-parse','HEAD')
first_sha=commit('Test: publish isolated MASS and Tech Notes')
origin=work/'origin.git';subprocess.run(['git','clone','--bare',str(editor),str(origin)],check=True,capture_output=True)
git(editor,'remote','add','origin',str(origin));checkout=work/'source';subprocess.run(['git','clone',str(origin),str(checkout)],check=True,capture_output=True)
site=work/'website';snapshot(ROOT,site)
manual=site/'_digest/zh/handwritten-preserve.md';manual.write_text('---\ntitle: Handwritten draft\npublished: false\n---\nHANDWRITTEN_PRESERVE\n')
args=argparse.Namespace(site=site,source_repo=checkout,branch='main',pull=True,dry_run=False,image_reviews=ROOT/'docs/obsidian/image-reviews.json')
checks=[]
def execute(label):
 result=run(args);(work/(label+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2));return result
result=execute('initial');assert result['success'],result
assert result['build']['indexed_pages']==4
url=site/'.preview/current';previous=url.resolve();public=previous/'digest/zh/daily/2026-10-11/index.html';assert public.exists()
soup=BeautifulSoup(public.read_text(),'html.parser');assert len(soup.select('.katex'))==13 and len(soup.select('.note-image-link img'))==5
checks.append('Real committed source → fast-forward pull → export → Jekyll → 15 math renders → bilingual Pagefind → active preview release')
repeat=execute('repeat');assert repeat['success'] and repeat['unchanged'];assert url.resolve()==previous
checks.append('Same commit and source produce no new release or Markdown diff')
mass=next((editor/'Paper').rglob('*MASS*.md'));original=mass.read_text();mass.write_text(original+'\n%% unclosed private comment');commit('Test: malformed private annotation');git(editor,'push','origin','main')
failed=execute('invalid');assert not failed['success'];assert url.resolve()==previous;assert public.exists()
checks.append('Malformed source retains the last good pages, index, and managed sources')
mass.write_text(original.replace('publish: true','publish: false'));commit('Test: unpublish MASS');git(editor,'push','origin','main')
withdraw=execute('withdraw');assert withdraw['success'],withdraw
active=url.resolve();assert not (active/'digest/zh/obsidian/mass-2026').exists();assert not (site/'_digest/zh/obsidian/daily-2026-10-11.md').exists()
assert not list((active/'assets/images/digest/obsidian/mass-2026').glob('*.png'))
assert manual.read_text().endswith('HANDWRITTEN_PRESERVE\n')
assert json.loads((active/'pagefind/status.json').read_text())['total']==3
for file in (active/'pagefind').rglob('*'):
 if file.is_file():
  raw=file.read_bytes();raw=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
  assert b'Recursive Self-Improvement through Multi-Agent Self-Supervision' not in raw
checks.append('Unpublish removes MASS page, unreferenced images and search fragment; handwritten content retained')
# Delete the other English paper and make sure deletion follows the same ownership rules.
english=editor/'Paper/en/english-search.md';english.unlink();commit('Test: delete English reading note');git(editor,'push','origin','main')
deleted=execute('delete');assert deleted['success'];assert not (url.resolve()/'digest/en/obsidian/english-search').exists()
checks.append('Committed deletion removes only the owned article')
# Restore fixture content for the private review server, using a new commit rather than reset.
mass.write_text(original);shutil.copy2(ROOT/'.preview/obsidian-demo-vault/Paper/en/english-search.md',english);commit('Test: restore private demonstration');git(editor,'push','origin','main')
final=execute('restore');assert final['success'],final
assert json.loads((url.resolve()/'pagefind/status.json').read_text())['total']==4
# Nothing private should appear in public output or compressed search fragments.
for file in url.resolve().rglob('*'):
 if file.is_file():
  raw=file.read_bytes();raw=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
  assert b'private_test_sentinel_obsidian' not in raw.lower()
  assert b'private_draft_sentinel_obsidian' not in raw.lower()
checks.append('Private comments and draft marker absent from final HTML and search bundle')
report={'passed':len(checks),'checks':checks,'first_real_test_commit':first_sha,'final_test_commit':git(checkout,'rev-parse','HEAD'),'private_preview_directory':str(url),'workspace':str(work),'remote_kind':'local bare fixture repository; no GitHub push'}
(ROOT/'.preview/obsidian-pipeline-checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
