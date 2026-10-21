"""Explicitly approved historical queue and append-only digest merging.
No model calls, scheduling changes, or direct website writes live in this module.
"""
import json
import datetime as dt
from pathlib import Path
import yaml

QUEUE = '.preview/research-jobs/backfill-queue.json'

def load_queue(root):
    path = root / QUEUE
    if not path.exists(): return {'enabled': False, 'entries': []}
    data = json.loads(path.read_text())
    if data.get('version') != 1 or not isinstance(data.get('entries'), list):
        raise ValueError('Invalid approved backfill queue')
    bounds = data.get('range')
    if not isinstance(bounds, list) or len(bounds) != 2 or not all(isinstance(x, str) for x in bounds):
        raise ValueError('Backfill approval must have an explicit date range')
    if dt.date.fromisoformat(bounds[0]) > dt.date.fromisoformat(bounds[1]):
        raise ValueError('Invalid backfill approval range')
    return data

def select_approved(root, state, config, day, one_off=False):
    from research_daily import read_batch, safe_path, TERMINAL
    queue = load_queue(root)
    if queue.get('enabled') is not True: return None, []
    exemption = queue.get('one_off', {})
    if one_off and exemption.get('enabled') is not True: return None, []
    errors = []
    for entry in sorted(queue['entries'], key=lambda x: x['file']):
        if one_off and entry.get('sha256') not in exemption.get('input_sha256', []): continue
        if entry.get('mode') not in {'generate', 'append_digest'}: continue
        try:
            path = safe_path(root / '.incoming/research', entry['file'])
            if path.parent != root / '.incoming/research': raise ValueError('Backfill file must be directly in inbox')
            data, digest, raw = read_batch(path)
            if not queue['range'][0] <= data['date'] <= queue['range'][1]: raise ValueError('Batch falls outside the approved date range')
            if digest != entry['sha256']: raise ValueError('Approved input changed; review queue approval')
            if data['date'] > day: continue
            previous = state['inputs'].get(digest, {})
            if previous.get('status') in TERMINAL - {'deferred_history'}: continue
            if previous.get('attempts', 0) >= config['max_attempts_per_input']:
                errors.append({'file': path.name, 'error': 'Backfill attempt limit reached; manual review required'})
                continue
            for other in path.parent.glob(data['date'] + '*.yaml'):
                newer, _, _ = read_batch(other)
                if newer['revision'] > data['revision']: raise ValueError('Newer revision needs explicit backfill approval')
            return (data['date'], data['revision'], path, data, digest, raw), errors
        except Exception as error: errors.append({'file': entry.get('file'), 'error': str(error)})
    return None, errors

