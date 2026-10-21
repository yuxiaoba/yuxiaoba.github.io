#!/usr/bin/env python3
"""Create private test fixtures from the handoff; never overwrite an existing demo vault."""
from pathlib import Path
import shutil,yaml,json
root=Path(__file__).resolve().parents[1];base=root/'.handoff/obsidian-sync-2026-10-15/obsidian-digest'
dest=root/'.preview/obsidian-demo-vault'
if dest.exists():raise SystemExit('Demo vault already exists; preserved unchanged.')
shutil.copytree(base/'sample-source',dest)
(dest/'Tech Report').mkdir(exist_ok=True)
p=next((dest/'Paper').rglob('*.md'));s=p.read_text().replace('publish: false','publish: true');s+= '\n\n%% PRIVATE_TEST_SENTINEL_OBSIDIAN %%\n\n[[Tech Report/sync-engine|技术说明]]\n'
p.write_text(s)
def note(path,title,ident,lang,body,publish=True,tags=None):
 path.parent.mkdir(parents=True,exist_ok=True)
 header={'title':title,'id':ident,'publish':publish,'lang':lang,'date':'2026-10-11','source_url':'https://example.org/technical-reference','paper_url':'https://example.org/paper','tags':tags or ['sync','test'],'summary':'用于验证同步与检索的临时笔记。' if lang=='zh' else 'A temporary synchronization and search test.'}
 path.write_text('---\n'+yaml.safe_dump(header,allow_unicode=True,sort_keys=False)+'---\n\n'+body)
note(dest/'Tech Report/sync-engine.md','临时技术验证：原子同步','sync-engine','zh','## 一句话\n\n原子同步通过 staged-build 防止断图和索引过期。TECH_ONLY_SENTINEL。\n\n> [!NOTE] 测试提示\n> 工作流分成两个阶段。\n\n内联公式 \\(x^2+y^2=z^2\\)。\n\n$$\n\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}\n$$\n\n[[Paper/Evolve/'+p.stem+'#核心问题与方法|公开阅读]]\n\n[[private-note|未公开说明]]\n\n```md\n![[demonstration.png]]\n{{ site.email }}\n```\n\n%% PRIVATE_TEST_SENTINEL_OBSIDIAN %%')
# Link to an actual heading in MASS; the text retains its original emoji prefix.
t=dest/'Tech Report/sync-engine.md';t.write_text(t.read_text().replace('#核心问题与方法','#研究方法和技术路线'))
note(dest/'Tech Report/en/sync-engine.md','Temporary technical check: atomic sync','sync-engine','en','Atomic sync keeps the last good version. ENGLISH_ONLY_SENTINEL.\n\n## Details\n\nThe staged-build transaction is reproducible.')
note(dest/'Paper/en/english-search.md','English search fixture','english-search','en','Recursive workflows and ENGLISH_PAPER_SENTINEL.',tags=['RSI'])
note(dest/'Paper/private-note.md','DRAFT_PRIVATE_NOTE','private-note','zh','PRIVATE_DRAFT_SENTINEL_OBSIDIAN',False)
print(dest)
