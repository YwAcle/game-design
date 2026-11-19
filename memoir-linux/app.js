'use strict';

(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const storageKey = 'hogwarts-always-v1';
  const houses = {
    gryffindor: { name: '格兰芬多', color: '#c48b74', message: '格兰芬多的勇气，会陪你走过每一场冒险。' },
    slytherin: { name: '斯莱特林', color: '#8ebaa0', message: '斯莱特林的灯，永远为你留在黑湖深处。' },
    ravenclaw: { name: '拉文克劳', color: '#8da9c9', message: '拉文克劳的星空，始终为你的好奇心敞开。' },
    hufflepuff: { name: '赫奇帕奇', color: '#d6bb75', message: '赫奇帕奇的壁炉旁，永远有一个你的座位。' }
  };
  const covers = ['letter', 'bridge', 'ballroom', 'fireworks'];
  const scenes = [
    ['黑湖 · 初见霍格沃茨', '那一晚，远处的灯火是我们的未来。'],
    ['廊桥 · 再等一场日落', '那条一起走过的长廊，一直都在。'],
    ['天文塔 · 星光落在肩上', '没说完的话，悄悄讲给星星听。'],
    ['宿舍 · 壁炉旁的位置', '「回来啦？就差你了。」']
  ];
  const examples = [
    { id: 'inspiration-letter', title: '那封信，真的寄到了', body: '记得第一次收到录取通知书时，我把手机里的那一页看了很久。\n\n原来小时候等过的猫头鹰，真的会找到长大后的我们。第一次穿过对角巷，第一次拿起魔杖，第一次站在分院帽前……那一天，好像我真的成为了一名巫师。\n\n如果能重来，我想再慢慢读一遍那封信。', author: '回忆灵感', house: '', cover: 'letter', category: '初入魔法世界', dateLabel: '故事的第一章' },
    { id: 'inspiration-ballroom', title: '「再跳一支，就下线。」', body: '总说只跳最后一支，却不知不觉在舞会待到很晚。\n\n我们从踩错拍子，到终于能默契地转身。没人在意分数，只想把那首熟悉的旋律再听一遍。\n\n那句「明天还来吗」，后来成了我每天最期待的邀请。想念的从来不只是一场舞会，还有屏幕那一边的你。', author: '回忆灵感', house: '', cover: 'ballroom', category: '那些并肩的日子', dateLabel: '与朋友的约定' },
    { id: 'inspiration-fireworks', title: '截图里，我们还站在一起', body: '烟花升起来的时候，大家都停下了手上的事。\n\n有人骑着扫帚经过，有人认真调整角度，还有人一直在喊：「往左一点，不要把我挡住了！」\n\n那时候只觉得是很普通的一晚。后来才发现，原来最想留住的，就是这样普通的一晚。\n\n愿下一次烟花亮起时，我们还能想起彼此。', author: '回忆灵感', house: '', cover: 'fireworks', category: '想留住的瞬间', dateLabel: '某个烟花之夜' }
  ];

  function validMemory(memory) {
    return memory && typeof memory === 'object' && typeof memory.id === 'string' && /^memory-[\w-]+$/.test(memory.id)
      && typeof memory.title === 'string' && memory.title.trim().length > 0 && memory.title.length <= 32
      && typeof memory.body === 'string' && memory.body.trim().length > 0 && memory.body.length <= 400
      && typeof memory.author === 'string' && memory.author.trim().length > 0 && memory.author.length <= 24
      && (memory.house === '' || Object.hasOwn(houses, memory.house)) && covers.includes(memory.cover)
      && typeof memory.created === 'string' && Number.isFinite(Date.parse(memory.created));
  }

  const state = { memories: [], favorites: [], house: '', reducedMotion: null };
  let storageAvailable = true;
  let corruptedStorage = false;
  try {
    const raw = localStorage.getItem(storageKey);
    if (raw) {
      const saved = JSON.parse(raw);
      if (!saved || saved.version !== 1 || !Array.isArray(saved.memories) || !saved.memories.every(validMemory)
        || new Set(saved.memories.map(m => m.id)).size !== saved.memories.length) {
        throw new Error('Invalid saved memories');
      }
      state.memories = saved.memories;
      const ids = new Set([...examples, ...state.memories].map(memory => memory.id));
      state.favorites = Array.isArray(saved.favorites) ? [...new Set(saved.favorites.filter(id => ids.has(id)))] : [];
      state.house = Object.hasOwn(houses, saved.house) ? saved.house : '';
      state.reducedMotion = typeof saved.reducedMotion === 'boolean' ? saved.reducedMotion : null;
    }
  } catch (error) {
    storageAvailable = false;
    corruptedStorage = error instanceof SyntaxError || error.message === 'Invalid saved memories';
  }

  let toastTimer;
  function toast(message) {
    const node = $('#toast');
    node.textContent = message;
    node.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => node.classList.remove('visible'), 4300);
  }

  function persist(patch) {
    if (corruptedStorage) {
      toast('已有回忆数据无法读取，为避免覆盖，暂时不能保存。请先备份原始数据。');
      return false;
    }
    const next = { ...state, ...patch, version: 1 };
    try {
      localStorage.setItem(storageKey, JSON.stringify(next));
      Object.assign(state, patch);
      storageAvailable = true;
      return true;
    } catch {
      storageAvailable = false;
      toast('浏览器暂时无法保存，请保留文字，或允许本地存储后再试。');
      return false;
    }
  }

  function formatDate(value) {
    const date = new Date(value);
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
  }

  function allMemories() { return [...state.memories, ...examples]; }
  function getMemory(id) { return allMemories().find(memory => memory.id === id); }
  function isMine(memory) { return state.memories.some(item => item.id === memory.id); }
  function houseLabel(memory) { return houses[memory.house]?.name || '一位相信魔法的巫师'; }
  function categoryLabel(memory) { return isMine(memory) ? '我的魔法故事' : '回忆灵感 · ' + memory.category; }
  function icon(symbol) {
    const node = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    node.classList.add('icon');
    node.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    use.setAttribute('href', '#i-' + symbol);
    node.append(use);
    return node;
  }
  function element(tag, className, content) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined) node.textContent = content;
    return node;
  }

  let filter = 'all';
  function renderMemories() {
    const grid = $('#memory-grid');
    const list = allMemories().filter(memory => filter === 'mine' ? isMine(memory) : filter === 'favorites' ? state.favorites.includes(memory.id) : true);
    grid.replaceChildren();
    $('#memory-count').textContent = allMemories().length;
    $('#empty-state').hidden = list.length > 0;
    $('#empty-message').textContent = filter === 'favorites' ? '点一下故事右上角的爱心，就能把它珍藏起来。' : '把你的第一个故事，轻轻放进来。';
    for (const memory of list) {
      const article = element('article', 'memory-card');
      const open = element('button', 'memory-open');
      open.type = 'button';
      open.setAttribute('aria-label', `读一读：${memory.title}`);
      const cover = element('span', 'memory-cover');
      cover.style.display = 'block';
      const img = element('img');
      img.src = `assets/${memory.cover}.webp`;
      img.alt = '';
      img.loading = 'lazy';
      cover.append(img, element('span', 'memory-category', isMine(memory) ? '我的故事' : '回忆灵感'));
      const content = element('span', 'memory-content');
      const heading = element('strong', 'memory-title', memory.title);
      const excerpt = element('span', 'memory-excerpt', memory.body.replace(/\n+/g, ' '));
      const meta = element('span', 'memory-meta');
      const author = element('span', 'memory-author');
      const dot = element('span', 'author-dot');
      dot.style.background = houses[memory.house]?.color || 'var(--gold)';
      author.append(dot, document.createTextNode(memory.author));
      const date = element('time', '', memory.created ? formatDate(memory.created) : memory.dateLabel);
      if (memory.created) date.dateTime = memory.created;
      meta.append(author, date);
      content.append(heading, excerpt, meta);
      open.append(cover, content);
      open.addEventListener('click', () => openMemory(memory.id));
      const favorite = element('button', 'favorite-button');
      const selected = state.favorites.includes(memory.id);
      favorite.type = 'button';
      favorite.setAttribute('aria-label', `${selected ? '取消珍藏' : '珍藏'}：${memory.title}`);
      favorite.setAttribute('aria-pressed', String(selected));
      favorite.append(icon('heart'));
      favorite.addEventListener('click', () => {
        const favorites = selected ? state.favorites.filter(id => id !== memory.id) : [...state.favorites, memory.id];
        if (persist({ favorites })) {
          renderMemories();
          const replacement = $$('article', grid).find(node => $('.memory-open', node)?.getAttribute('aria-label') === `读一读：${memory.title}`);
          if (replacement) $('.favorite-button', replacement).focus({ preventScroll: true });
          else $(`[data-filter="${filter}"]`).focus({ preventScroll: true });
          toast(selected ? '已从珍藏中取出。' : '这段回忆，替你收好了。');
        }
      });
      article.append(open, favorite);
      grid.append(article);
    }
  }

  $$('[data-filter]').forEach(button => button.addEventListener('click', () => {
    filter = button.dataset.filter;
    $$('[data-filter]').forEach(item => {
      item.classList.toggle('is-active', item === button);
      item.setAttribute('aria-pressed', String(item === button));
    });
    renderMemories();
  }));

  function updateHouse() {
    $$('[data-house]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.house === state.house)));
    $('#house-message').textContent = houses[state.house]?.message || '选一次自己的学院，让回忆有个归处。';
    document.documentElement.style.setProperty('--house-accent', houses[state.house]?.color || '#d0b57e');
  }
  $$('[data-house]').forEach(button => button.addEventListener('click', () => {
    if (persist({ house: button.dataset.house })) {
      updateHouse();
      toast(`欢迎回家，${houses[state.house].name}的巫师。`);
    }
  }));

  let activeScene = 0;
  function selectScene(index) {
    if (!scenes[index]) return;
    activeScene = index;
    $$('[data-scene-image]').forEach(img => img.classList.toggle('is-current', Number(img.dataset.sceneImage) === index));
    $$('[data-scene]').forEach(button => {
      const selected = Number(button.dataset.scene) === index;
      button.classList.toggle('is-selected', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    $('#scene-number').textContent = String(index + 1).padStart(2, '0');
    $('#scene-name').textContent = scenes[index][0];
    $('#scene-subtitle').textContent = scenes[index][1];
  }
  $$('[data-scene]').forEach(button => button.addEventListener('click', () => selectScene(Number(button.dataset.scene))));
  $$('[data-visit]').forEach(button => button.addEventListener('click', () => {
    selectScene(Number(button.dataset.visit));
    $('#home').scrollIntoView({ behavior: motionReduced() ? 'instant' : 'smooth' });
    $(`[data-scene="${activeScene}"]`).focus({ preventScroll: true });
  }));

  const dialogs = $$('dialog');
  function showDialog(id) { $(id).showModal(); }
  $$('[data-close]').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
  dialogs.forEach(dialog => dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  }));

  $$('[data-open-write]').forEach(button => button.addEventListener('click', () => {
    $('#form-error').hidden = true;
    // Preserve an unfinished draft when closing and reopening the letter.
    if (!$('#house-input').value) $('#house-input').value = state.house;
    showDialog('#write-dialog');
  }));
  $('#memory-body').addEventListener('input', event => { $('#character-count').textContent = `${event.target.value.length} / 400`; });
  $('#memory-form').addEventListener('submit', event => {
    event.preventDefault();
    const data = new FormData(event.target);
    const id = window.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const memory = { id: `memory-${id}`, author: String(data.get('author')).trim(), title: String(data.get('title')).trim(), body: String(data.get('body')).trim(), house: data.get('house'), cover: data.get('cover'), created: new Date().toISOString() };
    const error = $('#form-error');
    if (!validMemory(memory)) {
      error.textContent = '请写下巫师名字、回忆标题和故事，内容不能只有空格。';
      error.hidden = false;
      return;
    }
    if (!persist({ memories: [memory, ...state.memories] })) {
      error.textContent = corruptedStorage ? '原有数据暂时无法读取，已避免覆盖。你的草稿还在，请先复制保存。' : '保存没有成功。请复制保留故事，再检查浏览器是否允许保存网站数据。';
      error.hidden = false;
      return;
    }
    error.hidden = true;
    event.target.reset();
    $('#character-count').textContent = '0 / 400';
    $('#write-dialog').close();
    $('[data-filter="mine"]').click();
    $('#memories').scrollIntoView({ behavior: motionReduced() ? 'instant' : 'smooth' });
    toast('你和霍格沃茨的这一页，已经好好收进回忆册。');
  });

  let openedMemoryId = null;
  function openMemory(id) {
    const memory = getMemory(id);
    if (!memory) return;
    openedMemoryId = id;
    $('#detail-cover').src = `assets/${memory.cover}.webp`;
    $('#detail-cover').alt = memory.title + '的回忆封面';
    $('#detail-category').textContent = categoryLabel(memory);
    $('#detail-title').textContent = memory.title;
    $('#detail-body').textContent = memory.body;
    $('#detail-author').textContent = `${memory.author} · ${isMine(memory) ? houseLabel(memory) : '示例故事'}`;
    $('#detail-date').textContent = memory.created ? formatDate(memory.created) : memory.dateLabel;
    $('#delete-memory').hidden = !isMine(memory);
    $('#delete-memory').textContent = '删除这段回忆';
    showDialog('#detail-dialog');
  }
  let deleteConfirmTimer;
  $('#delete-memory').addEventListener('click', () => {
    const memory = getMemory(openedMemoryId);
    if (!memory || !isMine(memory)) return;
    const button = $('#delete-memory');
    if (button.textContent !== '确认删除？此操作不可撤销') {
      button.textContent = '确认删除？此操作不可撤销';
      clearTimeout(deleteConfirmTimer);
      deleteConfirmTimer = setTimeout(() => { button.textContent = '删除这段回忆'; }, 5000);
      return;
    }
    if (persist({ memories: state.memories.filter(item => item.id !== openedMemoryId), favorites: state.favorites.filter(id => id !== openedMemoryId) })) {
      clearTimeout(deleteConfirmTimer);
      $('#detail-dialog').close();
      renderMemories();
      toast('这一页已从回忆册移除。');
    }
  });

  function download(blob, filename) {
    const url = URL.createObjectURL(blob);
    const anchor = element('a');
    anchor.href = url;
    anchor.download = filename;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }
  function safeFilename(name) { return name.replace(/[<>:"/\\|?*\u0000-\u001f]/g, '').slice(0, 40) || '我的魔法回忆'; }
  $('#backup-button').addEventListener('click', () => {
    if (corruptedStorage) {
      try {
        download(new Blob([localStorage.getItem(storageKey) || ''], { type: 'text/plain;charset=utf-8' }), '魔法留声-原始回忆数据.txt');
        toast('原始数据已备份，未修改你的浏览器内容。');
      } catch { toast('无法读取浏览器存储，请先复制保留尚未保存的故事。'); }
      return;
    }
    const backup = { app: '魔法留声 · Hogwarts, Always', version: 1, exportedAt: new Date().toISOString(), house: state.house, memories: state.memories, favorites: state.favorites };
    download(new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json;charset=utf-8' }), `魔法留声-回忆备份-${formatDate(new Date())}.json`);
    toast('回忆已下载。愿这些故事一直陪着你。');
  });

  function wrapText(ctx, text, maxWidth) {
    const lines = [];
    for (const paragraph of text.split('\n')) {
      let line = '';
      for (const character of paragraph) {
        if (line && ctx.measureText(line + character).width > maxWidth) { lines.push(line); line = ''; }
        line += character;
      }
      lines.push(line);
    }
    return lines;
  }

  $('#postcard-button').addEventListener('click', async () => {
    const memory = getMemory(openedMemoryId);
    if (!memory) return;
    const button = $('#postcard-button');
    button.disabled = true;
    try {
      await document.fonts.ready;
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error('No canvas');
      const family = '"Songti SC", "STSong", "Noto Serif CJK SC", serif';
      ctx.font = `30px ${family}`;
      const bodyLines = wrapText(ctx, memory.body, 820);
      ctx.font = `52px ${family}`;
      const titleLines = wrapText(ctx, memory.title, 820);
      const bodyTop = 435 + titleLines.length * 77;
      canvas.width = 1080;
      canvas.height = Math.max(1340, bodyTop + bodyLines.length * 58 + 305);
      const h = canvas.height;
      const gradient = ctx.createLinearGradient(0, 0, 1080, h);
      gradient.addColorStop(0, '#1d352d'); gradient.addColorStop(1, '#10241d');
      ctx.fillStyle = gradient; ctx.fillRect(0, 0, 1080, h);
      ctx.strokeStyle = '#9d8c5e'; ctx.lineWidth = 1;
      ctx.strokeRect(36, 36, 1008, h - 72);
      ctx.strokeStyle = '#9d8c5e60'; ctx.strokeRect(47, 47, 986, h - 94);
      ctx.fillStyle = '#c9b17d'; ctx.textAlign = 'center'; ctx.font = '17px Georgia, serif';
      ctx.fillText('H O G W A R T S ,   A L W A Y S', 540, 107);
      // Draw the keepsake entirely on canvas so PNG export also works from file://.
      ctx.strokeStyle = '#cdb987'; ctx.lineWidth = 1.6;
      ctx.beginPath();
      ctx.moveTo(365, 310); ctx.lineTo(715, 310);
      for (const [x, y, width] of [[400, 234, 42], [466, 204, 47], [530, 162, 50], [603, 224, 42], [667, 247, 37]]) {
        ctx.moveTo(x - width / 2, 310); ctx.lineTo(x - width / 2, y); ctx.lineTo(x, y - 49); ctx.lineTo(x + width / 2, y); ctx.lineTo(x + width / 2, 310);
        ctx.moveTo(x - width / 2 - 5, y); ctx.lineTo(x + width / 2 + 5, y);
        ctx.moveTo(x, y - 49); ctx.lineTo(x, y - 69); ctx.lineTo(x + 15, y - 61); ctx.lineTo(x, y - 56);
      }
      ctx.stroke();
      ctx.fillStyle = '#d7c28f';
      for (const [x, y] of [[400, 263], [466, 245], [530, 218], [530, 264], [603, 265], [667, 278]]) ctx.fillRect(x - 3, y, 6, 12);
      for (const [x, y, size] of [[340, 205, 5], [740, 191, 6], [680, 139, 4], [390, 154, 3], [600, 120, 3]]) {
        ctx.beginPath(); ctx.moveTo(x, y - size); ctx.lineTo(x + 2, y - 2); ctx.lineTo(x + size, y); ctx.lineTo(x + 2, y + 2); ctx.lineTo(x, y + size); ctx.lineTo(x - 2, y + 2); ctx.lineTo(x - size, y); ctx.lineTo(x - 2, y - 2); ctx.closePath(); ctx.fill();
      }
      ctx.fillStyle = '#b6aa87'; ctx.font = `21px ${family}`; ctx.fillText(isMine(memory) ? '属于我的魔法故事' : '回忆灵感 · 示例故事', 540, 385);
      ctx.fillStyle = '#eadfc2'; ctx.font = `52px ${family}`;
      titleLines.forEach((line, i) => ctx.fillText(line, 540, 465 + i * 77));
      ctx.fillStyle = '#c4c9b2'; ctx.textAlign = 'left'; ctx.font = `30px ${family}`;
      bodyLines.forEach((line, i) => ctx.fillText(line, 130, bodyTop + i * 58));
      ctx.strokeStyle = '#b8a37066'; ctx.beginPath(); ctx.moveTo(130, h - 230); ctx.lineTo(950, h - 230); ctx.stroke();
      ctx.fillStyle = '#d6c59c'; ctx.font = `24px ${family}`; ctx.fillText(memory.author + (memory.house ? ' · ' + houseLabel(memory) : ''), 130, h - 176);
      ctx.textAlign = 'right'; ctx.font = '21px Georgia, serif'; ctx.fillText(memory.created ? formatDate(memory.created) : 'ALWAYS', 950, h - 176);
      ctx.textAlign = 'center'; ctx.font = `23px ${family}`; ctx.fillStyle = '#aeaf91'; ctx.fillText('故事会落幕，魔法永不散场。', 540, h - 103);
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
      if (!blob) throw new Error('PNG export failed');
      download(blob, `魔法留声-${safeFilename(memory.title)}.png`);
      toast('纪念卡片已保存，愿它替你留住这一刻。');
    } catch { toast('卡片暂时没能生成，请使用「备份回忆」保留文字。'); }
    finally { button.disabled = false; }
  });

  $('#about-button').addEventListener('click', () => showDialog('#about-dialog'));
  const mediaMotion = matchMedia('(prefers-reduced-motion: reduce)');
  function motionReduced() { return state.reducedMotion ?? mediaMotion.matches; }
  function updateMotion() {
    document.body.classList.toggle('reduced-motion', motionReduced());
    $('#motion-toggle').setAttribute('aria-pressed', String(motionReduced()));
    $('#motion-toggle').textContent = motionReduced() ? '开启动态魔法效果' : '关闭动态魔法效果';
  }
  $('#motion-toggle').addEventListener('click', () => {
    const value = !motionReduced();
    if (persist({ reducedMotion: value })) { updateMotion(); updateAnimation(); }
  });
  mediaMotion.addEventListener('change', () => { updateMotion(); updateAnimation(); });

  let lumos = false;
  $('#lumos-toggle').addEventListener('click', () => {
    lumos = !lumos;
    document.body.classList.toggle('lumos', lumos);
    $('#lumos-toggle').setAttribute('aria-pressed', String(lumos));
    $('#lumos-toggle small').textContent = lumos ? '魔法已点亮' : '点亮魔杖';
    toast(lumos ? 'Lumos. 总有一束光，替你照亮回家的路。' : 'Nox. 星星也需要休息一会儿。');
  });
  $('#snitch').addEventListener('click', event => {
    const button = event.currentTarget;
    button.classList.add('caught');
    toast('抓住了！愿你还记得第一次赢得的那场胜利。');
    setTimeout(() => button.classList.remove('caught'), 9000);
  });

  // A locally synthesized, original bell ambience; sound starts only after a click.
  let audioContext, audioMaster, soundTimer, soundEnabled = false, audioStep = 0;
  const notes = [261.63, 392, 523.25, 329.63, 440, 392, 293.66, 349.23, 523.25, 440, 329.63, 293.66];
  function stopAudio() {
    soundEnabled = false;
    clearInterval(soundTimer);
    if (audioContext && audioMaster) {
      audioMaster.gain.cancelScheduledValues(audioContext.currentTime);
      audioMaster.gain.setTargetAtTime(0, audioContext.currentTime, .1);
    }
    $('#sound-toggle').setAttribute('aria-pressed', 'false');
    $('.sound-status').textContent = '关';
  }
  function playBell() {
    if (!soundEnabled || document.hidden) return;
    const time = audioContext.currentTime;
    const frequency = notes[audioStep++ % notes.length];
    for (const [ratio, volume, decay] of [[1, .11, 3.8], [2, .025, 2.3], [3.005, .007, 1.6]]) {
      const oscillator = audioContext.createOscillator();
      const envelope = audioContext.createGain();
      oscillator.type = 'sine'; oscillator.frequency.value = frequency * ratio;
      envelope.gain.setValueAtTime(0, time); envelope.gain.linearRampToValueAtTime(volume, time + .025);
      envelope.gain.exponentialRampToValueAtTime(.0001, time + decay);
      oscillator.connect(envelope); envelope.connect(audioMaster);
      oscillator.start(time); oscillator.stop(time + decay + .1);
      oscillator.onended = () => { oscillator.disconnect(); envelope.disconnect(); };
    }
  }
  $('#sound-toggle').addEventListener('click', async () => {
    if (soundEnabled) { stopAudio(); return; }
    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) throw new Error('Audio unavailable');
      if (!audioContext) {
        audioContext = new AudioContextClass();
        audioMaster = audioContext.createGain();
        audioMaster.gain.value = 0;
        audioMaster.connect(audioContext.destination);
      }
      await audioContext.resume();
      soundEnabled = true;
      audioMaster.gain.setTargetAtTime(.65, audioContext.currentTime, .2);
      $('#sound-toggle').setAttribute('aria-pressed', 'true');
      $('.sound-status').textContent = '开';
      playBell(); soundTimer = setInterval(playBell, 2300);
    } catch { stopAudio(); toast('当前浏览器暂时无法播放环境音，画面仍可正常体验。'); }
  });

  const hero = $('#home');
  const canvas = $('#magic-canvas');
  let renderer = null;
  function makeRenderer() {
    let gl;
    try { gl = canvas.getContext('webgl', { alpha: true, antialias: false, depth: false, powerPreference: 'low-power', premultipliedAlpha: false }); }
    catch { gl = null; }
    if (!gl) {
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;
      return { name: 'Canvas 2D', resize(width, height, dpr) { canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }, draw(points, width, height) {
        ctx.clearRect(0, 0, width, height);
        for (let i = 0; i < points.length; i += 4) {
          ctx.fillStyle = `rgba(231,211,159,${points[i + 3]})`;
          ctx.beginPath(); ctx.arc(points[i], points[i + 1], points[i + 2] / 5, 0, Math.PI * 2); ctx.fill();
        }
      } };
    }
    const vertex = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vertex, 'attribute vec4 a_particle; uniform vec2 u_resolution; uniform float u_dpr; varying float v_alpha; void main(){vec2 p=a_particle.xy/u_resolution;gl_Position=vec4(p.x*2.0-1.0,1.0-p.y*2.0,0,1);gl_PointSize=a_particle.z*u_dpr;v_alpha=a_particle.w;}');
    gl.compileShader(vertex);
    const fragment = gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fragment, 'precision mediump float; varying float v_alpha; void main(){vec2 p=gl_PointCoord-0.5;float r=length(p);float halo=exp(-r*r*24.0)*0.5;float star=exp(-abs(p.x)*45.0-abs(p.y)*7.0)+exp(-abs(p.y)*45.0-abs(p.x)*7.0);gl_FragColor=vec4(0.91,0.81,0.56,(halo+star*0.3)*v_alpha);}');
    gl.compileShader(fragment);
    const program = gl.createProgram();
    gl.attachShader(program, vertex); gl.attachShader(program, fragment); gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return null;
    gl.deleteShader(vertex); gl.deleteShader(fragment);
    gl.useProgram(program);
    const buffer = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    const attribute = gl.getAttribLocation(program, 'a_particle');
    gl.enableVertexAttribArray(attribute); gl.vertexAttribPointer(attribute, 4, gl.FLOAT, false, 0, 0);
    gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
    const resolution = gl.getUniformLocation(program, 'u_resolution');
    const pixelRatio = gl.getUniformLocation(program, 'u_dpr');
    gl.clearColor(0, 0, 0, 0);
    canvas.addEventListener('webglcontextlost', event => { event.preventDefault(); renderer = null; updateAnimation(); $('#render-note').textContent = '动态魔法暂时休息，其他内容和回忆保存不受影响。'; });
    canvas.addEventListener('webglcontextrestored', () => { renderer = makeRenderer(); resize(); updateAnimation(); });
    return { name: 'WebGL', resize(width, height, dpr) {
      canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
      gl.viewport(0, 0, canvas.width, canvas.height); gl.uniform2f(resolution, width, height); gl.uniform1f(pixelRatio, dpr);
    }, draw(points) {
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.bufferData(gl.ARRAY_BUFFER, points, gl.DYNAMIC_DRAW);
      gl.drawArrays(gl.POINTS, 0, points.length / 4);
    } };
  }

  let width = hero.clientWidth, height = hero.clientHeight, frame = 0, lastTime = 0, visible = true;
  const particles = Array.from({ length: 68 }, () => ({ x: Math.random(), y: Math.random(), size: 3 + Math.random() * 7, speed: 6 + Math.random() * 12, phase: Math.random() * 6.28 }));
  const trails = [];
  const points = new Float32Array((68 + 80) * 4);
  let lastPointer = 0;
  try { renderer = makeRenderer(); } catch { renderer = null; }
  function resize() {
    width = hero.clientWidth; height = hero.clientHeight;
    renderer?.resize(width, height, Math.min(window.devicePixelRatio || 1, 2));
  }
  new ResizeObserver(resize).observe(hero);
  resize();
  hero.addEventListener('pointermove', event => {
    if (motionReduced() || event.pointerType === 'touch') return;
    const box = hero.getBoundingClientRect();
    const x = event.clientX - box.left, y = event.clientY - box.top;
    $('.scene-stage').style.setProperty('--px', `${(x / width - .5) * -12}px`);
    $('.scene-stage').style.setProperty('--py', `${(y / height - .5) * -7}px`);
    if (event.timeStamp - lastPointer < 28) return;
    lastPointer = event.timeStamp;
    trails.push({ x, y, age: 0, size: 7 + Math.random() * 8, vx: (Math.random() - .5) * 16 });
    if (trails.length > 80) trails.shift();
  }, { passive: true });
  hero.addEventListener('pointerleave', () => { $('.scene-stage').style.setProperty('--px', '0px'); $('.scene-stage').style.setProperty('--py', '0px'); });
  function animate(now) {
    const delta = Math.min((now - (lastTime || now)) / 1000, .05);
    lastTime = now;
    let count = 0;
    for (const particle of particles) {
      particle.y -= delta * particle.speed / height;
      if (particle.y < -.02) { particle.y = 1.02; particle.x = Math.random(); }
      points[count++] = particle.x * width + Math.sin(now / 4700 + particle.phase) * 17;
      points[count++] = particle.y * height;
      points[count++] = particle.size * (lumos ? 1.55 : 1);
      points[count++] = (.16 + (Math.sin(now / 1900 + particle.phase) + 1) * .18) * (lumos ? 1.6 : 1);
    }
    for (let i = trails.length - 1; i >= 0; i--) {
      const particle = trails[i]; particle.age += delta;
      if (particle.age > 1.05) { trails.splice(i, 1); continue; }
      particle.y -= delta * 17; particle.x += delta * particle.vx;
      points[count++] = particle.x; points[count++] = particle.y;
      points[count++] = particle.size * (1 - particle.age * .65); points[count++] = (1 - particle.age / 1.05) * .85;
    }
    renderer?.draw(points.subarray(0, count), width, height);
    frame = requestAnimationFrame(animate);
  }
  function updateAnimation() {
    cancelAnimationFrame(frame); frame = 0; lastTime = 0;
    if (renderer && visible && !document.hidden && !motionReduced()) frame = requestAnimationFrame(animate);
    if (renderer && motionReduced()) renderer.draw(new Float32Array(0), width, height);
  }
  new IntersectionObserver(entries => { visible = entries[0].isIntersecting; updateAnimation(); }, { threshold: .01 }).observe(hero);
  document.addEventListener('visibilitychange', () => {
    updateAnimation();
    if (document.hidden) stopAudio();
  });
  const navObserver = new IntersectionObserver(entries => {
    for (const entry of entries) if (entry.isIntersecting) $$('.main-nav a').forEach(link => link.classList.toggle('active', link.hash === '#' + entry.target.id));
  }, { rootMargin: '-15% 0px -55% 0px' });
  ['home', 'places', 'memories'].forEach(id => navObserver.observe($('#' + id)));

  updateHouse(); renderMemories(); updateMotion(); updateAnimation();
  $('#render-note').textContent = renderer?.name === 'WebGL' ? '魔法粒子由 WebGL 在你的设备上绘制；离开画面或切到后台时会自动暂停。支持 Retina 屏幕。' : '当前设备使用轻量画面模式；回忆的阅读、保存和导出仍可使用。';
  if (!storageAvailable) {
    $('.local-note').textContent = corruptedStorage ? '已有回忆数据读取异常，为避免覆盖已暂停写入，请先点击「备份回忆」。' : '当前浏览器暂时无法使用本地存储，写故事前请确认已允许保存网站数据。';
  }
})();
