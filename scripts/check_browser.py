#!/usr/bin/env python3
"""Actual Chromium checks against local servers for real and isolated fixture output."""
import functools,json,threading,os
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(Path(__file__).resolve().parents[1]/'.preview/browsers'))
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.preview';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def serve(path):
    server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(path)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    return server,f'http://127.0.0.1:{server.server_port}'

results=[];errors=[];fonts=[]
real,base=serve(OUT/'current');fixture,fb=serve(OUT/'fixture-site')
try:
 with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=p.chromium.executable_path,args=['--no-sandbox'])
    context=browser.new_context()
    page=context.new_page()
    page.on('pageerror',lambda err: errors.append(str(err)))
    page.on('response',lambda response: errors.append(f'{response.status} {response.url}') if response.status>=400 and '127.0.0.1' in response.url else None)
    widths=[320,390,600,601,768,820,821,1024,1440,1920]
    routes=['/','/zh/','/publications/','/zh/publications/','/digest/','/zh/digest/','/kitchen/','/zh/kitchen/']
    for width in widths:
        print(f'Checking width {width}px',flush=True)
        page.set_viewport_size({'width':width,'height':1000})
        for route in routes:
            page.goto(base+route,wait_until='networkidle')
            overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth')
            assert not overflow,f'Horizontal overflow: {width} {route}'
            assert page.locator('h1').is_visible(),f'h1 {route}'
            assert page.locator('.language-switch').is_visible(),f'language {route}'
            broken=page.locator('img').evaluate_all('(images)=>images.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)')
            assert not broken,(route,broken)
            if route in ['/','/zh/']:
                for selector in ['.portrait','.biography-copy','.profile-affiliation','.education-entry','.awards-list','a[href^="mailto:"]']:
                    assert page.locator(selector).first.is_visible(),(width,route,selector)
                if width<=600:
                    assert page.locator('.identity-intro').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ").length')==1
                    assert page.locator('.navigation').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ").length')==2
            if width<=820:
                for item in page.locator('.navigation a,.language-switch a,.socials a,.publication-links a').all():
                    assert item.bounding_box()['height']>=43.5,(width,route,'touch height')
            if width in [390,1440] and route in ['/','/zh/','/publications/','/zh/digest/','/zh/kitchen/']:
                page.screenshot(path=str(OUT/f'{width}-{route.strip("/").replace("/","-") or "home"}.png'),full_page=True)
            results.append({'width':width,'route':route,'source':'real'})
        for route in ['/digest/zh/2026-10-10-paired/','/digest/en/2026-10-10-paired/','/kitchen/zh/2026-10-10-paired/','/kitchen/en/2026-10-10-paired/','/zh/digest/','/digest/','/zh/kitchen/','/kitchen/','/publications/','/zh/publications/']:
            page.goto(fb+route,wait_until='networkidle')
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),f'Fixture overflow {width} {route}'
            for img in page.locator('img').all():
                img.scroll_into_view_if_needed()
                img.evaluate('(img)=>img.decode()')
            page.evaluate('window.scrollTo(0,0)')
            assert not page.locator('img').evaluate_all('(images)=>images.some(i=>!i.complete||!i.naturalWidth)'),f'Fixture image {route}'
            if width in [390,1440] and route in ['/digest/zh/2026-10-10-paired/','/zh/kitchen/']:
                page.screenshot(path=str(OUT/f'fixture-{width}-{route.strip("/").replace("/","-")}.png'),full_page=True)
            results.append({'width':width,'route':route,'source':'fixture'})
    page.goto(base+'/zh/')
    page.locator('.language-switch a[lang="en"]').click()
    assert page.url==base+'/' and page.locator('html').get_attribute('lang')=='en'
    page.get_by_role('link',name='Publications',exact=True).click()
    assert page.url==base+'/publications/'
    page.locator('.language-switch a[lang="zh"]').click()
    assert page.url==base+'/zh/publications/'
    for col in ['digest','kitchen']:
        page.goto(fb+f'/{col}/zh/2026-10-10-paired/')
        page.locator('.language-switch a[lang="en"]').click()
        assert page.url==fb+f'/{col}/en/2026-10-10-paired/'
        for name in ['only','unpublished-translation']:
            page.goto(fb+f'/{col}/zh/2026-10-10-{name}/')
            page.locator('.language-switch a[lang="en"]').click()
            assert page.url==fb+f'/{col}/?translation=missing'
            assert page.locator('[data-translation-notice]').is_visible()
            assert 'not yet available in English' in page.locator('[data-translation-notice]').text_content()
    page.goto(base+'/')
    page.keyboard.press('Tab')
    assert page.locator('.skip-link').evaluate('(el)=>el===document.activeElement')
    page.keyboard.press('Enter')
    assert page.url.endswith('#main')
    for lang,route,family in [('en','/','Manrope'),('zh','/zh/','Noto Serif SC')]:
        page.goto(base+route,wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        sample='余广坝' if lang=='zh' else 'Guangba Yu'
        loaded=page.evaluate('([family,sample])=>document.fonts.check(`600 40px "${family}"`, sample)',[family,sample])
        assert loaded, f'Heading font not loaded: {family}'
        fonts.append({'language':lang,'font':family,'loaded':loaded})
    assert not errors,errors
    (OUT/'browser-checks.json').write_text(json.dumps({'viewports_passed':len(results),'routes':results,'interaction_checks':'passed','console_errors':errors,'fonts':fonts},ensure_ascii=False,indent=2))
    browser.close()
    print(f'PASS: {len(results)} actual-browser viewport/page checks, navigation, paired/missing translations, images, touch targets, keyboard, no JS errors. Fonts: {fonts}')
finally:
 real.shutdown();fixture.shutdown()
