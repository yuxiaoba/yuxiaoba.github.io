import base64
import concurrent.futures
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from reading_metrics import create_app, Metrics, ORIGIN


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.catalog = self.root / 'catalog.json'
        self.path = '/tech/zh/test/'
        self.catalog.write_text(json.dumps({'version': 1, 'pages': [{'path': self.path, 'title': 'Test <script>bad</script>', 'lang': 'zh'}]}))
        self.settings = {'directory': str(self.root/'data'), 'secret': '17'*32, 'catalog': str(self.catalog),
                         'username': 'owner', 'password_sha256': hashlib.sha256(b'fixture-password').hexdigest()}
        self.app = create_app(self.settings); self.client = self.app.test_client()
        self.headers = {'Origin': ORIGIN, 'User-Agent': 'Fixture Browser 1.0'}
        self.auth = {'Authorization': 'Basic ' + base64.b64encode(b'owner:fixture-password').decode()}

    def send(self, n=1, path=None, headers=None, ip='203.0.113.7'):
        return self.client.post('/api/count', json={'path': path or self.path, 'event': f'{n:032x}'},
                                headers=headers or self.headers, environ_base={'REMOTE_ADDR': ip}, base_url='https://metrics.test')

    def report(self):
        return self.client.get('/api/stats', headers=self.auth, base_url='https://metrics.test').json

    def test_reloads_and_daily_unique_visitors(self):
        self.assertEqual(self.send(1).status_code, 204); self.send(2)
        self.assertEqual(self.report()['views'], 2); self.assertEqual(self.report()['visitors'], 1)
        self.send(3, ip='203.0.113.8'); self.assertEqual(self.report()['visitors'], 2)

    def test_request_id_deduplicates_retries(self):
        self.send(1); self.send(1); self.assertEqual(self.report()['views'], 1)

    def test_no_raw_ip_user_agent_or_event_id_in_storage(self):
        self.send(7)
        saved = next((self.root/'data').glob('*.json')).read_text()
        for value in ['203.0.113.7', 'Fixture Browser', f'{7:032x}']: self.assertNotIn(value, saved)

    def test_only_known_public_articles(self):
        for path in ['/zh/bookmarks/', '/search/?q=private', '/.metrics/settings.json', '/tech/zh/test/?secret=1', '/../tech/zh/test/', '/tech/zh/withdrawn/']:
            self.assertEqual(self.send(path=path).status_code, 400, path)
        self.assertEqual(self.report()['views'], 0)

    def test_cross_origin_is_rejected_and_private_routes_have_no_cors(self):
        for origin in ['https://evil.test', 'http://yuxiaoba.github.io', 'null']:
            response = self.send(headers={**self.headers, 'Origin': origin})
            self.assertEqual(response.status_code, 403); self.assertNotIn('Access-Control-Allow-Origin', response.headers)
        response = self.client.get('/api/stats', headers={**self.headers, **self.auth}, base_url='https://metrics.test')
        self.assertNotIn('Access-Control-Allow-Origin', response.headers)

    def test_preflight_and_no_write_methods(self):
        response = self.client.options('/api/count', headers=self.headers)
        self.assertEqual(response.status_code, 204); self.assertEqual(response.headers['Access-Control-Allow-Origin'], ORIGIN)
        self.assertNotIn('Access-Control-Allow-Credentials', response.headers)
        self.assertEqual(self.client.get('/api/count').status_code, 405)

    def test_payload_limits_and_unexpected_fields(self):
        for data in [None, [], {'path': self.path}, {'path': self.path, 'event': '../bad'}, {'path': self.path, 'event': '1'*32, 'bookmark': 'private'}]:
            response = self.client.post('/api/count', json=data, headers=self.headers)
            self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.post('/api/count', data='x'*3000, headers={**self.headers,'Content-Type':'application/json'}).status_code, 413)

    def test_bot_and_privacy_signals_do_not_count(self):
        for headers in [{'User-Agent':'HeadlessChrome'}, {'User-Agent':'Googlebot'}, {'DNT':'1'}, {'Sec-GPC':'1'}]:
            self.assertEqual(self.send(headers={**self.headers, **headers}).status_code, 204)
        self.assertEqual(self.report()['views'], 0)

    def test_authenticated_private_dashboard_and_escaping(self):
        for path in ['/admin','/api/stats']:
            self.assertEqual(self.client.get(path).status_code, 401)
            self.assertEqual(self.client.get(path, headers={'Authorization':'Basic eDph'}).status_code, 401)
        self.send(); response = self.client.get('/admin', headers=self.auth, base_url='https://metrics.test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('&lt;script&gt;', response.text); self.assertNotIn('<script>bad', response.text)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')

    def test_plain_http_nonlocal_dashboard_denied(self):
        response = self.client.get('/admin', headers=self.auth, environ_base={'REMOTE_ADDR':'203.0.113.7'})
        self.assertEqual(response.status_code, 401)

    def test_invalid_report_date_cannot_read_files(self):
        for day in ['../../settings', '2026-02-30', '20261028']:
            response = self.client.get('/api/stats', query_string={'date': day}, headers=self.auth, base_url='https://metrics.test')
            self.assertEqual(response.status_code, 400)

    def test_storage_survives_restart(self):
        self.send()
        client = create_app(self.settings).test_client()
        self.assertEqual(client.get('/api/stats',headers=self.auth,base_url='https://metrics.test').json['views'],1)

    def test_concurrent_writers_do_not_lose_counts(self):
        first = self.app.extensions['metrics']; second = Metrics(self.root/'data', self.settings['secret'], self.catalog)
        def count(n): return [first,second][n%2].record(self.path,f'{n:032x}','203.0.113.7','Fixture Browser',day='2026-10-28')
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor: list(executor.map(count, range(100)))
        report = first.report('2026-10-28'); self.assertEqual(report['views'],100); self.assertEqual(report['visitors'],1)

    def test_daily_hashes_rotate_and_counts_are_not_cross_day_people(self):
        metrics = self.app.extensions['metrics']
        for day in ['2026-10-27','2026-10-28']: metrics.record(self.path,'a'*32,'203.0.113.7','Fixture Browser',day=day)
        values=[json.loads(p.read_text())['pages'][self.path]['visitors'][0] for p in sorted((self.root/'data').glob('*.json'))]
        self.assertNotEqual(*values)

    def test_catalog_changes_reject_withdrawn_pages(self):
        self.send(); self.catalog.write_text(json.dumps({'version':1,'pages':[]}))
        self.assertEqual(self.send(2).status_code,400); self.assertEqual(self.report()['views'],1)

    def test_corrupt_storage_is_not_silently_reset(self):
        self.send(); file=next((self.root/'data').glob('*.json')); file.write_text('broken')
        self.assertEqual(self.send(2).status_code,503); self.assertEqual(file.read_text(),'broken')

    def test_rate_limit_and_spoofed_forwarded_header(self):
        self.send(1,headers={**self.headers,'X-Forwarded-For':'1.2.3.4'})
        self.send(2,headers={**self.headers,'X-Forwarded-For':'5.6.7.8'})
        self.assertEqual(self.report()['visitors'],1)
        for i in range(118): self.send(i+3)
        self.assertEqual(self.send(999).status_code,429)


if __name__ == '__main__': unittest.main()
