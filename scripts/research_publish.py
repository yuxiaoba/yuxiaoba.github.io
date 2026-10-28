"""Publish only a successful daily batch; never reset, stash, merge or force push."""
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

import yaml
from obsidian.transaction import atomic_json, locked


class PublicationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise PublicationError(message)


def git(root, *args, raw=False):
    result = subprocess.run(
        ['git', '-C', str(root), *args], capture_output=True, check=True, timeout=90,
        env={**os.environ, 'GIT_TERMINAL_PROMPT': '0',
             'GIT_SSH_COMMAND': 'ssh -o BatchMode=yes -o ConnectTimeout=20'})
    return result.stdout if raw else result.stdout.decode().strip()


def names(raw):
    return set(raw.decode().rstrip('\0').split('\0')) if raw else set()


def validate_batch(root, report):
    if report.get('origin') == 'approved_history':
        from research_history import require_approval
        require_approval(root, report.get('input'), report.get('input_sha256'))
    require(report.get('applied') is True and report.get('status') in
            {'completed', 'completed_with_deferred'}, 'Batch has not passed local validation')
    require(report.get('checks', {}).get('build') and report.get('checks', {}).get('browser'),
            'Missing build/browser evidence')
    files = report.get('files', {})
    require(bool(files), 'No verified files to publish')
    notes = set()
    for relative, digest in files.items():
        parts = Path(relative).parts
        require(not Path(relative).is_absolute() and '..' not in parts and '\\' not in relative,
                'Unsafe publication path')
        note = re.fullmatch(r'_(digest|tech)/(zh|en)/[a-z0-9./_-]+\.md', relative)
        image = re.fullmatch(r'assets/images/(digest|tech)/[a-zA-Z0-9./_-]+\.(png|jpe?g|webp|gif|svg)', relative)
        require(note or image, 'File outside daily content scope: ' + relative)
        current = root
        for part in parts:
            current = current / part
            require(not current.is_symlink(), 'Symlink in publication path')
        require(current.is_file() and hashlib.sha256(current.read_bytes()).hexdigest() == digest,
                'Verified file changed: ' + relative)
        if note:
            meta = yaml.safe_load(current.read_text().split('---', 2)[1])
            require(meta.get('published') is True, 'Draft in publication manifest')
            notes.add(relative)
    require(notes, 'No reading notes in manifest')
    for relative in notes:
        parts = relative.split('/'); parts[1] = 'en' if parts[1] == 'zh' else 'zh'
        require('/'.join(parts) in notes, 'Missing paired translation: ' + relative)
    return files


def verify_commit(root, commit, base, files):
    require(git(root, 'rev-list', '--parents', '-n', '1', commit).split() == [commit, base],
            'Publication commit must contain exactly one approved parent')
    changed = names(git(root, 'diff', '--name-only', '-z', base, commit, raw=True))
    require(changed == set(files), 'Commit contains missing or unrelated changes')
    for relative, digest in files.items():
        require(hashlib.sha256(git(root, 'show', commit + ':' + relative, raw=True)).hexdigest() == digest,
                'Commit differs from verified batch: ' + relative)


def deployment_status(config, commit, root=None):
    """A push is not proof of deployment. Reconcile on the next timer invocation."""
    try:
        req = urllib.request.Request(config['site_url'].rstrip('/') + '/build-info.json?release=' + commit,
                                     headers={'Cache-Control': 'no-cache', 'User-Agent': 'Homepage-daily-publisher'})
        with urllib.request.urlopen(req, timeout=15) as response:
            live = json.load(response).get('commit')
            if live == commit:
                return 'published', None
            if root and isinstance(live, str) and re.fullmatch(r'[0-9a-f]{40}', live):
                try:
                    git(root, 'merge-base', '--is-ancestor', commit, live)
                    return 'published', None  # A later approved release contains this batch.
                except subprocess.CalledProcessError:
                    pass
        # Public repository: no stored API token or extra credentials needed.
        url = 'https://api.github.com/repos/' + config['repository'] + '/actions/runs?head_sha=' + commit + '&per_page=20'
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Homepage-daily-publisher'}), timeout=15) as response:
            runs = json.load(response).get('workflow_runs', [])
        runs = [r for r in runs if r.get('path') == '.github/workflows/pages.yml' and
                r.get('head_branch') == config['production_branch'] and r.get('event') == 'push']
        if runs and runs[0].get('status') == 'completed' and runs[0].get('conclusion') != 'success':
            return 'deployment_failed', runs[0].get('html_url')
    except (OSError, ValueError, KeyError) as error:
        return 'awaiting_deployment', str(error)
    return 'awaiting_deployment', None


