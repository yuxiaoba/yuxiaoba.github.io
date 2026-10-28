(() => {
  'use strict';
  const controls = document.querySelector('[data-metrics-preference]');
  if (!controls) return;
  const zh = controls.dataset.lang === 'zh';
  const status = document.querySelector('[data-metrics-status]');
  const key = 'gy-reading-metrics-disabled';
  function show() {
    try {
      const disabled = localStorage.getItem(key) === '1';
      const signal = navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true;
      status.textContent = disabled ? (zh ? '此浏览器的统计已关闭。' : 'Analytics is disabled in this browser.') : signal ?
        (zh ? '浏览器已发送隐私信号，不会统计。' : 'Your browser privacy signal prevents collection.') :
        (zh ? '此浏览器允许文章访问统计；统计功能启用后生效。' : 'This browser allows article analytics when collection is enabled.');
    } catch (_) { status.textContent = zh ? '无法保存偏好；为保护你的选择，此浏览器不会发送统计。' : 'Preferences cannot be stored; this browser will not send analytics.'; }
  }
  controls.addEventListener('click', event => {
    if (!event.target.matches('[data-metrics-off],[data-metrics-on]')) return;
    try { localStorage.setItem(key, event.target.matches('[data-metrics-off]') ? '1' : '0'); } catch (_) {}
    show();
  });
  show();
})();
