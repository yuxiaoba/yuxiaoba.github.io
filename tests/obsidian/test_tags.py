import sys,tempfile,unittest
from pathlib import Path
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from obsidian.tags import load_taxonomy,normalize_tags
class TopicTests(unittest.TestCase):
 def test_aliases_and_labels_use_same_stable_ids(self):
  tags,unknown=normalize_tags(['AgentOps','智能体可靠性','RSI','self-improvement','可观测性与诊断'])
  self.assertEqual(tags,['agent-reliability','self-improvement','observability']);self.assertEqual(unknown,[])
 def test_unknown_tags_never_expand_search_vocabulary(self):
  tags,unknown=normalize_tags(['arXiv26','paper','unrecognized topic','AIOps'])
  self.assertEqual(tags,['anomaly-detection']);self.assertEqual(unknown,['arXiv26','paper','unrecognized topic'])
 def test_taxonomy_limit_and_ambiguous_aliases(self):
  items,_=load_taxonomy()
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'tags.yml';path.write_text(yaml.safe_dump(items*2))
   with self.assertRaisesRegex(ValueError,'1 and 10'):load_taxonomy(path)
   items[1]['aliases'].append('AgentOps');path.write_text(yaml.safe_dump(items))
   with self.assertRaisesRegex(ValueError,'different categories'):load_taxonomy(path)
 def test_every_category_has_both_languages(self):
  items,_=load_taxonomy();self.assertEqual(len(items),8)
  self.assertTrue(all(item.get('zh') and item.get('en') for item in items))
if __name__=='__main__':unittest.main()
