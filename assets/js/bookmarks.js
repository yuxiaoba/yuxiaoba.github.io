/* Private, browser-local reading bookmarks. No data is sent to a server. */
(() => {
  'use strict';
  const zh = document.documentElement.lang === 'zh';
  const t = zh ? {
    save: '收藏', saved: '已收藏', article: '收藏本文', paper: '收藏这篇论文', section: '收藏这节', reading: '收藏这条阅读', excerpt: '保存摘录',
    title: '我的收藏', empty: '还没有收藏。阅读时点击书签，或选中文字保存摘录。',
    open: '回到原文', remove: '取消收藏', error: '无法保存收藏，请检查浏览器的存储设置或先导出备份。',
    added: '已保存到我的收藏', removed: '已取消收藏', tooLong: '请选取不超过 6,000 字符的摘录。',
    invalid: '备份格式无效，原有收藏未改动。', imported: '已合并导入收藏', full: '收藏容量已满，请先导出并整理。',
    kinds: {article: '整篇笔记', paper: '论文', section: '延伸阅读', excerpt: '摘录'}, selection: '选中文字后可保存摘录',
    exportEmpty: '目前没有可导出的收藏。', count: n => `${n} 条收藏`
  } : {
    save: 'Save', saved: 'Saved', article: 'Save article', paper: 'Save this paper', section: 'Save section', reading: 'Save reading', excerpt: 'Save excerpt',
    title: 'Saved notes', empty: 'No bookmarks yet. Use the bookmark button or select text while reading.',
    open: 'Back to source', remove: 'Remove', error: 'Unable to save. Check browser storage settings or export a backup first.',
    added: 'Added to saved notes', removed: 'Bookmark removed', tooLong: 'Select an excerpt of up to 6,000 characters.',
    invalid: 'Invalid backup. Existing bookmarks were not changed.', imported: 'Bookmarks merged', full: 'Bookmark storage is full. Export and organize your collection first.',
    kinds: {article: 'Article', paper: 'Paper', section: 'Further reading', excerpt: 'Excerpt'}, selection: 'Select text to save an excerpt',
    exportEmpty: 'There are no bookmarks to export.', count: n => `${n} saved items`
  };
  const key = 'gy-reading-bookmarks-v1';
  const icon = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 3h12v18l-6-4-6 4Z"/></svg>';
  const status = document.createElement('p');
  status.className = 'bookmark-status'; status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
  document.body.append(status);
  let timer;
  const announce = message => { status.textContent = message; clearTimeout(timer); timer = setTimeout(() => {status.textContent = '';}, 6000); };
  const validUrl = value => typeof value === 'string' && value.length < 2000 &&
    /^\/(digest|tech)\/(zh|en)\/[a-zA-Z0-9/_-]+\/(?:#[^\s<>"\\]*)?$/.test(value);
  const validate = items => {
    if (!Array.isArray(items) || items.length > 1000) throw new Error(t.invalid);
    return items.map(item => {
      if (!item || !['article','paper','section','excerpt'].includes(item.kind) || !['zh','en'].includes(item.lang) ||
          !validUrl(item.url) || typeof item.title !== 'string' || !item.title.trim() || item.title.length > 600 ||
          typeof item.excerpt !== 'string' || item.excerpt.length > 6000 ||
          typeof item.section !== 'string' || item.section.length > 600 ||
          typeof item.savedAt !== 'string' || !Number.isFinite(Date.parse(item.savedAt)) ||
          (item.kind === 'excerpt' && !item.excerpt.trim())) throw new Error(t.invalid);
      return {kind:item.kind, lang:item.lang, url:item.url, title:item.title, section:item.section, excerpt:item.excerpt, savedAt:item.savedAt};
    });
  };
  const identity = item => JSON.stringify([item.kind,item.url,item.excerpt]);
  const read = () => {
    const raw = localStorage.getItem(key);
    if (!raw) return [];
    const data = JSON.parse(raw);
    if (data.version !== 1) throw new Error(t.invalid);
    return validate(data.items);
  };
  const write = items => {
    if (items.length > 1000) throw new Error(t.full);
    const data = JSON.stringify({version:1, items:validate(items)});
    if (new Blob([data]).size > 2*1024*1024) throw new Error(t.full);
    localStorage.setItem(key, data);
    refresh();
  };
  const button = (label, action) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'bookmark-button';
    b.innerHTML = icon; const span = document.createElement('span'); span.textContent = label; b.append(span);
    b.addEventListener('click', action); return b;
  };
  const toggles = [];
  const toggle = (item, label, compact=false) => {
    const b = button(label, () => {
      try {
        const items = read(); const found = items.some(x => identity(x) === identity(item));
        write(found ? items.filter(x => identity(x) !== identity(item)) : [{...item,savedAt:new Date().toISOString()},...items]);
        announce(found ? t.removed : t.added);
      } catch (error) {announce(error.message === t.full ? t.full : t.error);}
    });
    if (compact) b.classList.add('bookmark-paper-button');
    b.setAttribute('data-pagefind-ignore',''); toggles.push({b,item,label}); return b;
  };
  const article = document.querySelector('[data-bookmark-article]');
  let selected = null;
  let selectionPanel;
  if (article) {
    const body = article.querySelector('.article-body');
    const title = article.querySelector('h1').textContent.trim();
    const base = {kind:'article',lang:zh?'zh':'en',url:location.pathname,title,section:'',excerpt:''};
    const actions = document.createElement('div'); actions.className = 'bookmark-article-actions'; actions.setAttribute('data-pagefind-ignore','');
    actions.append(toggle(base,t.article));
    const hint = document.createElement('span'); hint.textContent = t.selection; actions.append(hint);
    article.querySelector('.article-header').append(actions);
    body.querySelectorAll('.daily-paper-title[id]').forEach(heading => {
      const wrapper = document.createElement('div'); wrapper.className = 'bookmark-paper-action'; wrapper.setAttribute('data-pagefind-ignore','');
      wrapper.append(toggle({...base,kind:'paper',url:location.pathname+'#'+encodeURIComponent(heading.id),section:heading.textContent.trim()},t.paper,true));
      heading.after(wrapper);
    });
    // Further-reading sections use ordinary Markdown headings, not paper titles.
    let furtherReading = false;
    body.querySelectorAll('h2,h3').forEach((heading, index) => {
      if (heading.tagName === 'H2') furtherReading = /^(further reading\b|延伸阅读)/i.test(heading.textContent.trim());
      if (!furtherReading || heading.classList.contains('daily-paper-title')) return;
      if (!heading.id) heading.id = 'reading-section-' + (index + 1);
      const wrapper = document.createElement('div'); wrapper.className = 'bookmark-paper-action'; wrapper.setAttribute('data-pagefind-ignore','');
      wrapper.append(toggle({...base,kind:'section',url:location.pathname+'#'+encodeURIComponent(heading.id),section:heading.textContent.trim()},heading.tagName==='H2'?t.section:t.reading,true));
      heading.after(wrapper);
    });
    selectionPanel = document.createElement('div'); selectionPanel.className = 'bookmark-selection'; selectionPanel.hidden = true;
    const save = button(t.excerpt, () => {
      if (!selected) return;
      if (selected.excerpt.length > 6000) {announce(t.tooLong);return;}
      try {
        const items = read();
        if (!items.some(x => identity(x) === identity(selected))) write([{...selected,savedAt:new Date().toISOString()},...items]);
        announce(t.added); selected = null; selectionPanel.hidden = true;
      } catch (error) {announce(error.message === t.full ? t.full : t.error);}
    });
    // Prevent pointer activation from clearing the selection before it is saved.
    save.addEventListener('pointerdown', event => {if (event.pointerType === 'mouse') event.preventDefault();});
    selectionPanel.append(save); document.querySelector('.personal-site').append(selectionPanel);
    const capture = () => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed || !selection.rangeCount) {
        if (!selectionPanel.contains(document.activeElement)) {selectionPanel.hidden=true;selected=null;}
        return;
      }
      const range = selection.getRangeAt(0);
      if (!body.contains(range.startContainer) || !body.contains(range.endContainer)) {selectionPanel.hidden=true;selected=null;return;}
      const text = selection.toString().trim();
      if (!text) return;
      let heading = null;
      for (const candidate of body.querySelectorAll('h2,h3,h4')) {
        const position = candidate.compareDocumentPosition(range.startContainer);
        if (candidate.contains(range.startContainer) || position & Node.DOCUMENT_POSITION_FOLLOWING) heading = candidate;
      }
      selected = {...base,kind:'excerpt',excerpt:text,section:heading?.textContent.trim() || '',
        url:location.pathname+(heading?.id ? '#'+encodeURIComponent(heading.id) : '')};
      selectionPanel.hidden=false;
    };
    document.addEventListener('selectionchange', () => setTimeout(capture, 80));
    document.addEventListener('keydown', event => {if (event.key === 'Escape') {selected=null;selectionPanel.hidden=true;}});
    document.addEventListener('pointerdown', event => {
      if (!body.contains(event.target) && !selectionPanel.contains(event.target)) {selected=null;selectionPanel.hidden=true;}
    });
  }
  const shelf = document.querySelector('[data-bookmark-shelf]');
  const list = shelf?.querySelector('[data-bookmark-list]');
  const render = items => {
    if (!list) return;
    list.replaceChildren();
    shelf.querySelector('[data-bookmark-count]').textContent = t.count(items.length);
    if (!items.length) {const p=document.createElement('p');p.className='bookmarks-empty';p.textContent=t.empty;list.append(p);return;}
    [...items].sort((a,b) => Date.parse(b.savedAt)-Date.parse(a.savedAt)).forEach(item => {
      const li = document.createElement('li'); li.className = 'saved-note';
      const meta = document.createElement('p'); meta.className = 'saved-note-meta';
      meta.textContent = t.kinds[item.kind]+' · '+(item.lang==='zh'?'中文':'EN')+' · '+new Date(item.savedAt).toLocaleDateString(zh?'zh-CN':'en-GB');
      const h = document.createElement('h2');const link = document.createElement('a');link.href=item.url;link.textContent=item.section || item.title;h.append(link);
      li.append(meta,h);
      if (item.section) {const context=document.createElement('p');context.className='saved-note-context';context.textContent=item.title;li.append(context);}
      if (item.excerpt) {const quote=document.createElement('blockquote');quote.textContent=item.excerpt;li.append(quote);}
      const controls = document.createElement('div'); controls.className = 'saved-note-controls';
      const source = document.createElement('a');source.href=item.url;source.textContent=t.open;
      const remove = document.createElement('button');remove.type='button';remove.textContent=t.remove;
      remove.addEventListener('click', () => {
        try {const next=li.nextElementSibling || li.previousElementSibling;const nextHref=next?.querySelector('h2 a')?.getAttribute('href');write(read().filter(x => identity(x)!==identity(item)));announce(t.removed);
          const target=[...list.querySelectorAll('h2 a')].find(a=>a.getAttribute('href')===nextHref);(target || shelf.querySelector('[data-bookmark-export]')).focus();
        } catch (_) {announce(t.error);}
      });
      controls.append(source,remove);li.append(controls);list.append(li);
    });
  };
  function refresh() {
    try {
      const items=read();
      toggles.forEach(({b,item,label}) => {
        const saved=items.some(x => identity(x)===identity(item));
        b.setAttribute('aria-pressed',String(saved));b.querySelector('span').textContent=saved?t.saved:label;
        b.setAttribute('aria-label',(saved?t.saved:label)+(item.section?' · '+item.section:''));
      });
      render(items);
    } catch (_) {
      if (list) {list.replaceChildren();const p=document.createElement('p');p.textContent=t.error;list.append(p);}
      announce(t.error);
    }
  }
  if (shelf) {
    shelf.querySelector('[data-bookmark-export]').addEventListener('click', () => {
      try {
        const items=read();if (!items.length) {announce(t.exportEmpty);return;}
        const url=URL.createObjectURL(new Blob([JSON.stringify({version:1,items},null,2)],{type:'application/json'}));
        const a=document.createElement('a');a.href=url;a.download='reading-bookmarks-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
      } catch (_) {announce(t.error);}
    });
    const input=shelf.querySelector('[data-bookmark-file]');
    shelf.querySelector('[data-bookmark-import]').addEventListener('click',()=>input.click());
    input.addEventListener('change', async () => {
      const file=input.files[0];if (!file) return;
      try {
        if (file.size>2*1024*1024) throw new Error(t.invalid);
        const data=JSON.parse(await file.text());if (data.version!==1) throw new Error(t.invalid);
        const imported=validate(data.items);const merged=new Map(read().map(item=>[identity(item),item]));
        imported.forEach(item=>{if (!merged.has(identity(item))) merged.set(identity(item),item);});
        write([...merged.values()]);announce(t.imported);
      } catch (error) {announce(error.message===t.full?t.full:t.invalid);}
      input.value='';
    });
  }
  window.addEventListener('storage',event=>{if (event.key===key || event.key===null) refresh();});
  refresh();
})();
