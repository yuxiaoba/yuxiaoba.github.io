"""Check Markdown further-reading bookmarks without publishing any fixture data."""
import argparse,json,os,re
from pathlib import Path
from urllib.parse import unquote
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--base',default='http://127.0.0.1:4001');p.add_argument('--label',default='preview');args=p.parse_args()
out=ROOT/'.preview/further-reading';out.mkdir(parents=True,exist_ok=True)
os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(ROOT/'.preview/browsers');key='gy-reading-bookmarks-v1';rows=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=p.chromium.executable_path,args=['--no-sandbox'])
 for lang,prefix in [('en',''),('zh','/zh')]:
  for date in ['2026-10-12','2026-10-15']:
   for width in [390,1440]:
    context=b.new_context(viewport={'width':width,'height':1000},accept_downloads=True)
    page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    route='/digest/'+lang+'/daily/'+date+'/'
    assert page.goto(args.base+route,wait_until='networkidle').status==200
    heading=page.locator('.article-body h2').filter(has_text=re.compile(r'^(Further reading|延伸阅读)'))
    assert heading.count()==1
    button=heading.locator('xpath=following-sibling::*[1]').locator('button')
    button.click();assert button.get_attribute('aria-pressed')=='true'
    children=page.locator('.article-body').evaluate("body=>{let active=false;const ids=[];for(const h of body.querySelectorAll('h2,h3')){if(h.tagName==='H2')active=/^(further reading|延伸阅读)/i.test(h.textContent);else if(active)ids.push(h.id)}return ids}")
    assert len(children)==(2 if date=='2026-10-15' else 0)
    for ident in children:
     page.locator('[id='+json.dumps(ident,ensure_ascii=False)+']').locator('xpath=following-sibling::*[1]').locator('button').click()
    # Existing article bookmarks coexist with the new section type.
    page.locator('.bookmark-article-actions button').click()
    page.reload(wait_until='networkidle');assert button.get_attribute('aria-pressed')=='true'
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    if width==390:heading.scroll_into_view_if_needed();page.screenshot(path=str(out/f'{args.label}-{lang}-{date}.png'))
    items=json.loads(page.evaluate('(k)=>localStorage.getItem(k)',key))['items'];assert len(items)==len(children)+2
    assert len([i for i in items if i['kind']=='section'])==len(children)+1
    page.goto(args.base+prefix+'/bookmarks/',wait_until='networkidle');assert page.locator('.saved-note').count()==len(items)
    with page.expect_download() as download:page.locator('[data-bookmark-export]').click()
    backup=Path(download.value.path()).read_bytes()
    page.evaluate('(k)=>localStorage.removeItem(k)',key);page.reload(wait_until='networkidle')
    page.locator('[data-bookmark-file]').set_input_files({'name':'further-reading.json','mimeType':'application/json','buffer':backup})
    page.wait_for_function('(n)=>document.querySelectorAll(".saved-note").length===n',arg=len(items))
    for item in items:
     if item['kind']!='section':continue
     page.goto(args.base+item['url'],wait_until='networkidle')
     target=page.locator('[id='+json.dumps(unquote(item['url'].split('#')[1]),ensure_ascii=False)+']')
     assert target.inner_text()==item['section']
     assert target.locator('xpath=following-sibling::*[1]').locator('button').get_attribute('aria-pressed')=='true'
    # Cancel only the parent; child and old article bookmarks remain.
    button=page.locator('.article-body h2').filter(has_text=re.compile(r'^(Further reading|延伸阅读)')).locator('xpath=following-sibling::*[1]').locator('button')
    button.click();assert len(json.loads(page.evaluate('(k)=>localStorage.getItem(k)',key))['items'])==len(items)-1
    assert not errors,errors
    rows.append({'lang':lang,'date':date,'width':width,'independent_readings':len(children),'backup_and_anchors':True});context.close()
 b.close()
(out/(args.label+'.json')).write_text(json.dumps(rows,indent=2));print('PASS:',len(rows),'bilingual further-reading save/restore/anchor/remove checks')
