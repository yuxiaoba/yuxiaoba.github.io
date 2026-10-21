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
      if (section && section.getBoundingClientRect().top <= 80) current = index;
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
