#!/usr/bin/env python3
"""Check an isolated real-day build, without publishing source notes."""
import argparse,functools,json,os,threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(ROOT/'.preview/browsers'))
from playwright.sync_api import sync_playwright,expect
p=argparse.ArgumentParser();p.add_argument('--site',type=Path,required=True);a=p.parse_args()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(a.site)))
threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
day='/digest/zh/daily/2026-10-11/';checks=[];errors=[]
try:
 with sync_playwright() as play:
  browser=play.chromium.launch(executable_path=play.chromium.executable_path,args=['--no-sandbox']);page=browser.new_page()
  page.on('pageerror',lambda error:errors.append(str(error)))
  for width in [320,390,768,1280]:
   page.set_viewport_size({'width':width,'height':1000})
   for route in [day,'/zh/digest/','/digest/','/zh/search/','/search/','/zh/tech/','/tech/']:
    page.goto(base+route,wait_until='networkidle')
    if route==day:
     expect(page.locator('.daily-toc li')).to_have_count(6)
     expect(page.locator('.daily-paper-title')).to_have_count(6)
     expect(page.locator('.note-image-link img')).to_have_count(24)
     expect(page.locator('.katex')).to_have_count(60)
     for img in page.locator('.note-image-link img').all():
      img.scroll_into_view_if_needed();img.evaluate('(i)=>i.decode()')
      assert img.locator('..').get_attribute('target')=='_blank'
      assert img.evaluate('(i)=>{const r=i.getBoundingClientRect();return Math.abs((r.width/r.height)/(i.naturalWidth/i.naturalHeight)-1)<0.01}')
     ids=page.locator('[id]').evaluate_all('(es)=>es.map(e=>e.id)');assert len(ids)==len(set(ids))
     for link in page.locator('.daily-toc a').all():
      target=link.get_attribute('href');assert page.locator(target).count()==1
     page.evaluate("scrollTo({top:0,behavior:'instant'})")
     page.screenshot(path=str(ROOT/f'.preview/daily-{width}.png'))
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,route)
    checks.append(f'{width} {route}')
  page.goto(base+'/zh/search/',wait_until='networkidle')
  for query in ['MASS','Cadence','MORA','NosRacer','工作流','RSI']:
   page.locator('input[name=q]').fill(query)
   expect(page.locator('.search-results a').filter(has_text='2026年10月11日')).to_have_count(1)
   checks.append('search '+query)
  if page.locator('.search-refinements').count():page.locator('.search-refinements > summary').click()
  page.locator('select[name=type]').select_option('tech');expect(page.locator('.search-results a')).to_have_count(0)
  page.locator('select[name=type]').select_option('paper');page.locator('select[name=tag]').select_option('self-improvement');expect(page.locator('.search-results a')).to_have_count(1)
  page.goto(base+'/search/',wait_until='networkidle');page.locator('input[name=q]').fill('MASS');expect(page.locator('.search-results a')).to_have_count(0)
  page.goto(base+'/digest/zh/obsidian/mass-2026/',wait_until='networkidle');assert page.url==base+day+'#paper-mass-2026'
  page.locator('.language-switch a[lang=en]').click();assert page.url==base+'/digest/?translation=missing'
  page.goto(base+day,wait_until='networkidle');page.locator('.daily-toc a[href="#paper-cadence-2026"]').click();assert page.url.endswith('#paper-cadence-2026')
  assert not errors,errors
  browser.close()
  report={'viewport_checks':28,'papers':6,'images':24,'math_expressions':60,'search_queries':6,'filters':'passed','redirects_and_anchors':'passed','missing_translation':'passed','console_errors':errors,'checks':checks}
  (ROOT/'.preview/daily-browser-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
finally:server.shutdown()
