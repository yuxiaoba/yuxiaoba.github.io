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
    analytics_enabled=yaml.safe_load((ROOT/'_config.yml').read_text()).get('reading_metrics',{}).get('enabled') is True
    catalog=json.loads((site/'reading-metrics.json').read_text())
    catalog_paths={p['path'] for p in catalog['pages']}
    check(catalog['version']==1 and len(catalog_paths)==len(catalog['pages']),'analytics catalog has unique routes')
    published=[metadata(p) for p in (ROOT/'_publications').rglob('*.md') if metadata(p).get('published') is not False]
    years={str(p.get('year') or str(p['date'])[:4]) for p in published}
    for lang, prefix in [('en',''),('zh','zh/')]:
        for section in ['','publications/','digest/','tech/','life/','search/','bookmarks/']:
            page=site/prefix/section/'index.html'
            check(page.exists(),f'route {prefix}{section}')
            doc=soup(page)
            check(doc.html['lang']==lang,f'language {prefix}{section}')
            check(len(doc.select('.navigation a'))==5,f'navigation {prefix}{section}')
            check(doc.select_one('.bookmark-entry')['href']=='/'+prefix+'bookmarks/',f'bookmark entrance {prefix}{section}')
        saved=soup(site/prefix/'bookmarks/index.html')
        privacy=soup(site/prefix/'privacy/index.html')
        check(privacy.html['lang']==lang and privacy.select_one('[data-metrics-off]') is not None,f'bilingual analytics preference {lang}')
        check(not saved.select('script[data-reading-metrics]') and not privacy.select('script[data-reading-metrics]'),f'private/preference pages do not count {lang}')
        check(saved.select_one('[data-bookmark-shelf]') is not None and not saved.select('[data-pagefind-body],.saved-note'),f'private bookmarks start empty and unindexed {lang}')
        home=soup(site/prefix/'index.html')
        diagram=home.select_one('[data-research-diagram]')
        check(diagram is not None and [n.get('data-direction') for n in diagram.select('button[disabled]')]==['cloud','ai','chaos'],f'research diagram has a static no-JS fallback {lang}')
        check(len(diagram.select('.rd-topics strong'))==4 and diagram.select_one('.rd-method-note').get_text(strip=True),f'research directions remain readable without JavaScript {lang}')
        for collection in ['digest','tech']:
            archive=soup(site/prefix/collection/'index.html')
            attribution=archive.select_one('.note-attribution')
            expected=yaml.safe_load((ROOT/'_data/locales.yml').read_text())[lang]['note_attribution']
            check(attribution is not None and attribution.get_text(strip=True)==expected,f'AI assistance attribution {collection} {lang}')
            for page_path in (site/collection/lang).rglob('index.html'):
                article=soup(page_path)
                if article.select_one('meta[http-equiv="refresh"]'):
                    continue  # Historical per-paper URLs redirect into a daily digest.
                check(article.select_one('[data-bookmark-article]') is not None,f'bookmark controls enabled for {page_path.relative_to(site)}')
                route='/'+str(page_path.relative_to(site)).removesuffix('index.html')
                check(route in catalog_paths,f'published article in metrics allowlist {route}')
                counter=article.select_one('script[data-reading-metrics]')
                check(bool(counter)==analytics_enabled,f'analytics follows enabled configuration {route}')
                if counter:check(counter['data-path']==route,f'analytics sends canonical article path {route}')
                byline=article.select_one('.article-header .door-detail')
                check(byline is not None and byline.select_one('time') is not None and byline.get_text(strip=True)==byline.time.get_text(strip=True),f'reading header shows date without personal byline {page_path.relative_to(site)}')
        check([x.get('class')[0] for x in home.select('.identity-intro,.home-updates,.quiet-news,.profile-biography')]==['identity-intro','profile-biography','quiet-news','home-updates'],f'homepage section order {lang}')
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
            archive=soup(site/prefix/collection/'index.html')
            groups=archive.select('.archive-month')
            expected_months=sorted({str(m['date'])[:7] for m in entries},reverse=True)
            if len(entries)>1:
                check([g['id'] for g in groups]==['month-'+m for m in expected_months],f'{collection} month groups ordered {lang}')
                check([g.has_attr('open') for g in groups]==[True]+[False]*(len(groups)-1),f'{collection} latest month open only {lang}')
                for group,month in zip(groups,expected_months):
                    count=sum(str(m['date']).startswith(month) for m in entries)
                    check(len(group.select('.digest-archive-row'))==count,f'{collection} month entries preserved {month} {lang}')
                    check(group.select_one('.archive-month-count').text.strip().split()[0]==str(count),f'{collection} month count {month} {lang}')
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
        # Diagram controls start disabled until their JS handlers are ready;
        # their content remains readable. Resource links still cannot be fake.
        disabled=[b for b in doc.select('button[disabled]') if b not in doc.select('[data-research-diagram] .rd-node[data-direction]')]
        check(not doc.select('a[href="#"]') and not disabled,f'no fake links {path.relative_to(site)}')
    for excluded in ['.handoff','docs','scripts','AGENTS.md','vendor','.preview','.metrics']:
        check(not (site/excluded).exists(),f'excluded output {excluded}')
    check(hashlib.sha256((ROOT/'files/ASPLOS25/Mint.pdf').read_bytes()).hexdigest()=='689902a7753a9fa3c9ba031e3be338c6d7e120a1399c4f600c67caf6427f4c03','Mint unchanged from user baseline')
    check(not (ROOT/'files/FSE24/changerca.pdf').exists(),'ChangeRCA deletion preserved')

