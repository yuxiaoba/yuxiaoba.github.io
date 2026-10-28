"""Verify owner-approved editorial withdrawals without changing browser storage."""
import argparse,json,os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(ROOT/'.preview/browsers')
parser=argparse.ArgumentParser();parser.add_argument('--base',default='http://127.0.0.1:4001');parser.add_argument('--label',default='preview');args=parser.parse_args()
out=ROOT/'.preview/curation-apply-2026-10-27';out.mkdir(parents=True,exist_ok=True)
withdrawn=['deepseek-search-fetch','aws-well-architected-agent','grafana-workflows','agentic-distributed-systems','modal-observability','fca-ai-near-misses']
checks=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=p.chromium.executable_path,args=['--no-sandbox'])
 context=browser.new_context();page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
 index=context.request.get(args.base+'/pagefind/status.json').json()
 assert index['total']==186,index['total']
 for lang,prefix in [('zh','/zh'),('en','')]:
  for slug in withdrawn:
   route=f'/tech/{lang}/{slug}/'
   assert context.request.get(args.base+route).status==404,route
   assert route.strip('/')+'/index.html' not in index['pages']
  assert f'tech/{lang}/minimax-m31-flash/index.html' not in index['pages']
  for width in [390,1440]:
   page.set_viewport_size({'width':width,'height':950})
   for day in ['03','07','09','15','16','27']:
    route=f'/digest/{lang}/daily/2026-10-{day}/'
    assert page.goto(args.base+route,wait_until='networkidle').status==200
    body=page.locator('.article-body');text=body.inner_text();links=body.locator('a[href]').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))')
    if day=='03':assert not any('2106054821065425221' in u for u in links)
    if day=='07':
     assert page.locator('.daily-paper-title').count()==4
     assert page.locator('#paper-arxiv-2610\\.10256').count()==0
     assert 'OOM-RL' not in page.locator('main').inner_text()
     assert page.locator('#paper-arxiv-2610\\.10961').inner_text().startswith('04')
     results=page.evaluate('async()=>{const pf=await import("/pagefind/pagefind.js");return (await pf.search("OOM-RL II")).results.length}')
     assert results==0,results
     if width==390:page.screenshot(path=str(out/f'{args.label}-{lang}-digest.png'))
    if day=='09':
     assert not any('2108630569026294124' in u for u in links)
     assert 'CVE-2026-69435' in text
    if day=='15':
     assert f'/tech/{lang}/scout-sre/' in links
     assert 'RaReCache' in text and '2610.11358' in ' '.join(links)
     assert not any('/scout.png' in s for s in body.locator('img').evaluate_all('(es)=>es.map(e=>e.getAttribute("src"))'))
    if day=='16':
     assert not any('2111170417259958620' in u for u in links)
     assert any('2111092741954515119' in u for u in links)
    if day=='27':
     assert f'/digest/{lang}/daily/2026-10-22/#paper-arxiv-2610.28577' in links
     assert 'Resin' in text and page.locator('.daily-paper-title').count()==6
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),route
    checks.append({'lang':lang,'width':width,'route':route,'passed':True})
   page.goto(args.base+f'/tech/{lang}/minimax-m31-flash/',wait_until='networkidle')
   page.wait_for_url('**/minimax-m31-serving/')
   assert page.locator('.article-body a[href="https://www.minimax.io/blog/minimax-m31f"]').count()==1
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   checks.append({'lang':lang,'width':width,'merged_redirect':True})
   page.goto(args.base+prefix+'/tech/',wait_until='networkidle')
   for slug in withdrawn+['minimax-m31-flash']:
    assert page.locator(f'a[href="/tech/{lang}/{slug}/"]').count()==0
   assert page.locator(f'a[href="/tech/{lang}/minimax-m31-serving/"]').count()>0
   checks.append({'lang':lang,'width':width,'archive_exclusion':True})
 assert not errors,errors
 browser.close()
(out/(args.label+'-checks.json')).write_text(json.dumps({'checks':checks,'index_pages':186,'withdrawn_routes':12},indent=2))
print('PASS:',len(checks),'bilingual page/layout checks; 12 withdrawals; merged redirects; search exclusion')
