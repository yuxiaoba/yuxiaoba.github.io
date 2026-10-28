/* Progressive enhancement: headings, tables and original-image links work without JS. */
(() => {
  const reader = document.querySelector('[data-tech-reader]');
  if (!reader) return;
  const body = reader.querySelector('.article-body');
  const zh = document.documentElement.lang.startsWith('zh');
  const mobile = () => window.matchMedia('(max-width:600px)').matches;
  const headings = [...body.querySelectorAll('h2, h3')];
  if (headings.length) {
    const toc = document.createElement('details');
    toc.className = 'tech-toc';
    toc.setAttribute('data-pagefind-ignore', '');
    toc.open = !mobile();
    const summary = document.createElement('summary');
    summary.textContent = zh ? `本文目录 · ${headings.length} 节` : `Contents · ${headings.length} sections`;
    const nav = document.createElement('nav');
    nav.setAttribute('aria-label', zh ? '本文目录' : 'Article contents');
    const list = document.createElement('ol');
    headings.forEach((heading, index) => {
      if (!heading.id) heading.id = `tech-section-${index + 1}`;
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = '#' + encodeURIComponent(heading.id);
      link.textContent = heading.textContent;
      link.addEventListener('click', () => {
        if (mobile()) toc.open = false;
        heading.tabIndex = -1;
        // Move keyboard focus to content without changing the native anchor navigation.
        requestAnimationFrame(() => heading.focus({preventScroll: true}));
      });
      item.append(link); list.append(item);
    });
    nav.append(list); toc.append(summary, nav); body.before(toc);
  }

  const tables = [...body.querySelectorAll('table')].map(table => {
    const region = document.createElement('div');
    region.className = 'tech-table-scroll';
    region.setAttribute('role', 'region');
    region.setAttribute('aria-label', zh ? '数据表，可横向滚动' : 'Data table, horizontally scrollable');
    const hint = document.createElement('p');
    hint.className = 'tech-table-hint';
    hint.setAttribute('data-pagefind-ignore', '');
    hint.textContent = zh ? '左右滑动查看完整表格' : 'Scroll sideways to view the full table';
    table.before(region); region.append(table); region.after(hint);
    return {region, hint};
  });
  const updateTables = () => tables.forEach(({region, hint}) => {
    const scrollable = region.scrollWidth > region.clientWidth + 1;
    hint.hidden = !scrollable;
    region.tabIndex = scrollable ? 0 : -1;
  });
  updateTables();
  window.addEventListener('resize', updateTables, {passive: true});

  if (!('HTMLDialogElement' in window)) return;
  const dialog = document.createElement('dialog');
  dialog.className = 'tech-image-dialog';
  dialog.setAttribute('aria-labelledby', 'tech-image-title');
  const toolbar = document.createElement('div'); toolbar.className = 'tech-image-toolbar';
  const zoom = document.createElement('button'); zoom.type = 'button';
  const close = document.createElement('button'); close.type = 'button'; close.textContent = zh ? '关闭' : 'Close';
  close.setAttribute('aria-label', zh ? '关闭大图' : 'Close image');
  const title = document.createElement('p'); title.id = 'tech-image-title'; title.className = 'tech-image-title';
  const viewport = document.createElement('div'); viewport.className = 'tech-image-viewport'; viewport.tabIndex = 0;
  viewport.setAttribute('aria-label', zh ? '放大后可上下左右滑动图片' : 'Pan the enlarged image');
  const image = document.createElement('img'); viewport.append(image);
  toolbar.append(zoom, close); dialog.append(toolbar, title, viewport); document.body.append(dialog);
  let trigger, previousOverflow = '';
  const setZoom = expanded => {
    dialog.toggleAttribute('data-zoomed', expanded);
    image.style.width = expanded && image.naturalWidth ? image.naturalWidth + 'px' : '';
    zoom.textContent = expanded ? (zh ? '适应屏幕' : 'Fit to screen') : (zh ? '放大查看' : 'Zoom in');
    zoom.setAttribute('aria-pressed', String(expanded));
    viewport.scrollTo(0, 0);
  };
  zoom.addEventListener('click', () => setZoom(!dialog.hasAttribute('data-zoomed')));
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    const box = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow;
    trigger?.focus({preventScroll: true});
  });
  body.querySelectorAll('.note-image-link').forEach(link => {
    link.setAttribute('aria-haspopup', 'dialog');
    const label = link.querySelector('.note-image-action');
    if (label) label.textContent = zh ? '点击放大' : 'Enlarge image';
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); trigger = link;
      const original = link.querySelector('img');
      image.src = original.currentSrc || original.src; image.alt = original.alt; title.textContent = original.alt;
      setZoom(false); previousOverflow = document.body.style.overflow; document.body.style.overflow = 'hidden';
      dialog.showModal(); close.focus();
    });
  });
})();
