"""Small, file-backed article metrics service. No raw IPs, cookies or public reports."""
import datetime as dt
import fcntl
import hashlib
import hmac
import json
import os
import re
import tempfile
import threading
import time
from pathlib import Path
from zoneinfo import ZoneInfo
from flask import Flask, Response, jsonify, render_template_string, request

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://yuxiaoba.github.io'
TZ = ZoneInfo('Asia/Shanghai')
EVENT = re.compile(r'(?:[0-9a-f]{32}|[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\Z')
BOTS = re.compile(r'bot|crawler|spider|headless|playwright|curl|wget|python|httpx', re.I)


def atomic_json(path, value):
    fd, temporary = tempfile.mkstemp(prefix='.metrics-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, ensure_ascii=False, separators=(',', ':'))
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


class RateLimit:
    def __init__(self):
        self.lock = threading.Lock(); self.counts = {}; self.window = -1

    def allow(self, key, maximum):
        minute = int(time.monotonic() // 60)
        with self.lock:
            if minute != self.window:
                self.counts.clear(); self.window = minute
            if key not in self.counts and len(self.counts) >= 4096: return False
            count = self.counts.get(key, 0) + 1
            self.counts[key] = count
            return count <= maximum


class Metrics:
    def __init__(self, directory, secret, catalog):
        self.directory = Path(directory); self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.secret = bytes.fromhex(secret)
        if len(self.secret) < 32: raise ValueError('Metrics key must contain at least 32 random bytes')
        self.catalog_path = Path(catalog); self.catalog = {}; self.catalog_time = None
        self.lock = threading.RLock()

    def digest(self, value):
        return hmac.new(self.secret, value.encode(), hashlib.sha256).hexdigest()

    def pages(self):
        with self.lock:
            stamp = self.catalog_path.stat().st_mtime_ns
            if stamp != self.catalog_time:
                value = json.loads(self.catalog_path.read_text())
                if value.get('version') != 1: raise ValueError('Invalid reading catalog')
                pages = {p['path']: p for p in value['pages']}
                if any(not re.fullmatch(r'/(?:digest|tech)/(?:zh|en)/[a-zA-Z0-9/._-]+/', p) for p in pages):
                    raise ValueError('Invalid catalog route')
                self.catalog = pages; self.catalog_time = stamp
            return dict(self.catalog)

    def record(self, path, event, ip, user_agent, day=None):
        day = day or dt.datetime.now(TZ).date().isoformat()
        file = self.directory / (day + '.json')
        visitor = self.digest('visitor\0' + day + '\0' + ip + '\0' + user_agent[:512])
        event_key = self.digest('event\0' + day + '\0' + event)
        with self.lock, (self.directory / 'write.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            value = json.loads(file.read_text()) if file.exists() else {'version': 1, 'date': day, 'pages': {}, 'events': {}}
            if event_key in value['events']: return False
            if len(value['events']) >= 50000: raise OverflowError('Daily event storage capacity reached')
            row = value['pages'].setdefault(path, {'views': 0, 'visitors': []})
            row['views'] += 1
            if visitor not in row['visitors']: row['visitors'].append(visitor)
            value['events'][event_key] = True
            atomic_json(file, value)
            return True

    def report(self, day):
        dt.date.fromisoformat(day)
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', day): raise ValueError('Invalid report date')
        file = self.directory / (day + '.json')
        value = json.loads(file.read_text()) if file.exists() else {'pages': {}}
        pages = self.pages(); rows = []; visitors = set()
        for path, data in value['pages'].items():
            visitors.update(data['visitors'])
            rows.append({'path': path, 'title': pages.get(path, {}).get('title', path),
                         'views': data['views'], 'visitors': len(data['visitors'])})
        return {'date': day, 'views': sum(r['views'] for r in rows), 'visitors': len(visitors),
                'pages': sorted(rows, key=lambda r: (-r['views'], r['path']))}


def create_app(settings=None):
    if settings is None:
        settings = json.loads(Path(os.environ.get('READING_METRICS_SETTINGS', ROOT / '.metrics/settings.json')).read_text())
    app = Flask(__name__); app.config['MAX_CONTENT_LENGTH'] = 2048
    metrics = Metrics(settings['directory'], settings['secret'], settings['catalog'])
    app.extensions['metrics'] = metrics; limiter = RateLimit()

    def address(): return request.remote_addr or ''  # Never trust forwarded IP headers.

    def owner():
        if not request.is_secure and address() not in {'127.0.0.1', '::1'}: return False
        auth = request.authorization
        if not auth or auth.type.lower() != 'basic': return False
        candidate = hashlib.sha256((auth.password or '').encode()).hexdigest()
        return hmac.compare_digest(auth.username or '', settings['username']) and hmac.compare_digest(candidate, settings['password_sha256'])

    @app.after_request
    def headers(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
        if request.path == '/api/count' and request.headers.get('Origin') == ORIGIN:
            response.headers['Access-Control-Allow-Origin'] = ORIGIN
            response.headers['Vary'] = 'Origin'
        return response

    @app.get('/health')
    def health(): return jsonify(ok=True)

    @app.route('/api/count', methods=['POST', 'OPTIONS'])
    def count():
        if request.headers.get('Origin') != ORIGIN: return jsonify(error='origin'), 403
        if request.method == 'OPTIONS':
            response = Response(status=204)
            response.headers['Access-Control-Allow-Methods'] = 'POST'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.headers['Access-Control-Max-Age'] = '600'
            return response
        key = metrics.digest('rate\0' + address())
        if not limiter.allow('count:' + key, 120): return jsonify(error='rate'), 429
        if request.headers.get('DNT') == '1' or request.headers.get('Sec-GPC') == '1': return Response(status=204)
        agent = request.headers.get('User-Agent', '')
        if not agent or BOTS.search(agent): return Response(status=204)
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or set(data) != {'path', 'event'}: return jsonify(error='payload'), 400
        if not isinstance(data['path'], str) or not isinstance(data['event'], str) or not EVENT.fullmatch(data['event']):
            return jsonify(error='payload'), 400
        try:
            if data['path'] not in metrics.pages(): return jsonify(error='path'), 400
            metrics.record(data['path'], data['event'], address(), agent)
        except (OSError, ValueError, KeyError, OverflowError):
            app.logger.error('Metrics storage unavailable')  # No visitor identifiers in logs.
            return jsonify(error='unavailable'), 503
        return Response(status=204)

    @app.route('/admin')
    @app.route('/api/stats')
    def admin():
        key = metrics.digest('admin\0' + address())
        if not owner():
            if not limiter.allow('failed-admin:' + key, 20): return jsonify(error='rate'), 429
            return Response('Owner login required', 401, {'WWW-Authenticate': 'Basic realm="Reading metrics", charset="UTF-8"'})
        if not limiter.allow('admin:' + key, 120): return jsonify(error='rate'), 429
        day = request.args.get('date', dt.datetime.now(TZ).date().isoformat())
        try: report = metrics.report(day)
        except (ValueError, OSError, KeyError): return jsonify(error='invalid date or unavailable report'), 400
        if request.path == '/api/stats': return jsonify(report)
        template = (ROOT / 'docs/metrics/dashboard.html').read_text()
        return render_template_string(template, report=report, origin=ORIGIN)

    return app
