"""Exercise the bilingual research diagram on the running preview."""
import argparse
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(ROOT / '.preview/browsers')
parser = argparse.ArgumentParser()
parser.add_argument('--base', default='http://127.0.0.1:4001')
args = parser.parse_args()
out = ROOT / '.preview/research-diagram'
out.mkdir(parents=True, exist_ok=True)
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=p.chromium.executable_path, args=['--no-sandbox'])
    for lang, route in [('en', '/'), ('zh', '/zh/')]:
        for width in [320, 390, 600, 768, 1024, 1440]:
            context = browser.new_context(viewport={'width': width, 'height': 1000}, has_touch=width < 601)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            assert page.goto(args.base + route, wait_until='networkidle').status == 200
            diagram = page.locator('[data-research-diagram]')
            diagram.scroll_into_view_if_needed()
            page.wait_for_timeout(1400)
            assert diagram.locator('button').count() == 3
            assert diagram.locator('.rd-topics strong').all_text_contents() == [
                'AIOps & LLM4Ops', '系统优化' if lang == 'zh' else 'Systems Optimization', 'Ops4LLM', 'AgentOps']
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            assert diagram.locator('button').evaluate_all('(nodes) => nodes.every(n => n.scrollWidth <= n.clientWidth + 1 && n.clientHeight >= 44)')
            assert diagram.locator('button').evaluate_all('(nodes) => nodes.every(n => parseFloat(getComputedStyle(n).paddingLeft) >= 20 && getComputedStyle(n).borderTopWidth === "1px")')
            for direction in ['cloud', 'ai', 'chaos']:
                node = diagram.locator('[data-direction=' + direction + ']')
                if width < 601:
                    node.tap()
                else:
                    node.click()
                assert node.get_attribute('aria-pressed') == 'true'
                assert diagram.locator('[aria-pressed=true]').count() == 1
                assert diagram.locator('[data-research-caption]').inner_text() == node.get_attribute('data-caption')
            if width in [390, 1440]:
                diagram.screenshot(path=str(out / f'{lang}-{width}.png'))
            # Escape clears the selection, Enter toggles, Tab reaches the next node.
            cloud = diagram.locator('[data-direction=cloud]')
            cloud.focus()
            page.keyboard.press('Escape')
            assert diagram.locator('[aria-pressed=true]').count() == 0
            page.keyboard.press('Enter')
            assert cloud.get_attribute('aria-pressed') == 'true'
            page.keyboard.press('Enter')
            assert cloud.get_attribute('aria-pressed') == 'false'
            page.keyboard.press('Tab')
            assert page.locator(':focus').get_attribute('data-direction') == 'ai'
            if width == 1440:
                cloud.hover()
                assert diagram.get_attribute('data-preview') == 'cloud'
                assert diagram.locator('[data-research-caption]').inner_text() == cloud.get_attribute('data-caption')
                page.mouse.move(0, 0)
                assert diagram.get_attribute('data-preview') is None
            assert not errors, errors
            results.append({'lang': lang, 'width': width, 'interactions_and_layout': 'passed'})
            context.close()
        for mode in ['no-js', 'reduced-motion']:
            context = browser.new_context(viewport={'width': 390, 'height': 1000}, java_script_enabled=mode != 'no-js', reduced_motion='reduce')
            page = context.new_page()
            page.goto(args.base + route, wait_until='networkidle')
            diagram = page.locator('[data-research-diagram]')
            diagram.scroll_into_view_if_needed()
            assert diagram.locator('.rd-method-note').is_visible()
            assert diagram.locator('.rd-topics strong').count() == 4
            assert diagram.locator('.rd-node').evaluate_all('(nodes) => nodes.every(n => getComputedStyle(n).opacity === "1" && getComputedStyle(n).animationName === "none")')
            if mode == 'no-js':
                assert diagram.locator('button:disabled').count() == 3
                assert not diagram.locator('.rd-hint').is_visible()
            else:
                diagram.locator('[data-direction=chaos]').click()
                assert diagram.locator('[aria-pressed=true]').count() == 1
            results.append({'lang': lang, 'mode': mode, 'passed': True})
            context.close()
    browser.close()
(out / 'checks.json').write_text(json.dumps(results, indent=2))
print(f'PASS: {len(results)} bilingual responsive, interaction and accessibility checks')
