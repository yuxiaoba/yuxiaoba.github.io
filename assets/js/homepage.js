'use strict';
if (new URLSearchParams(window.location.search).get('translation') === 'missing') {
  const notice = document.querySelector('[data-translation-notice]');
  if (notice) notice.hidden = false;
}

// Keep the year sidebar in step with both anchor navigation and ordinary scrolling.
const yearLinks = [...document.querySelectorAll('.year-navigation a')];
if (yearLinks.length) {
  const sections = yearLinks.map(link => document.getElementById(link.hash.slice(1)));
  let pending = false;
  const updateYear = () => {
    let current = 0;
    sections.forEach((section, index) => {
      if (section && section.getBoundingClientRect().top <= 110) current = index;
    });
    yearLinks.forEach((link, index) => {
      if (index === current) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    pending = false;
  };
  const scheduleUpdate = () => {
    if (!pending) { pending = true; requestAnimationFrame(updateYear); }
  };
  window.addEventListener('scroll', scheduleUpdate, { passive: true });
  window.addEventListener('resize', scheduleUpdate);
  window.addEventListener('load', updateYear);
  updateYear();
}

// Daily editions pair by date; a link into one paper retains per-paper translation rules.
const dailyContents = document.querySelector('[data-daily-papers]');
if (dailyContents) {
  const ids = dailyContents.dataset.dailyPapers.split(',').sort((a,b)=>b.length-a.length);
  const updateDailyLanguage = () => {
    const hash = decodeURIComponent(location.hash);
    const id = ids.find(value => hash === '#paper-'+value || hash.startsWith('#paper-'+value+'-h-'));
    document.querySelectorAll('[data-daily-language]').forEach(link => {
      if (!id) { link.href = link.dataset.dayUrl; return; }
      link.href = link.dataset.dailyIds.split(',').includes(id)
        ? link.dataset.dayUrl.split('#')[0]+'#paper-'+id
        : link.dataset.missingUrl;
    });
  };
  window.addEventListener('hashchange',updateDailyLanguage);
  updateDailyLanguage();
}

// Active paper scrollspy in the sticky daily table of contents.
const dailyToc = document.querySelector('.daily-toc');
const dailyLinks = dailyToc ? [...dailyToc.querySelectorAll('a[href^="#paper-"]')] : [];
if (dailyLinks.length) {
  const sections = dailyLinks.map(link => {
    try { return document.getElementById(decodeURIComponent(link.hash.slice(1))); }
    catch { return null; }
  });
  let tocPending = false;
  const updateDailyToc = () => {
    let current = 0;
    sections.forEach((section, index) => {
      if (section && section.getBoundingClientRect().top <= 130) current = index;
    });
    dailyLinks.forEach((link, index) => {
      if (index === current) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    const active = dailyLinks[current];
    if (active && dailyToc.scrollHeight > dailyToc.clientHeight) {
      const tocBox = dailyToc.getBoundingClientRect();
      const linkBox = active.getBoundingClientRect();
      if (linkBox.top < tocBox.top || linkBox.bottom > tocBox.bottom) {
        active.scrollIntoView({ block: 'nearest' });
      }
    }
    tocPending = false;
  };
  const scheduleDailyToc = () => {
    if (!tocPending) { tocPending = true; requestAnimationFrame(updateDailyToc); }
  };
  window.addEventListener('scroll', scheduleDailyToc, { passive: true });
  window.addEventListener('resize', scheduleDailyToc, { passive: true });
  window.addEventListener('load', updateDailyToc);
  updateDailyToc();
}

// Press '/' on archive or search pages to jump cleanly into search input.
const quickSearch = document.querySelector('.note-search input[name="q"]');
if (quickSearch) {
  document.addEventListener('keydown', event => {
    if (event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey) return;
    const target = event.target;
    if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT' || target.isContentEditable)) return;
    event.preventDefault();
    quickSearch.focus();
  });
}

// Progressive code-copy buttons inside article bodies without unsafe DOM sinks.
const articleBody = document.querySelector('.article-body');
if (articleBody) {
  const zh = document.documentElement.lang.startsWith('zh');
  articleBody.querySelectorAll('pre').forEach(pre => {
    if (pre.closest('.code-block')) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'code-block';
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'code-copy-btn';
    btn.setAttribute('data-pagefind-ignore', '');
    const label = zh ? '复制' : 'Copy';
    btn.textContent = label;
    btn.setAttribute('aria-label', zh ? '复制代码' : 'Copy code');
    let resetTimer = 0;
    btn.addEventListener('click', () => {
      const source = pre.querySelector('code') || pre;
      const text = source.textContent || '';
      if (!navigator.clipboard || !navigator.clipboard.writeText) return;
      navigator.clipboard.writeText(text).then(() => {
        clearTimeout(resetTimer);
        btn.textContent = zh ? '已复制 ✓' : 'Copied ✓';
        btn.dataset.copied = 'true';
        resetTimer = window.setTimeout(() => {
          btn.textContent = label;
          delete btn.dataset.copied;
        }, 1600);
      }).catch(() => {});
    });
    pre.before(wrapper);
    wrapper.append(pre, btn);
  });
}