def merge_digest(root, data, input_hash, files, pairs):
    """Transform an isolated supplement into a guarded append to an approved old pair."""
    from research_daily import frontmatter, safe_path, sha, require, ReviewRequired, today
    queue = load_queue(root)
    entries = [e for e in queue['entries'] if e['sha256'] == input_hash and e.get('mode') == 'append_digest']
    if not entries: return files, pairs, {}
    plan = entries[0]; original_plan = plan.get('originals', {})
    generated = {lang: f'_digest/{lang}/daily-{data["date"]}.md' for lang in ['zh', 'en']}
    if not any(p in files for p in generated.values()): return files, pairs, {}
    require(all(p in files for p in generated.values()), 'Supplement must be bilingual')
    transformed = dict(files); replacements = {}; merged_ids = []
    for lang in ['zh', 'en']:
        old_spec = original_plan.get(lang, {})
        relative = old_spec.get('path', '')
        require(relative.startswith(f'_digest/{lang}/') and relative.endswith('.md'), 'Invalid approved original digest path')
        path = safe_path(root, relative)
        if not path.is_file() or sha(path.read_bytes()) != old_spec.get('sha256'):
            raise ReviewRequired(f'Original digest changed since approval: {relative}')
        old_meta, old_body = frontmatter(path)
        pieces = files[generated[lang]].decode('utf-8').split('---', 2)
        require(len(pieces) == 3, 'Invalid supplement front matter')
        new_meta = yaml.safe_load(pieces[1]); new_body = pieces[2]
        require(old_meta.get('daily_digest') is True and str(old_meta['date'])[:10] == data['date'], 'Original is not the expected daily digest')
        require(new_meta['permalink'] == old_meta['permalink'] and new_meta['lang'] == lang, 'Supplement route/language mismatch')
        old_ids, new_ids = old_meta.get('paper_ids', []), new_meta.get('paper_ids', [])
        require(new_ids and not set(old_ids) & set(new_ids), 'Supplement overlaps original paper anchors')
        meta = dict(old_meta)
        meta['paper_ids'] = old_ids + new_ids
        meta['daily_papers'] = old_meta['daily_papers'] + new_meta['daily_papers']
        meta['paper_count'] = len(meta['paper_ids'])
        meta['tags'] = list(dict.fromkeys(old_meta.get('tags', []) + new_meta.get('tags', [])))
        extra = f' 新增 {len(new_ids)} 篇补充阅读。' if lang == 'zh' else f' Includes {len(new_ids)} additional paper readings.'
        meta['summary'] = old_meta.get('summary', '') + extra
        meta.setdefault('backfill_additions', [])
        meta['backfill_additions'] = list(meta['backfill_additions']) + [{'input_sha256': input_hash, 'added_on': today(), 'paper_ids': new_ids}]
        if lang == 'zh':
            notice = f'*原有 {len(old_ids)} 篇解读完整保留；文末新增 {len(new_ids)} 篇补充阅读。目录涵盖两部分。*\n\n'
            heading = '\n\n## 补充阅读\n\n'
        else:
            notice = f'*The original {len(old_ids)} readings are retained in full. A supplement below adds {len(new_ids)} additional readings; the contents cover both parts.*\n\n'
            heading = '\n\n## Additional readings\n\n'
        # The original body is a byte-identical substring; no rewriting or deletion.
        body = notice + old_body + heading + new_body
        raw = ('---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + '---\n' + body).encode()
        require(old_body.encode() in raw, 'Original body preservation failed')
        del transformed[generated[lang]]
        transformed[relative] = raw
        replacements[relative] = old_spec['sha256']
        merged_ids.append(meta['paper_ids'])
    require(merged_ids[0] == merged_ids[1], 'Merged bilingual paper order mismatch')
    return transformed, pairs, replacements

def progress(root, state):
    queue = load_queue(root); rows = []
    for entry in queue['entries']:
        current = state['inputs'].get(entry['sha256'], {})
        status = current.get('status', 'pending')
        if entry.get('mode') == 'covered_existing': status = 'covered_existing'
        elif status == 'deferred_history': status = 'queued'
        rows.append({'file': entry['file'], 'mode': entry['mode'], 'status': status,
                     'job': current.get('job'), 'counts': entry.get('counts', {}), 'note': entry.get('note', '')})
    return {'range': queue.get('range'), 'rows': rows,
            'remaining_queue': sum(r['mode'] in {'generate', 'append_digest'} and r['status'] in {'queued','pending','failed','running'} for r in rows),
            'policy': ('User-approved October 3–15 one-off first, excluded from daily run quota; attempt/time limits unchanged.'
                       if queue.get('one_off', {}).get('enabled') else
                       'New daily input first; shared daily run/attempt/time limits; no extra timer.')}


def write_progress(root, state):
    from research_daily import atomic_json
    report = progress(root, state)
    folder = root / '.preview/research-jobs'
    atomic_json(folder / 'backfill-progress.json', report)
    labels = {'queued': '待补写', 'pending': '待补写', 'running': '处理中', 'completed': '本批已完成',
              'completed_with_deferred': '已收录可核验内容；有延期条目', 'needs_review': '待核验／人工审阅',
              'covered_existing': '已有双语稿覆盖', 'failed': '失败，等待有限重试'}
    lines = ['# 10 月 1—18 日补更进度', '',
             report['policy'] + ' 待办不等于已完成，延期不等于已发布。', '',
             '| 日期 | 论文 / 技术 / 社交 | 当前状态 |', '| --- | --- | --- |']
    for row in report['rows']:
        counts = row['counts']; status = labels.get(row['status'], row['status'])
        if row['mode'] == 'append_digest' and row['status'] in {'queued', 'pending'}: status = '待追加合并，保留原稿'
        lines.append('| ' + row['file'].removesuffix('.yaml') + ' | ' + ' / '.join(str(counts.get(k, 0)) for k in ['paper', 'tech', 'social']) + ' | ' + status + ' |')
    lines += ['', f'仍待生成／合并的批次：{report["remaining_queue"]}。', '',
              '10/17、10/18 的二手周报与社交线索另有延期说明；不会为了补齐日期生成空论文集或伪造原创报告。', '',
              '详细输入哈希、原稿保护与模式见 backfill-queue.json；各批具体来源去向见对应任务 report.json。']
    (folder / 'backfill-progress.md').write_text('\n'.join(lines) + '\n')
    return report
