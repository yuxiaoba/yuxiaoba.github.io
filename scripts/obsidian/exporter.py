"""Read-only vault conversion. Only explicitly published notes become owned outputs."""
from __future__ import annotations
import copy, datetime as dt, hashlib, html, json, re, urllib.parse
from dataclasses import dataclass
from pathlib import Path
import yaml
from markdown_it import MarkdownIt
from PIL import Image
from .tags import load_taxonomy, normalize_tags

ROOTS = {'Paper': 'digest', 'Tech Report': 'tech'}
IMAGE_TYPES = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
ID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
MANIFEST = '.sync-state/manifest.json'

class ExportError(ValueError): pass

class StrictLoader(yaml.SafeLoader): pass
StrictLoader.yaml_implicit_resolvers = copy.deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)
for key, rules in StrictLoader.yaml_implicit_resolvers.items():
    StrictLoader.yaml_implicit_resolvers[key] = [(tag, rx) for tag, rx in rules if tag != 'tag:yaml.org,2002:bool']
StrictLoader.add_implicit_resolver('tag:yaml.org,2002:bool', re.compile(r'^(?:true|false)$'), list('tf'))
def unique_mapping(loader, node, deep=False):
    result = {}
    for key, value in node.value:
        k = loader.construct_object(key, deep=deep)
        if not isinstance(k, str) or k in result: raise ExportError('YAML keys must be unique strings')
        result[k] = loader.construct_object(value, deep=deep)
    return result
StrictLoader.add_constructor('tag:yaml.org,2002:map', unique_mapping)

