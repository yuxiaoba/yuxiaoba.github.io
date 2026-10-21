#!/usr/bin/env python3
"""Focused regression checks for publication navigation, authors and topic labels."""
import functools,json,os,threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(ROOT/'.preview/browsers'))
from playwright.sync_api import sync_playwright,expect
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'.preview/fixture-site')))
threading.Thread(target=server.serve_forever,daemon=True).start()
rows=[];errors=[]
from verify_site import metadata
publication_count=sum(metadata(p).get("published") is not False for p in (ROOT/"_publications").rglob("*.md"))
try:
 with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=p.chromium.executable_path,args=['--no-sandbox'])
    page=browser.new_page(reduced_motion='reduce')
    page.on('pageerror',lambda e:errors.append(str(e)))
    for width in [320,390,600,601,768,820,821,1024,1440,1920]:
        print(f'Publication checks: {width}px',flush=True)
        page.set_viewport_size({'width':width,'height':900})
        for lang in ['en','zh']:
            path='/zh/publications/' if lang=='zh' else '/publications/'
            for kind,base,total in [('real','http://127.0.0.1:4000',publication_count),('fixture',f'http://127.0.0.1:{server.server_port}',publication_count+1)]:
                page.goto(base+path,wait_until='networkidle')
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,lang,kind)
                assert page.locator('.publication-entry').count()==total
                if kind=='real':
                    assert page.locator('.publication-source').count()==publication_count
                    assert page.locator('.publication-kind').count()==0
                for record in page.locator('.publication-entry').all():
                    assert record.locator('.venue-year').text_content().strip()==record.evaluate('(el)=>el.closest(".publication-year").dataset.year')
                    rank=record.locator('.venue-rank')
                    if rank.count():
                        assert rank.text_content() in ['CCF-A','CCF-B','CCF-C']
                        assert rank.evaluate('(el)=>getComputedStyle(el).whiteSpace')=='nowrap'
                        line=record.locator('.venue-line').bounding_box()
                        assert rank.bounding_box()['y']>=line['y']+line['height']
                        assert rank.bounding_box()['height']<20

                sidebar=page.locator('.publication-sidebar');listing=page.locator('.publication-list')
                if width>820:
                    assert sidebar.bounding_box()['x']+sidebar.bounding_box()['width']<=listing.bounding_box()['x']
                    assert sidebar.evaluate('(el)=>getComputedStyle(el).position')=='sticky'
                else:
                    assert sidebar.bounding_box()['y']+sidebar.bounding_box()['height']<=listing.bounding_box()['y']+1
                for link in page.locator('.year-navigation a').all():assert link.bounding_box()['height']>=44
                marker=page.locator('.corresponding-author').first
                assert marker.text_content()=='✉️'
                assert marker.get_attribute('aria-label')==('通讯作者' if lang=='zh' else 'Corresponding author')
                assert '†' not in page.locator('.authors').all_text_contents()[0]
                assert page.locator('[data-publication="_publications/2025/FSE-L4.md"] .paper-topics li').count()==3
                if kind=='real' and width in [390,1440]:
                    page.screenshot(path=str(ROOT/f'.preview/publications-refined-{lang}-{width}.png'),full_page=False)
                page.locator('.year-navigation a[href="#year-2021"]').click()
                expect(page.locator('.year-navigation a[href="#year-2021"]')).to_have_attribute('aria-current','location')
                assert page.url.endswith('#year-2021')
                if width>820:assert 20<=sidebar.bounding_box()['y']<=30
                page.locator('#year-2023').evaluate('(el)=>el.scrollIntoView()')
                expect(page.locator('.year-navigation a[href="#year-2023"]')).to_have_attribute('aria-current','location')
                assert page.locator('.year-navigation [aria-current="location"]').count()==1
                rows.append({'width':width,'language':lang,'kind':kind})
    page.goto('http://127.0.0.1:4000/publications.html#year-2020',wait_until='networkidle')
    expect(page.locator('.year-navigation a[href="#year-2020"]')).to_have_attribute('aria-current','location')
    assert not errors,errors
    (ROOT/'.preview/publication-browser-checks.json').write_text(json.dumps({'passed':len(rows),'checks':rows,'scroll_navigation':'passed','legacy_deep_link':'passed','console_errors':errors},indent=2))
    print(f'PASS: {len(rows)} publication viewport/language/data combinations; sidebar, scroll highlight, anchors, topics, envelope markers, legacy deep link.')
    browser.close()
finally:server.shutdown()