def fixtures():
    dest=REPORT/'fixture-site'
    with tempfile.TemporaryDirectory(prefix='homepage-content-') as work:
        source=Path(work)/'source'
        shutil.copytree(ROOT,source,ignore=shutil.ignore_patterns('.git','.handoff','.preview','.metrics','vendor','node_modules','_site','.bundle','.sass-cache','__pycache__'))
        private_metrics=source/'.metrics';private_metrics.mkdir();(private_metrics/'secret.json').write_text('METRICS_SECRET_FIXTURE_NEVER_OUTPUT')
        private_life=source/'.incoming/life/private-fixture';private_life.mkdir(parents=True,exist_ok=True)
        (private_life/'note.txt').write_text('LIFE_PRIVATE_FIXTURE_NEVER_OUTPUT')
        def article(collection,lang,name,title,published=True,extra='',when='2026-10-10',updated=None):
            p=source/f'_{collection}'/lang/(name+'.md');p.parent.mkdir(parents=True,exist_ok=True)
            meta={'title':title,'date':when,'published':published,'summary':'测试导读' if lang=='zh' else 'A test summary'}
            if updated:meta['updated_at']=updated
            p.write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True)+'---\n\n'+extra)
        for col in ['digest','kitchen']:
            for lang in ['zh','en']:
                article(col,lang,'2026-10-10-paired','测试双语文章' if lang=='zh' else 'Paired article fixture',extra='[Original source](https://example.org/paper)\n\n## Original Paper Title\n\n'+('长标题与阅读内容。'*60 if lang=='zh' else 'Long reading content. '*60)+'\n\n![Image](/assets/images/photos/guangba.jpg)\n\n| Column A | Column B |\n| --- | --- |\n| '+('very-long-token-'*25)+' | value |\n\nhttps://example.org/'+('long-segment-'*30))
                article(col,lang,'2026-10-10-draft','DRAFT_MARKER_NEVER_OUTPUT',False)
                article(col,lang,'nested/2026-10-10-paired','嵌套文章' if lang=='zh' else 'Nested article')
            article(col,'zh','2026-10-10-only','仅中文测试文章')
            article(col,'zh','2026-10-10-unpublished-translation','译文草稿测试')
            article(col,'en','2026-10-10-unpublished-translation','DRAFT_TRANSLATION_NEVER_OUTPUT',False)
        for lang in ['zh','en']:
            photo_meta={'title':'PHOTO_FEED_FIXTURE','date':'2026-01-01','published':True,'layout':'life-album','photo_album':True,'location':'Fixture location','photos':[{'src':'/assets/images/photos/guangba.jpg','width':400,'height':500,'alt':'Fixture photo','caption':'Fixture caption'}]*3}
            (source/f'_kitchen/{lang}/feed-photos.md').write_text('---\n'+yaml.safe_dump(photo_meta)+'---\n')
        # Fixtures must remain newer than real daily content as the site grows.
        published_dates=[dt.date.fromisoformat(str(metadata(p)['date'])[:10]) for col in ['_digest','_tech'] for p in (ROOT/col).rglob('*.md') if metadata(p).get('published') is True]
        latest=max(published_dates,default=dt.date(2026,10,10))+dt.timedelta(days=3)
        fixture_config=yaml.safe_load((source/'_config.yml').read_text());fixture_config['future']=True
        (source/'_config.yml').write_text(yaml.safe_dump(fixture_config,allow_unicode=True,sort_keys=False))
        for lang in ['zh','en']:
            title=(f'{latest.year}年{latest.month}月{latest.day}日｜' if lang=='zh' else latest.isoformat()+' | ')+'RECENT_DIGEST_FIXTURE'
            article('digest',lang,'home-recent',title,when=latest.isoformat())
            same_day=(latest-dt.timedelta(days=1)).isoformat()
            article('tech',lang,'home-recent','RECENT_TECH_FIXTURE',when=same_day,updated=same_day+'T09:00:00+08:00')
            article('tech',lang,'aaa-same-day-newest','SAME_DAY_NEWEST_FIXTURE',when=same_day,updated=same_day+'T10:00:00+08:00')
            article('tech',lang,'home-older','OLDER_TECH_FIXTURE',when=(latest-dt.timedelta(days=2)).isoformat(),updated=latest.isoformat()+'T23:00:00+08:00')
            article('tech',lang,'home-draft','RECENT_TECH_DRAFT_NEVER_OUTPUT',False,when=latest.isoformat())
        article('tech','zh','home-untranslated','ZH_ONLY_RECENT_TECH',when=latest.isoformat())
        previous_month=(latest.replace(day=1)-dt.timedelta(days=1)).isoformat()
        previous_year=f'{latest.year-1}-01-03'
        for col in ['digest','tech']:
            for lang in ['zh','en']:
                article(col,lang,'archive-previous-month','ARCHIVE_PREVIOUS_MONTH',when=previous_month,extra='ARCHIVE_MONTH_SEARCHABLE')
                article(col,lang,'archive-previous-year','ARCHIVE_PREVIOUS_YEAR',when=previous_year)
                article(col,lang,'archive-private-month','ARCHIVE_DRAFT_NEVER_OUTPUT',False,when='1900-01-01')
        p=source/'_publications/2027/fixture.md';p.parent.mkdir(exist_ok=True)
        p.write_text('---\n'+yaml.safe_dump({'title':'FIXTURE: '+('A very long original paper title '*12),'authors':['Guangba Yu*#','Test Author✉️'],'venue':'Test Conference','year':2027,'domains':['cloud','ai'],'topics':['agentops'],'published':True,'links':{'pdf':'','slides':'#','code':'https://example.org/code','bib':None}},sort_keys=False)+'---\n')
        p=source/'_publications/2027/draft.md';p.write_text('---\ntitle: DRAFT_PAPER_NEVER_OUTPUT\nyear: 2027\npublished: false\n---\n')
        build(source,dest)
        check(not (dest/'.incoming').exists(),'private Life inbox excluded from site and search inputs')
        for lang,prefix in [('en',''),('zh','zh/')]:
            listing=soup(dest/prefix/'life/index.html')
            moment=listing.select_one(f'h2 a[href="/kitchen/{lang}/feed-photos/"]').find_parent('article')
            check(len(moment.select('[data-photo-open]'))==3,f'Life photo list drives three-image feed {lang}')
            check('Fixture location' in moment.text,f'Life location automatically rendered {lang}')
            album=soup(dest/f'kitchen/{lang}/feed-photos/index.html')
            check(len(album.select('.life-album [data-photo-open]'))==3,f'Life shared photo list drives detail {lang}')
            check(not listing.select('.small-action'),f'Life feed has no read-more step {lang}')
        search_manifest=json.loads((dest/'pagefind/status.json').read_text())
        for col in ['digest','tech']:
            for lang,prefix in [('en',''),('zh','zh/')]:
                archive=soup(dest/prefix/col/'index.html')
                groups=archive.select('.archive-month')
                check([g['id'] for g in groups]==sorted([g['id'] for g in groups],reverse=True),f'{col} fixture cross-year month order {lang}')
                check([g.has_attr('open') for g in groups]==[True]+[False]*(len(groups)-1),f'{col} fixture older months closed {lang}')
                for name,when in [('archive-previous-month',previous_month),('archive-previous-year',previous_year)]:
                    group=archive.find(id='month-'+when[:7])
                    check(group is not None and not group.has_attr('open') and group.select(f'a[href="/{col}/{lang}/{name}/"]'),f'{col} older note in closed month {lang} {name}')
                    check(f'{col}/{lang}/{name}/index.html' in search_manifest['pages'],f'{col} closed month remains searchable {lang} {name}')
                check(archive.find(id='month-1900-01') is None,f'{col} draft-only month excluded {lang}')
        for lang,prefix in [('en',''),('zh','zh/')]:
            updates=soup(dest/prefix/'index.html').select_one('.home-updates')
            check(updates.select_one('.update-digest h3').text.strip()=='RECENT_DIGEST_FIXTURE',f'new digest automatically promoted and title date removed {lang}')
            check(len(updates.select('.update-tech .recent-note'))==2,f'home limits technical notes {lang}')
            check('SAME_DAY_NEWEST_FIXTURE' in updates.text,f'later update on same day is promoted {lang}')
            tech_titles=[h.text.strip() for h in updates.select('.update-tech h3')]
            check(tech_titles==(['ZH_ONLY_RECENT_TECH','SAME_DAY_NEWEST_FIXTURE'] if lang=='zh' else ['SAME_DAY_NEWEST_FIXTURE','RECENT_TECH_FIXTURE']),f'reading day then activity order, independent of filename {lang}')
            check('OLDER_TECH_FIXTURE' not in updates.text,f'old reading date does not jump ahead after update {lang}')
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
