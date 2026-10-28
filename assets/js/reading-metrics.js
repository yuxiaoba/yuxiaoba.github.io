(() => {
  'use strict';
  const script = document.querySelector('script[data-reading-metrics]');
  const disabled = 'gy-reading-metrics-disabled';
  if (!script || location.origin !== 'https://yuxiaoba.github.io' || window.top !== window.self) return;
  const path = script.dataset.path;
  if (!/^\/(digest|tech)\/(zh|en)\/[a-zA-Z0-9/._-]+\/$/.test(path)) return;
  let endpoint;
  try {
    endpoint = new URL(script.dataset.endpoint);
    if (endpoint.protocol !== 'https:' || endpoint.username || endpoint.password || endpoint.pathname !== '/api/count') return;
  } catch (_) { return; }
  const display = document.querySelector('[data-article-views]');
  function refreshViews() {
    if (!display) return;
    const url = new URL('/api/views', endpoint); url.searchParams.set('path', path);
    const controller = new AbortController(); const timeout = setTimeout(() => controller.abort(), 3000);
    fetch(url.href, {mode: 'cors', credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer', signal: controller.signal})
      .then(response => response.ok ? response.json() : null)
      .then(data => { if (data && Number.isSafeInteger(data.views) && data.views >= 0) display.textContent = data.views.toLocaleString(document.documentElement.lang); })
      .catch(() => {}).finally(() => clearTimeout(timeout));
  }
  let skip = navigator.webdriver || navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true;
  try { skip = skip || localStorage.getItem(disabled) === '1'; } catch (_) { skip = true; }
  if (skip) { refreshViews(); return; }
  let counted = false;
  function count() {
    if (counted || document.visibilityState !== 'visible' || document.prerendering) return;
    try { if (localStorage.getItem(disabled) === '1') return; } catch (_) { return; }
    if (!window.crypto || !crypto.getRandomValues) return;
    counted = true;
    const event = Array.from(crypto.getRandomValues(new Uint8Array(16)), b => b.toString(16).padStart(2, '0')).join('');
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);
    fetch(endpoint.href, {
      method: 'POST', mode: 'cors', credentials: 'omit', cache: 'no-store', keepalive: true,
      referrerPolicy: 'no-referrer', signal: controller.signal,
      headers: {'Content-Type': 'application/json'}, body: JSON.stringify({path, event})
    }).catch(() => {}).finally(() => { clearTimeout(timeout); refreshViews(); });
  }
  document.addEventListener('visibilitychange', count);
  document.addEventListener('prerenderingchange', count);
  window.addEventListener('pageshow', event => { if (event.persisted) counted = false; count(); });
  count();
})();
