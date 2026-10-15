/* 하복당 가맹 사이트: 아임웹 공통 스크립트
   로딩 화면, 히어로 슬라이더, 탭, 지점 이야기 슬라이더, 하단 상담 바, 섹션 내비, 스크롤 진행 막대,
   GSAP(ScrollTrigger)이 있으면 스크롤 장면 연출까지 붙임.
   스크립트나 GSAP이 없어도 모든 내용은 정지 상태로 그대로 보이게 만듦.
   아임웹 코드 위젯은 내용을 늦게(AJAX) 넣는 경우가 있어, 새 .hbd가 생기면 다시 초기화함. */
(function () {
  'use strict';
  if (window.__hbdBooted) return;
  window.__hbdBooted = true;

  var reduce = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var finePointer = !!(window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches);
  var each = function (list, fn) { Array.prototype.forEach.call(list || [], fn); };
  var $$ = function (sel, root) { return (root || document).querySelectorAll(sel); };
  var hasGsap = function () { return !reduce && window.gsap && window.ScrollTrigger; };

  function inView(el) {
    var r = el.getBoundingClientRect();
    return r.top < (window.innerHeight || 800) && r.bottom > 0;
  }

  function fmt(n, dec) {
    var s = n.toFixed(dec).split('.');
    s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return s.join('.');
  }

  /* 아임웹 고정 헤더 높이 (고정 장면이 헤더 아래에서 멈추도록) */
  function headerOffset() {
    var x = Math.round(window.innerWidth / 2), best = 0;
    [4, 30, 60].forEach(function (y) {
      var el = document.elementFromPoint(x, y);
      while (el && el !== document.body && el !== document.documentElement) {
        if (el.closest && el.closest('.hbd')) break;
        var pos = window.getComputedStyle(el).position;
        if (pos === 'fixed' || pos === 'sticky') {
          var b = el.getBoundingClientRect().bottom;
          if (b > best && b < 220) best = b;
          break;
        }
        el = el.parentElement;
      }
    });
    return Math.round(best);
  }

  function countUp(el) {
    if (el.getAttribute('data-counted')) return;
    el.setAttribute('data-counted', '1');
    var end = parseFloat(el.getAttribute('data-count'));
    var dec = parseInt(el.getAttribute('data-dec') || '0', 10);
    if (!end || reduce) return;
    if (window.gsap) {
      var o = { v: 0 };
      window.gsap.to(o, { v: end, duration: 1.8, ease: 'power3.out', onUpdate: function () { el.textContent = fmt(o.v, dec); }, onComplete: function () { el.textContent = fmt(end, dec); } });
      return;
    }
    var t0 = null, dur = 1500;
    function step(t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / dur, 1);
      el.textContent = fmt(end * (1 - Math.pow(1 - p, 3)), dec);
      if (p < 1) requestAnimationFrame(step); else el.textContent = fmt(end, dec);
    }
    el.textContent = fmt(0, dec);
    requestAnimationFrame(step);
  }

  /* ---------------- 로딩 화면 ---------------- */
  var heroQueue = [];
  var loaderDone = false;
  function onLoaderDone(fn) { if (loaderDone) fn(); else heroQueue.push(fn); }
  function finishLoader() {
    if (loaderDone) return;
    loaderDone = true;
    heroQueue.splice(0).forEach(function (fn) { try { fn(); } catch (e) { /* 다음 작업 계속 */ } });
  }

  function initLoader() {
    var el = document.getElementById('hbd-loader');
    if (!el || el.getAttribute('data-started')) { if (!el) finishLoader(); return; }
    el.setAttribute('data-started', '1');
    var seen = false;
    try { seen = window.sessionStorage.getItem('hbd-loader-seen') === '1'; } catch (e) { seen = false; }
    if (seen || reduce) { el.classList.add('is-gone'); finishLoader(); return; }
    try { window.sessionStorage.setItem('hbd-loader-seen', '1'); } catch (e) { /* 저장소를 못 써도 진행 */ }
    var pct = el.querySelector('.hbd-loader__pct b');
    var start = Date.now(), minT = 2000, maxT = 4800;
    var loaded = document.readyState === 'complete';
    window.addEventListener('load', function () { loaded = true; });
    var shown = 0;
    (function tick() {
      var t = Date.now() - start;
      var target = loaded ? 100 : Math.min(92, (t / maxT) * 100);
      var timeCap = Math.min(100, (t / minT) * 100);
      shown += (Math.min(target, timeCap) - shown) * 0.12;
      if (loaded && t >= minT && shown > 99.4) shown = 100;
      if (pct) pct.textContent = Math.floor(shown);
      if (shown >= 100 || t >= maxT) {
        if (pct) pct.textContent = '100';
        el.classList.add('is-out');
        setTimeout(finishLoader, 380);
        setTimeout(function () { el.classList.add('is-gone'); }, 1000);
        return;
      }
      requestAnimationFrame(tick);
    })();
  }

  /* ---------------- 탭 ---------------- */
  function initTabs(root) {
    each($$('[data-hbd-tabs]', root), function (list) {
      var btns = list.querySelectorAll('[role="tab"]');
      function select(btn, animate) {
        each(btns, function (b) {
          var on = b === btn;
          b.setAttribute('aria-selected', on ? 'true' : 'false');
          b.tabIndex = on ? 0 : -1;
          var p = document.getElementById(b.getAttribute('aria-controls'));
          if (!p) return;
          p.hidden = !on;
          if (on && animate && hasGsap()) {
            window.gsap.from(p.querySelectorAll('.hbd-card, .hbd-split > *, .hbd-chips li'), { y: 40, opacity: 0, duration: .6, stagger: .06, ease: 'power3.out', clearProps: 'transform,opacity' });
          }
        });
        if (window.ScrollTrigger) window.ScrollTrigger.refresh();
      }
      each(btns, function (b, i) {
        b.addEventListener('click', function () { select(b, true); });
        b.addEventListener('keydown', function (e) {
          var n = btns.length, j = -1;
          if (e.key === 'ArrowRight') j = (i + 1) % n;
          if (e.key === 'ArrowLeft') j = (i - 1 + n) % n;
          if (j > -1) { e.preventDefault(); btns[j].focus(); select(btns[j], true); }
        });
      });
      select(list.querySelector('[aria-selected="true"]') || btns[0], false);
    });
  }

  /* ---------------- 자동 슬라이더 (히어로 사진, 지점 이야기) ---------------- */
  function autoSlide(items, dots, ms, host) {
    if (items.length < 2) return;
    var i = 0, timer = null, visible = true;
    function go(n) {
      items[i].classList.remove('is-on'); if (dots[i]) dots[i].classList.remove('is-on');
      i = (n + items.length) % items.length;
      items[i].classList.add('is-on'); if (dots[i]) dots[i].classList.add('is-on');
    }
    function run() { clearInterval(timer); if (!reduce && visible) timer = setInterval(function () { go(i + 1); }, ms); }
    each(dots, function (d, k) { d.addEventListener('click', function () { go(k); run(); }); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { visible = en[0].isIntersecting; run(); }).observe(host);
    }
    run();
  }

  function initSliders(root) {
    each($$('[data-hbd-slider]', root), function (s) {
      autoSlide(s.querySelectorAll('img'), s.querySelectorAll('.hbd-slider__dots i'), 4200, s);
    });
    each($$('[data-hbd-stories]', root), function (s) {
      var nav = s.parentNode.querySelectorAll('.hbd-stories__nav i');
      autoSlide(s.querySelectorAll('article'), nav, 5600, s);
    });
  }

  /* ---------------- 카드 기울이기 ---------------- */
  function initTilt(root) {
    if (!finePointer || reduce) return;
    each($$('.hbd-tilt', root), function (el) {
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        el.style.transform = 'perspective(900px) rotateY(' + (x * 12) + 'deg) rotateX(' + (-y * 12) + 'deg) translateY(-6px)';
      });
      el.addEventListener('mouseleave', function () { el.style.transform = ''; });
    });
  }

  /* ---------------- GSAP이 없을 때: 간단한 등장 효과 ---------------- */
  function initFallbackMotion(root) {
    var targets = [];
    each($$('[data-up], [data-split], [data-pop]', root), function (el) { targets.push(el); });
    each($$('[data-stagger]', root), function (el) { each(el.children, function (c) { targets.push(c); }); });
    var nums = root.querySelectorAll('[data-count]');
    if (!('IntersectionObserver' in window) || reduce) return;
    targets.forEach(function (el) { el.setAttribute('data-reveal', ''); if (inView(el)) el.classList.add('is-in'); });
    root.classList.add('hbd-anim');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-in');
        if (en.target.hasAttribute('data-count')) countUp(en.target);
        io.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    targets.forEach(function (el) { if (!el.classList.contains('is-in')) io.observe(el); });
    each(nums, function (el) { io.observe(el); });
  }

  /* ---------------- GSAP 스크롤 연출 ---------------- */
  function splitLines(el) {
    if (!el.getAttribute('data-split-done')) {
      var parts = el.innerHTML.split(/<br\s*\/?>/i);
      el.innerHTML = parts.map(function (p) { return '<span class="hbd-ln"><span>' + p + '</span></span>'; }).join('');
      el.setAttribute('data-split-done', '1');
    }
    return el.querySelectorAll('.hbd-ln > span');
  }

  function initGsapMotion(root) {
    var gsap = window.gsap, ST = window.ScrollTrigger;
    gsap.registerPlugin(ST);
    root.classList.add('hbd-gsap');
    var hdr = function () { return headerOffset(); };
    var narrow = window.innerWidth <= 960;
    if (root.id === 'hbd-small') { each($$('[data-stagger]', root), function (el) { el.removeAttribute('data-stagger'); }); }

    /* 제목: 줄마다 아래에서 밀려 올라옴 */
    each($$('[data-split]', root), function (el) {
      var lines = splitLines(el);
      if (el.classList.contains('hbd-hero__title')) return;
      gsap.from(lines, { yPercent: 115, rotate: 3, duration: 1, ease: 'power4.out', stagger: .13, scrollTrigger: { trigger: el, start: 'top 86%' } });
    });
    each($$('.hbd-head .hbd-eyebrow', root), function (el) {
      gsap.from(el, { letterSpacing: '.6em', opacity: 0, duration: 1.1, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 90%' } });
    });
    each($$('[data-up]', root), function (el) {
      gsap.from(el, { y: 60, opacity: 0, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 88%' } });
    });
    each($$('[data-stagger]', root), function (el) {
      var pop = el.classList.contains('hbd-stores') || el.classList.contains('hbd-limit') || el.classList.contains('hbd-mkt__list');
      gsap.from(el.children, pop
        ? { scale: 0, opacity: 0, rotate: -12, duration: .8, ease: 'back.out(2.2)', stagger: .05, scrollTrigger: { trigger: el, start: 'top 85%' } }
        : { y: 80, opacity: 0, rotateX: -14, transformOrigin: '50% 0%', duration: 1, ease: 'power3.out', stagger: .12, scrollTrigger: { trigger: el, start: 'top 86%' } });
    });
    each($$('[data-count]', root), function (el) {
      if (el.closest('.hbd-hero') || el.closest('#hbd-small')) return;
      ST.create({ trigger: el, start: 'top 92%', once: true, onEnter: function () { countUp(el); } });
    });
    each($$('[data-pop]', root), function (el) {
      gsap.from(el, { scale: 0, rotate: -25, duration: 1.1, ease: 'elastic.out(1,.5)', scrollTrigger: { trigger: el, start: 'top 88%' },
        onComplete: function () { gsap.to(el, { rotate: '+=5', y: -4, duration: 1.3, yoyo: true, repeat: -1, ease: 'sine.inOut' }); } });
    });
    each($$('[data-parallax]', root), function (img) {
      gsap.fromTo(img, { yPercent: -7 }, { yPercent: 7, ease: 'none', scrollTrigger: { trigger: img.parentNode, start: 'top bottom', end: 'bottom top', scrub: true } });
    });
    each($$('[data-float]', root), function (el) {
      var sp = parseFloat(el.getAttribute('data-float')) || 1;
      gsap.to(el, { y: -140 * sp, rotate: 40 * sp, ease: 'none', scrollTrigger: { trigger: root, start: 'top bottom', end: 'bottom top', scrub: 1 } });
    });
    each($$('.hbd-bigword span', root), function (el) {
      gsap.fromTo(el, { xPercent: 0 }, { xPercent: -30, ease: 'none', scrollTrigger: { trigger: root, start: 'top bottom', end: 'bottom top', scrub: 1 } });
    });
    each($$('[data-marquee] ul', root), function (ul) { ul.setAttribute('data-skew', ''); });

    /* 히어로: 로딩이 끝나면 한 번에 등장 */
    if (root.id === 'hbd-top') {
      var lines = root.querySelectorAll('.hbd-hero__title .hbd-ln > span');
      var q = function (s) { return root.querySelectorAll(s); };
      gsap.set(lines, { yPercent: 115 });
      gsap.set(q('[data-hero="pill"],[data-hero="lead"],[data-hero="cta"]'), { y: 30, opacity: 0 });
      gsap.set(q('[data-hero="visual"]'), { scale: .82, rotate: -5, opacity: 0 });
      gsap.set(q('[data-hero="sticker"]'), { scale: 0 });
      gsap.set(q('.hbd-float > span'), { scale: 0 });
      onLoaderDone(function () {
        var tl = gsap.timeline({ defaults: { ease: 'power4.out' } });
        tl.to(q('[data-hero="pill"]'), { y: 0, opacity: 1, duration: .7 })
          .to(lines, { yPercent: 0, duration: 1.1, stagger: .14 }, '-=.4')
          .to(q('[data-hero="visual"]'), { scale: 1, rotate: 0, opacity: 1, duration: 1.3, ease: 'back.out(1.4)' }, '-=1')
          .to(q('[data-hero="lead"],[data-hero="cta"]'), { y: 0, opacity: 1, duration: .8, stagger: .12 }, '-=.9')
          .to(q('[data-hero="sticker"]'), { scale: 1, duration: 1, ease: 'elastic.out(1,.45)', stagger: .15 }, '-=.6')
          .to(q('.hbd-float > span'), { scale: 1, duration: .9, ease: 'back.out(2)', stagger: .07 }, '-=1');
      });
      gsap.to(q('.hbd-hero__copy'), { y: -80, opacity: .25, ease: 'none', scrollTrigger: { trigger: root, start: 'top top', end: 'bottom top', scrub: true } });
      gsap.to(q('.hbd-hero__visual'), { y: 60, ease: 'none', scrollTrigger: { trigger: root, start: 'top top', end: 'bottom top', scrub: true } });
    }

    /* 소자본 창업: 화면에 고정된 채 사진이 줌아웃되고 카드가 올라옴 */
    if (root.id === 'hbd-small') {
      var bg = root.querySelector('.hbd-small__bg img');
      var cards = root.querySelectorAll('.hbd-small__cards > li');
      var tl2 = gsap.timeline({ scrollTrigger: { trigger: root, start: function () { return 'top ' + hdr() + 'px'; }, end: '+=110%', pin: true, scrub: 1, anticipatePin: 1, invalidateOnRefresh: true,
        onEnter: function () { each(root.querySelectorAll('[data-count]'), countUp); } } });
      tl2.fromTo(bg, { scale: 1.35 }, { scale: 1, ease: 'none' }, 0)
        .fromTo(cards, { y: 220, opacity: 0, rotate: function (i) { return (i - 1) * 6; } }, { y: 0, opacity: 1, rotate: 0, stagger: .18, ease: 'power2.out' }, .05);
    }

    /* 실제 운영 데이터: 막대와 도넛이 그려짐 */
    if (root.id === 'hbd-auto') {
      var card = root.querySelector('.hbd-auto__card');
      gsap.from(root.querySelectorAll('.hbd-auto__tiles i'), { width: 0, duration: 1.4, ease: 'power3.out', stagger: .15, scrollTrigger: { trigger: card, start: 'top 75%' } });
      gsap.from(root.querySelectorAll('.hbd-donut .seg'), { attr: { 'stroke-dasharray': '0 251.33' }, duration: .7, ease: 'power2.inOut', stagger: .35, scrollTrigger: { trigger: root.querySelector('.hbd-donut'), start: 'top 80%' } });
      gsap.from(root.querySelectorAll('.hbd-legend li'), { x: 30, opacity: 0, stagger: .1, duration: .6, scrollTrigger: { trigger: root.querySelector('.hbd-donut'), start: 'top 80%' } });
      gsap.from(root.querySelector('.hbd-auto__profit'), { scale: .7, opacity: 0, duration: 1, ease: 'back.out(1.8)', scrollTrigger: { trigger: root.querySelector('.hbd-auto__profit'), start: 'top 85%' } });
    }

    /* 원가 비교: 양쪽 카드가 부딪히듯 들어오고 VS가 돎 */
    if (root.id === 'hbd-supply') {
      var trig = { trigger: root.querySelector('.hbd-vs'), start: 'top 75%' };
      gsap.from(root.querySelector('[data-vs="left"]'), { x: -160, rotate: -6, opacity: 0, duration: 1.1, ease: 'power3.out', scrollTrigger: trig });
      gsap.from(root.querySelector('[data-vs="right"]'), { x: 160, rotate: 6, opacity: 0, duration: 1.1, ease: 'power3.out', scrollTrigger: trig });
      gsap.from(root.querySelector('[data-vs="badge"]'), { scale: 0, rotate: -540, duration: 1.4, delay: .5, ease: 'back.out(1.7)', scrollTrigger: trig });
      gsap.from(root.querySelectorAll('.hbd-route li'), { x: -24, opacity: 0, stagger: .07, duration: .5, delay: .6, scrollTrigger: trig });
      gsap.from(root.querySelectorAll('.hbd-vs__price'), { scale: .6, opacity: 0, duration: .9, delay: 1.1, ease: 'elastic.out(1,.6)', stagger: .2, scrollTrigger: trig });
    }

    /* 박스당 1,000원 */
    if (root.id === 'hbd-satisfy') {
      var fig = root.querySelector('.hbd-satisfy__fig .big');
      gsap.from(fig, { scale: .3, opacity: 0, duration: 1.4, ease: 'elastic.out(1,.55)', scrollTrigger: { trigger: fig, start: 'top 82%' } });
    }

    /* 지점 이야기: 차양이 떨어지듯 내려옴 */
    if (root.id === 'hbd-story') {
      gsap.from(root.querySelector('.hbd-storybox__roof'), { y: -80, rotateX: 70, transformOrigin: '50% 0%', opacity: 0, duration: 1.2, ease: 'bounce.out', scrollTrigger: { trigger: root.querySelector('.hbd-storybox'), start: 'top 80%' } });
    }

    /* 손익표: 표의 행이 차례로 채워짐 */
    if (root.id === 'hbd-multi') {
      each(root.querySelectorAll('.hbd-plc'), function (art) {
        gsap.from(art.querySelectorAll('tbody tr, tfoot tr'), { x: -24, opacity: 0, stagger: .05, duration: .45, ease: 'power2.out', scrollTrigger: { trigger: art, start: 'top 70%' } });
      });
    }

    /* 문의 현황: 타임라인 막대가 스크롤에 맞춰 채워짐 */
    if (root.id === 'hbd-demand') {
      var bar = root.querySelector('.hbd-timeline__bar i');
      var tlx = root.querySelector('.hbd-timeline');
      gsap.fromTo(bar, narrow ? { scaleY: 0 } : { scaleX: 0 }, { scaleX: 1, scaleY: 1, ease: 'none', scrollTrigger: { trigger: tlx, start: 'top 75%', end: 'bottom 50%', scrub: true } });
      gsap.from(tlx.querySelectorAll('li'), { scale: .5, opacity: 0, stagger: .15, duration: .7, ease: 'back.out(2)', scrollTrigger: { trigger: tlx, start: 'top 75%' } });
    }

    /* 신메뉴: 화면에 고정된 채 포스터가 가로로 지나감 */
    if (root.id === 'hbd-new') {
      var pinEl = root.querySelector('.hbd-new__pin');
      var track = root.querySelector('.hbd-new__track');
      var dist = function () { return Math.max(0, track.scrollWidth - window.innerWidth); };
      var tween = gsap.to(track, { x: function () { return -dist(); }, ease: 'none',
        scrollTrigger: { trigger: pinEl, start: function () { return 'top ' + hdr() + 'px'; }, end: function () { return '+=' + dist(); }, pin: true, scrub: 1, anticipatePin: 1, invalidateOnRefresh: true } });
      each(track.querySelectorAll('li'), function (li) {
        gsap.fromTo(li, { rotateY: -32, scale: .82, opacity: .55 }, { rotateY: 0, scale: 1, opacity: 1, ease: 'none',
          scrollTrigger: { trigger: li, containerAnimation: tween, start: 'left 98%', end: 'center 55%', scrub: true } });
      });
    }

    /* 원가 문장: 배경 사진이 천천히 줌아웃 */
    if (root.id === 'hbd-cintro') {
      gsap.fromTo(root.querySelector('.hbd-cintro__bg img'), { scale: 1.35 }, { scale: 1, ease: 'none', scrollTrigger: { trigger: root, start: 'top bottom', end: 'bottom top', scrub: true } });
    }

    /* 마케팅: 고정된 화면 위로 포스터가 날아오름 */
    if (root.id === 'hbd-marketing') {
      var stage = root.querySelector('.hbd-mkt__stage');
      var posters = root.querySelectorAll('.hbd-mkt__posters img');
      var tl3 = gsap.timeline({ scrollTrigger: { trigger: stage, start: function () { return 'top ' + hdr() + 'px'; }, end: '+=130%', pin: true, scrub: 1, anticipatePin: 1, invalidateOnRefresh: true } });
      each(posters, function (p, i) {
        var vh = window.innerHeight;
        tl3.fromTo(p, { y: vh * (0.75 + (i % 3) * 0.2), rotate: (i % 2 ? 14 : -14), scale: .8 },
          { y: -vh * (0.65 + (i % 4) * 0.15), rotate: (i % 2 ? -10 : 10), scale: 1.05, ease: 'none' }, (i % 4) * 0.06);
      });
      tl3.fromTo(root.querySelector('.hbd-mkt__in'), { scale: .85, opacity: 0 }, { scale: 1, opacity: 1, ease: 'power2.out', duration: .25 }, 0);
    }

    /* 운영 구조: 카드가 위로 겹쳐 쌓임 */
    if (root.id === 'hbd-operation') {
      var ops = root.querySelectorAll('.hbd-ops > li');
      if (ops.length > 1) {
        var tl4 = gsap.timeline({ scrollTrigger: { trigger: root, start: function () { return 'top ' + hdr() + 'px'; }, end: '+=' + (ops.length - 1) * 85 + '%', pin: true, scrub: 1, anticipatePin: 1, invalidateOnRefresh: true } });
        each(ops, function (li, i) {
          if (i === 0) return;
          tl4.fromTo(li, { yPercent: 160, rotate: 5 }, { yPercent: i * 6, rotate: 0, ease: 'power2.out' }, i - 1)
            .to(ops[i - 1], { scale: .93, opacity: .6, ease: 'none' }, i - 1);
        });
      }
    }

    /* 창업 비용: 행이 차례로 들어옴 */
    if (root.id === 'hbd-cost') {
      var rows = root.querySelectorAll('[data-rows] tr, tfoot tr');
      gsap.from(rows, { x: -40, opacity: 0, stagger: .1, duration: .6, ease: 'power3.out', scrollTrigger: { trigger: root.querySelector('.hbd-cost'), start: 'top 70%' } });
    }

    /* 절차: 진행선이 차고 단계가 하나씩 켜짐 */
    if (root.id === 'hbd-process') {
      var wrap = root.querySelector('.hbd-steps-wrap');
      var fill = root.querySelector('.hbd-steps__line i');
      var steps = root.querySelectorAll('.hbd-steps > li');
      gsap.set(fill, { scaleX: 0 });
      ST.create({ trigger: wrap, start: 'top 78%', end: 'bottom 45%', scrub: true,
        onUpdate: function (self) {
          gsap.set(fill, { scaleX: self.progress });
          var n = Math.round(self.progress * steps.length);
          each(steps, function (s, k) { s.classList.toggle('is-lit', k < n && !s.classList.contains('is-key')); });
        } });
      gsap.from(steps, { y: 50, opacity: 0, stagger: .1, duration: .8, ease: 'power3.out', scrollTrigger: { trigger: wrap, start: 'top 85%' } });
    }
  }

  /* 스크롤 속도에 따라 흐르는 띠가 기울어짐 */
  function initSkew() {
    if (!hasGsap() || window.__hbdSkew) return;
    window.__hbdSkew = true;
    var set = function (v) { each($$('[data-skew]'), function (el) { el.style.transform = 'skewX(' + v + 'deg)'; }); };
    var cur = 0;
    window.ScrollTrigger.create({ start: 0, end: 'max', onUpdate: function (self) {
      var v = Math.max(-14, Math.min(14, self.getVelocity() / -250));
      if (Math.abs(v) > Math.abs(cur)) { cur = v; set(cur); window.gsap.to({ v: cur }, { v: 0, duration: .8, ease: 'power3.out', overwrite: true, onUpdate: function () { cur = this.targets()[0].v; set(cur); } }); }
    } });
  }

  /* ---------------- 하단 상담 바 ---------------- */
  function initDock() {
    if (document.querySelector('.hbd-dock')) return;
    var hero = document.getElementById('hbd-top');
    var contact = document.getElementById('hbd-contact');
    if (!hero || !contact) return;
    var tel = contact.getAttribute('data-tel') || '';
    var dock = document.createElement('div');
    dock.className = 'hbd-dock';
    dock.setAttribute('role', 'region');
    dock.setAttribute('aria-label', '가맹 상담 바로가기');
    dock.innerHTML = '<div class="hbd-dock__in"><p class="hbd-dock__txt"><b>하복당 가맹 1:1 미팅</b> <span class="opt">· 서울·경기·인천 50호점까지만 모집</span></p>' +
      (tel ? '<a class="tel" href="tel:' + tel.replace(/[^0-9+]/g, '') + '">' + tel + '</a>' : '') +
      '<a class="go" href="#hbd-contact">미팅 신청</a></div>';
    document.body.appendChild(dock);
    /* 히어로를 지나면 나타나고, 문의 섹션부터 그 아래(입력폼)에서는 숨김 */
    var ticking = false;
    function sync() {
      ticking = false;
      var on = hero.getBoundingClientRect().bottom < 0 && contact.getBoundingClientRect().top > window.innerHeight * 0.85;
      dock.classList.toggle('is-on', on);
    }
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(sync); } }, { passive: true });
    window.addEventListener('resize', sync);
    sync();
  }

  /* ---------------- 스크롤 진행 막대와 섹션 내비 ---------------- */
  function initChrome() {
    if (!document.getElementById('hbd-top')) return;
    if (!document.querySelector('.hbd-progress')) {
      var bar = document.createElement('div');
      bar.className = 'hbd-progress';
      bar.innerHTML = '<i></i>';
      document.body.appendChild(bar);
      var fill = bar.firstChild, ticking = false;
      var upd = function () {
        ticking = false;
        var h = document.documentElement.scrollHeight - window.innerHeight;
        fill.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, window.pageYOffset / h) : 0) + ')';
      };
      window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(upd); } }, { passive: true });
      upd();
    }
    var secs = document.querySelectorAll('.hbd[data-nav]');
    var nav = document.querySelector('.hbd-nav');
    if (!nav) {
      nav = document.createElement('nav');
      nav.className = 'hbd-nav';
      nav.setAttribute('aria-label', '섹션 바로가기');
      document.body.appendChild(nav);
    }
    nav.innerHTML = '';
    each(secs, function (s) {
      var a = document.createElement('a');
      a.href = '#' + s.id;
      a.innerHTML = '<span>' + s.getAttribute('data-nav') + '</span>';
      a.setAttribute('aria-label', s.getAttribute('data-nav'));
      nav.appendChild(a);
    });
    var links = nav.querySelectorAll('a');
    var hero = document.getElementById('hbd-top');
    var update = function () {
      var mid = window.innerHeight * .45, active = -1;
      each(secs, function (s, i) { var r = s.getBoundingClientRect(); if (r.top <= mid) active = i; });
      each(links, function (a, i) { a.classList.toggle('is-on', i === active); });
      nav.classList.toggle('is-on', hero.getBoundingClientRect().bottom < 0);
    };
    if (!window.__hbdNavScroll) {
      window.__hbdNavScroll = true;
      var t = false;
      window.addEventListener('scroll', function () { if (!t) { t = true; requestAnimationFrame(function () { t = false; update(); }); } }, { passive: true });
    }
    update();
  }

  function initAnchors() {
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href^="#hbd-"]');
      if (!a) return;
      var t = document.getElementById(a.getAttribute('href').slice(1));
      if (!t) return;
      e.preventDefault();
      var y = t.getBoundingClientRect().top + window.pageYOffset - headerOffset();
      window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
    });
  }

  /* ---------------- 시작 ---------------- */
  var anchorsDone = false;
  function init() {
    initLoader();
    var roots = document.querySelectorAll('.hbd:not([data-hbd-ready])');
    if (!roots.length) return;
    each(roots, function (root) {
      root.setAttribute('data-hbd-ready', '');
      root.classList.add('hbd-js');
      try {
        initTabs(root);
        initSliders(root);
        initTilt(root);
        if (hasGsap()) initGsapMotion(root); else initFallbackMotion(root);
      } catch (err) {
        root.classList.remove('hbd-gsap');
        if (window.console) console.warn('[hbd]', err);
      }
    });
    if (!hasGsap()) onLoaderDone(function () {
      each($$('#hbd-top [data-count]'), countUp);
    });
    initSkew();
    initDock();
    initChrome();
    if (!anchorsDone) { initAnchors(); anchorsDone = true; }
    if (window.ScrollTrigger) setTimeout(function () { window.ScrollTrigger.refresh(); }, 60);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  window.addEventListener('load', function () {
    init();
    if (window.ScrollTrigger) window.ScrollTrigger.refresh();
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (window.ScrollTrigger) window.ScrollTrigger.refresh(); });
  if ('MutationObserver' in window) {
    var pending = null;
    var mo = new MutationObserver(function () {
      if (pending) return;
      pending = setTimeout(function () { pending = null; if (document.querySelector('.hbd:not([data-hbd-ready])')) init(); }, 120);
    });
    var start = function () { if (document.body) mo.observe(document.body, { childList: true, subtree: true }); };
    if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
    setTimeout(function () { mo.disconnect(); }, 20000);
  }
})();
