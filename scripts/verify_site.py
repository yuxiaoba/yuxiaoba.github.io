#!/usr/bin/env python3
"""Check real output and build isolated publishing fixtures; never edit real content."""
import argparse, hashlib, json, shutil, subprocess, tempfile, os, re
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import yaml
import datetime as dt
ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / '.preview'
REPORT.mkdir(exist_ok=True)
checks = []
def check(condition, message):
    if not condition:
        raise AssertionError(message)
    checks.append(message)
def soup(path):
    return BeautifulSoup(path.read_text(), 'html.parser')
def metadata(path):
    return yaml.safe_load(re.split(r'^---\s*$',path.read_text(),maxsplit=2,flags=re.M)[1])
def build(source, dest):
    from build_site import build as complete_build
    complete_build(source,dest)
def audit(site):
    published=[metadata(p) for p in (ROOT/'_publications').rglob('*.md') if metadata(p).get('published') is not False]
    years={str(p.get('year') or str(p['date'])[:4]) for p in published}
    for lang, prefix in [('en',''),('zh','zh/')]:
        for section in ['','publications/','digest/','tech/','life/','search/']:
            page=site/prefix/section/'index.html'
            check(page.exists(),f'route {prefix}{section}')
            doc=soup(page)
            check(doc.html['lang']==lang,f'language {prefix}{section}')
            check(len(doc.select('.navigation a'))==5,f'navigation {prefix}{section}')
        home=soup(site/prefix/'index.html')
        check([x.get('class')[0] for x in home.select('.identity-intro,.home-updates,.quiet-news,.profile-biography')]==['identity-intro','home-updates','quiet-news','profile-biography'],f'homepage section order {lang}')
        check(not home.select('main .cooking-door,main a[href$="/life/"]'),f'Life only in top navigation {lang}')
        updates=home.select_one('.home-updates')
        check(updates is not None,f'recent updates section {lang}')
        for collection,selector,limit in [('digest','.update-digest',1),('tech','.update-tech',2)]:
            entries=[metadata(p) for p in (ROOT/('_'+collection)/lang).rglob('*.md') if metadata(p).get('published') is True]
            dates=sorted([str(m['date'])[:10] for m in entries],reverse=True)[:limit]
            cards=updates.select(selector+' .recent-note')
            check([c.select_one('time')['datetime'] for c in cards]==dates,f'latest {collection} dates {lang}')
            check(all(c.select_one('h3 a')['href'].startswith('/'+collection+'/'+lang+'/') for c in cards),f'recent {collection} language isolation {lang}')
            check(all(not re.match(r'^\d{4}[-年]',c.select_one('h3').text.strip()) for c in cards),f'date separated from title {collection} {lang}')
        profile=yaml.safe_load((ROOT/('_data/profile_zh.yml' if lang=='zh' else '_data/profile.yml')).read_text())
        check(len(home.select('.education-entry'))==len(profile['education']),f'education {lang}')
        check(len(home.select('.awards-list li'))==len(profile['awards']),f'all awards {lang}')
        check(home.select_one('a[href="mailto:guangbayu@cuhk.edu.hk"]').text=='guangbayu@cuhk.edu.hk',f'visible email {lang}')
        check(len(home.select('.service li'))==sum(not x.get('hidden') for x in profile['service']),f'academic service {lang}')
        papers=soup(site/prefix/'publications/index.html')
        for source in sorted((ROOT/'_publications').rglob('*.md')):
            meta=metadata(source)
            record=papers.select_one(f'[data-publication="{source.relative_to(ROOT)}"]')
            check(record is not None, f'paper retained {lang} {source.name}')
            check(record.h2.text==meta['title'],f'original title {lang} {source.name}')
            authors=record.select_one('.authors').get_text(' ',strip=True)
            names=[re.sub('[†#✉\ufe0f]', '', a).strip() for a in meta.get('authors',[]) if a]
            rendered_names=[re.sub('✉\ufe0f?', '', a.get_text('',strip=True)) for a in record.select('.author')]
            check(rendered_names==names,f'original author names {lang} {source.name}')
            check(len(record.select('.corresponding-author'))==sum(any(mark in a for mark in ['†','#','✉']) and re.sub('[†#✉\ufe0f*]', '', a).strip()=='Guangba Yu' for a in meta.get('authors',[]) if a),f'corresponding author markers {lang} {source.name}')
            positions=[authors.index(a) for a in names]
            check(positions==sorted(positions),f'authors in original order {lang} {source.name}')
            if meta.get('pub'):
                check(BeautifulSoup(meta['pub'],'html.parser').text.strip() in record.get_text(' ',strip=True),f'original venue {lang} {source.name}')
        check(len(papers.select('.publication-entry'))==len(published),f'all {len(published)} papers {lang}')
        check(len(papers.select('.publication-sidebar .year-navigation a'))==len(years),f'year sidebar {lang}')
        approved=yaml.safe_load((ROOT/'_data/publication_topics.yml').read_text())
        for paper_path,topics in approved.items():
            labels=papers.select_one(f'[data-publication="{paper_path}"] .paper-topics')
            check([li.text for li in labels.select('li')]==topics[lang],f'approved topics {lang} {paper_path}')
        check(not papers.select('a[href*="changerca.pdf"]'),f'deleted PDF hidden {lang}')
        check(bool(papers.select('a[href="https://doi.org/10.1145/3643728"]')),f'ChangeRCA DOI retained {lang}')
        check(bool(papers.select('a[href="/files/ASPLOS25/Mint.pdf"]')),f'local Mint used {lang}')
        check(len(home.select('.quiet-news time'))==len([p for p in (ROOT/'_news').glob('*.md') if metadata(p).get('published') is not False]),f'news coverage {lang}')
    check(soup(site/'publications.html').select('.publication-entry'), 'legacy publication URL')
    for path in site.rglob('*.html'):
        doc=soup(path)
        for tag in doc.select('[href], [src]'):
            raw=tag.get('href',tag.get('src',''))
            url=urlsplit(raw)
            if url.scheme or url.netloc or not url.path:
                continue
            target=(site/unquote(url.path.lstrip('/'))) if url.path.startswith('/') else path.parent/unquote(url.path)
            if target.is_dir():target=target/'index.html'
            check(target.exists(),f'local resource {path.relative_to(site)} → {raw}')
            if url.fragment and target.suffix=='.html':
                check(soup(target).find(id=unquote(url.fragment)) is not None,f'anchor {raw}')
        check(not doc.select('a[href="#"],button[disabled]'),f'no fake links {path.relative_to(site)}')
    for excluded in ['.handoff','docs','scripts','AGENTS.md','vendor','.preview']:
        check(not (site/excluded).exists(),f'excluded output {excluded}')
    check(hashlib.sha256((ROOT/'files/ASPLOS25/Mint.pdf').read_bytes()).hexdigest()=='689902a7753a9fa3c9ba031e3be338c6d7e120a1399c4f600c67caf6427f4c03','Mint unchanged from user baseline')
    check(not (ROOT/'files/FSE24/changerca.pdf').exists(),'ChangeRCA deletion preserved')

