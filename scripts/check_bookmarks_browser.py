"""Exercise private bookmarks using an isolated browser context; no test data is uploaded."""
import argparse,json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--base',default='http://127.0.0.1:4001');parser.add_argument('--label',default='preview');args=parser.parse_args()
out=ROOT/'.preview/bookmarks';out.mkdir(exist_ok=True);os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(ROOT/'.preview/browsers')
KEY='gy-reading-bookmarks-v1';rows=[]
def passed(name):rows.append(name)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=p.chromium.executable_path,args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':390,'height':900},accept_downloads=True)
 page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
 route='/digest/zh/daily/2026-10-22/'
 assert page.goto(args.base+route,wait_until='networkidle').status==200
 page.locator('.bookmark-article-actions button').click();assert page.locator('.bookmark-article-actions button').get_attribute('aria-pressed')=='true'
 page.reload(wait_until='networkidle');assert page.locator('.bookmark-article-actions button').get_attribute('aria-pressed')=='true';passed('article bookmark persists after reload')
 page.locator('.bookmark-paper-button').first.click();assert page.locator('.bookmark-paper-button').first.get_attribute('aria-pressed')=='true';passed('individual paper bookmark')
 text=page.locator('.article-body p').nth(3).inner_text()
 page.locator('.article-body p').nth(3).evaluate("e=>{const r=document.createRange();r.selectNodeContents(e);const s=getSelection();s.removeAllRanges();s.addRange(r);document.dispatchEvent(new Event('selectionchange'));}")
 page.locator('.bookmark-selection button').click();passed('selected excerpt saved')
 page.goto(args.base+'/zh/bookmarks/',wait_until='networkidle');assert page.locator('.saved-note').count()==3;assert page.locator('blockquote').inner_text()==text
 assert '#paper-' in page.locator('.saved-note h2 a').nth(1).get_attribute('href');passed('collection contains article, paper anchor and excerpt')
 page.screenshot(path=str(out/(args.label+'-mobile.png')),full_page=True)
 with page.expect_download() as download:page.locator('[data-bookmark-export]').click()
 exported=download.value.path().read_text();data=json.loads(exported);assert len(data['items'])==3;passed('JSON export')
 page.locator('.language-switch a[lang=en]').click();assert page.locator('.saved-note').count()==3;assert page.locator('[data-bookmark-import]').inner_text()=='Import backup';passed('same collection across language switch')
 page.locator('.saved-note-controls button').first.click();assert page.locator('.saved-note').count()==2;passed('remove one bookmark')
 page.locator('[data-bookmark-file]').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':exported.encode()});page.wait_for_function("document.querySelectorAll('.saved-note').length===3")
 page.locator('[data-bookmark-file]').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':exported.encode()});page.wait_for_timeout(150);assert page.locator('.saved-note').count()==3;passed('import merges without duplicates')
 bad=json.loads(exported);bad['items'][0]['url']='javascript:alert(1)';before=page.evaluate('(k)=>localStorage.getItem(k)',KEY)
 page.locator('[data-bookmark-file]').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':json.dumps(bad).encode()});page.wait_for_timeout(150)
 assert page.evaluate('(k)=>localStorage.getItem(k)',KEY)==before;passed('unsafe import rejected without data loss')
 html=json.loads(exported);html['items'][0]['title']='<img src=x onerror=alert(1)>';html['items'][0]['excerpt']='literal <script>alert(1)</script>';html['items'][0]['kind']='excerpt'
 page.locator('[data-bookmark-file]').set_input_files({'name':'text.json','mimeType':'application/json','buffer':json.dumps(html).encode()});page.wait_for_timeout(150)
 assert page.locator('[data-bookmark-list] img,[data-bookmark-list] script').count()==0;passed('imported text cannot execute HTML')
 # Another tab updates article state through the storage event.
 other=context.new_page();other.goto(args.base+route,wait_until='networkidle');other.locator('.bookmark-article-actions button').click();page.wait_for_function("document.querySelectorAll('.saved-note').length===3");passed('cross-tab state refresh')
 # Check both languages and small/wide layouts, including header navigation.
 for lang,prefix in [('zh','/zh'),('en','')]:
  for width in [320,390,768,1440]:
   page.set_viewport_size({'width':width,'height':900})
   for path in [prefix+'/',prefix+'/bookmarks/','/tech/'+lang+'/eagle-4/']:
    assert page.goto(args.base+path,wait_until='networkidle').status==200
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,path)
   passed(f'{lang} {width}px homepage, bookmarks and article')
 # Browser storage errors must never claim successful saving.
 blocked=browser.new_context();blocked.add_init_script("Storage.prototype.setItem=function(){throw new DOMException('full','QuotaExceededError')}")
 bp=blocked.new_page();bp.goto(args.base+'/tech/en/eagle-4/',wait_until='networkidle');bp.locator('.bookmark-article-actions button').click()
 assert bp.locator('.bookmark-status').inner_text().startswith('Unable to save');assert bp.locator('.bookmark-article-actions button').get_attribute('aria-pressed')=='false';passed('storage write failure reported honestly');blocked.close()
 corrupt=browser.new_context();cp=corrupt.new_page();cp.goto(args.base+'/bookmarks/');cp.evaluate('(k)=>localStorage.setItem(k,"broken")',KEY);cp.reload(wait_until='networkidle')
 assert 'Unable to save' in cp.locator('[data-bookmark-list]').inner_text();assert cp.evaluate('(k)=>localStorage.getItem(k)',KEY)=='broken';passed('corrupt storage preserved');corrupt.close()
 nojs=browser.new_context(java_script_enabled=False);np=nojs.new_page();np.goto(args.base+'/tech/en/eagle-4/');assert np.locator('.article-body').inner_text();np.goto(args.base+'/bookmarks/');assert np.locator('noscript').is_visible();passed('no-JS reading and explanation');nojs.close()
 # Touch-sized selection saving and keyboard accessibility.
 touch=browser.new_context(is_mobile=True,has_touch=True,viewport={'width':390,'height':844})
 tp=touch.new_page();tp.goto(args.base+'/tech/zh/eagle-4/',wait_until='networkidle')
 tp.locator('.article-body p').first.evaluate("e=>{const r=document.createRange();r.selectNodeContents(e);const s=getSelection();s.removeAllRanges();s.addRange(r);document.dispatchEvent(new Event('selectionchange'));}")
 tp.locator('.bookmark-selection button').tap();assert '已保存' in tp.locator('.bookmark-status').inner_text();passed('touch activation saves selection');touch.close()
 keyboard=browser.new_context();kp=keyboard.new_page();kp.goto(args.base+'/tech/en/eagle-4/',wait_until='networkidle');kb=kp.locator('.bookmark-article-actions button');kb.focus();kp.keyboard.press('Enter');assert kb.get_attribute('aria-pressed')=='true';passed('keyboard bookmark toggle');keyboard.close()
 assert not errors,errors
 context.close();browser.close()
(out/(args.label+'-checks.json')).write_text(json.dumps({'base':args.base,'passed':len(rows),'checks':rows},indent=2));print('PASS:',len(rows),'bookmark behavior and responsive checks')
