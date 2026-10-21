#!/usr/bin/env python3
"""Real-browser checks against a private fixture build, never production notes."""
import argparse,functools,gzip,json,os,threading,urllib.parse
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(ROOT/'.preview/browsers'))
from playwright.sync_api import sync_playwright,expect
p=argparse.ArgumentParser();p.add_argument('--site',type=Path,default=ROOT/'.preview/obsidian-demo-site');a=p.parse_args()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(a.site)))
threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
checks=[];errors=[]
try:
 with sync_playwright() as play:
  browser=play.chromium.launch(executable_path=play.chromium.executable_path,args=['--no-sandbox']);page=browser.new_page()
  page.on('pageerror',lambda e:errors.append(str(e)))
  routes=['/zh/digest/','/digest/','/zh/tech/','/tech/','/zh/search/','/search/','/digest/zh/obsidian/mass-2026/','/tech/zh/obsidian/sync-engine/','/tech/en/obsidian/sync-engine/']
  for width in [320,390,768,821,1280,1440]:
   page.set_viewport_size({'width':width,'height':1000})
   for route in routes:
    page.goto(base+route,wait_until='networkidle')
    for img in page.locator('.article-body img').all():img.scroll_into_view_if_needed();img.evaluate('(i)=>i.decode()')
    page.evaluate('window.scrollTo(0,0)')
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,route)
    assert page.locator('.navigation a').count()==5
    if 'mass-2026' in route:
     assert page.locator('.article-body img').count()==5
     assert page.locator('.katex').count()==13
     for image in page.locator('.article-body img').all():assert image.locator('..').get_attribute('target')=='_blank'
    if width in [390,1280] and route in ['/digest/zh/obsidian/mass-2026/','/zh/search/','/zh/tech/']:
     page.screenshot(path=str(ROOT/f'.preview/obsidian-{width}-{route.strip("/").replace("/","-")}.png'),full_page=True)
    checks.append(f'{width} {route}')
  # Test both actual user-facing forms and the language-specific search API.
  page.goto(base+'/zh/search/',wait_until='networkidle')
  for query in ['MASS','recursive','工作流','RSI']:
   page.locator('input[name=q]').fill(query)
   expect(page.locator('.search-results a').filter(has_text='2026年10月11日 · 论文阅读')).to_have_count(1)
   checks.append('Chinese index query '+query)
  if page.locator('.search-refinements').count():page.locator('.search-refinements > summary').click()
  page.locator('select[name=type]').select_option('tech')
  expect(page.locator('.search-results a').filter(has_text='2026年10月11日 · 论文阅读')).to_have_count(0)
  page.locator('input[name=q]').fill('原子同步')
  expect(page.locator('.search-results a').filter(has_text='临时技术验证')).to_have_count(1)
  page.locator('select[name=tag]').select_option('self-improvement')
  expect(page.locator('.search-results a')).to_have_count(0)
  page.locator('[data-search-clear]').click()
  expect(page.locator('input[name=q]')).to_be_focused()
  page.locator('select[name=type]').select_option('paper')
  page.locator('select[name=tag]').select_option('self-improvement')
  expect(page.locator('.search-results a').filter(has_text='2026年10月11日 · 论文阅读')).to_have_count(1)
  page.locator('input[name=q]').fill('PRIVATE_TEST_SENTINEL_OBSIDIAN')
  expect(page.locator('.search-results a')).to_have_count(0)
  for route,expected in [('/zh/digest/','paper'),('/zh/tech/','tech')]:
   page.goto(base+route,wait_until='networkidle');expect(page.locator('select[name=type]')).to_have_value(expected)
  page.goto(base+'/search/',wait_until='networkidle');page.locator('input[name=q]').fill('MASS');expect(page.locator('.search-results a')).to_have_count(0)
  page.locator('input[name=q]').fill('ENGLISH_ONLY_SENTINEL');expect(page.locator('.search-results a').filter(has_text='Temporary technical')).to_have_count(1)
  page.goto(base+'/digest/zh/obsidian/mass-2026/');page.locator('.language-switch a[lang=en]').click()
  assert page.url==base+'/digest/?translation=missing';expect(page.locator('[data-translation-notice]')).to_be_visible()
  page.goto(base+'/tech/zh/obsidian/sync-engine/');page.locator('.language-switch a[lang=en]').click();assert page.url==base+'/tech/en/obsidian/sync-engine/'
  page.goto(base+'/tech/zh/obsidian/sync-engine/');page.get_by_role('link',name='公开阅读',exact=True).click()
  target=urllib.parse.unquote(urllib.parse.urlsplit(page.url).fragment);assert page.locator(f'[id="{target}"]').count()==1
  page.goto(base+'/tech/zh/obsidian/sync-engine/');assert '{{ site.email }}' in page.locator('pre code').inner_text();assert 'guangbayu@cuhk.edu.hk' not in page.locator('pre code').inner_text()
  assert not errors,errors
  # Searchable fragments and public output must not contain private markers, even compressed.
  for path in a.site.rglob('*'):
   if not path.is_file():continue
   raw=path.read_bytes()
   if raw.startswith(b'\x1f\x8b'):raw=gzip.decompress(raw)
   assert b'private_test_sentinel_obsidian' not in raw.lower(),str(path)
   assert b'private_draft_sentinel_obsidian' not in raw.lower(),str(path)
  browser.close()
  result={'viewport_checks':54,'search_queries':4,'interaction_checks':'passed','privacy_scan':'passed','console_errors':errors,'checks':checks}
  (ROOT/'.preview/obsidian-browser-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
  print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
finally:server.shutdown()
