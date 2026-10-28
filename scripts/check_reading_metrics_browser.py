"""Exercise real TLS/CORS against isolated validation storage; never pollute live metrics."""
import base64
import json
import mimetypes
import os
from pathlib import Path
from urllib.parse import urlsplit, unquote
import requests
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(ROOT/'.preview/browsers')
settings=json.loads((ROOT/'.metrics/settings.json').read_text())
assert settings['directory'].endswith('/validation'), 'Browser writes must use isolated validation data'
access=json.loads((ROOT/'.metrics/admin-access.json').read_text())
origin='https://yuxiaoba.github.io';endpoint='https://111.119.236.134'
auth=(access['username'],access['password'])
out=ROOT/'.preview/metrics-browser';out.mkdir(exist_ok=True)
base=ROOT/'.preview/current'
def stats():
 r=requests.get(endpoint+'/api/stats',auth=auth,timeout=15);r.raise_for_status();return r.json()
def count():return stats()['views']
checks=[]
def serve(route):
 url=urlsplit(route.request.url);path=(base/unquote(url.path).lstrip('/'))
 if path.is_dir():path=path/'index.html'
 if path.is_file():route.fulfill(status=200,content_type=mimetypes.guess_type(path.name)[0] or 'application/octet-stream',body=path.read_bytes())
 else:route.fulfill(status=404,body='Not found')

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=p.chromium.executable_path,args=['--no-sandbox'])
 def context(init='',real_browser=True,width=390):
  ctx=browser.new_context(viewport={'width':width,'height':950},user_agent='Mozilla/5.0 MetricsValidation Chrome/140.0 Safari/537.36')
  if real_browser:ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>false});")
  if init:ctx.add_init_script(init)
  ctx.route(origin+'/**',serve)
  return ctx
 before=count();ctx=context();page=ctx.new_page();sent=[];errors=[]
 page.on('request',lambda r:sent.append(r.post_data_json) if r.url==endpoint+'/api/count' and r.method=='POST' else None)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(origin+'/tech/zh/scout-sre/?query=PRIVATE#paper-PRIVATE',wait_until='networkidle')
 assert count()==before+1
 assert sent[-1]['path']=='/tech/zh/scout-sre/' and set(sent[-1])=={'path','event'}
 page.reload(wait_until='networkidle');assert count()==before+2
 page.goto(origin+'/tech/en/scout-sre/',wait_until='networkidle');assert count()==before+3
 rows={r['path']:r for r in stats()['pages']};assert rows['/tech/zh/scout-sre/']['visitors']==1
 checks.append('Real IP TLS + cross-origin JSON preflight + pageviews + daily visitor dedup + canonical paths')
 page.goto(origin+'/zh/privacy/',wait_until='networkidle')
 page.locator('[data-metrics-off]').click();assert '关闭' in page.locator('[data-metrics-status]').inner_text()
 page.goto(origin+'/tech/zh/scout-sre/',wait_until='networkidle');assert count()==before+3
 page.goto(origin+'/privacy/',wait_until='networkidle');assert 'disabled' in page.locator('[data-metrics-status]').inner_text()
 page.locator('[data-metrics-on]').click();page.goto(origin+'/tech/en/scout-sre/',wait_until='networkidle');assert count()==before+4
 assert not errors;ctx.close();checks.append('Cross-language browser opt-out, persistence and re-enable')
 for name,init,real in [('automation','',False),('dnt',"Object.defineProperty(navigator,'doNotTrack',{get:()=> '1'});",True),('gpc',"Object.defineProperty(navigator,'globalPrivacyControl',{get:()=>true});",True),('blocked_storage',"Storage.prototype.getItem=()=>{throw new Error('blocked')};",True)]:
  before=count();ctx=context(init,real);page=ctx.new_page();page.goto(origin+'/tech/zh/scout-sre/',wait_until='networkidle');assert count()==before;ctx.close();checks.append(name+' excluded')
 before=count();ctx=context();page=ctx.new_page()
 for route in ['/','/zh/','/bookmarks/','/zh/bookmarks/','/search/','/zh/search/']:
  page.goto(origin+route,wait_until='networkidle');assert page.locator('script[data-reading-metrics]').count()==0
 assert count()==before;ctx.close();checks.append('Home, search and private bookmarks excluded')
 before=count();ctx=context();page=ctx.new_page();page.goto('http://127.0.0.1:4001/tech/zh/scout-sre/',wait_until='networkidle');assert count()==before;ctx.close();checks.append('Existing preview never sends production metrics')
 before=count();ctx=context();ctx.route(endpoint+'/api/count',lambda route:route.abort());page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(origin+'/tech/zh/scout-sre/',wait_until='networkidle');assert page.locator('.article-body').is_visible();assert not errors;assert count()==before;ctx.close();checks.append('Metrics outage does not break reading')
 before=count();ctx=context("Object.defineProperty(document,'visibilityState',{get:()=>window.testVisibility||'hidden'});");page=ctx.new_page();page.goto(origin+'/tech/zh/scout-sre/',wait_until='networkidle');assert count()==before
 page.evaluate("window.testVisibility='visible';document.dispatchEvent(new Event('visibilitychange'))");page.wait_for_timeout(1000);assert count()==before+1
 page.evaluate("document.dispatchEvent(new Event('visibilitychange'))");page.wait_for_timeout(300);assert count()==before+1;ctx.close();checks.append('Hidden page waits for visibility and counts only once')
 assert requests.get(endpoint+'/admin',timeout=15).status_code==401
 assert requests.get(endpoint+'/api/stats',timeout=15).status_code==401
 assert requests.get(endpoint+'/.metrics/settings.json',timeout=15).status_code==404
 ctx=browser.new_context(http_credentials={'username':auth[0],'password':auth[1]})
 page=ctx.new_page()
 for width in [390,1440]:
  page.set_viewport_size({'width':width,'height':950});page.goto(endpoint+'/admin',wait_until='networkidle')
  assert page.locator('h1').inner_text()=='私人阅读统计';assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.screenshot(path=str(out/f'dashboard-{width}.png'))
 ctx.close();checks.append('Owner-only dashboard, no private file exposure, mobile/desktop layout')
 for lang in ['zh','en']:
  for width in [320,390,1440]:
   ctx=context(width=width);page=ctx.new_page();page.goto(origin+('/zh' if lang=='zh' else '')+'/privacy/',wait_until='networkidle')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');ctx.close()
 checks.append('Bilingual privacy page at 320/390/1440px')
 browser.close()
(out/'checks.json').write_text(json.dumps(checks,indent=2));print('PASS:',len(checks),'analytics integration checks; validation data remains isolated')
