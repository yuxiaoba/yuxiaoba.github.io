(() => {
  const dialog = document.querySelector('.life-viewer');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const image = dialog.querySelector('[data-photo-image]');
  const caption = dialog.querySelector('[data-photo-caption]');
  const count = dialog.querySelector('[data-photo-count]');
  const previous = dialog.querySelector('[data-photo-previous]');
  const next = dialog.querySelector('[data-photo-next]');
  let photos = [], index = 0, opener, overflow;
  function show(offset = 0) {
    index = (index + offset + photos.length) % photos.length;
    const link = photos[index];
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    caption.textContent = link.dataset.photoCaption || image.alt;
    count.textContent = `${index + 1} / ${photos.length}`;
    previous.hidden = next.hidden = photos.length < 2;
  }
  document.querySelectorAll('[data-photo-open]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      photos = [...link.closest('[data-photo-group]').querySelectorAll('[data-photo-open]')];
      index = photos.indexOf(link); opener = link;
      show(); dialog.showModal();
      overflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
    });
  });
  previous.addEventListener('click', () => show(-1));
  next.addEventListener('click', () => show(1));
  dialog.querySelector('[data-photo-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault(); show(event.key === 'ArrowLeft' ? -1 : 1);
    }
  });
  dialog.addEventListener('click', event => {
    const box = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.style.overflow = overflow;
    image.removeAttribute('src');
    opener?.focus({preventScroll:true});
  });
})();
