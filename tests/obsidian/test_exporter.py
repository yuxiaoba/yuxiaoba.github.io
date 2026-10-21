import json,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from obsidian.exporter import Exporter,ExportError,apply_files,plan_changes

class ExportTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.vault=self.root/'vault';self.site=self.root/'site';self.site.mkdir()
  for name in ['Paper','Tech Report']:(self.vault/name).mkdir(parents=True)
 def tearDown(self):self.tmp.cleanup()
 def note(self,name='Paper/note.md',header='',body='Public text'):
  p=self.vault/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('---\ntitle: Test\nid: test\npublish: true\ncreated_date: 2026-10-11\npaper_url: https://example.org/paper\nsource_url: https://example.org/tech\n'+header+'---\n'+body);return p
 def export(self):e=Exporter(self.vault);return e,e.run()
 def test_drafts_missing_and_false(self):
  for publish in ['', 'publish: false\n']:
   (self.vault/'Paper/n.md').write_text('---\n'+publish+'---\nPRIVATE')
   self.assertEqual(self.export()[1],{})
 def test_only_literal_boolean(self):
  for value in ['"true"','"false"','yes','on','1','null']:
   p=self.note();p.write_text(p.read_text().replace('publish: true','publish: '+value))
   with self.assertRaises(ExportError):self.export()
 def test_date_and_id_errors(self):
  for old,new in [('2026-10-11','2026-99-11'),('2026-10-11','2026'),('id: test','id: ../bad'),('id: test','id: Upper')]:
   p=self.note();p.write_text(p.read_text().replace(old,new))
   with self.assertRaises(ExportError):self.export()
 def test_yaml_duplicate_and_invalid(self):
  for header in ['publish: false\n','company: Foo: Bar\n']:
   self.note(header=header)
   with self.assertRaises(ExportError):self.export()
 def test_default_language_and_date_priority(self):
  self.note(header='date: 2026-10-12\n');e,files=self.export();text=files['_digest/zh/obsidian/daily-2026-10-12.md'].decode()
  self.assertIn('date: 2026-10-12',text);self.assertEqual(len(e.warnings),1)
 def test_duplicate_ids_and_translations(self):
  self.note();self.note('Paper/duplicate.md')
  with self.assertRaises(ExportError):self.export()
  self.note('Paper/duplicate.md',header='lang: en\n');self.assertEqual(sum(k.endswith('.md') for k in self.export()[1]),2)
 def test_tech_is_separate(self):
  self.note();self.note('Tech Report/note.md');files=self.export()[1];self.assertIn('_tech/zh/obsidian/test.md',files)
 def test_comments_code_and_liquid(self):
  self.note(body='%% SECRET_MARKER %%\nPublic {{ site.email }}\n`[[not a link]]`\n\n```md\n![[not-an-image.png]]\n{{ site.email }}\n```')
  _,files=self.export();text=next(v for k,v in files.items() if k.endswith('.md')).decode();self.assertNotIn('SECRET_MARKER',text);self.assertIn('[[not a link]]',text);self.assertIn('![[not-an-image.png]]',text);self.assertNotIn('{{ site.email }}',text)
 def test_unclosed_private_comment(self):
  self.note(body='%% SECRET')
  with self.assertRaises(ExportError):self.export()
 def test_private_metadata_not_exported(self):
  self.note(header='notebook: PRIVATE_NOTEBOOK\narchive_path: PRIVATE_ARCHIVE\n');text=next(v for k,v in self.export()[1].items() if k.endswith('.md')).decode();self.assertNotIn('PRIVATE_',text)
 def test_link_to_public_private_and_alias(self):
  self.note(body='[[second|Read this]] [[secret|Private alias]]')
  self.note('Paper/second.md').write_text(self.note('Paper/second.md').read_text().replace('id: test','id: second'))
  (self.vault/'Paper/secret.md').write_text('Secret body')
  e,files=self.export();text=files['_digest/zh/obsidian/daily-2026-10-11.md'].decode();self.assertIn('[Read this](/digest/zh/daily/2026-10-11/#paper-second)',text);self.assertIn('Private alias',text);self.assertNotIn('Secret body',text)
 def test_image_resolution_size_and_collision(self):
  (self.vault/'Paper/figure').mkdir();Image.new('RGB',(20,10)).save(self.vault/'Paper/figure/img.png')
  self.note(body='![[figure/img.png|100x100]]\n![Caption](figure/img.png)')
  e,files=self.export();self.assertEqual(len(e.assets),1);self.assertIn('width="20"',files['_digest/zh/obsidian/daily-2026-10-11.md'].decode());self.assertNotIn('height="100"',files['_digest/zh/obsidian/daily-2026-10-11.md'].decode())
 def test_missing_and_ambiguous_image(self):
  self.note(body='![[img.png]]')
  with self.assertRaises(ExportError):self.export()
  for name in ['a','b']:
   (self.vault/name).mkdir();Image.new('RGB',(10,10)).save(self.vault/name/'img.png')
  with self.assertRaises(ExportError):self.export()
 def test_traversal_symlink_and_unsupported_embeds(self):
  for target in ['../outside.png','doc.pdf','note.md','https://example.org/x.png']:
   self.note(body=f'![[{target}]]')
   with self.assertRaises(ExportError):self.export()
  outside=self.root/'outside.png';Image.new('RGB',(10,10)).save(outside);(self.vault/'Paper/link.png').symlink_to(outside)
  self.note(body='![[link.png]]')
  with self.assertRaises(ExportError):self.export()
 def test_callout_math_and_summary(self):
  self.note(body='## 一句话\n\nA concise summary.\n\n> [!NOTE] Important\n> Callout text\n\nInline \\(x^2\\) and $y^2$.\n\n\\[z^2\\]')
  text=next(v for k,v in self.export()[1].items() if k.endswith('.md')).decode();self.assertIn('A concise summary.',text);self.assertIn('> **Important**',text);self.assertIn('$$x^2$$',text);self.assertIn('$$y^2$$',text)
 def test_stable_id_and_repeat_and_unpublish(self):
  p=self.note();_,files=self.export();first=apply_files(self.site,files);self.assertEqual(len(first['write']),2)
  self.assertEqual(apply_files(self.site,self.export()[1]),{'write':[],'remove':[]})
  p.rename(self.vault/'Paper/renamed.md');self.assertEqual(apply_files(self.site,self.export()[1]),{'write':[],'remove':[]})
  manual=self.site/'_digest/zh/manual.md';manual.write_text('User content')
  q=self.vault/'Paper/renamed.md';q.write_text(q.read_text().replace('publish: true','publish: false'))
  changes=apply_files(self.site,self.export()[1]);self.assertEqual(len(changes['remove']),2);self.assertEqual(manual.read_text(),'User content')
 def test_unmanaged_or_modified_output_protected(self):
  self.note();files=self.export()[1];p=self.site/'_digest/zh/obsidian/daily-2026-10-11.md';p.parent.mkdir(parents=True);p.write_text('Handwritten')
  with self.assertRaises(ExportError):plan_changes(self.site,files)
  p.unlink();apply_files(self.site,files);p.write_text('Edited by user')
  with self.assertRaises(ExportError):plan_changes(self.site,files)
 def test_missing_source_does_not_clear_previous(self):
  self.note();apply_files(self.site,self.export()[1]);(self.vault/'Tech Report').rmdir()
  with self.assertRaises(ExportError):self.export()
  self.assertTrue((self.site/'_digest/zh/obsidian/daily-2026-10-11.md').exists())
 def test_shared_asset_survives_manual_reference(self):
  Image.new('RGB',(10,10)).save(self.vault/'Paper/img.png');p=self.note(body='![[img.png]]')
  e,files=self.export();asset=next(k for k in files if k.startswith('assets/'));apply_files(self.site,files)
  manual=self.site/'_digest/zh/manual.md';manual.write_text('![reuse](/'+asset+')')
  p.write_text(p.read_text().replace('publish: true','publish: false'));apply_files(self.site,self.export()[1]);self.assertTrue((self.site/asset).exists())
  manual.write_text('No image now');apply_files(self.site,self.export()[1]);self.assertFalse((self.site/asset).exists())
 def test_relative_parent_inside_vault_and_private_summary(self):
  (self.vault/'images').mkdir();Image.new('RGB',(10,10)).save(self.vault/'images/img.png')
  self.note(header='summary: "Public %%PRIVATE_META%% summary"\n',body='![caption](../images/img.png)')
  files=self.export()[1];self.assertNotIn('PRIVATE_META',files['_digest/zh/obsidian/daily-2026-10-11.md'].decode())
 def test_unclosed_math_and_html_image(self):
  for body in [r'Broken \(x',r'$$ x', '<img src="https://example.org/x.png">']:
   self.note(body=body)
   with self.assertRaises(ExportError):self.export()
 def test_unsupported_dataview(self):
  self.note(body='```dataview\nLIST\n```')
  with self.assertRaises(ExportError):self.export()
 def test_daily_grouping_and_withdrawal(self):
  first=self.note(body='FIRST_PUBLIC')
  second=self.note('Paper/second.md',body='SECOND_PUBLIC');second.write_text(second.read_text().replace('id: test','id: second'))
  files=self.export()[1];day='_digest/zh/obsidian/daily-2026-10-11.md'
  self.assertEqual(sum(k.endswith('.md') for k in files),1);self.assertIn('paper_count: 2',files[day].decode())
  apply_files(self.site,files);second.write_text(second.read_text().replace('publish: true','publish: false'))
  files=self.export()[1];apply_files(self.site,files);self.assertIn('FIRST_PUBLIC',files[day].decode());self.assertNotIn('SECOND_PUBLIC',files[day].decode());self.assertFalse((self.site/'digest/zh/obsidian/second/index.html').exists())
  first.unlink();apply_files(self.site,self.export()[1]);self.assertFalse((self.site/day).exists())
 def test_daily_date_move_and_legacy_migration(self):
  note=self.note();old='_digest/zh/obsidian/test.md';apply_files(self.site,{old:b'Legacy export'})
  apply_files(self.site,self.export()[1]);self.assertFalse((self.site/old).exists())
  note.write_text(note.read_text().replace('2026-10-11','2026-10-12'));files=self.export()[1];apply_files(self.site,files)
  self.assertFalse((self.site/'_digest/zh/obsidian/daily-2026-10-11.md').exists());self.assertIn('/2026-10-12/#paper-test',files['digest/zh/obsidian/test/index.html'].decode())
 def test_daily_separate_days_and_languages(self):
  self.note();p=self.note('Paper/second.md',header='date: 2026-10-12\n');p.write_text(p.read_text().replace('id: test','id: second'))
  self.note('Paper/en.md',header='lang: en\n');files=self.export()[1]
  self.assertEqual(sum(k.endswith('.md') for k in files),3)
 def test_daily_heading_links_and_private_metadata(self):
  self.note(header='tags: ["Public %%SECRET_TAG%%"]\n',body='## Shared\n[[second#Shared|Jump]]')
  p=self.note('Paper/second.md',body='## Shared\nSecond');p.write_text(p.read_text().replace('id: test','id: second').replace('title: Test','title: "Test %%SECRET_TITLE%%"'))
  files=self.export()[1];text=files['_digest/zh/obsidian/daily-2026-10-11.md'].decode()
  self.assertIn('paper-test-h-shared',text);self.assertIn('paper-second-h-shared',text)
  self.assertIn('/digest/zh/daily/2026-10-11/#paper-second-h-shared',text)
  self.assertNotIn('SECRET_',b''.join(files.values()).decode())
if __name__=='__main__':unittest.main()
