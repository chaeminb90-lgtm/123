/* 하복당 가맹 사이트 — 아임웹 공통 스크립트
   탭, 숫자 카운트, 스크롤 등장, 하단 상담 바. 스크립트가 없어도 내용은 모두 보이게 만듦. */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function inView(el) {
    var r = el.getBoundingClientRect();
    return r.top < (window.innerHeight || 800) && r.bottom > 0;
  }

  function initTabs(root) {
    var lists = root.querySelectorAll('[data-hbd-tabs]');
    Array.prototype.forEach.call(lists, function (list) {
      var btns = list.querySelectorAll('[role="tab"]');
      function select(btn) {
        Array.prototype.forEach.call(btns, function (b) {
          var on = b === btn;
          b.setAttribute('aria-selected', on ? 'true' : 'false');
          b.tabIndex = on ? 0 : -1;
          var p = document.getElementById(b.getAttribute('aria-controls'));
          if (p) p.hidden = !on;
        });
      }
      Array.prototype.forEach.call(btns, function (b, i) {
        b.addEventListener('click', function () { select(b); });
        b.addEventListener('keydown', function (e) {
          var k = e.key, n = btns.length, j = -1;
          if (k === 'ArrowRight') j = (i + 1) % n;
          if (k === 'ArrowLeft') j = (i - 1 + n) % n;
          if (j > -1) { e.preventDefault(); btns[j].focus(); select(btns[j]); }
        });
      });
      select(list.querySelector('[aria-selected="true"]') || btns[0]);
    });
  }

  function fmt(n, dec) {
    var s = n.toFixed(dec).split('.');
    s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return s.join('.');
  }

  function countUp(el) {
    if (el.getAttribute('data-counted') || reduce) return;
    el.setAttribute('data-counted', '1');
    var end = parseFloat(el.getAttribute('data-count'));
    var dec = parseInt(el.getAttribute('data-dec') || '0', 10);
    if (!end) return;
    var t0 = null, dur = 1400;
    function step(t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / dur, 1);
      el.textContent = fmt(end * (1 - Math.pow(1 - p, 3)), dec);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = fmt(end, dec);
    }
    el.textContent = fmt(0, dec);
    requestAnimationFrame(step);
  }

  function initMotion(root) {
    var items = root.querySelectorAll('[data-reveal]');
    var nums = root.querySelectorAll('[data-count]');
    if (!('IntersectionObserver' in window) || reduce) return;
    Array.prototype.forEach.call(items, function (el) { if (inView(el)) el.classList.add('is-in'); });
    root.classList.add('hbd-anim');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-in');
        if (en.target.hasAttribute('data-count')) countUp(en.target);
        io.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    Array.prototype.forEach.call(items, function (el) { if (!el.classList.contains('is-in')) io.observe(el); });
    Array.prototype.forEach.call(nums, function (el) { io.observe(el); });
  }

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
    var heroOut = false, contactIn = false;
    function sync() { dock.classList.toggle('is-on', heroOut && !contactIn); }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (e) { heroOut = !e[0].isIntersecting; sync(); }).observe(hero);
      new IntersectionObserver(function (e) { contactIn = e[0].isIntersecting; sync(); }).observe(contact);
    } else {
      heroOut = true; sync();
    }
  }

  function initAnchors() {
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href^="#hbd-"]');
      if (!a) return;
      var t = document.getElementById(a.getAttribute('href').slice(1));
      if (!t) return;
      e.preventDefault();
      t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    });
  }

  var done = false;
  function init() {
    var roots = document.querySelectorAll('.hbd:not([data-hbd-ready])');
    Array.prototype.forEach.call(roots, function (root) {
      root.setAttribute('data-hbd-ready', '');
      root.classList.add('hbd-js');
      initTabs(root);
      initMotion(root);
    });
    initDock();
    if (!done) { initAnchors(); done = true; }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
  window.addEventListener('load', init);
  // 아임웹 코드 위젯은 페이지가 뜬 뒤 AJAX로 내용을 넣는 경우가 있어, 새 .hbd가 생기면 다시 초기화
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