def publish(root, report_path, config):
    """Caller holds the research consumer lock; serialize index work with preview builds."""
    report = json.loads(report_path.read_text())
    publication = report.get('publication', {})
    if not config.get('enabled') or publication.get('requested') is not True:
        return {'status': 'disabled'}
    if publication.get('status') == 'published':
        return publication
    if publication.get('commit') and publication.get('pushed'):
        status, error = deployment_status(config, publication['commit'], root)
        if status == 'published':
            publication.update(status=status, error=None)
            atomic_json(report_path, report)
            return publication
    try:
        with locked(root):
            files = validate_batch(root, report)
            remote = config['remote']; branch = config['work_branch']; production = config['production_branch']
            require(git(root, 'remote', 'get-url', remote) == config['remote_url'], 'Unexpected Git remote')
            require(git(root, 'symbolic-ref', '--short', 'HEAD') == branch, 'Unexpected checkout branch')
            head = git(root, 'rev-parse', 'HEAD')
            pending = names(git(root, 'diff', '--name-only', '-z', 'HEAD', raw=True))
            pending |= names(git(root, 'ls-files', '--others', '--exclude-standard', '-z', raw=True))
            require(pending <= set(files), 'Unrelated local changes; leaving all user work untouched')
            git(root, 'fetch', remote, '+refs/heads/' + production + ':refs/remotes/' + remote + '/' + production,
                '+refs/heads/' + branch + ':refs/remotes/' + remote + '/' + branch)
            heads = [git(root, 'rev-parse', 'refs/remotes/' + remote + '/' + b) for b in [production, branch]]
            base = publication.get('base')
            commit = publication.get('commit')
            if not base:
                require(heads == [head, head], 'Remote/local branches differ; refusing automatic merge or extra commits')
                require(not git(root, 'diff', '--cached', '--name-only'), 'Existing staged changes; refusing to commit')
                publication.update(base=head, status='prepared')
                report['publication'] = publication; atomic_json(report_path, report)
                base = head
            if not commit and head != base:
                # Recover a crash between git commit and saving its SHA.
                verify_commit(root, head, base, files)
                commit = head
            if not commit:
                require(heads == [base, base], 'Remote changed before commit; refusing automatic merge')
                staged = names(git(root, 'diff', '--cached', '--name-only', '-z', raw=True))
                require(staged <= set(files), 'Unrelated staged changes')
                for relative in staged:
                    require(hashlib.sha256(git(root, 'show', ':' + relative, raw=True)).hexdigest() == files[relative],
                            'Staged content changed since validation')
                git(root, 'add', '--', *sorted(files))
                require(names(git(root, 'diff', '--cached', '--name-only', '-z', raw=True)) == set(files),
                        'Unexpected staged file set')
                for relative, digest in files.items():
                    require(hashlib.sha256(git(root, 'show', ':' + relative, raw=True)).hexdigest() == digest,
                            'Staged file differs from validated output')
                git(root, 'commit', '-m', 'Publish bilingual research notes for ' + report['date'])
                commit = git(root, 'rev-parse', 'HEAD')
            require(head in {base, commit}, 'Local history changed after publication commit')
            verify_commit(root, commit, base, files)
            publication.update(commit=commit, status='committed')
            report['publication'] = publication; atomic_json(report_path, report)
            require(all(h in {base, commit} for h in heads), 'Remote advanced independently; refusing to overwrite it')
            require(not git(root, 'status', '--porcelain'), 'Worktree changed during commit; refusing push')
            # Atomic, normal fast-forwards: both refs advance or neither does.
            git(root, 'push', '--atomic', remote, commit + ':refs/heads/' + branch, commit + ':refs/heads/' + production)
            publication.update(status='awaiting_deployment', pushed=True, error=None)
            report['publication'] = publication; atomic_json(report_path, report)
        status, error = deployment_status(config, commit, root)
        publication.update(status=status, error=error)
    except Exception as error:
        detail = str(error)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            detail += ': ' + error.stderr.decode(errors='replace')[-2000:].strip()
        publication.update(status='blocked', error=detail)
    report['publication'] = publication
    atomic_json(report_path, report)
    return publication


def retry_pending(root, config):
    if not config.get('enabled'):
        return []
    results = []
    for path in sorted((root / '.preview/research-jobs/runs').glob('*/report.json')):
        report = json.loads(path.read_text()); publication = report.get('publication', {})
        if publication.get('requested') is True and publication.get('status') != 'published':
            result = publish(root, path, config)
            results.append({'job': str(path.parent.relative_to(root)), **result})
            if result['status'] != 'published':
                break
    return results
