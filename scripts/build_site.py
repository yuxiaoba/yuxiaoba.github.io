#!/usr/bin/env python3
"""Complete Jekyll → math → Pagefind build. No serving or deployment side effects."""
import argparse,json,os,subprocess,shutil
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
def build(source:Path,destination:Path):
 source=source.resolve();destination=destination.resolve()
 from obsidian.tags import load_taxonomy
 load_taxonomy(source/'_data/note_tags.yml')
 if destination==source or destination in source.parents:raise ValueError('Unsafe build destination')
 # Each release is clean; callers use new destinations rather than mutating served output.
 bundler=shutil.which('bundle') or shutil.which('bundle3.2')
 if not bundler:raise RuntimeError('Bundler is required to build the site')
 subprocess.run([bundler,'exec','jekyll','build','--strict_front_matter','--source',str(source),'--destination',str(destination)],cwd=source,env={**os.environ,'BUNDLE_GEMFILE':str(ROOT/'Gemfile')},check=True)
 subprocess.run(['node',str(ROOT/'scripts/render_math.mjs'),str(destination)],cwd=ROOT,check=True)
 indexed=[];languages={};reading_pages=[]
 for p in destination.rglob('*.html'):
  soup=BeautifulSoup(p.read_text(),'html.parser')
  if soup.select_one('[data-pagefind-body]'):
   indexed.append(str(p.relative_to(destination)));lang=soup.html.get('lang','');languages[lang]=languages.get(lang,0)+1
   if soup.select_one('[data-bookmark-article]'):
    route='/'+str(p.relative_to(destination)).removesuffix('index.html')
    reading_pages.append({'path':route,'title':soup.select_one('h1').get_text(' ',strip=True),'lang':lang})
 (destination/'reading-metrics.json').write_text(json.dumps({'version':1,'pages':reading_pages},ensure_ascii=False)+'\n')
 if indexed: subprocess.run([str(ROOT/'node_modules/.bin/pagefind'),'--site',str(destination),'--root-selector','[data-pagefind-body]'],cwd=ROOT,check=True)
 status=destination/'pagefind/status.json';status.parent.mkdir(parents=True,exist_ok=True)
 status.write_text(json.dumps({'total':len(indexed),'pages':indexed,'languages':languages})+'\n')
 # Fail the candidate if an emitted local image reference is broken.
 for p in destination.rglob('*.html'):
  soup=BeautifulSoup(p.read_text(),'html.parser')
  for img in soup.select('.article-body img[src]'):
   src=img['src']
   if src.startswith('/') and not (destination/src.lstrip('/')).is_file():raise ValueError(f'Broken generated image in {p.name}: {src}')
  if soup.select('script[type^="math/tex"]'):raise ValueError('Unrendered mathematics')
 for forbidden in ['.handoff','.sync-state','.metrics','docs','scripts','node_modules','AGENTS.md']:
  if (destination/forbidden).exists():raise ValueError(f'Private/build content leaked: {forbidden}')
 return {'indexed_pages':len(indexed),'destination':str(destination)}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=ROOT);parser.add_argument('--destination',type=Path,default=ROOT/'.preview/build')
 a=parser.parse_args();print(json.dumps(build(a.source,a.destination)))
