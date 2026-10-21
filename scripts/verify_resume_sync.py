#!/usr/bin/env python3
"""Audit the sync against the recorded source snapshot and original site records."""
import hashlib,json,re
from pathlib import Path
from bs4 import BeautifulSoup
from verify_site import metadata
ROOT=Path(__file__).resolve().parents[1]
audit=json.loads((ROOT/'docs/resume-sync-data.json').read_text())
source=Path(audit['source']);checks=[]
def check(ok,message):
 assert ok,message
 checks.append(message)
clean=lambda value:re.sub('[†#✉\ufe0f*]','',value).strip()
for file,digest in audit['source_hashes'].items():check(hashlib.sha256((source/file).read_bytes()).hexdigest()==digest,'resume source unchanged '+file)
for row in audit['publication_mapping']:
 d=metadata(ROOT/row['path'])
 check(d['title']==row['title'],'source title '+row['path'])
 check([clean(a) for a in d['authors']]==row['authors'],'source authors '+row['path'])
 check(d['year']==row['year'],'source year '+row['path'])
 check(d['venue']==row['venue'] and d.get('ccf')==row['ccf'],'source venue/CCF '+row['path'])
 if row['positive_corresponding']:check(any(clean(a)=='Guangba Yu' and any(m in a for m in ['†','#','✉']) for a in d['authors']),'source corresponding '+row['path'])
 check(bool(d.get('preprint'))==row['preprint'],'source publication status '+row['path'])
# The old raw abstracts and local/remote resources must survive the metadata update.
for row in json.loads((ROOT/'.preview/resume-sync-baseline.json').read_text()):
 d=metadata(ROOT/row['path'])
 check(d.get('abstract')==row['data'].get('abstract'),'original abstract preserved '+row['path'])
 check(d.get('links')==row['data'].get('links'),'original resources preserved '+row['path'])
for path in audit['retained_outside_resume']:check((ROOT/path).exists(),'existing publication absent from CV retained '+path)
for lang,filename,heading in [('en','cv-en.html','Honors & Awards'),('zh','cv-A-zh.html','获奖情况')]:
 cv=BeautifulSoup((source/filename).read_text(),'html.parser')
 node=next(h for h in cv.select('h3') if h.get_text('',strip=True)==heading)
 expected=[]
 for el in node.find_next_siblings():
  if el.name=='h3':break
  if 'row' in el.get('class',[]):expected.append(el.find('div').get_text(' ',strip=True))
 home=BeautifulSoup((ROOT/'.preview/current'/('zh/' if lang=='zh' else '')/'index.html').read_text(),'html.parser')
 actual=[el.get_text(' ',strip=True) for el in home.select('.awards-list li span')]
 check(len(actual)==len(expected)==11,'all 11 sourced awards '+lang)
 for name in expected:
  # The last Rhino-Bird item keeps the previously confirmed special-scholarship suffix.
  check(any(name==a or ('Rhino-Bird' in name and 'Rhino-Bird' in a) or ('犀牛鸟' in name and '犀牛鸟' in a) for a in actual),'award source '+lang+' '+name)
 check(('National Scholarship' if lang=='en' else '国家奖学金') in home.text,'scholarship visible '+lang)
 check(len(home.select('.education-entry'))==3,'three degrees '+lang)
 check('2014.09–2018.07' in home.text and ('Xiufeng Liu' if lang=='en' else '刘秀峰') in home.text,'undergraduate details '+lang)
 check(('Sub-reviewer' if lang=='en' else '协助审稿') not in home.select_one('.service').text,'sub-reviewer hidden '+lang)
 check('FSE 2027' in home.select_one('.service').text and 'ICSME 2026' in home.select_one('.service').text,'new service visible '+lang)
 check(('traditional Chinese medicine' if lang=='en' else '起点不是代码，而是中医') in home.text,'personal story retained '+lang)
 pubs=BeautifulSoup((ROOT/'.preview/current'/('zh/' if lang=='zh' else '')/'publications/index.html').read_text(),'html.parser')
 check(len(pubs.select('.publication-entry'))==59,'59 publication records '+lang)
 check(sum(v.text.strip()=='arXiv' for v in pubs.select('.venue-name'))==3,'three arXiv source labels '+lang)
 check(not pubs.select('.publication-kind'),'no extra Preprint label '+lang)
 check(len(pubs.select('.publication-source'))==59,'full source line on every paper '+lang)
 check(not pubs.select('.paper-abstract'),'abstract display remains removed '+lang)
 check(len(pubs.select('.publication-award'))==4,'three paper awards and one ESI label '+lang)
 for item in pubs.select('.publication-entry'):
  d=metadata(ROOT/item['data-publication'])
  check(item.select_one('.venue-year').text.strip()==str(d.get('year') or str(d['date'])[:4]),'rendered venue year '+lang+' '+item['data-publication'])
 check(all(m.parent.get_text().startswith('Guangba Yu') for m in pubs.select('.corresponding-author')),'only owner correspondence '+lang)
(ROOT/'.preview/resume-sync-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks},ensure_ascii=False,indent=2))
print(f'PASS: {len(checks)} resume-source, original-record preservation, scholarship, service, publication-status and venue/year assertions')
