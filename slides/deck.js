/* deck.js - NTUT workshop lecture slides engine. Vanilla, no dependencies. Contract: site/slides/README.md.
   Keys: Right/Space/PageDown next, Left/PageUp prev, Home/End, F fullscreen, N teacher notes, O overview, Esc close.
   Also: click right/left half, touch swipe, #n deep link (browser Back works), data-anim animations. */
(function () {
  'use strict';
  var d = document, root = d.documentElement, body = d.body;
  root.classList.remove('no-js');
  var deck = d.querySelector('main.deck');
  if (!deck) return;
  var slides = Array.prototype.slice.call(deck.querySelectorAll(':scope > section.slide'));
  var N = slides.length;
  if (!N) return;
  var cur = -1, overviewOpen = false;
  var lessonN = deck.getAttribute('data-lesson') || '';
  var lessonName = deck.getAttribute('data-title') || (lessonN ? '第' + ['', '一', '二', '三', '四'][+lessonN] + '堂' : '工作坊');

  function el(tag, cls, txt) {
    var e = d.createElement(tag);
    if (cls) e.className = cls;
    if (txt) e.textContent = txt;
    return e;
  }

  /* ---- footer on each slide ---- */
  slides.forEach(function (s, i) {
    if (s.querySelector('.slide-foot')) return;
    var f = el('footer', 'slide-foot');
    f.appendChild(el('span', 'lesson', 'NTUT 工作坊　' + lessonName));
    if (lessonN) {
      var a = el('a', null, '實作頁');
      a.href = 'https://goodedunote.web.app/prepare/session1-lab.html';
      f.appendChild(a);
    }
    f.appendChild(el('span', 'count', (i + 1) + ' / ' + N));
    s.appendChild(f);
  });

  /* ---- chrome ---- */
  var bar = el('div', 'deck-progress');
  bar.setAttribute('role', 'progressbar');
  bar.setAttribute('aria-valuemin', '1');
  bar.setAttribute('aria-valuemax', String(N));
  body.appendChild(bar);
  var firstHandoff = document.querySelector('.slide .handoff'); if (firstHandoff) firstHandoff.classList.add('first');
  var hint = el('div', 'deck-hint', '← → 換頁　F 全螢幕　O 總覽');
  body.appendChild(hint);
  var live = el('div');
  live.setAttribute('aria-live', 'polite');
  live.style.cssText = 'position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)';
  body.appendChild(live);
  try { if (!sessionStorage.getItem('deck-hint')) { body.classList.add('show-hint'); sessionStorage.setItem('deck-hint', '1'); setTimeout(function () { body.classList.remove('show-hint'); }, 5000); } } catch (e) {}

  /* ---- scale ---- */
  function fit() {
    var s = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    root.style.setProperty('--s', String(s));
    if (overviewOpen) sizeThumbs();
  }
  window.addEventListener('resize', fit);
  fit();

  /* ---- animation ---- */
  function playAnims(s) {
    var items = s.querySelectorAll('[data-anim]');
    Array.prototype.forEach.call(items, function (n) {
      n.classList.remove('play');
      var dl = n.getAttribute('data-anim-delay'), du = n.getAttribute('data-anim-dur');
      n.style.animationDelay = dl ? parseFloat(dl) + 's' : '';
      if (du) n.style.setProperty('--dur', parseFloat(du) + 's');
    });
    if (!items.length) return;
    void s.offsetWidth;
    Array.prototype.forEach.call(items, function (n) { n.classList.add('play'); });
  }

  /* ---- show ---- */
  function clamp(i) { return Math.max(0, Math.min(N - 1, i)); }
  function show(i) {
    i = clamp(i);
    if (i === cur) return;
    if (cur >= 0) { slides[cur].classList.remove('active'); var au = slides[cur].querySelector('audio'); if (au && !au.paused) au.pause(); }
    cur = i;
    slides[i].classList.add('active');
    playAnims(slides[i]);
    bar.style.width = ((i + 1) / N * 100) + '%';
    bar.setAttribute('aria-valuenow', String(i + 1));
    var k = slides[i].querySelector('.key');
    live.textContent = (i + 1) + ' / ' + N + (k ? '　' + k.textContent.trim() : '');
    if (overviewOpen) markCurrent();
  }
  function fromHash() {
    var h = decodeURIComponent((location.hash || '').replace(/^#/, ''));
    if (/^\d+$/.test(h)) return clamp(parseInt(h, 10) - 1);
    if (h) { for (var i = 0; i < N; i++) if (slides[i].id === h) return i; }
    return 0;
  }
  function go(i) {
    i = clamp(i);
    if (i === cur) return;
    try { history.pushState(null, '', '#' + (i + 1)); } catch (e) { location.hash = '#' + (i + 1); }
    show(i);
  }
  window.addEventListener('hashchange', function () { show(fromHash()); });
  (function init() {
    var i = fromHash();
    if (!/^#\d+$/.test(location.hash)) {
      try { history.replaceState(null, '', '#' + (i + 1)); } catch (e) {}
    }
    show(i);
  })();

  /* ---- audio with a transcript that follows it: <audio> plus <div class="cues"><p data-t="12.5">…</p></div> ---- */
  slides.forEach(function (s) {
    var au = s.querySelector('audio'), box = s.querySelector('.cues');
    if (!au || !box) return;
    var ps = Array.prototype.slice.call(box.querySelectorAll('[data-t]'));
    var ts = ps.map(function (p) { return parseFloat(p.getAttribute('data-t')) || 0; });
    var last = -2;
    function sync() {
      var t = au.currentTime, on = -1;
      for (var i = 0; i < ts.length; i++) { if (t >= ts[i]) on = i; else break; }
      if (on === last) return;
      last = on;
      ps.forEach(function (p, i) { p.classList.toggle('on', i === on); p.classList.toggle('past', i < on); });
      if (on >= 0) box.scrollTop = ps[on].offsetTop - box.clientHeight / 2 + ps[on].clientHeight / 2;
    }
    au.addEventListener('timeupdate', sync);
    au.addEventListener('seeked', sync);
    ps.forEach(function (p, i) {
      p.addEventListener('click', function () { au.currentTime = ts[i]; au.play(); });
    });
  });

  /* ---- fullscreen / notes / overview ---- */
  function fullscreen() {
    try {
      if (d.fullscreenElement) d.exitFullscreen();
      else if (root.requestFullscreen) root.requestFullscreen();
    } catch (e) {}
  }
  function toggleNotes() { body.classList.toggle('show-notes'); }

  var ov = null;
  function sizeThumbs() {
    if (!ov) return;
    Array.prototype.forEach.call(ov.children, function (t) {
      var w = t.clientWidth - 6;
      var inner = t.firstChild;
      if (inner) inner.style.transform = 'scale(' + (w / 1280) + ')';
    });
  }
  function markCurrent() {
    if (!ov) return;
    Array.prototype.forEach.call(ov.children, function (t, i) { t.classList.toggle('current', i === cur); });
    var c = ov.children[cur];
    if (c && c.scrollIntoView) c.scrollIntoView({ block: 'nearest' });
  }
  function buildOverview() {
    ov = el('div', 'deck-overview');
    ov.setAttribute('role', 'dialog');
    ov.setAttribute('aria-label', '簡報總覽');
    slides.forEach(function (s, i) {
      var t = el('button', 'deck-thumb');
      t.type = 'button';
      t.setAttribute('aria-label', '第 ' + (i + 1) + ' 張');
      var inner = el('div', 'inner');
      var c = s.cloneNode(true);
      c.classList.add('active');
      c.removeAttribute('id');
      Array.prototype.forEach.call(c.querySelectorAll('[id]'), function (n) { n.removeAttribute('id'); });
      Array.prototype.forEach.call(c.querySelectorAll('a,button'), function (n) { n.setAttribute('tabindex', '-1'); });
      inner.appendChild(c);
      t.appendChild(inner);
      t.appendChild(el('span', 'num', String(i + 1)));
      t.addEventListener('click', function () { closeOverview(); go(i); });
      ov.appendChild(t);
    });
    body.appendChild(ov);
  }
  function openOverview() {
    if (!ov) buildOverview();
    overviewOpen = true;
    body.classList.add('show-overview');
    sizeThumbs();
    markCurrent();
    var c = ov.children[cur];
    if (c) c.focus();
  }
  function closeOverview() {
    overviewOpen = false;
    body.classList.remove('show-overview');
  }

  /* ---- keyboard ---- */
  d.addEventListener('keydown', function (e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    var t = e.target, tag = t && t.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || tag === 'AUDIO') return;
    var k = e.key, used = true;
    if (overviewOpen) {
      if (k === 'Escape' || k === 'o' || k === 'O') closeOverview();
      else if (k === 'Enter' && t && t.classList && t.classList.contains('deck-thumb')) return;
      else used = false;
      if (used) e.preventDefault();
      return;
    }
    if (k === 'ArrowRight' || k === 'PageDown' || (k === ' ' && !e.shiftKey)) go(cur + 1);
    else if (k === 'ArrowLeft' || k === 'PageUp' || (k === ' ' && e.shiftKey)) go(cur - 1);
    else if (k === 'Home') go(0);
    else if (k === 'End') go(N - 1);
    else if (k === 'f' || k === 'F') fullscreen();
    else if (k === 'n' || k === 'N') toggleNotes();
    else if (k === 'o' || k === 'O') openOverview();
    else used = false;
    if (used) e.preventDefault();
  });

  /* ---- click left/right half ---- */
  d.addEventListener('click', function (e) {
    if (overviewOpen || e.defaultPrevented || e.button) return;
    if (e.target.closest && e.target.closest('a,button,summary,input,select,textarea,audio,.cues,.notes,.deck-overview')) return;
    var sel = window.getSelection && window.getSelection();
    if (sel && String(sel).length) return;
    go(e.clientX < window.innerWidth / 2 ? cur - 1 : cur + 1);
  });

  /* ---- touch swipe ---- */
  var tx = 0, ty = 0, tt = 0;
  d.addEventListener('touchstart', function (e) {
    if (e.touches.length !== 1) return;
    tx = e.touches[0].clientX; ty = e.touches[0].clientY; tt = Date.now();
  }, { passive: true });
  d.addEventListener('touchend', function (e) {
    if (overviewOpen || !e.changedTouches.length) return;
    var dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5 && Date.now() - tt < 800) {
      go(dx < 0 ? cur + 1 : cur - 1);
      swiped = Date.now();
    }
  }, { passive: true });
  var swiped = 0;
  d.addEventListener('click', function (e) { if (Date.now() - swiped < 400) e.stopImmediatePropagation(); }, true);
})();
