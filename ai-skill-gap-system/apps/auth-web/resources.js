const pageResources = (() => {
  'use strict';

  const local = location.protocol === 'file:';
  let embedded;
  const ready = local ? new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'local-assets.js';
    script.onload = () => {
      embedded = window.localArtwork;
      delete window.localArtwork;
      script.remove();
      if (embedded) resolve();
      else reject(new Error('Thiếu tài nguyên mở file trực tiếp'));
    };
    script.onerror = () => reject(new Error('Không tải được local-assets.js'));
    document.head.append(script);
  }) : Promise.resolve();

  function embeddedValue(path) {
    const key = path.split(/[?#]/)[0];
    if (!(key in embedded)) throw new Error(`Không tìm thấy tài nguyên: ${key}`);
    return embedded[key];
  }

  async function text(path) {
    await ready;
    if (local) return embeddedValue(path);
    const response = await fetch(path);
    if (!response.ok) throw new Error(`Không tải được tài nguyên: ${path}`);
    return response.text();
  }

  function url(path) {
    if (!local) return path;
    const value = embeddedValue(path);
    return value.startsWith('data:')
      ? value
      : `data:image/svg+xml;charset=utf-8,${encodeURIComponent(value)}`;
  }

  ready.then(() => {
    const style = document.documentElement.style;
    style.setProperty('--sky-mask', `url("${url('images/sky-mask.svg')}")`);
    style.setProperty('--beam-mask', `url("${url('images/beam-mask.svg')}")`);
    const font = new FontFace('Grenze Gotisch', `url("${url('fonts/GrenzeGotisch.ttf')}")`, {
      weight: '100 900',
      style: 'normal',
      display: 'swap',
    });
    document.fonts.add(font);
    return font.load();
  }).catch(error => console.warn('Không tải được font hoặc mặt nạ:', error.message));

  return {
    text,
    async json(path) {
      return JSON.parse(await text(path));
    },
  };
})();
