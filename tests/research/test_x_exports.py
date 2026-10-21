import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from research_x_exports import freeze_exports
from research_daily import sha

class XExportTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name); self.base = self.root / '.incoming/research/x_exports'; self.base.mkdir(parents=True)
        self.work = self.root / 'job/work'; (self.work / 'sources').mkdir(parents=True)
        self.data = {'date': '2026-10-20', 'items': [{'id': 'social-one', 'type': 'social', 'url': 'https://x.com/person/status/123'}]}
        self.post = {'id': '123', 'url': 'https://x.com/person/status/123', 'text': 'Original post', 'article_text': 'Full original article', 'author': {'username': 'person'}}
    def write(self, posts=None, name='2026-10-20.json', date='2026-10-20'):
        p = self.base / name; p.write_text(json.dumps({'date': date, 'timezone': 'Asia/Shanghai', 'posts': posts if posts is not None else [self.post]})); return p
    def run_export(self): return freeze_exports(self.root, self.work, self.data)
    def test_missing_is_explicit(self): self.assertEqual(self.run_export()['status'], 'missing')
    def test_only_selected_posts_and_hashes(self):
        self.write([self.post, {**self.post, 'id': '456', 'url': 'https://x.com/other/status/456'}])
        r = self.run_export(); self.assertEqual(len(r['posts']), 1)
        e = r['posts'][0]; p = self.work / e['local_file']; self.assertEqual(sha(p.read_bytes()), e['sha256']); self.assertIn('Full original article', p.read_text())
        self.assertFalse((self.work/'sources/x_exports/456').exists())
    def test_revision_and_partial(self):
        self.write(); self.write([{**self.post, 'text': 'Revision two'}], '2026-10-20.r002.json')
        (self.base/'2026-10-20.r003.json.part').write_text('partial')
        r=self.run_export(); self.assertEqual(r['file'], '2026-10-20.r002.json')
        self.assertIn('Revision two',(self.work/r['posts'][0]['local_file']).read_text())
    def test_invalid_newest_does_not_fall_back(self):
        self.write(); (self.base/'2026-10-20.r002.json').write_text('{broken')
        self.assertEqual(self.run_export()['status'],'unavailable')
    def test_match_primary_paper_and_twitter_alias(self):
        self.data['items'][0]['url']='https://arxiv.org/pdf/2610.23233v1'
        self.write([{**self.post,'primary_source':'https://arxiv.org/abs/2610.23233'}])
        self.assertEqual(self.run_export()['posts'][0]['source_ids'],['social-one'])
    def test_match_related_url(self):
        self.data['items'][0]['url']='https://example.org/report'; self.data['items'][0]['related_urls']=['https://twitter.com/person/status/123']
        self.write();self.assertEqual(self.run_export()['status'],'matched')
    def test_post_tracking_query_and_handle_case(self):
        self.data['items'][0]['url']='https://twitter.com/PERSON/status/123?s=20'
        self.write();self.assertEqual(self.run_export()['status'],'matched')
    def test_article_url_matches_export_link(self):
        self.data['items'][0]['url']='https://x.com/i/article/987?s=20'
        self.write([{**self.post,'linked_urls':[{'url':'https://x.com/i/article/987'}]}])
        self.assertEqual(self.run_export()['status'],'matched')
    def test_wrong_date(self):
        self.write(date='2026-10-19');self.assertEqual(self.run_export()['status'],'unavailable')
    def test_wrong_id(self):
        self.write([{**self.post,'id':'999'}]);self.assertEqual(self.run_export()['status'],'unavailable')
    def test_duplicate_id(self):
        self.write([self.post,self.post]);self.assertEqual(self.run_export()['status'],'unavailable')
    def test_attachment_freeze_and_path_escape(self):
        (self.base/'article.md').write_text('Complete article body')
        outside=self.root/'private.txt';outside.write_text('MUST_NOT_COPY')
        self.write([{**self.post,'article_file':'article.md','media_files':['../../../private.txt']}])
        r=self.run_export();self.assertEqual(len(r['posts'][0]['attachments']),1);self.assertTrue(r['warnings'])
        self.assertFalse(any('MUST_NOT_COPY' in p.read_text() for p in (self.work/'sources').rglob('*') if p.is_file()))
    def test_symlink_export_blocked(self):
        outside=self.root/'outside.json';outside.write_text('{}');(self.base/'2026-10-20.json').symlink_to(outside)
        self.assertEqual(self.run_export()['status'],'unavailable')
    def test_symlink_attachment_blocked(self):
        (self.base/'article.md').symlink_to(self.root/'private.md');(self.root/'private.md').write_text('secret')
        self.write([{**self.post,'article_file':'article.md'}]);r=self.run_export()
        self.assertEqual(r['posts'][0]['attachments'],[]);self.assertTrue(r['warnings'])

if __name__=='__main__': unittest.main()
