#!/usr/bin/env python3
"""Scheduled inbox consumer. Generates in isolation; only adds verified paired content.
An explicitly enabled publisher commits only verified daily output. No source-vault writes.
"""
import argparse, collections, contextlib, datetime as dt, fcntl, functools
import hashlib, json, os, re, shutil, signal, subprocess, sys, threading, time, uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, unquote
from zoneinfo import ZoneInfo
import yaml
from bs4 import BeautifulSoup
from build_site import build
from obsidian_sync import snapshot
from obsidian.transaction import locked, fingerprint, activate, atomic_json

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo('Asia/Shanghai')
TERMINAL = {'completed', 'completed_with_deferred', 'needs_review', 'already_covered', 'deferred_history'}

class IntakeError(ValueError): pass
class ReviewRequired(IntakeError): pass
class UniqueLoader(yaml.SafeLoader): pass

def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result: raise IntakeError(f'Duplicate YAML field: {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)

def sha(raw): return hashlib.sha256(raw).hexdigest()
def now(): return dt.datetime.now(TZ).isoformat()
def today(): return dt.datetime.now(TZ).date().isoformat()
def require(ok, message):
    if not ok: raise IntakeError(message)

def source_key(url):
    u = urlsplit(url)
    require(u.scheme == 'https' and u.hostname and not u.username and not u.password and not any(c.isspace() for c in url), 'Expected an HTTPS source URL without credentials')
    host = u.hostname.lower()
    # Verified publisher aliases; compare identities without rewriting source URLs.
    if host == 'blog.vllm.ai' and u.path.startswith('/blog/'): host = 'vllm.ai'
    if host == 'techstrong.tv' and u.path.startswith('/videos/'): host = 'www.techstrong.tv'
    if host in {'arxiv.org', 'www.arxiv.org'}:
        match = re.fullmatch(r'/(?:abs|pdf|html)/(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?/?', u.path)
        if match: return 'arxiv:' + match[1]
    return urlunsplit(('https', host, u.path.rstrip('/'), u.query, ''))

def read_batch(path):
    require(not path.is_symlink(), 'Input cannot be a symlink')
    raw = path.read_bytes()
    require(len(raw) <= 1024 * 1024, 'Input exceeds 1 MiB')
    data = yaml.load(raw.decode('utf-8'), Loader=UniqueLoader)
    require(isinstance(data, dict), 'Batch must be a mapping')
    require('_intake_corrections' not in data, 'Reserved intake metadata field')
    require(type(data.get('schema_version')) is int and data['schema_version'] == 1, 'schema_version must be integer 1')
    date = data.get('date')
    require(isinstance(date, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', date), 'date must be a YYYY-MM-DD string')
    dt.date.fromisoformat(date)
    require(data.get('timezone') == 'Asia/Shanghai', 'timezone must be Asia/Shanghai')
    revision = data.get('revision')
    require(type(revision) is int and revision >= 1, 'revision must be a positive integer')
    expected = date + ('' if revision == 1 else f'.r{revision:03d}') + '.yaml'
    require(path.name == expected, 'Filename/date/revision mismatch')
    require(data.get('status') == 'ready', 'Batch is not ready')
    require(isinstance(data.get('items'), list), 'items must be a list')
    ids, urls, corrections = set(), set(), []
    for position, item in enumerate(data['items']):
        require(isinstance(item, dict), 'Item must be a mapping')
        ident = item.get('id')
        # IDs are internal labels, not URLs or author names. Preserve the raw file
        # and its hash; only repair unambiguous ASCII case/outer whitespace here.
        if isinstance(ident, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*', ident.strip()):
            normalized = ident.strip().lower()
            if normalized != ident:
                corrections.append({'item': position, 'field': 'id', 'before': ident, 'after': normalized,
                                    'reason': 'ASCII lowercase and surrounding whitespace'})
                item['id'] = ident = normalized
        require(isinstance(ident, str) and re.fullmatch(r'[a-z0-9][a-z0-9.-]*', ident) and '..' not in ident, 'Invalid item id')
        require(ident not in ids, 'Duplicate item id'); ids.add(ident)
        require(item.get('type') in {'paper', 'tech', 'social'}, 'Invalid item type')
        require(isinstance(item.get('title'), str) and item['title'].strip(), 'Missing title')
        require(isinstance(item.get('url'), str), 'Missing URL')
        key = source_key(item['url'])
        require(key not in urls, 'Duplicate source within batch'); urls.add(key)
        if item['type'] == 'paper' and key.startswith('arxiv:'):
            require(ident == 'arxiv-' + key[6:], 'arXiv id and URL disagree')
        require(item.get('priority', 'normal') in {'normal', 'high'}, 'Invalid priority')
        if 'published_at' in item:
            value = item['published_at']; require(isinstance(value, str), 'published_at must be string')
            if len(value) == 10: dt.date.fromisoformat(value)
            else: require(dt.datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo is not None, 'Timestamp needs timezone')
        related = item.get('related_urls', [])
        require(isinstance(related, list), 'related_urls must be list')
        for url in related: source_key(url)
    if corrections: data['_intake_corrections'] = corrections
    return data, sha(raw), raw

def safe_path(base, relative):
    require(isinstance(relative, str) and relative and not relative.startswith('/'), 'Expected relative path')
    parts = Path(relative).parts
    require('..' not in parts and '.' not in parts and '\\' not in relative, 'Unsafe relative path')
    path = base / relative
    current = base
    require(not base.is_symlink(), 'Symlink root forbidden')
    for part in parts:
        current = current / part
        require(not current.is_symlink(), f'Symlink forbidden: {relative}')
    require(path.resolve().is_relative_to(base.resolve()), 'Path escapes job root')
    return path

def frontmatter(path):
    pieces = re.split(r'^---\s*$', path.read_text(), maxsplit=2, flags=re.M)
    require(len(pieces) == 3 and not pieces[0].strip(), f'Missing front matter: {path.name}')
    data = yaml.load(pieces[1], Loader=UniqueLoader)
    require(isinstance(data, dict), 'Front matter must be mapping')
    return data, pieces[2]

def published_sources(root):
    keys = set()
    for collection in ['_digest', '_tech']:
        for path in (root / collection).rglob('*.md'):
            meta, _ = frontmatter(path)
            if meta.get('published') is not True: continue
            for url in re.findall(r'https://[^\s<>"\)]+', path.read_text()):
                try: keys.add(source_key(url))
                except ValueError: pass
    return keys

def stamp_note_activity(root, files, timestamp):
    """Record the server publication attempt, consistently across a bilingual batch."""
    require(dt.datetime.fromisoformat(timestamp).tzinfo is not None, 'Activity timestamp needs timezone')
    stamped = dict(files)
    for relative, raw in files.items():
        if not relative.startswith(('_digest/', '_tech/')) or not relative.endswith('.md'): continue
        pieces = re.split(r'^---\s*$', raw.decode(), maxsplit=2, flags=re.M)
        require(len(pieces) == 3, 'Missing front matter for activity timestamp')
        meta = yaml.load(pieces[1], Loader=UniqueLoader)
        target = safe_path(root, relative)
        if target.exists():
            previous, _ = frontmatter(target)
            if previous.get('published_at'): meta['published_at'] = previous['published_at']
            else: meta.pop('published_at', None)  # Unknown historic publication time stays unknown.
        else: meta['published_at'] = timestamp
        meta['updated_at'] = timestamp
        stamped[relative] = ('---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + '---' + pieces[2]).encode()
    return stamped

def select_batch(root, state, config, day):
    latest, errors, invalid_revisions = {}, [], {}
    for path in sorted((root / '.incoming/research').glob('*.yaml')):
        try:
            data, digest, raw = read_batch(path)
            if data['date'] < config['start_date'] or data['date'] > day: continue
            candidate = (data['date'], data['revision'], path, data, digest, raw)
            key = data['date']
            if key not in latest or data['revision'] > latest[key][1]: latest[key] = candidate
        except Exception as error:
            errors.append({'file': path.name, 'error': str(error)})
            match = re.fullmatch(r'(\d{4}-\d{2}-\d{2})(?:\.r(\d{3,}))?\.yaml', path.name)
            if match:
                invalid_revisions[match[1]] = max(invalid_revisions.get(match[1], 0), int(match[2] or 1))
    candidates = []
    for candidate in latest.values():
        # A broken newest upload must not silently publish an older revision.
        if invalid_revisions.get(candidate[0], 0) >= candidate[1]: continue
        previous = state['inputs'].get(candidate[4], {})
        if previous.get('status') in TERMINAL: continue
        if previous.get('attempts', 0) >= config['max_attempts_per_input']:
            errors.append({'file': candidate[2].name, 'error': 'Attempt limit reached; manual review required'})
            continue
        candidates.append(candidate)
    return (sorted(candidates, key=lambda c: (c[0] != day, c[0], c[1]))[0] if candidates else None), errors

def select_manual_batch(root, state, config, day, filename):
    path = safe_path(root / '.incoming/research', filename)
    require(path.parent == root / '.incoming/research', 'Manual batch must be a filename in the inbox')
    data, digest, raw = read_batch(path)
    require(data['date'] <= day, 'Cannot publish a future reading batch')
    for other in path.parent.glob(data['date'] + '*.yaml'):
        newer, _, _ = read_batch(other)
        require(newer['revision'] <= data['revision'], 'Use the newest revision of this batch')
    previous = state['inputs'].get(digest, {})
    require(previous.get('status') not in TERMINAL - {'deferred_history'}, 'This input was already processed; inspect its report before revising')
    require(previous.get('attempts', 0) < config['max_attempts_per_input'], 'Attempt limit reached; inspect the existing candidate')
    return (data['date'], data['revision'], path, data, digest, raw), []

@contextlib.contextmanager
def queue_lock(folder):
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'consumer.lock').open('a') as handle:
        try: fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise IntakeError('Another research consumer is running')
        yield

def initialize(root, config):
    folder = root / '.preview/research-jobs'
    with queue_lock(folder):
        state_path = folder / 'state.json'
        require(not state_path.exists(), 'State already initialized; refusing to replace it')
        inputs = {}
        for path in sorted((root / '.incoming/research').glob('*.yaml')):
            data, digest, _ = read_batch(path)
            if data['date'] < config['start_date']:
                inputs[digest] = {'file': path.name, 'date': data['date'], 'status': 'deferred_history', 'attempts': 0}
        atomic_json(state_path, {'version': 1, 'initialized_at': now(), 'inputs': inputs, 'daily_runs': {}})
        return {'status': 'initialized', 'historical_batches_deferred': len(inputs), 'start_date': config['start_date']}

def prepare_work(root, job, data):
    work = job / 'work'; work.mkdir()
    (work / 'output').mkdir(); (work / 'sources').mkdir(); (work / 'examples').mkdir()
    from research_x_exports import freeze_exports
    freeze_exports(root, work, data)
    atomic_json(work / 'input.json', {**data, 'x_exports_manifest': 'sources/x_exports/manifest.json'})
    shutil.copy2(root / 'docs/digest-drafts/EDITORIAL.md', work / 'editorial.md')
    shutil.copy2(root / '_data/note_tags.yml', work / 'tags.yml')
    for lang in ['zh', 'en']:
        for source, dest in [(f'_digest/{lang}/obsidian/daily-2026-10-01.md', f'digest-{lang}.md'), (f'_tech/{lang}/lmcache-kv-cache-intro.md', f'tech-{lang}.md')]:
            shutil.copy2(root / source, work / 'examples' / dest)
    return work

def invoke_worker(root, work, config, extra=''):
    prompt = (root / 'docs/research-inbox/DAILY_PROMPT.md').read_text() + '\n' + extra
    (work / 'task.md').write_text(prompt)
    cmd = [config['codex_bin'], '--no-daemon', '--search', '-a', 'never',
           'exec', '--sandbox', 'workspace-write', '-c', 'sandbox_workspace_write.network_access=true',
           '-c', 'sandbox_workspace_write.writable_roots=[]', '--skip-git-repo-check', '--ephemeral',
           '--color', 'never', '--json', '-C', str(work),
           '--output-schema', str(root / 'docs/research-inbox/result-schema.json'),
           '-o', str(work / 'result.json'), '-']
    with (work / 'task.md').open() as inp, (work / 'events.jsonl').open('w') as out, (work / 'stderr.log').open('w') as err:
        child = subprocess.Popen(cmd, stdin=inp, stdout=out, stderr=err, start_new_session=True)
        try: code = child.wait(timeout=config['max_run_seconds'])
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGTERM)
            try: child.wait(timeout=10)
            except subprocess.TimeoutExpired: os.killpg(child.pid, signal.SIGKILL); child.wait()
            raise IntakeError('Writing task exceeded its time budget; preview unchanged')
    require(code == 0, f'Codex exited {code}; see {work / "stderr.log"}')
    return json.loads((work / 'result.json').read_text())

def validate_outputs(root, work, data, result):
    from PIL import Image
    output = work / 'output'; allowed = {}; routes = []; covered = set(); pairs = []
    items = {item['id']: item for item in data['items']}
    known_tags = {x['id'] for x in yaml.safe_load((root / '_data/note_tags.yml').read_text())}
    require(isinstance(result, dict), 'Result must be object')
    for name in ['articles', 'deferred', 'evidence', 'images']: require(isinstance(result.get(name), list), f'Missing result {name}')
    evidence_ids = set()
    for ev in result['evidence']:
        require(ev['source_id'] in items and ev.get('review_notes', '').strip(), 'Evidence must identify an input and review notes')
        source_key(ev['url']); require(ev['local_file'].startswith('sources/'), 'Evidence must be saved in sources/')
        path = safe_path(work, ev['local_file'])
        require(path.is_file() and path.stat().st_size > 0 and sha(path.read_bytes()) == ev['sha256'], 'Evidence missing or hash mismatch')
        evidence_ids.add(ev['source_id'])
    paper_articles = 0
    for article in result['articles']:
        kind = article['kind']; require(kind in {'paper', 'tech'}, 'Invalid article kind')
        ids = article['source_ids']; require(ids and len(ids) == len(set(ids)), 'Article source IDs missing or duplicated')
        require(set(ids) <= set(items) and not (set(ids) & covered), 'Unknown or multiply published input')
        require(set(ids) <= evidence_ids, 'Included sources lack frozen evidence')
        if kind == 'tech': require(len(ids) == 1 and items[ids[0]]['type'] in {'tech', 'social'}, 'Tech article must match one technical or reviewed social input')
        else:
            paper_articles += 1
            require(any(items[i]['type'] == 'paper' for i in ids) and all(items[i]['type'] in {'paper', 'social'} for i in ids), 'Digest needs papers and optional verified social items')
        covered.update(ids); metas = []
        for lang in ['zh', 'en']:
            relative = article[lang + '_path']
            if kind == 'paper': require(relative == f'_digest/{lang}/daily-{data["date"]}.md', 'Unexpected digest path')
            else: require(re.fullmatch(rf'_tech/{lang}/[a-z0-9][a-z0-9.-]*\.md', relative), 'Unexpected tech path')
            require('..' not in relative and relative not in allowed, 'Duplicate or unsafe output')
            path = safe_path(output, relative); meta, body = frontmatter(path)
            require(meta.get('lang') == lang and meta.get('published') is True and meta.get('layout') == 'article', 'Invalid language/published/layout')
            require(meta.get('source_type') == kind and meta.get('maintenance') == 'daily-research', 'Invalid ownership or type')
            require(isinstance(meta.get('id'), str) and re.fullmatch(r'[a-z0-9][a-z0-9.-]*', meta['id']) and '..' not in meta['id'], 'Invalid article ID')
            require(isinstance(meta.get('date'), str), 'Article date must be string'); dt.date.fromisoformat(meta['date'])
            require(isinstance(meta.get('tags'), list) and set(meta['tags']) <= known_tags, 'Unknown topic')
            require(isinstance(meta.get('summary'), str) and meta['summary'].strip(), 'Missing summary')
            date = dt.date.fromisoformat(meta['date']); prefix = f'{date.year}年{date.month}月{date.day}日｜' if lang == 'zh' else meta['date'] + ' | '
            require(isinstance(meta.get('title'), str) and meta['title'].startswith(prefix), 'Date-led title required')
            require(len(body.strip()) >= 400, 'Article body is incomplete')
            require(not re.search(r'<\s*(script|iframe|object|embed)\b|\bon\w+\s*=|javascript:', body, re.I), 'Executable markup is not content')
            require('{{' not in body and '{%' not in body and '![[' not in body, 'Unprocessed template syntax')
            expected = f'/digest/{lang}/daily/{data["date"]}/' if kind == 'paper' else f'/tech/{lang}/{meta["id"]}/'
            require(meta.get('permalink') == expected, 'Invalid permalink'); routes.append(expected)
            if kind == 'paper':
                require(meta['date'] == data['date'] and meta.get('daily_digest') is True, 'Digest date/type mismatch')
                paper_ids = meta.get('paper_ids', [])
                require(len(paper_ids) == len(set(paper_ids)) == meta.get('paper_count') == len([i for i in ids if items[i]['type'] == 'paper']), 'Digest paper count mismatch')
                require([x['id'] for x in meta.get('daily_papers', [])] == paper_ids, 'Digest TOC mismatch')
                for ident in paper_ids: require(f'id="paper-{ident}"' in body, 'Missing digest section anchor')
            else:
                require(meta.get('long_read') is True, 'Tech must use long reader'); source_key(meta['source_url'])
                if items[ids[0]]['type'] == 'social':
                    require(meta.get('source_format') == 'x-article', 'Social promotion requires a full X article')
            metas.append(meta); allowed[relative] = path.read_bytes()
        require(metas[0]['id'] == metas[1]['id'] and metas[0]['date'] == metas[1]['date'] and metas[0]['tags'] == metas[1]['tags'], 'Translation metadata mismatch')
        require(article['zh_path'].replace('/zh/', '/en/') == article['en_path'], 'Translation file pair mismatch')
        if kind == 'paper': require(metas[0]['paper_ids'] == metas[1]['paper_ids'], 'Translation paper order mismatch')
        pairs.append((routes[-2], routes[-1]))
    require(paper_articles <= 1, 'At most one digest per batch')
    for entry in result['deferred']:
        require(entry['id'] in items and entry['id'] not in covered and entry.get('reason', '').strip(), 'Invalid or duplicate deferral')
        covered.add(entry['id'])
    require(covered == set(items), 'Every input needs an explicit disposition')
    for img in result['images']:
        rel = img['path']
        require(re.fullmatch(r'assets/images/(digest/\d{4}-\d{2}-\d{2}|tech/[a-z0-9][a-z0-9.-]*)/[a-zA-Z0-9_.-]+\.(png|jpg|jpeg|webp|gif)', rel), 'Invalid image path')
        require(img['source_id'] in evidence_ids and img.get('review_notes', '').strip(), 'Image lacks source review')
        source_key(img['source_url']); path = safe_path(output, rel)
        require(path.stat().st_size < 25 * 1024 * 1024, 'Image too large')
        with Image.open(path) as image: image.verify()
        require(rel not in allowed, 'Duplicate image'); allowed[rel] = path.read_bytes()
    # Reject unmanifested output and enforce local image provenance.
    for p in output.rglob('*'):
        require(not p.is_symlink(), 'Output contains symlink')
        if p.is_file(): require(str(p.relative_to(output)) in allowed, 'Output contains unmanifested file')
    for rel, raw in allowed.items():
        if not rel.endswith('.md'): continue
        text = raw.decode()
        image_paths = re.findall(r'<img\b[^>]*\bsrc=["\']([^"\']+)', text, re.I) + re.findall(r'!\[[^\]]*\]\(([^\s)]+)', text)
        for src in image_paths: require(src.startswith('/assets/images/') and src[1:] in allowed, 'Images must have local reviewed provenance')
    require(len(routes) == len(set(routes)), 'Duplicate routes')
    return allowed, pairs

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass

def check_rendered(root, site, pairs):
    from playwright.sync_api import sync_playwright
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(root / '.preview/browsers')
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    errors, count = [], 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=p.chromium.executable_path, args=['--no-sandbox'])
            page = browser.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
            for width in [390, 1440]:
                page.set_viewport_size({'width': width, 'height': 950})
                for pair in pairs:
                    for lang, route, other in [('zh', pair[0], pair[1]), ('en', pair[1], pair[0])]:
                        response = page.goto(f'http://127.0.0.1:{server.server_port}' + route, wait_until='networkidle')
                        require(response.status == 200, 'New route not served')
                        require(page.locator('html').get_attribute('lang') == lang, 'Rendered language mismatch')
                        require(page.locator('[data-pagefind-body]').count() == 1, 'Published page missing search body')
                        require(not page.evaluate('document.documentElement.scrollWidth>innerWidth'), 'Responsive overflow')
                        opposite = 'en' if lang == 'zh' else 'zh'
                        require(page.locator(f'.language-switch a[lang={opposite}]').get_attribute('href') == other, 'Wrong translation link')
                        page.locator('.article-body img').evaluate_all("async es=>{for(const e of es)e.loading='eager';await Promise.all(es.map(e=>e.decode()))}")
                        if route.startswith('/tech/'):
                            require(page.locator('.tech-toc').count() == 1, 'Missing long-read contents')
                            if page.locator('.note-image-link').count():
                                page.locator('.note-image-link').first.click()
                                page.locator('.tech-image-dialog').wait_for(state='visible')
                                page.locator('.tech-image-toolbar button').first.click()
                                require(page.locator('.tech-image-dialog').get_attribute('data-zoomed') is not None, 'Image zoom failed')
                                page.keyboard.press('Escape')
                                page.locator('.tech-image-dialog').wait_for(state='hidden')
                        shots = site.parent / 'screenshots'; shots.mkdir(exist_ok=True)
                        page.locator('.article-header').evaluate("e=>e.scrollIntoView({behavior:'instant'})")
                        page.screenshot(path=str(shots / (route.strip('/').replace('/', '-') + f'-{width}.png')))
                        count += 1
            require(not errors, 'Browser JavaScript errors: ' + str(errors)); browser.close()
    finally: server.shutdown(); server.server_close()
    return {'pages_at_widths': count, 'console_errors': errors}

def build_candidate(root, job, files, pairs, replacements=None):
    replacements = replacements or {}
    for rel in files:
        target = safe_path(root, rel)
        if target.exists() and (rel not in replacements or sha(target.read_bytes()) != replacements[rel]):
            raise ReviewRequired(f'Existing file requires manual review: {rel}')
        if rel in replacements: require(target.is_file(), 'Approved replacement disappeared')
    existing_routes = set()
    for col in ['_digest', '_tech']:
        for path in (root / col).rglob('*.md'):
            meta, _ = frontmatter(path)
            if meta.get('permalink') and str(path.relative_to(root)) not in replacements: existing_routes.add(meta['permalink'])
    if set(x for pair in pairs for x in pair) & existing_routes: raise ReviewRequired('Existing route requires manual review')
    before = fingerprint(root); source = job / 'candidate-source'; snapshot(root, source)
    for rel, raw in files.items():
        target = safe_path(source, rel); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    site = job / 'candidate-site'; result = build(source, site)
    for forbidden in ['.incoming', '.preview', 'docs', 'scripts']: require(not (site / forbidden).exists(), 'Private files leaked')
    for pair in pairs:
        for route in pair:
            path = site / route.strip('/') / 'index.html'; doc = BeautifulSoup(path.read_text(), 'html.parser')
            require(not doc.select('.katex-error,script[type^="math/tex"]'), 'Formula rendering failed')
            for tag in doc.select('.article-body [href],.article-body [src]'):
                url = urlsplit(tag.get('href', tag.get('src', '')))
                if url.scheme or url.netloc: continue
                dest = site / unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent / unquote(url.path)
                if not url.path: dest = path
                if dest.is_dir(): dest = dest / 'index.html'
                require(dest.exists(), f'Broken local resource: {url.path}')
                if url.fragment and dest.suffix == '.html': require(BeautifulSoup(dest.read_text(), 'html.parser').find(id=unquote(url.fragment)), 'Broken anchor')
    report = check_rendered(root, site, pairs)
    require(fingerprint(root) == before, 'Website changed during candidate build; preview retained')
    return site, before, {'build': result, 'browser': report}

def apply_candidate(root, site, files, before, report, replacements=None):
    replacements = replacements or {}
    backups = {}
    require(fingerprint(root) == before, 'Website changed before apply')
    for rel in files:
        path = safe_path(root, rel)
        if rel in replacements:
            require(path.is_file() and sha(path.read_bytes()) == replacements[rel], 'Approved original changed before merge')
            backups[rel] = path.read_bytes()
        else: require(not path.exists(), 'Existing file appeared before apply')
    # Keep the optional, explicitly marked Life design demo available on this preview.
    previous = root / '.preview/current/review/life-layout'
    if previous.is_dir() and not (site / 'review/life-layout').exists(): shutil.copytree(previous, site / 'review/life-layout')
    release = root / '.preview/releases' / ('research-' + dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
    release.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(site), release)
    written = []
    try:
        for rel, raw in files.items():
            target = safe_path(root, rel); target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name('.' + target.name + '.research-' + uuid.uuid4().hex)
            try:
                with temporary.open('xb') as handle:
                    handle.write(raw); handle.flush(); os.fsync(handle.fileno())
                if rel in replacements:
                    require(sha(target.read_bytes()) == replacements[rel], 'Original changed during merge')
                    os.replace(temporary, target)
                else:
                    os.link(temporary, target)  # Atomic creation; never replace an unapproved file.
                written.append(rel)
            finally:
                temporary.unlink(missing_ok=True)
        atomic_json(root / '.preview/release-meta' / (release.name + '.json'), report)
        activate(root, release)
    except Exception:
        for rel in written:
            target = root / rel
            if target.exists() and sha(target.read_bytes()) == sha(files[rel]):
                if rel in backups:
                    temporary = target.with_name('.' + target.name + '.restore-' + uuid.uuid4().hex)
                    temporary.write_bytes(backups[rel]); os.replace(temporary, target)
                else: target.unlink()
        raise
    return str(release)

def run(root, config, dry_run=False, batch=None, one_off=False):
    folder = root / '.preview/research-jobs'; state_path = folder / 'state.json'
    with queue_lock(folder):
        require(state_path.exists(), 'Initialize the historical baseline before enabling the consumer')
        state = json.loads(state_path.read_text()); day = today()
        from research_publish import retry_pending, publish
        publication_config = config.get('publication', {})
        publication_retries = [] if dry_run else retry_pending(root, publication_config)
        if publication_retries and publication_retries[-1]['status'] != 'published':
            report = {'status': 'publication_pending', 'applied': False, 'input_errors': [],
                      'publication_retries': publication_retries, 'finished_at': now()}
            atomic_json(folder / 'latest-run.json', report)
            return report
        from research_backfill import select_approved, merge_digest, write_progress
        require(not (batch and one_off), 'Choose --batch or --one-off, not both')
        origin = 'manual' if batch else 'daily'
        selected, errors = (None, []) if batch else select_approved(root, state, config, day, one_off=True)
        exempt = selected is not None
        if exempt: origin = 'one_off_backfill'
        elif not one_off:
            selected, daily_errors = select_manual_batch(root, state, config, day, batch) if batch else select_batch(root, state, config, day)
            errors.extend(daily_errors)
        if selected is None and not batch and not one_off:
            selected, backfill_errors = select_approved(root, state, config, day)
            errors.extend(backfill_errors)
            if selected is not None: origin = 'approved_backfill'
        report = {'started_at': now(), 'input_errors': errors, 'applied': False, 'manual_batch': batch, 'origin': origin, 'daily_quota_exempt': exempt}
        if publication_retries: report['publication_retries'] = publication_retries
        reviews = [{k: e[k] for k in ['file', 'date', 'review_reason', 'counts', 'limits', 'job'] if k in e}
                   for e in state['inputs'].values() if e.get('status') == 'needs_review']
        if reviews: report['pending_reviews'] = reviews
        if selected is None:
            report['status'] = 'input_errors' if errors else ('awaiting_review' if reviews else 'no_new_batch')
        else:
            _, _, path, data, digest, raw = selected
            report.update(input=path.name, input_sha256=digest, date=data['date'])
            if data.get('_intake_corrections'): report['intake_corrections'] = data['_intake_corrections']
            if dry_run: report['status'] = 'pending'; report['counts'] = dict(collections.Counter(i['type'] for i in data['items']))
            elif not exempt and state['daily_runs'].get(day, 0) >= config['max_model_runs_per_day']: report['status'] = 'daily_budget_reached'
            else:
                existing = published_sources(root)
                selected_items = [i for i in data['items'] if source_key(i['url']) not in existing]
                report['already_covered'] = [i['id'] for i in data['items'] if i not in selected_items]
                entry = state['inputs'].setdefault(digest, {'file': path.name, 'date': data['date'], 'attempts': 0})
                if data.get('_intake_corrections'): entry['intake_corrections'] = data['_intake_corrections']
                if not selected_items: report['status'] = entry['status'] = 'already_covered'
                elif any(collections.Counter(i['type'] for i in selected_items)[kind] > limit for kind, limit in config['max_items'].items()):
                    report['status'] = entry['status'] = 'needs_review'; report['reason'] = 'Batch exceeds configured item limits; no model call made'
                    report.update(counts=dict(collections.Counter(i['type'] for i in selected_items)), limits=config['max_items'])
                    entry.update(review_reason=report['reason'], counts=report['counts'], limits=dict(config['max_items']), reviewed_at=now())
                else:
                    job = folder / 'runs' / (dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + digest[:10] + '-' + uuid.uuid4().hex[:6]); job.mkdir(parents=True)
                    (job / path.name).write_bytes(raw); report['job'] = str(job.relative_to(root))
                    entry.update(status='running', attempts=entry['attempts'] + 1, job=report['job'])
                    ledger = state.setdefault('one_off_runs', {}) if exempt else state['daily_runs']
                    ledger[day] = ledger.get(day, 0) + 1
                    atomic_json(state_path, state)
                    try:
                        work = prepare_work(root, job, {**data, 'items': selected_items})
                        report['x_exports'] = json.loads((work / 'sources/x_exports/manifest.json').read_text())
                        result = invoke_worker(root, work, config)
                        for line in (work / 'events.jsonl').read_text().splitlines():
                            try:
                                event = json.loads(line)
                                if event.get('type') == 'turn.completed': report['model_usage'] = event.get('usage', {})
                            except json.JSONDecodeError: pass
                        files, pairs = validate_outputs(root, work, {**data, 'items': selected_items}, result)
                        files, pairs, replacements = merge_digest(root, {**data, 'items': selected_items}, digest, files, pairs)
                        files = stamp_note_activity(root, files, now())
                        report.update(summary=result['summary'], deferred=result['deferred'], appended_originals=list(replacements))
                        if not pairs: report['status'] = 'needs_review'
                        else:
                            with locked(root):
                                site, before, checks = build_candidate(root, job, files, pairs, replacements)
                                require(sha(path.read_bytes()) == digest, 'Input changed during processing')
                                report.update(checks=checks, files={rel: sha(raw) for rel, raw in files.items()})
                                report['release'] = apply_candidate(root, site, files, before, report, replacements)
                                report['applied'] = True
                            report['status'] = 'completed_with_deferred' if result['deferred'] else 'completed'
                    except ReviewRequired as error:
                        report.update(status='needs_review', error=str(error))
                    except Exception as error:
                        report.update(status='failed', error=str(error))
                    entry.update(status=report['status'], finished_at=now())
                    if report['status'] == 'needs_review':
                        entry['review_reason'] = report.get('error') or report.get('reason') or report.get('summary', 'No publishable output; inspect the task report')
                    atomic_json(job / 'report.json', report)
                    if publication_config.get('enabled') and origin == 'daily' and report.get('applied') and report['status'] in {'completed', 'completed_with_deferred'}:
                        report['publication'] = {'requested': True, 'status': 'pending'}
                        atomic_json(job / 'report.json', report)
                        report['publication'] = publish(root, job / 'report.json', publication_config)
                atomic_json(state_path, state)
        report['finished_at'] = now()
        if not dry_run:
            atomic_json(folder / 'latest-run.json', report)
            write_progress(root, state)
        return report

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['initialize', 'run', 'status']); parser.add_argument('--dry-run', action='store_true'); parser.add_argument('--batch', help='Explicit inbox filename for a requested historical backfill; scheduled runs never set this')
    parser.add_argument('--one-off', action='store_true', help='Only consume the hash-pinned, quota-exempt one-off queue')
    args = parser.parse_args(); config = json.loads((ROOT / 'docs/research-inbox/daily-config.json').read_text())
    if args.action == 'initialize': report = initialize(ROOT, config)
    elif args.action == 'status': report = json.loads((ROOT / '.preview/research-jobs/state.json').read_text())
    else: report = run(ROOT, config, args.dry_run, args.batch, args.one_off)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report.get('status') in {'failed', 'input_errors'} else 0
if __name__ == '__main__':
    try: sys.exit(main())
    except Exception as error: print(json.dumps({'status': 'failed', 'error': str(error)})); sys.exit(1)
