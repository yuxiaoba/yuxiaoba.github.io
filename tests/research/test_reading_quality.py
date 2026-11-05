import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from research_daily import validate_reading_quality,IntakeError
class ReadingQualityTests(unittest.TestCase):
 def test_long_single_paragraph_does_not_make_a_tech_article(self):
  with self.assertRaises(IntakeError):validate_reading_quality('A summary sentence. '*100,'tech')
 def test_empty_headings_and_link_padding_do_not_pass(self):
  with self.assertRaises(IntakeError):validate_reading_quality('\n'.join('## Section\n'+'[source](https://example.org) '*100 for _ in range(3)),'tech')
 def test_explained_sections_pass_in_both_languages(self):
  for sentence in ['Describe the concrete mechanism and its workload-specific evidence. ','说明具体问题、执行机制和实验条件，区分测量结果与推测。']:
   validate_reading_quality('\n'.join('## Section\n'+sentence*8 for _ in range(3)),'tech')
 def test_abstract_only_is_not_full_source_review(self):
  with self.assertRaises(IntakeError):validate_reading_quality('本简述依据原始摘要；未独立复现实验。','paper')
 def test_paper_brief_does_not_need_tech_structure(self):
  validate_reading_quality('A concise source-checked research finding.','paper')