def digest(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def frontmatter(text):
    if not re.match(r'\A---\s*\r?\n', text): return {}, text
    m = re.match(r'\A---\s*\r?\n(.*?)^---\s*\r?\n?', text, re.S | re.M)
    if not m: raise ExportError('Unclosed YAML front matter')
    try: data = yaml.load(m[1], Loader=StrictLoader) or {}
    except (yaml.YAMLError, ValueError) as exc:
        mark = getattr(exc, 'problem_mark', None)
        raise ExportError(f'Invalid YAML{f" at header line {mark.line + 1}" if mark else ""}') from exc
    if not isinstance(data, dict): raise ExportError('Front matter must be a mapping')
    return data, text[m.end():]

def url(value, field, required=False):
    if not value and not required: return None
    if not isinstance(value, str): raise ExportError(f'{field} must be an http(s) URL')
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.password:
        raise ExportError(f'{field} must be an http(s) URL without credentials')
    return value

def heading_slug(value):
    value = re.sub(r'<[^>]+>|[*_`]', '', value).strip().lower()
    value = re.sub(r'[^\w\s-]', '', value).strip()
    slug = re.sub(r'\s+', '-', value) or 'section'
    return 'h-' + (slug if slug.isascii() else hashlib.sha256(slug.encode()).hexdigest()[:12])

def date(value, field):
    if isinstance(value, dt.datetime): raise ExportError(f'{field} requires a date, not a timestamp')
    if isinstance(value, dt.date): return value
    if isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        try: return dt.date.fromisoformat(value)
        except ValueError: pass
    raise ExportError(f'{field} requires a valid YYYY-MM-DD date')

def inside(root: Path, path: Path):
    resolved = path.resolve()
    if not resolved.is_relative_to(root): raise ExportError('Path or symlink escapes the vault')
    return resolved

@dataclass
class Note:
    path: Path
    collection: str
    data: dict
    body: str
    public: bool
    @property
    def output(self):
        name = 'daily-' + self.data['date'].isoformat() if self.collection == 'digest' else self.data['id']
        return f'_{self.collection}/{self.data["lang"]}/obsidian/{name}.md'
    @property
    def page_url(self):
        if self.collection == 'digest': return f'/digest/{self.data["lang"]}/daily/{self.data["date"].isoformat()}/'
        return f'/tech/{self.data["lang"]}/obsidian/{self.data["id"]}/'
    @property
    def web_url(self): return self.page_url + ('#paper-' + self.data['id'] if self.collection == 'digest' else '')
    def heading_id(self, slug): return ('paper-' + self.data['id'] + '-' if self.collection == 'digest' else '') + slug
    @property
    def alias_output(self): return f'digest/{self.data["lang"]}/obsidian/{self.data["id"]}/index.html'


class Exporter:
    def __init__(self, vault: Path, review_file: Path | None = None):
        self.vault = vault.resolve()
        self.scanned_count = 0; self.notes = []; self.files = {}; self.warnings = []; self.errors = []; self.assets = {}
        self.image_reviews = json.loads(review_file.read_text()) if review_file and review_file.exists() else {}
    def warn(self, note, message): self.warnings.append({'source': str(note.path.relative_to(self.vault)), 'message': message})
    def scan(self):
        if not self.vault.is_dir(): raise ExportError('Vault is not readable')
        # Read a complete source tree before computing any removals.
        for folder in ROOTS:
            if not (self.vault/folder).is_dir(): raise ExportError(f'Missing source directory: {folder}; refusing cleanup')
        self.paths = []
        for p in sorted(self.vault.rglob('*')):
            rel = p.relative_to(self.vault)
            if any(part.startswith('.') for part in rel.parts): continue
            if p.is_symlink(): inside(self.vault, p)
            if p.is_file(): self.paths.append(p)
        identities = set()
        for folder, collection in ROOTS.items():
            for p in self.paths:
                if not p.is_relative_to(self.vault/folder) or p.suffix.lower() != '.md': continue
                self.scanned_count += 1
                try:
                    text = p.read_text(encoding='utf-8-sig'); meta, body = frontmatter(text)
                    if 'publish' in meta and type(meta['publish']) is not bool:
                        raise ExportError('publish must be literal true or false, not a string/number/yes/on')
                    public = meta.get('publish') is True
                    note = Note(p, collection, meta, body, public)
                    if public:
                        def clean_public_value(value):
                            if isinstance(value, str):
                                if value.count('%%') % 2: raise ExportError('Unclosed private comment in public metadata')
                                return re.sub(r'%%[\s\S]*?%%', '', value).strip()
                            if isinstance(value, list): return [clean_public_value(v) for v in value]
                            return value
                        for field in ('title','summary','tags','conference','venue','authors','university','organization'):
                            if field in meta: meta[field] = clean_public_value(meta[field])
                        if not isinstance(meta.get('id'), str) or not ID.fullmatch(meta['id']): raise ExportError('Published notes need a stable lowercase id')
                        if not isinstance(meta.get('title'), str) or not meta['title'].strip(): raise ExportError('Published notes need a title')
                        meta['lang'] = meta.get('lang', 'zh')
                        if meta['lang'] not in ('zh', 'en'): raise ExportError('lang must be zh or en')
                        ident = (collection, meta['lang'], meta['id'])
                        if ident in identities: raise ExportError('Duplicate id in the same collection and language')
                        identities.add(ident)
                        day = date(meta.get('date', meta.get('created_date')), 'date/created_date')
                        if 'date' in meta and 'created_date' in meta and day != date(meta['created_date'], 'created_date'):
                            self.warn(note, 'date overrides conflicting created_date')
                        meta['date'] = day
                        tags = meta.get('tags', [])
                        if not isinstance(tags, list) or any(not isinstance(t, str) or not t.strip() for t in tags): raise ExportError('tags must be a list of nonempty strings')
                        meta['tags'], unknown = normalize_tags(tags)
                        if unknown: self.warn(note, 'Tags outside the fixed topic vocabulary were omitted: '+', '.join(unknown))
                        if 'summary' in meta and not isinstance(meta['summary'], str): raise ExportError('summary must be text')
                        meta['source_url'] = url(meta.get('paper_url') if collection == 'digest' else meta.get('source_url'), 'paper_url/source_url', required=True)
                        if meta.get('repo'):
                            try: meta['repo'] = url(meta['repo'], 'repo')
                            except ExportError: self.warn(note, 'repo is not a URL; code link omitted'); meta.pop('repo')
                    self.notes.append(note)
                except (ExportError, OSError, UnicodeError) as exc:
                    self.errors.append({'source': str(p.relative_to(self.vault)), 'message': str(exc)})
        if self.errors: raise ExportError('Source preflight failed; no output changed')
        self.by_path = {n.path.resolve(): n for n in self.notes}
    def resolve(self, note, target, note_link=False):
        target = urllib.parse.unquote(target).replace('\\', '/')
        if '\x00' in target or re.match(r'^[a-z]+:', target, re.I): raise ExportError('Unsupported local reference')
        if target.startswith('/'): raise ExportError('Absolute/traversal reference is not allowed')
        candidate_names = [target]
        if note_link and not Path(target).suffix: candidate_names.append(target + '.md')
        for base in [note.path.parent, self.vault]:
            for name in candidate_names:
                p = base/name; resolved = inside(self.vault, p)
                if p.is_file(): return resolved
        # Only bare filenames have a global filename fallback.
        if '/' not in target:
            candidates = {inside(self.vault, p) for p in self.paths if p.name in candidate_names}
            if len(candidates) > 1: raise ExportError(f'Ambiguous attachment/note name: {target}')
            if candidates: return candidates.pop()
        return None
    def image(self, note, target, alt='', size=None):
        if urllib.parse.urlsplit(target).scheme: raise ExportError('Remote image requires explicit local import')
        p = self.resolve(note, target)
        if not p: raise ExportError(f'Missing image: {target}')
        if p.suffix.lower() not in IMAGE_TYPES: raise ExportError('Unsupported embed; only PNG/JPEG/WebP/GIF images are exported')
        raw = p.read_bytes(); sha = digest(raw)
        try:
            with Image.open(p) as im: width, height = im.size; fmt = im.format; im.verify()
        except Exception as exc: raise ExportError(f'Image cannot be decoded: {target}') from exc
        formats={'.png':'PNG','.jpg':'JPEG','.jpeg':'JPEG','.webp':'WEBP','.gif':'GIF'}
        if fmt != formats[p.suffix.lower()]: raise ExportError('Image extension and format disagree')
        name = re.sub(r'[^a-zA-Z0-9._-]', '-', p.stem).strip('-') or 'image'
        out = f'assets/images/{note.collection}/obsidian/{note.data["id"]}/{name}-{sha[:16]}{p.suffix.lower()}'
        if out in self.files and self.files[out] != raw: raise ExportError('Asset output collision')
        self.files[out] = raw
        self.assets[sha] = {'sha256':sha, 'path':out, 'width':width, 'height':height, 'reviewed':sha in self.image_reviews}
        if sha not in self.image_reviews: self.warn(note, f'New/changed image needs visual review: {sha}')
        attrs = ''
        if size:
            m = re.fullmatch(r'(\d+)(?:x(\d+))?', size)
            if not m: raise ExportError('Image size must be width or widthxheight')
            requested = int(m[1]); attrs = f' width="{min(width, max(1, requested))}"'
            # Height is intentionally not forced: never crop or distort scientific figures.
        source = '/' + out
        return f'<a class="note-image-link" href="{source}" target="_blank" rel="noopener"><img src="{source}" alt="{html.escape(alt or note.data["title"], quote=True)}"{attrs} loading="lazy"></a>'
    def note_link(self, note, target, alias=None):
        base, sep, anchor = target.partition('#')
        if anchor.startswith('^'): raise ExportError('Obsidian block references require manual conversion')
        p = note.path.resolve() if not base else self.resolve(note, base, note_link=True)
        dest = self.by_path.get(p)
        label = alias or base or anchor
        if not dest or not dest.public:
            self.warn(note, 'Unpublished or missing note link kept as visible text only')
            return html.escape(label)
        fragment = ''
        if sep:
            heading = heading_slug(anchor)
            parsed = MarkdownIt('commonmark').parse(re.sub(r'%%[\s\S]*?%%', '', dest.body))
            headings = [heading_slug(parsed[i+1].content) for i,t in enumerate(parsed[:-1]) if t.type == 'heading_open']
            if heading not in headings: raise ExportError('Linked public note has no matching heading')
            fragment = '#' + urllib.parse.quote(dest.heading_id(heading))
        return f'[{label}]({dest.page_url + fragment if sep else dest.web_url})'
    def convert(self, note):
        body = note.body; protected = {}
        prefix = 'OBSIDIANPROTECTED' + digest(body.encode())[:12]
        def save(value):
            key = f'{prefix}X{len(protected)}X'; protected[key] = value; return key
        # Block-token maps protect fenced and indented code before handling Obsidian syntax.
        lines=body.splitlines(keepends=True); offsets=[0]
        for line in lines: offsets.append(offsets[-1]+len(line))
        spans=[]
        for token in MarkdownIt('commonmark').parse(body):
            if token.type in ('fence','code_block') and token.map: spans.append((offsets[token.map[0]],offsets[token.map[1]]))
        for a,b in reversed(spans): body=body[:a]+save(body[a:b])+body[b:]
        body=re.sub(r'(?<!`)(`+)(?!`)([\s\S]*?)(?<!`)\1(?!`)',lambda m:save(m[0]),body)
        if len(re.findall(r'(?<!\\)%%',body))%2: raise ExportError('Unclosed private %% comment')
        body=re.sub(r'(?<!\\)%%[\s\S]*?(?<!\\)%%','',body)
        if re.search(r'(?im)^\s*`{3,}\s*dataview', '\n'.join(protected.values())): raise ExportError('Dataview cannot be exported')
        if re.search(r'(?m)^.*\s\^[\w-]+\s*$',body): raise ExportError('Obsidian block IDs require manual conversion')
        # Reject active HTML, then retain ordinary Markdown and safe static content.
        if re.search(r'<\s*(?:script|iframe|object|embed|style)\b|<[^>]+\son\w+\s*=|javascript\s*:',body,re.I): raise ExportError('Active HTML is not allowed in exported notes')
        for opening,closing in [(r'\(',r'\)'),(r'\[',r'\]')]:
            if body.count(opening)!=body.count(closing): raise ExportError('Unclosed math delimiter')
        if len(re.findall(r'(?<!\\)\$\$',body)) % 2: raise ExportError('Unclosed display math delimiter')
        if re.search(r'<\s*img\b',body,re.I): raise ExportError('HTML image embeds require Markdown or Obsidian image syntax')
        # Normalize all supported math to kramdown's math delimiters; protect it from wiki-link matching.
        body=re.sub(r'\\\[([\s\S]*?)\\\]',lambda m:save('\n\n$$\n'+m[1].strip()+'\n$$\n\n'),body)
        body=re.sub(r'\\\((.*?)\\\)',lambda m:save('$$'+m[1]+'$$'),body,flags=re.S)
        body=re.sub(r'(?<!\\)\$\$([\s\S]*?)(?<!\\)\$\$',lambda m:save(m[0]),body)
        body=re.sub(r'(?<![\\$])\$(?![\s$])([^\n$]*?\S)(?<!\\)\$(?!\$)',lambda m:save('$$'+m[1]+'$$'),body)
        def wiki(m):
            embed=m[1]=='!'; parts=m[2].split('|'); target=parts[0]
            if embed:
                if target.lower().endswith('.md') or not Path(target).suffix: raise ExportError('Note transclusion is not supported')
                size=parts[-1] if len(parts)>1 and re.fullmatch(r'\d+(?:x\d+)?',parts[-1]) else None
                alt=parts[1] if len(parts)>2 or (len(parts)>1 and not size) else ''
                return save(self.image(note,target,alt,size))
            return save(self.note_link(note,target,parts[1] if len(parts)>1 else None))
        body=re.sub(r'(!?)\[\[([^\]\n]+)\]\]',wiki,body)
        def markdown_image(m):
            target=m[2].strip(); target=target[1:-1] if target.startswith('<') and target.endswith('>') else target
            # Optional quoted title after the filename is not part of the path.
            target=re.sub(r'\s+[\"\'][^\n]*[\"\']$','',target)
            return save(self.image(note,target,m[1]))
        body=re.sub(r'!\[([^\]\n]*)\]\((<[^>]+>|[^\n)]*)\)',markdown_image,body)
        # Reference-style images are rejected explicitly rather than leaving a broken reference.
        if re.search(r'!\[[^\]]*\](?:\[|\s*$)',body,re.M): raise ExportError('Reference-style images require inline image syntax')
        def markdown_link(m):
            target=m[2]; parsed=urllib.parse.urlsplit(target)
            if parsed.scheme or target.startswith(('#','/')): return m[0]
            if parsed.path.endswith('.md'):
                return self.note_link(note,parsed.path+('#'+parsed.fragment if parsed.fragment else ''),m[1])
            return m[0]
        body=re.sub(r'(?<!!)\[([^\]\n]+)\]\(([^\s)]+)\)',markdown_link,body)
        body=re.sub(r'(?m)^(\s*>\s*)\[!([^\]]+)\][+-]?\s*([^\n]*)',lambda m:m[1]+'**'+(m[3].strip() or m[2].capitalize())+'**',body)
        body=re.sub(r'\A\s*#\s+[^\n]+\n','',body)
        counts = {}
        def header_id(match):
            slug = heading_slug(match[2]); counts[slug] = counts.get(slug, 0) + 1
            anchor = note.heading_id(slug if counts[slug] == 1 else f'{slug}-{counts[slug]}')
            level = min(6, len(match[1]) + (1 if note.collection == 'digest' else 0))
            return '#' * level + ' ' + match[2] + '\n{: #' + anchor + '}'
        body=re.sub(r'(?m)^(#{1,6})\s+([^\n]+)$',header_id,body)
        # A duplicate H1 is redundant because the site renders front matter title.
        body=re.sub(r'\A\s*#\s+[^\n]+\n','',body)
        for key,value in protected.items(): body=body.replace(key,value)
        # Escape delimiters rather than raw/endraw wrappers, which notes could accidentally close.
        body=body.replace('{{','&#123;&#123;').replace('{%','&#123;%')
        meta={k:note.data[k] for k in ('id','title','date','lang','tags','summary','source_url','conference','venue','year','authors','university','organization','repo') if k in note.data}
        for key in ('conference','venue','university','organization'):
            if key in meta and not isinstance(meta[key],str): raise ExportError(f'{key} must be text')
        if 'authors' in meta and not (isinstance(meta['authors'],str) or isinstance(meta['authors'],list) and all(isinstance(a,str) for a in meta['authors'])): raise ExportError('authors must be text or a list of names')
        if 'year' in meta and not re.fullmatch(r'\d{4}', str(meta['year'])): raise ExportError('year must contain four digits')
        if not meta.get('summary'):
            match=re.search(r'(?m)^#{2,3}\s+[^\n]*(?:核心直觉|一句话)[^\n]*\n(?:\{:[^\n]*\}\n)?\n*([^\n#{][^\n]*)',body)
            if match: meta['summary']=re.sub(r'[*_`]|<[^>]+>','',match[1]).strip()
        def public_text(value):
            if isinstance(value,str):
                if value.count('%%')%2:raise ExportError('Unclosed private comment in public metadata')
                return re.sub(r'%%[\s\S]*?%%','',value).strip()
            if isinstance(value,list):return [public_text(item) for item in value]
            return value
        for field in ('title','summary','conference','venue','authors','university','organization','tags'):
            if field in meta:meta[field]=public_text(meta[field])
        if not meta['title']:raise ExportError('Title is empty after removing private comments')
        meta.update(published=True,source_type='paper' if note.collection=='digest' else 'tech',layout='article')
        return ('---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False,width=1000)+'---\n\n'+body.strip()+'\n').encode()
    def daily_digest(self, notes, converted):
        notes = sorted(notes, key=lambda n: n.data['id'])
        day = notes[0].data['date']; lang = notes[0].data['lang']; count = len(notes)
        title = (f'{day.year}年{day.month}月{day.day}日 · 论文阅读' if lang == 'zh' else f'Paper Digest · {day.isoformat()}')
        metadata = {'id':'daily-'+day.isoformat(),'title':title,'date':day,'lang':lang,'published':True,
                    'source_type':'paper','layout':'article','permalink':notes[0].page_url,'daily_digest':True,
                    'paper_count':count,'paper_ids':[n.data['id'] for n in notes],
                    'summary':f'本日整理 {count} 篇论文阅读笔记。' if lang=='zh' else f'{count} paper reading notes for this day.',
                    'tags':[],
                    'daily_papers':[]}
        sections=[]
        for index,note in enumerate(notes,1):
            meta,body=frontmatter(converted[note.data['id']].decode())
            for tag in meta.get('tags',[]):
                if tag and tag not in metadata['tags']:metadata['tags'].append(tag)
            metadata['daily_papers'].append({'id':note.data['id'],'title':meta['title'],'tags':meta.get('tags',[])})
            heading=f'<h2 id="paper-{note.data["id"]}" class="daily-paper-title" data-pagefind-weight="3"><span class="paper-number">{index:02d}</span> {html.escape(meta["title"])}</h2>'
            source_label='原文' if lang=='zh' else 'Original paper'
            links=f'<a href="{html.escape(meta["source_url"],quote=True)}">{source_label} ↗</a>'
            if meta.get('repo'): links+=f' · <a href="{html.escape(meta["repo"],quote=True)}">'+('代码' if lang=='zh' else 'Code')+' ↗</a>'
            venue=' '.join(str(v) for v in [meta.get('conference') or meta.get('venue'),meta.get('year')] if v)
            if venue:links+=' · '+html.escape(venue)
            labels={item['id']:item[lang] for item in load_taxonomy()[0]}
            tags=''.join('<span>'+html.escape(labels[tag])+'</span>' for tag in meta.get('tags',[]))
            intro='<p class="daily-paper-summary">'+html.escape(meta['summary'])+'</p>' if meta.get('summary') else ''
            sections.append(heading+'\n\n<p class="daily-paper-source">'+links+'</p>\n\n'+intro+'\n\n<div class="daily-paper-tags">'+tags+'</div>\n\n'+body.strip())
        body='\n\n'.join(sections).replace('{{','&#123;&#123;').replace('{%','&#123;%')
        return ('---\n'+yaml.safe_dump(metadata,allow_unicode=True,sort_keys=False,width=1000)+'---\n\n'+body+'\n').encode()
    def redirect(self,note,converted):
        meta,_=frontmatter(converted.decode())
        target=html.escape(note.web_url,quote=True)
        label='前往当天论文阅读' if note.data['lang']=='zh' else 'Open this day’s Paper Digest'
        return (f'<!doctype html><html lang="{note.data["lang"]}"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
                f'<meta http-equiv="refresh" content="0;url={target}"><link rel="canonical" href="{html.escape(note.page_url,quote=True)}">'
                f'<title>{html.escape(meta["title"])}</title></head><body data-pagefind-ignore="all"><a href="{target}">{label}</a></body></html>').encode()
    def run(self):
        self.scan(); groups={}; converted={}
        for note in self.notes:
            if not note.public: continue
            try:
                output=self.convert(note)
                if note.collection=='digest':
                    key=(note.data['lang'],note.data['date']);groups.setdefault(key,[]).append(note)
                    converted[(key,note.data['id'])]=output
                    self.files[note.alias_output]=self.redirect(note,output)
                else:self.files[note.output]=output
            except (ExportError,OSError) as exc:self.errors.append({'source':str(note.path.relative_to(self.vault)),'message':str(exc)})
        if self.errors: raise ExportError('Conversion failed; no output changed')
        for key,notes in sorted(groups.items()):
            self.files[notes[0].output]=self.daily_digest(notes,{n.data['id']:converted[(key,n.data['id'])] for n in notes})
        return self.files
    def report(self):
        return {'notes_scanned':self.scanned_count,'notes_parsed':len(self.notes),'published':sum(n.public for n in self.notes),'daily_digests':len({(n.data['lang'],n.data['date']) for n in self.notes if n.public and n.collection=='digest'}),'errors':self.errors,'warnings':self.warnings,'assets':list(self.assets.values())}

def owned(path):
    return bool(re.fullmatch(r'digest/(zh|en)/obsidian/[a-z0-9-]+/index\.html',path) or re.fullmatch(r'_(digest|tech)/(zh|en)/obsidian/[a-z0-9-]+\.md',path) or re.fullmatch(r'assets/images/(digest|tech)/obsidian/[a-z0-9-]+/[a-zA-Z0-9._-]+',path))

def plan_changes(site:Path,files:dict):
    manifest=inside(site.resolve(),site/MANIFEST)
    old=json.loads(manifest.read_text()) if manifest.exists() else {'version':1,'outputs':{}}
    if old.get('version')!=1 or not isinstance(old.get('outputs'),dict):raise ExportError('Unsupported ownership manifest')
    for path,sha in old['outputs'].items():
        if not owned(path): raise ExportError('Manifest contains a path outside owned areas')
        p=inside(site.resolve(),site/path)
        if not p.is_file() or digest(p.read_bytes())!=sha: raise ExportError(f'Managed file was changed outside the exporter: {path}')
    for path in files:
        if not owned(path):raise ExportError('Exporter attempted an unowned output')
        p=inside(site.resolve(),site/path)
        if p.exists() and path not in old['outputs']:raise ExportError(f'Will not overwrite an unmanaged file: {path}')
    # A manually maintained article may deliberately reuse an exported image.
    # Keep those assets until no hand-written source references them.
    effective=dict(files)
    candidates=[name for name in old['outputs'] if name.startswith('assets/images/') and name not in effective]
    if candidates:
        manual=[]
        for directory in [site/'_digest',site/'_tech',site/'_kitchen',site/'_pages',site/'_includes',site/'_layouts',site/'_data']:
            if directory.exists():
                for path in directory.rglob('*'):
                    if path.is_file() and path.suffix in ('.md','.html','.yml','.yaml') and str(path.relative_to(site)) not in old['outputs']:
                        manual.append(path.read_text())
        manual.extend(p.read_text() for p in site.glob('*.html'))
        for name in candidates:
            if any(name in text for text in manual):effective[name]=(site/name).read_bytes()
    new={'version':1,'outputs':{p:digest(b) for p,b in sorted(effective.items())}}
    return old,new,{'write':[p for p,h in new['outputs'].items() if old['outputs'].get(p)!=h], 'remove':[p for p in old['outputs'] if p not in effective]}

def apply_files(site:Path,files:dict):
    """Apply only to an isolated candidate. The runner promotes it after full validation."""
    old,new,changes=plan_changes(site,files)
    for name in changes['remove']: (site/name).unlink()
    for name in changes['write']:
        p=site/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(files[name])
    if old!=new:
        p=site/MANIFEST;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(new,indent=2)+'\n')
    return changes
