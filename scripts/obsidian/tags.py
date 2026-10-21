"""A small shared topic vocabulary for generated notes and search filters."""
import re
from pathlib import Path
import yaml

DEFAULT = Path(__file__).resolve().parents[2] / '_data/note_tags.yml'

def load_taxonomy(path=DEFAULT):
    items = yaml.safe_load(Path(path).read_text())
    if not isinstance(items, list) or not 1 <= len(items) <= 10:
        raise ValueError('Note topics must contain between 1 and 10 categories')
    seen = set(); aliases = {}
    for item in items:
        ident = item.get('id') if isinstance(item, dict) else None
        if not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in seen:
            raise ValueError('Note topic IDs must be unique lowercase slugs')
        seen.add(ident)
        if any(not isinstance(item.get(lang), str) or not item[lang].strip() for lang in ('zh', 'en')):
            raise ValueError('Every note topic needs Chinese and English labels')
        extra = item.get('aliases', [])
        if not isinstance(extra, list) or any(not isinstance(value, str) or not value.strip() for value in extra):
            raise ValueError('Topic aliases must be nonempty strings')
        for value in [ident, item['zh'], item['en'], *extra]:
            key = value.strip().casefold()
            if key in aliases and aliases[key] != ident:
                raise ValueError('Topic aliases cannot refer to different categories')
            aliases[key] = ident
    return items, aliases

def normalize_tags(values, taxonomy=None):
    items, aliases = taxonomy or load_taxonomy()
    selected = set(); unknown = []
    for value in values:
        ident = aliases.get(value.strip().casefold())
        if ident: selected.add(ident)
        elif value not in unknown: unknown.append(value)
    return [item['id'] for item in items if item['id'] in selected], unknown
