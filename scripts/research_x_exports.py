"""Freeze only X exports associated with the selected daily input. No network calls."""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def freeze_exports(root, work, data):
    from research_daily import safe_path, source_key, sha, require, atomic_json
    destination = work / 'sources/x_exports'
    destination.mkdir(parents=True)
    manifest = {'date': data['date'], 'status': 'missing', 'posts': [], 'warnings': []}

    def key(url):
        u = urlsplit(source_key(url))
        host = 'x.com' if u.hostname in {'x.com', 'www.x.com', 'twitter.com', 'www.twitter.com'} else u.netloc
        if host == 'x.com':
            status = re.fullmatch(r'/[^/]+/status/(\d+)', u.path)
            if status: return 'https://x.com/i/status/' + status[1]
            if re.fullmatch(r'/i/article/\d+', u.path): return 'https://x.com' + u.path
        return urlunsplit((u.scheme, host, u.path, u.query, ''))

    try:
        base = safe_path(root, '.incoming/research/x_exports')
        candidates = []
        for p in base.glob(data['date'] + '*.json'):
            match = re.fullmatch(re.escape(data['date']) + r'(?:\.r(\d{3,}))?\.json', p.name)
            if match: candidates.append((int(match[1] or 1), p.name))
        if not candidates:
            atomic_json(destination / 'manifest.json', manifest)
            return manifest
        _, name = max(candidates)
        path = safe_path(base, name)
        require(path.stat().st_size <= 8 * 1024 * 1024, 'X export exceeds 8 MiB')
        raw = path.read_bytes(); export = json.loads(raw)
        require(export.get('date') == data['date'], 'X export date mismatch')
        require(export.get('timezone') == 'Asia/Shanghai', 'X export timezone mismatch')
        require(isinstance(export.get('posts'), list) and len(export['posts']) <= 500, 'Invalid X export posts')
        manifest.update(status='available', file=name, sha256=sha(raw))
        selection = {}
        for item in data['items']:
            for url in [item['url'], *item.get('related_urls', [])]:
                selection.setdefault(key(url), set()).add(item['id'])
        seen = set()
        for post in export['posts']:
            require(isinstance(post, dict), 'Invalid X post record')
            ident = post.get('id'); require(isinstance(ident, str) and re.fullmatch(r'\d+', ident), 'Invalid X post ID')
            require(ident not in seen, 'Duplicate X post ID'); seen.add(ident)
            u = urlsplit(key(post['url']))
            require(u.hostname == 'x.com' and re.fullmatch(r'/[^/]+/status/' + ident, u.path), 'X post URL/ID mismatch')
        for post in export['posts']:
            ident = post['id']
            try:
                urls = [post['url']]
                if post.get('primary_source'): urls.append(post['primary_source'])
                urls.extend(x['url'] for x in post.get('linked_urls', []) if isinstance(x, dict) and x.get('url'))
                matched = sorted(set().union(*(selection.get(key(url), set()) for url in urls)))
                if not matched: continue
                require(isinstance(post.get('text'), str) and post['text'].strip(), 'X post has no text')
                local = destination / ident; local.mkdir()
                frozen = dict(post); attachments = []; warnings = []
                requested = [('article_file', post['article_file'])] if post.get('article_file') else []
                require(isinstance(post.get('media_files', []), list), 'media_files must be a list')
                requested += [('media', rel) for rel in post.get('media_files', [])]
                require(len(requested) <= 12, 'Too many X attachments')
                for index, (kind, rel) in enumerate(requested):
                    try:
                        attachment = safe_path(base, rel)
                        extensions = {'.txt', '.md', '.html', '.json'} if kind == 'article_file' else {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
                        require(attachment.suffix.lower() in extensions, 'Unsupported X attachment type')
                        require(attachment.stat().st_size <= (8 if kind == 'article_file' else 25) * 1024 * 1024, 'X attachment too large')
                        content = attachment.read_bytes(); target = local / (f'{index:02d}-' + attachment.name)
                        target.write_bytes(content)
                        attachments.append({'kind': kind, 'local_file': str(target.relative_to(work)), 'sha256': sha(content)})
                    except Exception as error: warnings.append(f'{kind}: {error}')
                frozen['source_ids'] = matched; frozen['frozen_attachments'] = attachments
                frozen['attachment_warnings'] = warnings
                record = local / 'post.json'; atomic_json(record, frozen)
                entry = {'post_id': ident, 'source_ids': matched, 'url': post['url'], 'local_file': str(record.relative_to(work)), 'sha256': sha(record.read_bytes()), 'attachments': attachments}
                manifest['posts'].append(entry)
                manifest['warnings'].extend(f'{ident}: {w}' for w in warnings)
            except Exception as error: manifest['warnings'].append(f'{ident}: {error}')
        manifest['status'] = 'matched' if manifest['posts'] else 'no_matching_posts'
    except Exception as error:
        manifest['status'] = 'unavailable'; manifest['warnings'].append(str(error))
    atomic_json(destination / 'manifest.json', manifest)
    return manifest
