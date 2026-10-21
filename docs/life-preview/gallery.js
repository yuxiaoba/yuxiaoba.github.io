(() => {
  const root = document.querySelector('[data-life-demo]');
  if (!root) return;
  const data = JSON.parse(root.querySelector('[data-gallery-data]').textContent);
  const wall = root.querySelector('.photo-wall');
  const title = root.querySelector('[data-album-title]');
  const description = root.querySelector('.layout-description');
  const controls = [...root.querySelectorAll('[data-layout-option]')];
  const albums = [...root.querySelectorAll('[data-album]')];
  let layout = 'natural';
  function renderAlbum(index) {
    const album = data.albums[index];
    title.textContent = album.title;
    albums.forEach((link, i) => link.setAttribute('aria-current', String(i === index)));
    wall.replaceChildren();
    album.photos.forEach(photo => {
      const figure = document.createElement('figure'); figure.className = 'photo-tile';
      const link = document.createElement('a'); link.className = 'photo-frame'; link.href = photo.src; link.target = '_blank'; link.rel = 'noopener'; link.setAttribute('aria-label', photo.alt + ' · ' + data.open);
      const image = document.createElement('img'); image.src = photo.src; image.alt = photo.alt; image.width = photo.width; image.height = photo.height; image.loading = 'lazy'; image.style.objectPosition = photo.position;
      const caption = document.createElement('figcaption'); caption.textContent = photo.caption;
      link.append(image); figure.append(link, caption); wall.append(figure);
    });
  }
  function setLayout(value) {
    layout = value; wall.dataset.layout = layout;
    controls.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.layoutOption === layout)));
    description.textContent = data.descriptions[layout];
  }
  controls.forEach(button => button.addEventListener('click', () => setLayout(button.dataset.layoutOption)));
  albums.forEach((link, index) => link.addEventListener('click', () => renderAlbum(index)));
  setLayout('natural');
})();