def fixtures():
    dest=REPORT/'fixture-site'
    with tempfile.TemporaryDirectory(prefix='homepage-content-') as work:
        source=Path(work)/'source'
        shutil.copytree(ROOT,source,ignore=shutil.ignore_patterns('.git','.handoff','.preview','vendor','node_modules','_site','.bundle','.sass-cache','__pycache__'))
        def article(collection,lang,name,title,published=True,extra='',when='2026-10-10'):
            p=source/f'_{collection}'/lang/(name+'.md');p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('---\n'+yaml.safe_dump({'title':title,'date':when,'published':published,'summary':'测试导读' if lang=='zh' else 'A test summary'},allow_unicode=True)+'---\n\n'+extra)
        for col in ['digest','kitchen']:
            for lang in ['zh','en']:
                article(col,lang,'2026-10-10-paired','测试双语文章' if lang=='zh' else 'Paired article fixture',extra='[Original source](https://example.org/paper)\n\n## Original Paper Title\n\n'+('长标题与阅读内容。'*60 if lang=='zh' else 'Long reading content. '*60)+'\n\n![Image](/assets/images/photos/guangba.jpg)\n\n| Column A | Column B |\n| --- | --- |\n| '+('very-long-token-'*25)+' | value |\n\nhttps://example.org/'+('long-segment-'*30))
                article(col,lang,'2026-10-10-draft','DRAFT_MARKER_NEVER_OUTPUT',False)
                article(col,lang,'nested/2026-10-10-paired','嵌套文章' if lang=='zh' else 'Nested article')
            article(col,'zh','2026-10-10-only','仅中文测试文章')
            article(col,'zh','2026-10-10-unpublished-translation','译文草稿测试')
            article(col,'en','2026-10-10-unpublished-translation','DRAFT_TRANSLATION_NEVER_OUTPUT',False)
        # Fixtures must remain newer than real daily content as the site grows.
        published_dates=[dt.date.fromisoformat(str(metadata(p)['date'])[:10]) for col in ['_digest','_tech'] for p in (ROOT/col).rglob('*.md') if metadata(p).get('published') is True]
        latest=max(published_dates,default=dt.date(2026,10,10))+dt.timedelta(days=3)
        fixture_config=yaml.safe_load((source/'_config.yml').read_text());fixture_config['future']=True
        (source/'_config.yml').write_text(yaml.safe_dump(fixture_config,allow_unicode=True,sort_keys=False))
        for lang in ['zh','en']:
            title=(f'{latest.year}年{latest.month}月{latest.day}日｜' if lang=='zh' else latest.isoformat()+' | ')+'RECENT_DIGEST_FIXTURE'
            article('digest',lang,'home-recent',title,when=latest.isoformat())
            article('tech',lang,'home-recent','RECENT_TECH_FIXTURE',when=(latest-dt.timedelta(days=1)).isoformat())
            article('tech',lang,'home-older','OLDER_TECH_FIXTURE',when=(latest-dt.timedelta(days=2)).isoformat())
            article('tech',lang,'home-draft','RECENT_TECH_DRAFT_NEVER_OUTPUT',False,when=latest.isoformat())
        article('tech','zh','home-untranslated','ZH_ONLY_RECENT_TECH',when=latest.isoformat())
        p=source/'_publications/2027/fixture.md';p.parent.mkdir(exist_ok=True)
        p.write_text('---\n'+yaml.safe_dump({'title':'FIXTURE: '+('A very long original paper title '*12),'authors':['Guangba Yu*#','Test Author✉️'],'venue':'Test Conference','year':2027,'domains':['cloud','ai'],'topics':['agentops'],'published':True,'links':{'pdf':'','slides':'#','code':'https://example.org/code','bib':None}},sort_keys=False)+'---\n')
        p=source/'_publications/2027/draft.md';p.write_text('---\ntitle: DRAFT_PAPER_NEVER_OUTPUT\nyear: 2027\npublished: false\n---\n')
        build(source,dest)
        for lang,prefix in [('en',''),('zh','zh/')]:
            updates=soup(dest/prefix/'index.html').select_one('.home-updates')
            check(updates.select_one('.update-digest h3').text.strip()=='RECENT_DIGEST_FIXTURE',f'new digest automatically promoted and title date removed {lang}')
            check(len(updates.select('.update-tech .recent-note'))==2,f'home limits technical notes {lang}')
            check('RECENT_TECH_FIXTURE' in updates.text,f'new tech automatically promoted {lang}')
            check(('ZH_ONLY_RECENT_TECH' in updates.text)==(lang=='zh'),f'home untranslated tech stays in source language {lang}')
            check(not updates.select('[href*="home-draft"]'),f'home draft excluded {lang}')
        for col in ['digest','kitchen']:
            for lang in ['en','zh']:
                article_page=dest/col/lang/'2026-10-10-paired/index.html'
                check(article_page.exists(),f'{col} {lang} detail generated')
                d=soup(article_page)
                check(d.html['lang']==lang,f'{col} {lang} inferred from directory')
                other='en' if lang=='zh' else 'zh'
                check(d.select_one(f'.language-switch a[lang="{other}"]')['href']==f'/{col}/{other}/2026-10-10-paired/',f'{col} {lang} translation pairing')
                nested=soup(dest/col/lang/'nested/2026-10-10-paired/index.html')
                check(nested.select_one(f'.language-switch a[lang="{other}"]')['href']==f'/{col}/{other}/nested/2026-10-10-paired/',f'{col} {lang} nested translation pairing')
                prefix='zh/' if lang=='zh' else ''
                listing=soup(dest/prefix/('life' if col=='kitchen' else col)/'index.html')
                check(bool(listing.select(f'a[href="/{col}/{lang}/2026-10-10-paired/"]')),f'{col} {lang} automatic listing')
                check(not listing.select(f'a[href^="/{col}/{other}/"]'),f'{col} {lang} no mixed-language articles')
                if col=='kitchen':
                    check(bool(listing.select('img[src="/assets/images/photos/guangba.jpg"]')),f'kitchen {lang} first body photograph displayed')
                home=soup(dest/prefix/'index.html')
                if col=='digest':
                    check(bool(home.select(f'a[href^="/{col}/{lang}/"]')),f'{col} {lang} homepage latest updates')
                else:
                    check(bool(home.select(f'.navigation a[href="/{prefix}life/"]')),f'Life top navigation {lang}')
                    check(not home.select(f'main a[href^="/kitchen/{lang}/"]'),f'Life articles absent from homepage {lang}')
                check(not (dest/col/lang/'2026-10-10-draft').exists(),f'{col} {lang} draft has no output')
            for name in ['only','unpublished-translation']:
                d=soup(dest/col/'zh'/f'2026-10-10-{name}/index.html')
                check(d.select_one('.language-switch a[lang="en"]')['href']==f'/{"life" if col=="kitchen" else col}/?translation=missing',f'{col} missing/{name} fallback')
        for lang in ['en','zh']:
            d=soup(dest/('zh/' if lang=='zh' else '')/'publications/index.html')
            check(len(d.select('.publication-entry'))==len(list((ROOT/'_publications').rglob('*.md')))+1,f'{lang} new paper appears without template edit')
            check(d.find(id='year-2027') is not None,f'{lang} new year archive')
            paper=d.select_one('[data-publication="_publications/2027/fixture.md"]')
            check([a['href'] for a in paper.select('.publication-links a')]==['https://example.org/code'],f'{lang} blank/null/hash resource keys hidden')
            check(len(paper.select('.corresponding-author'))==1 and 'Guangba Yu*' in paper.select_one('.authors').text,f'{lang} only profile owner marked, coauthor envelope hidden, equal contribution retained')
            check(('智能体运维' if lang=='zh' else 'AgentOps') in paper.select_one('.paper-topics').text,f'{lang} new Markdown topic displayed')
        for f in dest.rglob('*.html'):
            check('NEVER_OUTPUT' not in f.read_text(),f'no draft leak {f.relative_to(dest)}')
        check(not (ROOT/'_digest/zh/2026-10-10-paired.md').exists(),'fixtures never written to real content')
    return dest

if __name__=='__main__':
    build(ROOT,REPORT/'content-test-site')
    audit(REPORT/'content-test-site')
    fixtures()
    (REPORT/'content-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks},ensure_ascii=False,indent=2))
    print(f'PASS: {len(checks)} content, metadata, route and resource assertions')
