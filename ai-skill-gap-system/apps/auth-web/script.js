(() => {
  'use strict';

  async function loadVectorArtwork() {
    const sources = new Map();
    const placeholders = [...document.querySelectorAll('[data-svg]')];
    await Promise.all(placeholders.map(async placeholder => {
      const path = placeholder.dataset.svg;
      if (!sources.has(path)) sources.set(path, pageResources.text(path));
      const source = await sources.get(path);
      const artwork = new DOMParser().parseFromString(source, 'image/svg+xml');
      placeholder.replaceWith(document.importNode(artwork.documentElement, true));
    }));
  }

  const texts = {
    night: 'Bật đêm Halloween',
    day: 'Trở về ban ngày',
    lightOn: 'Chiếu đèn pin để xem mật khẩu',
    lightOff: 'Tắt đèn pin',
    show: 'Hiện mật khẩu',
    hide: 'Ẩn mật khẩu',
    resetStatus: 'Chức năng đặt lại mật khẩu chưa được thiết lập.',
    signupStatus: 'Chức năng đăng ký chưa được thiết lập.',
    signinStatus: 'Chức năng đăng nhập chưa được thiết lập.',
  };

  function showStatus(key) {
    statusMessage.textContent = texts[key];
  }
  const passwordInput = document.getElementById('password');
  const toggleButton = document.getElementById('show-password');
  const statusMessage = document.getElementById('status');
  const beam = document.getElementById('flash-beam');
  const passwordOverlay = document.getElementById('password-reveal');
  const passwordChars = document.getElementById('reveal-text');
  const flashlight = document.getElementById('flashlight');
  const owl = document.getElementById('email-owl');
  const themeButton = document.getElementById('theme-toggle');

  let nightMode = false;
  let revealEnabled = false;
  let cursor = { x: 0, y: 0 };
  let beamAngle = Math.PI;

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }
  let leafStates = [];
  let leafAnimation = 0;
  let leafPrevious = 0;
  function animateLitLeaves() {
    if (leafAnimation || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    leafPrevious = performance.now();
    function tick(now) {
      const dt = Math.min((now - leafPrevious) / 1000, .06);
      leafPrevious = now;
      let moving = false;
      leafStates.forEach((leaf, index) => {
        const easing = 1 - Math.exp(-dt / (leaf.target > leaf.strength ? .22 : .45));
        leaf.strength += (leaf.target - leaf.strength) * easing;
        leaf.phase += dt * (2.6 + (index % 4) * .23);
        const angle = (Math.sin(leaf.phase) * 7 + Math.sin(leaf.phase * 1.7) * 1.4) * leaf.strength;
        if (leaf.strength > .002 || leaf.target > 0) {
          leaf.node.style.transform = `rotate(${angle.toFixed(3)}deg)`;
          moving = true;
        } else {
          leaf.strength = 0;
          leaf.node.style.removeProperty('transform');
        }
      });
      leafAnimation = moving ? requestAnimationFrame(tick) : 0;
    }
    leafAnimation = requestAnimationFrame(tick);
  }

  function updateOwlGaze(dx, dy, lit) {
    const distance = Math.max(1, Math.hypot(dx, dy));
    const x = lit ? dx / distance : 0;
    const y = lit ? dy / distance : 0;
    const newlyLit = lit && !owl.classList.contains('is-lit');
    owl.classList.toggle('is-lit', lit);
    if (newlyLit) owl.classList.add('just-lit');
    if (!lit) owl.classList.remove('just-lit');
    owl.style.setProperty('--owl-gaze-x', `${x * 70}px`);
    owl.style.setProperty('--owl-gaze-y', `${y * 45}px`);
    owl.style.setProperty('--owl-head-x', `${x * 22}px`);
    owl.style.setProperty('--owl-head-y', `${y * 12}px`);
    owl.style.setProperty('--owl-tilt', `${x * 5}deg`);
  }

  function renderPassword() {
    passwordChars.replaceChildren(...Array.from(passwordInput.value, (letter) => {
      const character = document.createElement('span');
      character.className = 'reveal-char';
      const masked = document.createElement('span');
      masked.className = 'masked-char';
      masked.textContent = '•';
      const plain = document.createElement('span');
      plain.className = 'plain-char';
      plain.textContent = letter;
      character.append(masked, plain);
      return character;
    }));
  }

  function updateFlashlight() {
    if (!nightMode || !revealEnabled) return;

    const eyeRect = toggleButton.getBoundingClientRect();
    const fieldRect = passwordInput.getBoundingClientRect();
    const eyeX = eyeRect.left + eyeRect.width / 2;
    const eyeY = eyeRect.top + eyeRect.height / 2;
    const pointerDistance = Math.hypot(cursor.x - eyeX, cursor.y - eyeY);
    if (pointerDistance > 24) {
      beamAngle = Math.atan2(cursor.y - eyeY, cursor.x - eyeX);
    }
    const angleDeg = beamAngle * 180 / Math.PI;
    const unitX = Math.cos(beamAngle);
    const unitY = Math.sin(beamAngle);
    const originX = eyeX + unitX * 13;
    const originY = eyeY + unitY * 13;
    const beamLength = clamp(pointerDistance * 1.65, 160, 1600);
    const beamHeight = beamLength * .38;

    beam.style.left = `${originX}px`;
    beam.style.top = `${originY - beamHeight / 2}px`;
    beam.style.width = `${beamLength}px`;
    beam.style.height = `${beamHeight}px`;
    beam.style.transform = `rotate(${angleDeg}deg)`;
    flashlight.style.left = `${eyeX - 17}px`;
    flashlight.style.top = `${eyeY - 17}px`;
    flashlight.style.transform = `rotate(${angleDeg}deg)`;

    passwordOverlay.style.left = `${fieldRect.left}px`;
    passwordOverlay.style.top = `${fieldRect.top}px`;
    passwordOverlay.style.width = `${Math.max(0, fieldRect.width - 45)}px`;
    passwordOverlay.style.height = `${fieldRect.height}px`;
    passwordChars.style.transform = `translateX(${-passwordInput.scrollLeft}px)`;

    function getLightLevel(x, y) {
      const offsetX = x - originX;
      const offsetY = y - originY;
      const along = offsetX * unitX + offsetY * unitY;
      const sideways = Math.abs(-offsetX * unitY + offsetY * unitX);
      const halfBeam = beamHeight * (.01 + .49 * Math.max(0, along) / beamLength);
      const edgeFade = clamp((halfBeam - sideways + 4) / 16, 0, 1);
      const tail = clamp((along / beamLength - .55) / .41, 0, 1);
      const endFade = 1 - tail * tail * (3 - 2 * tail);
      return along >= 0 ? edgeFade * endFade : 0;
    }
    for (const character of passwordChars.children) {
      const bounds = character.getBoundingClientRect();
      character.style.setProperty('--lit', String(getLightLevel(bounds.left + bounds.width / 2, fieldRect.top + fieldRect.height / 2)));
    }
    const owlBounds = owl.getBoundingClientRect();
    const owlX = owlBounds.left + owlBounds.width / 2;
    const owlY = owlBounds.top + owlBounds.height / 2;
    const owlLight = getLightLevel(owlX, owlY);
    owl.style.opacity = String(owlLight);
    updateOwlGaze(originX - owlX, originY - (owlBounds.top + owlBounds.height * .36), owlLight > .08);
    document.querySelectorAll('.pumpkin-reaction').forEach(pumpkin => {
      const face = pumpkin.querySelector('.pumpkin-face-normal').getBoundingClientRect();
      const level = getLightLevel(face.left + face.width / 2, face.top + face.height / 2);
      const threshold = pumpkin.classList.contains('is-beam-lit') ? .06 : .14;
      pumpkin.classList.toggle('is-beam-lit', level > threshold);
    });
    leafStates.forEach(leaf => {
      const bounds = leaf.node.getBoundingClientRect();
      const level = getLightLevel(bounds.left + bounds.width / 2, bounds.top + bounds.height / 2);
      leaf.target = level > .08 ? level : 0;
    });
    const wolf = document.querySelector('.summit-stage image');
    const wolfStage = document.querySelector('.summit-stage');
    if (wolf) {
      const bounds = wolf.getBoundingClientRect();
      const level = getLightLevel(bounds.left + bounds.width * .6, bounds.top + bounds.height * .5);
      wolfStage.classList.toggle('is-beam-lit', level > (wolfStage.classList.contains('is-beam-lit') ? .06 : .14));
    }
    animateLitLeaves();
  }

  function setPasswordReveal(enabled) {
    revealEnabled = enabled;
    document.body.classList.toggle('flashlight-on', nightMode && enabled);
    passwordInput.type = !nightMode && enabled ? 'text' : 'password';
    toggleButton.setAttribute('aria-pressed', String(enabled));
    const description = nightMode
      ? texts[enabled ? 'lightOff' : 'lightOn']
      : texts[enabled ? 'hide' : 'show'];
    toggleButton.setAttribute('aria-label', description);
    if (nightMode && enabled) {
      renderPassword();
      const fieldRect = passwordInput.getBoundingClientRect();
      beamAngle = Math.PI;
      cursor = { x: fieldRect.left, y: fieldRect.top + fieldRect.height / 2 };
      updateFlashlight();
    } else {
      passwordChars.replaceChildren();
      document.querySelector('.summit-stage').classList.remove('is-beam-lit');
      owl.style.opacity = '0';
      updateOwlGaze(0, 0, false);
      document.querySelectorAll('.pumpkin-reaction').forEach(pumpkin => pumpkin.classList.remove('is-beam-lit'));
      leafStates.forEach(leaf => {
        leaf.target = 0;
      });
      animateLitLeaves();
    }
  }

  let dayTransitionTimer = 0;
  let departingFlights = [];
  function setNightMode(enabled) {
    clearTimeout(dayTransitionTimer);
    departingFlights.forEach(animation => animation.cancel());
    departingFlights = [];
    nightMode = enabled;
    const retiring = !enabled && document.body.classList.contains('night')
      && !matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.body.classList.toggle('night-exiting', retiring);
    if (enabled) document.body.classList.add('night');
    else if (!retiring) document.body.classList.remove('night');
    if (retiring) {
      document.querySelectorAll('.sky-bat, .sky-witch').forEach(flyer => {
        const bounds = flyer.getBoundingClientRect();
        const direction = bounds.left + bounds.width / 2 < innerWidth / 2 ? -1 : 1;
        departingFlights.push(flyer.animate([
          { transform: getComputedStyle(flyer).transform, opacity: getComputedStyle(flyer).opacity },
          { transform: `translate(${direction * 90}px, -90px) rotate(${direction * 12}deg)`, opacity: 0 },
        ], { duration: 1200, easing: 'cubic-bezier(.4,0,.7,1)', fill: 'forwards' }));
      });
      dayTransitionTimer = setTimeout(() => {
        document.body.classList.remove('night', 'night-exiting');
        departingFlights.forEach(animation => animation.cancel());
        departingFlights = [];
      }, 3700);
    }
    animateVines(enabled);
    themeButton.setAttribute('aria-pressed', String(enabled));
    const themeDescription = texts[enabled ? 'day' : 'night'];
    themeButton.setAttribute('aria-label', themeDescription);
    setPasswordReveal(false);
  }

  document.addEventListener('pointermove', (event) => {
    if (!nightMode || !revealEnabled) return;
    cursor = { x: event.clientX, y: event.clientY };
    updateFlashlight();
  });

  passwordInput.addEventListener('input', () => {
    if (nightMode && revealEnabled) renderPassword();
    updateFlashlight();
  });

  passwordInput.addEventListener('scroll', updateFlashlight);
  window.addEventListener('resize', updateFlashlight);
  window.addEventListener('scroll', updateFlashlight, true);
  toggleButton.addEventListener('click', () => {
    setPasswordReveal(!revealEnabled);
  });

  themeButton.addEventListener('click', () => setNightMode(!nightMode));

  const forgotBtn = document.getElementById('forgot-password');
  if (forgotBtn) {
    forgotBtn.addEventListener('click', () => {
      showStatus('resetStatus');
    });
  }
  let vineNodes = [];
  let vineFrames = [];
  let vineProgress = 0;
  let vineTarget = 0;
  let vineAnimation = 0;
  let vineReady = false;
  const reducedVineMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function paintVineFrame(progress) {
    if (!vineReady) return;
    const position = progress * (vineFrames.length - 1);
    const first = Math.floor(position);
    const second = Math.min(first + 1, vineFrames.length - 1);
    const mix = position - first;
    vineNodes.forEach((node, index) => {
      const a = vineFrames[first][index];
      const b = vineFrames[second][index];
      const interpolate = key => a[key] + (b[key] - a[key]) * mix;
      if ('dash' in a) {
        const dash = interpolate('dash');
        node.setAttribute('stroke-dashoffset', dash.toFixed(2));
        node.setAttribute('opacity', dash >= 999.99 ? '0' : '1');
      } else {
        node.setAttribute('opacity', interpolate('opacity').toFixed(3));
        node.setAttribute('transform', `rotate(${interpolate('angle').toFixed(2)}) scale(${interpolate('scale').toFixed(4)})`);
      }
    });
  }

  function animateVines(enabled) {
    vineTarget = enabled ? 1 : 0;
    cancelAnimationFrame(vineAnimation);
    if (!vineReady) return;
    if (reducedVineMotion.matches) {
      vineProgress = vineTarget;
      paintVineFrame(vineProgress);
      return;
    }
    let previous;
    function tick(now) {
      if (previous !== undefined) {
        const step = Math.min(now - previous, 50) / 3600;
        vineProgress = vineTarget ? Math.min(1, vineProgress + step) : Math.max(0, vineProgress - step);
      }
      previous = now;
      paintVineFrame(vineProgress);
      if (vineProgress !== vineTarget) vineAnimation = requestAnimationFrame(tick);
    }
    vineAnimation = requestAnimationFrame(tick);
  }
  function fitVineArtwork(svg) {
    const host = document.getElementById('halloween-vines');
    const main = [...svg.querySelectorAll('[data-layout="main"]')];
    const branches = [...svg.querySelectorAll('[data-layout="branch"]')];
    const ornaments = [...svg.querySelectorAll('[data-layout="ornament"]')];
    const numbers = /-?\d+(?:\.\d+)?/g;
    const rootOf = group => group.dataset.path.match(numbers).slice(0, 2).map(Number);
    function resize() {
      const { width, height } = host.getBoundingClientRect();
      if (!width || !height) return;
      const unit = Math.min(width / 1000, height / 620);
      const card = document.querySelector('.login-card');
      const bounds = card.getBoundingClientRect(), frame = host.getBoundingClientRect();
      const left = bounds.left - frame.left, top = bounds.top - frame.top;
      const right = bounds.right - frame.left, bottom = bounds.bottom - frame.top;
      const radius = parseFloat(getComputedStyle(card).borderTopLeftRadius) || 32;
      const interpolate = (value, source, target) => {
        const i = value < source[1] ? 0 : value > source[2] ? 2 : 1;
        return target[i] + (value - source[i]) * (target[i + 1] - target[i]) / (source[i + 1] - source[i]);
      };
      const map = (x, y) => [
        interpolate(x, [58, 98, 902, 942], [left, left + radius, right - radius, right]),
        interpolate(y, [55, 95, 537, 565], [top, top + radius, bottom - radius, bottom]),
      ];
      svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
      function draw(group, mapping) {
        const values = group.dataset.path.match(numbers).map(Number);
        let n = 0;
        const path = group.dataset.path.replace(numbers, () => {
          const coordinate = n % 2;
          const at = n - coordinate;
          const point = mapping(values[at], values[at + 1]);
          n++;
          return point[coordinate].toFixed(3);
        });
        for (const node of group.children) {
          node.setAttribute('d', path);
          node.setAttribute('stroke-width', node.dataset.width * unit);
        }
      }
      main.forEach(group => draw(group, map));
      const samples = main.flatMap(group => {
        const path = group.firstElementChild, length = path.getTotalLength();
        return Array.from({ length: 401 }, (_, i) => path.getPointAtLength(length * i / 400));
      });
      const attach = (x, y) => {
        const [px, py] = map(x, y);
        const closest = samples.reduce((best, point) => (point.x - px) ** 2 + (point.y - py) ** 2 < (best.x - px) ** 2 + (best.y - py) ** 2 ? point : best);
        return [closest.x, closest.y];
      };
      branches.forEach(group => {
        const [x, y] = rootOf(group), [px, py] = attach(x, y);
        draw(group, (cx, cy) => [px + (cx - x) * unit, py + (cy - y) * unit]);
      });
      ornaments.forEach(group => {
        const { art, x, y, scale, rotation } = group.dataset;
        let point = art === 'pumpkin' ? map(+x, +y) : attach(+x, +y);
        if (group.dataset.branchRootX !== undefined) {
          const rx = Number(group.dataset.branchRootX), ry = Number(group.dataset.branchRootY);
          const anchor = attach(rx, ry);
          point = [anchor[0] + (+x - rx) * unit, anchor[1] + (+y - ry) * unit];
        }
        if (art === 'lantern') {
          const root = +x < 500 ? [65, 219] : [946, 300];
          const anchor = attach(...root);
          point = [anchor[0] + (+x - root[0]) * unit, anchor[1] + (+y - root[1]) * unit];
        }
        group.setAttribute('transform', `translate(${point[0]} ${point[1]}) rotate(${rotation}) scale(${scale * unit})`);
      });
    }
    const observer = new ResizeObserver(resize);
    observer.observe(host);
    const cardEl = document.querySelector('.login-card');
    if (cardEl) {
      observer.observe(cardEl);
    }
    resize();
  }

  const vineAssets = ['images/vine-styles/outer/artwork.svg?v=1', 'images/vine-styles/outer/keyframes.json?v=1'];
  async function loadVines() {
    try {
      const [source, frames] = await Promise.all([
        pageResources.text(vineAssets[0]),
        pageResources.json(vineAssets[1]),
      ]);
      const artwork = new DOMParser().parseFromString(source, 'image/svg+xml');
      const svg = document.importNode(artwork.documentElement, true);
      const nodes = [...svg.querySelectorAll('[data-grow]')];
      if (!frames.length || frames.some(frame => frame.length !== nodes.length)) {
        throw new Error('Vine frames do not match artwork');
      }
      cancelAnimationFrame(vineAnimation);
      svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
      document.getElementById('halloween-vines').replaceChildren(svg);
      fitVineArtwork(svg);
      vineNodes = nodes;
      vineFrames = frames;
      leafStates = [...svg.querySelectorAll('.leaf-reaction')].map((node, index) => ({
        node,
        strength: 0,
        target: 0,
        phase: index * 1.31,
      }));
      vineReady = true;
      paintVineFrame(vineProgress);
      animateVines(nightMode);
    } catch (error) {
      console.warn('Không tải được dây leo:', error.message);
    }
  }
  loadVines();
  reducedVineMotion.addEventListener('change', () => animateVines(nightMode));

  owl.addEventListener('animationend', event => {
    if (event.animationName === 'owl-startle') owl.classList.remove('just-lit');
  });
  const witch = document.querySelector('.sky-witch');
  const cardElement = document.querySelector('.login-card');
  function updateWitchRoute() {
    const card = cardElement.getBoundingClientRect();
    const sky = witch.parentElement.getBoundingClientRect();
    const width = parseFloat(getComputedStyle(witch).width) || 100;
    witch.style.setProperty('--witch-left', `${Math.max(6, card.left - sky.left - 94)}px`);
    witch.style.setProperty('--witch-right', `${Math.min(sky.width - width - 6, card.right - sky.left + 94 - width)}px`);
    witch.style.setProperty('--witch-top', `${Math.max(16, card.top - sky.top - 150)}px`);
  }
  updateWitchRoute();
  new ResizeObserver(updateWitchRoute).observe(cardElement);
  window.addEventListener('resize', updateWitchRoute);

  loadVectorArtwork().catch(error => console.warn('Không tải được hình SVG:', error.message));
})();
