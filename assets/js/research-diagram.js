(() => {
  'use strict';
  document.querySelectorAll('[data-research-diagram]').forEach(diagram => {
    const nodes = [...diagram.querySelectorAll('[data-direction]')];
    const caption = diagram.querySelector('[data-research-caption]');
    const original = caption.textContent;
    let selected = null;
    const showCaption = node => { caption.textContent = node ? node.dataset.caption : original; };
    nodes.forEach(node => {
      node.disabled = false;
      node.addEventListener('click', () => {
        selected = selected === node ? null : node;
        nodes.forEach(item => item.setAttribute('aria-pressed', String(item === selected)));
        diagram.dataset.active = selected ? selected.dataset.direction : '';
        showCaption(selected);
      });
      node.addEventListener('pointerenter', event => {
        if (event.pointerType !== 'mouse') return;
        diagram.dataset.preview = node.dataset.direction;
        showCaption(node);
      });
      node.addEventListener('pointerleave', () => { delete diagram.dataset.preview; showCaption(selected); });
      node.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
          selected = null;
          nodes.forEach(item => item.setAttribute('aria-pressed', 'false'));
          delete diagram.dataset.active;
          delete diagram.dataset.preview;
          showCaption(null);
        }
      });
    });
    diagram.querySelector('.rd-hint').hidden = false;
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        if (entries.some(entry => entry.isIntersecting)) {
          diagram.classList.add('rd-enter');
          observer.disconnect();
        }
      }, { threshold: .15 });
      observer.observe(diagram);
    }
  });
})();
