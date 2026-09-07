/* ══════════════════════════════════════════════════════════════════
   La Sombra
   Native scrolling stays intact; scroll-linked visuals are lerped in a
   single rAF loop. Every module is guarded so pages only pay for what
   they actually use.
   ══════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
  var lerp  = function (a, b, t) { return a + (b - a) * t; };
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', function (e) { reduce = e.matches; });

  var page = document.body.dataset.page;

  /* ── shared rAF ───────────────────────────────────────────── */
  var jobs = [], running = false, frame = { y: 0, vh: 0 };
  function tick() {
    frame.y = window.scrollY || 0;
    frame.vh = window.innerHeight;
    var busy = false;
    for (var i = 0; i < jobs.length; i++) if (jobs[i](frame) === true) busy = true;
    if (busy) requestAnimationFrame(tick); else running = false;
  }
  function kick() { if (!running) { running = true; requestAnimationFrame(tick); } }
  addEventListener('scroll', kick, { passive: true });
  addEventListener('resize', kick, { passive: true });

  /* ── bar ──────────────────────────────────────────────────── */
  (function () {
    var bar = $('#bar'); if (!bar) return;
    var on = null;
    jobs.push(function (f) {
      var want = f.y > 24;
      if (want !== on) { on = want; bar.classList.toggle('is-lifted', want); }
      return false;
    });
  })();

  /* ── mobile sheet ─────────────────────────────────────────── */
  (function () {
    var b = $('#burger'), s = $('#sheet'); if (!b || !s) return;
    var open = false, last = null;
    function set(v) {
      if (v === open) return;
      open = v;
      b.setAttribute('aria-expanded', String(v));
      b.setAttribute('aria-label', v ? 'Close menu' : 'Open menu');
      document.body.style.overflow = v ? 'hidden' : '';
      if (v) {
        last = document.activeElement; s.hidden = false;
        requestAnimationFrame(function () { s.classList.add('is-open'); });
        var a = s.querySelector('a'); if (a) a.focus({ preventScroll: true });
      } else {
        s.classList.remove('is-open');
        setTimeout(function () { if (!open) s.hidden = true; }, 300);
        if (last) last.focus({ preventScroll: true });
      }
    }
    b.addEventListener('click', function () { set(!open); });
    document.addEventListener('keydown', function (e) {
      if (!open) return;
      if (e.key === 'Escape') return set(false);
      if (e.key !== 'Tab') return;
      var f = $$('a,button', s); if (!f.length) return;
      var first = f[0], lastEl = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); lastEl.focus(); }
      else if (!e.shiftKey && document.activeElement === lastEl) { e.preventDefault(); first.focus(); }
    });
    matchMedia('(min-width: 981px)').addEventListener('change', function (e) { if (e.matches) set(false); });
  })();

  /* ── the estate's day: shared solar model ─────────────────── */
  var DAY = {
    // solar day used across the dial, the hours page and the shade study
    rise: 6.6, set: 20.9,
    // what is happening, in the same order as the Hours page
    marks: [
      [5.67, 'First light'], [7.0, 'Breakfast'], [9.25, 'Gardeners move'],
      [11.0, 'Sea hour'], [13.0, 'The long table'], [14.5, 'Siesta'],
      [16.5, 'Shade returns west'], [18.33, 'Golden hour'], [19.75, 'Sundown'],
      [20.5, 'Dinner'], [22.5, 'Lamps down']
    ],
    now: function () { var d = new Date(); return d.getHours() + d.getMinutes() / 60; },
    // fraction of the way from sunrise to sunset, clamped
    frac: function (h) { return clamp((h - this.rise) / (this.set - this.rise), 0, 1); },
    // rough solar altitude in degrees, 21 June at this latitude
    alt: function (h) {
      var f = this.frac(h);
      return Math.max(0, Math.sin(f * Math.PI) * 72);
    },
    // azimuth: -90 at sunrise (east), 0 at noon (south), +90 at sunset (west)
    az: function (h) { return (this.frac(h) - 0.5) * 180; },
    label: function (h) {
      var best = this.marks[0];
      for (var i = 0; i < this.marks.length; i++) if (this.marks[i][0] <= h) best = this.marks[i];
      if (h < this.marks[0][0]) best = this.marks[this.marks.length - 1];
      return best[1];
    },
    hhmm: function (h) {
      var m = Math.round(h * 60), hh = Math.floor(m / 60) % 24;
      return String(hh).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
    }
  };

  /* ── header dial ──────────────────────────────────────────── */
  (function () {
    var track = $('#dialTrack'), sun = $('#dialSun'), t = $('#dialTime'), n = $('#dialNow');
    if (!track) return;
    var L = track.getTotalLength();
    track.style.strokeDasharray = L;

    function paint() {
      var h = DAY.now(), f = DAY.frac(h);
      track.style.strokeDashoffset = (L * (1 - f)).toFixed(2);
      var p = track.getPointAtLength(L * f);
      sun.setAttribute('cx', p.x.toFixed(2));
      sun.setAttribute('cy', p.y.toFixed(2));
      sun.style.opacity = (h < DAY.rise || h > DAY.set) ? '.34' : '1';
      t.textContent = DAY.hhmm(h);
      n.textContent = DAY.label(h);
    }
    paint();
    setInterval(paint, 30000);
  })();

  /* ── hero: load sequence, parallax, playback control ──────── */
  if (window.SOMBRA_HERO) {
    document.body.classList.add('on-hero');

    (function () {
      var v = $('#heroVideo'); if (!v) return;
      var m = matchMedia, c = navigator.connection || {};
      var thin = c.saveData === true || /^(slow-2g|2g)$/.test(c.effectiveType || '');
      var name = 'canopy-1920', poster = 'poster-canopy';
      if (m('(max-width: 720px)').matches) { name = 'canopy-mobile'; poster = 'poster-mobile'; }
      else if (m('(max-width: 1400px)').matches) { name = 'canopy-1280'; }
      v.poster = 'assets/media/' + poster + '.webp';
      v.dataset.src = 'assets/media/' + name + '.mp4';
      if (reduce || thin) document.documentElement.classList.add('still');
      else { v.setAttribute('src', v.dataset.src); v.preload = 'auto'; }
    })();

    (function () {
      var media = $('.hero__media'); if (!media || reduce) return;
      var cur = 0;
      jobs.push(function (f) {
        var t = clamp(f.y / (f.vh || 1), 0, 1);
        var d = Math.abs(t - cur);
        cur = lerp(cur, t, d > 0.15 ? 0.3 : 0.11);
        if (Math.abs(cur - t) < 0.0008) cur = t;
        media.style.transform = 'translate3d(0,' + (cur * 60).toFixed(1) + 'px,0) scale(' + (1 + cur * 0.06).toFixed(4) + ')';
        return cur !== t;
      });
    })();

    (function () {
      var seq = $$('.hero__h .ln > span').concat([$('.hero__lede'), $('.hero__acts')]).filter(Boolean);
      function play() {
        if (reduce) { seq.forEach(function (e) { e.style.opacity = 1; e.style.transform = 'none'; }); return; }
        seq.forEach(function (e, i) {
          e.style.transition = 'opacity .95s cubic-bezier(.16,1,.3,1) ' + (0.1 + i * 0.09) + 's,' +
                               'transform 1.1s cubic-bezier(.16,1,.3,1) ' + (0.1 + i * 0.09) + 's';
          requestAnimationFrame(function () { e.style.opacity = 1; e.style.transform = 'none'; });
        });
      }
      var fired = false, go = function () { if (!fired) { fired = true; play(); } };
      if (document.fonts && document.fonts.ready) { document.fonts.ready.then(go); setTimeout(go, 900); }
      else go();
    })();
  }

  /* ── video lifecycle + the one motion control ─────────────── */
  (function () {
    var root = document.documentElement;
    var vids = $$('video[data-src], #heroVideo');
    if (!vids.length) return;
    var btn = $('#motionBtn'), label = $('#motionLabel');
    var seen = new WeakMap();
    var armed = false;

    var wanted = function () { return !root.classList.contains('still'); };

    function arm(v) {
      if (!v.getAttribute('src') && v.dataset.src) { v.setAttribute('src', v.dataset.src); v.preload = 'auto'; }
      return !!v.getAttribute('src');
    }
    function play(v) {
      if (!wanted() || !seen.get(v)) return;
      if (!arm(v)) return;
      var p = v.play();
      if (p && p.catch) p.catch(function () {
        setMotion(false);
        if (armed) return;
        armed = true;
        ['pointerdown', 'keydown', 'touchstart'].forEach(function (t) {
          document.addEventListener(t, function once() {
            ['pointerdown', 'keydown', 'touchstart'].forEach(function (u) { document.removeEventListener(u, once); });
            setMotion(true);
          }, { once: true, passive: true });
        });
      });
    }
    function setMotion(on) {
      root.classList.toggle('still', !on);
      if (btn) { btn.setAttribute('aria-pressed', String(on)); label.textContent = on ? 'Playing' : 'Paused'; }
      vids.forEach(function (v) { on ? play(v) : (v.getAttribute('src') && v.pause()); });
    }
    if (btn) { setMotion(wanted()); btn.addEventListener('click', function () { setMotion(!wanted()); }); }

    vids.forEach(function (v) {
      seen.set(v, false);
      v.addEventListener('loadeddata', function () { v.classList.add('is-live'); play(v); });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (es) {
          es.forEach(function (e) {
            seen.set(v, e.isIntersecting);
            if (e.isIntersecting) play(v);
            else if (v.getAttribute('src')) v.pause();
          });
        }, { rootMargin: '25% 0px' }).observe(v.closest('section') || v);
      } else { seen.set(v, true); play(v); }
    });

    document.addEventListener('visibilitychange', function () {
      vids.forEach(function (v) {
        if (!v.getAttribute('src')) return;
        document.hidden ? v.pause() : play(v);
      });
    });
  })();

  /* ── reveals ──────────────────────────────────────────────── */
  (function () {
    var items = $$('.reveal');
    if (!items.length) return;
    if (!('IntersectionObserver' in window) || reduce) {
      return items.forEach(function (e) { e.classList.add('is-in'); });
    }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        var i = Array.prototype.indexOf.call(el.parentNode.children, el);
        el.style.transitionDelay = (Math.min(i, 5) * 0.055) + 's';
        el.classList.add('is-in');
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });
    items.forEach(function (e) { io.observe(e); });
  })();

  /* ── shade study (estate) ─────────────────────────────────── */
  if (window.SOMBRA_STUDY) (function () {
    var svg = $('#planSvg'); if (!svg) return;
    var NS = 'http://www.w3.org/2000/svg';
    function el(t, a) { var n = document.createElementNS(NS, t); for (var k in a) n.setAttribute(k, a[k]); return n; }

    /* Plan is 760 x 520, north up, east right — so the sun sits east (right) at
       sunrise, south (below) at noon, west (left) at sunset, and shadows fall the
       opposite way. Shadow length follows 1/tan(altitude) but is scaled up: at true
       scale a 69-degree sun gives a shadow a few pixels long and the drawing says
       nothing. */
    var BUILD = [
      { x: 96,  y: 116, w: 236, h: 66, hgt: 30, n: 'Main house' },
      { x: 96,  y: 200, w: 82,  h: 150, hgt: 26, n: 'Arcada' },
      { x: 430, y: 104, w: 128, h: 92,  hgt: 36, n: 'Mirador' },
      { x: 606, y: 224, w: 112, h: 78,  hgt: 24, n: 'Cisterna' },
      { x: 214, y: 400, w: 142, h: 66,  hgt: 22, n: 'Huerta' }
    ];
    var PALMS = [
      { x: 214, y: 250, r: 30, hgt: 74 }, { x: 282, y: 318, r: 34, hgt: 84 },
      { x: 356, y: 244, r: 26, hgt: 64 }, { x: 400, y: 330, r: 31, hgt: 78 },
      { x: 486, y: 262, r: 27, hgt: 68 }, { x: 548, y: 348, r: 33, hgt: 82 },
      { x: 152, y: 330, r: 24, hgt: 58 }, { x: 620, y: 148, r: 28, hgt: 70 },
      { x: 668, y: 392, r: 30, hgt: 76 }, { x: 318, y: 176, r: 22, hgt: 54 },
      { x: 452, y: 424, r: 25, hgt: 62 }
    ];
    var ZONES = [
      { n: 'The courtyard',  x: 318, y: 268, w: 116, h: 74 },
      { n: 'East arcade',    x: 196, y: 206, w: 50,  h: 100 },
      { n: 'West terrace',   x: 596, y: 316, w: 112, h: 62 },
      { n: 'Pool deck',      x: 452, y: 396, w: 128, h: 58 },
      { n: 'Reading garden', x: 74,  y: 392, w: 100, h: 62 }
    ];

    var gShadow = $('#planShadows'), gBuild = $('#planBuild'),
        gZone = $('#planZones'), gPalm = $('#planPalms'), gLab = $('#planLabels');

    // survey grid, so the drawing reads as a plan rather than a diagram
    var gGrid = el('g', { opacity: '.5' });
    for (var gx = 40; gx < 760; gx += 40)
      gGrid.appendChild(el('line', { x1: gx, y1: 0, x2: gx, y2: 520, stroke: 'rgba(240,237,230,.05)', 'stroke-width': 1 }));
    for (var gy = 40; gy < 520; gy += 40)
      gGrid.appendChild(el('line', { x1: 0, y1: gy, x2: 760, y2: gy, stroke: 'rgba(240,237,230,.05)', 'stroke-width': 1 }));
    svg.insertBefore(gGrid, gShadow);

    // compass, so "north up" is stated rather than assumed
    var comp = el('g', { transform: 'translate(714,54)' });
    comp.appendChild(el('line', { x1: 0, y1: 16, x2: 0, y2: -14, stroke: 'rgba(240,237,230,.5)', 'stroke-width': 1 }));
    comp.appendChild(el('path', { d: 'M0 -18 L4 -9 L0 -11 L-4 -9 Z', fill: 'rgba(240,237,230,.62)' }));
    var nt = el('text', { x: 0, y: 30, 'text-anchor': 'middle', fill: 'rgba(240,237,230,.5)', 'font-size': 10, 'letter-spacing': '.12em' });
    nt.textContent = 'N'; comp.appendChild(nt);
    gLab.appendChild(comp);

    ZONES.forEach(function (z, i) {
      gZone.appendChild(el('rect', { x: z.x, y: z.y, width: z.w, height: z.h, rx: 3,
        fill: 'none', stroke: 'rgba(240,237,230,.34)', 'stroke-width': 1.2,
        'stroke-dasharray': '5 4', id: 'z' + i }));
      // label sits above the box so it never collides with a canopy
      var t = el('text', { x: z.x, y: z.y - 7, fill: 'rgba(240,237,230,.72)',
        'font-size': 11, 'letter-spacing': '.07em', id: 'zt' + i });
      t.textContent = z.n; gLab.appendChild(t);
    });
    BUILD.forEach(function (b) {
      gBuild.appendChild(el('rect', { x: b.x, y: b.y, width: b.w, height: b.h, rx: 2,
        fill: '#0A2029', stroke: 'rgba(240,237,230,.3)', 'stroke-width': 1 }));
      var t = el('text', { x: b.x + b.w / 2, y: b.y + b.h / 2 + 4, fill: 'rgba(240,237,230,.52)',
        'font-size': 10, 'text-anchor': 'middle', 'letter-spacing': '.09em' });
      t.textContent = b.n; gLab.appendChild(t);
    });
    PALMS.forEach(function (p) {
      gPalm.appendChild(el('circle', { cx: p.x, cy: p.y, r: p.r, fill: 'rgba(150,134,74,.16)',
        stroke: 'rgba(205,190,132,.46)', 'stroke-width': 1 }));
      gPalm.appendChild(el('circle', { cx: p.x, cy: p.y, r: 2.6, fill: 'rgba(210,196,140,.9)' }));
    });

    // sun marker rides an ellipse outside the plan at the real azimuth
    var gSun = el('g');
    var sunRay = el('line', { stroke: 'rgba(232,181,88,.45)', 'stroke-width': 1, 'stroke-dasharray': '4 5' });
    var sunDot = el('circle', { r: 9, fill: '#E8B558' });
    var sunGlow = el('circle', { r: 17, fill: 'rgba(232,181,88,.18)' });
    gSun.appendChild(sunRay); gSun.appendChild(sunGlow); gSun.appendChild(sunDot);
    svg.appendChild(gSun);

    function hull(pts) {
      pts = pts.slice().sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
      var cross = function (o, a, b) { return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]); };
      var lo = [], up = [], i;
      for (i = 0; i < pts.length; i++) {
        while (lo.length >= 2 && cross(lo[lo.length - 2], lo[lo.length - 1], pts[i]) <= 0) lo.pop();
        lo.push(pts[i]);
      }
      for (i = pts.length - 1; i >= 0; i--) {
        while (up.length >= 2 && cross(up[up.length - 2], up[up.length - 1], pts[i]) <= 0) up.pop();
        up.push(pts[i]);
      }
      lo.pop(); up.pop();
      return lo.concat(up);
    }
    function inPoly(px, py, poly) {
      var c = false;
      for (var i = 0, j = poly.length - 1; i < poly.length; j = i++) {
        var xi = poly[i][0], yi = poly[i][1], xj = poly[j][0], yj = poly[j][1];
        if ((yi > py) !== (yj > py) && px < (xj - xi) * (py - yi) / (yj - yi) + xi) c = !c;
      }
      return c;
    }

    var hourEl = $('#studyHour'), altEl = $('#studyAlt'), listEl = $('#studyList'), input = $('#sunTime');
    listEl.innerHTML = ZONES.map(function (z, i) {
      return '<li data-shaded="0" id="zl' + i + '"><span class="k"></span>' +
             '<span class="z">' + z.n + '</span><span class="s">—</span></li>';
    }).join('');

    function render(h) {
      var alt = DAY.alt(h), az = DAY.az(h), rad = az * Math.PI / 180;
      var lit = alt > 3;
      // sun sits at (-sin az, +cos az); the shadow runs the other way
      var ux = Math.sin(rad), uy = -Math.cos(rad);
      var len = clamp(alt > 2 ? 1 / Math.tan(alt * Math.PI / 180) : 6, 0.28, 5.4);

      gShadow.textContent = '';
      var polys = [], circles = [];

      if (lit) {
        BUILD.forEach(function (b) {
          var ox = ux * b.hgt * 0.42 * len, oy = uy * b.hgt * 0.42 * len;
          var pts = [[b.x, b.y], [b.x + b.w, b.y], [b.x + b.w, b.y + b.h], [b.x, b.y + b.h]];
          var hu = hull(pts.concat(pts.map(function (p) { return [p[0] + ox, p[1] + oy]; })));
          polys.push(hu);
          gShadow.appendChild(el('polygon', {
            points: hu.map(function (p) { return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' '),
            fill: 'rgba(3,14,20,.60)'
          }));
        });
        PALMS.forEach(function (p) {
          var ox = ux * p.hgt * 0.42 * len, oy = uy * p.hgt * 0.42 * len;
          circles.push({ x: p.x + ox, y: p.y + oy, r: p.r * 1.05 });
          gShadow.appendChild(el('ellipse', {
            cx: (p.x + ox).toFixed(1), cy: (p.y + oy).toFixed(1),
            rx: (p.r * 1.05).toFixed(1), ry: (p.r * 0.95).toFixed(1),
            fill: 'rgba(3,14,20,.52)'
          }));
        });
      }

      // sample five points per zone rather than the centroid alone
      ZONES.forEach(function (z, i) {
        var pts = [[z.x + z.w / 2, z.y + z.h / 2],
                   [z.x + z.w * .22, z.y + z.h * .25], [z.x + z.w * .78, z.y + z.h * .25],
                   [z.x + z.w * .22, z.y + z.h * .75], [z.x + z.w * .78, z.y + z.h * .75]];
        var hit = 0;
        if (lit) {
          pts.forEach(function (q) {
            var covered = false, a, c;
            for (a = 0; a < circles.length && !covered; a++) {
              c = circles[a];
              if ((q[0] - c.x) * (q[0] - c.x) + (q[1] - c.y) * (q[1] - c.y) < c.r * c.r) covered = true;
            }
            for (a = 0; a < polys.length && !covered; a++) if (inPoly(q[0], q[1], polys[a])) covered = true;
            if (covered) hit++;
          });
        }
        var shaded = !lit || hit >= 3;
        var part = lit && hit > 0 && hit < 3;

        var box = document.getElementById('z' + i);
        box.setAttribute('fill', shaded ? 'rgba(95,168,206,.20)' : part ? 'rgba(240,237,230,.09)' : 'rgba(232,181,88,.17)');
        box.setAttribute('stroke', shaded ? 'rgba(120,190,225,.75)' : part ? 'rgba(240,237,230,.5)' : 'rgba(232,181,88,.7)');
        var li = document.getElementById('zl' + i);
        li.dataset.shaded = shaded ? '1' : part ? '2' : '0';
        li.querySelector('.s').textContent = !lit ? 'after dark' : shaded ? 'shaded' : part ? 'part shade' : 'full sun';
      });

      // sun marker, plus a ray showing which way the shadows run
      var cx = 380, cy = 250, RX = 348, RY = 230;
      var sx = cx - Math.sin(rad) * RX, sy = cy + Math.cos(rad) * RY;
      gSun.style.opacity = lit ? '1' : '.25';
      sunDot.setAttribute('cx', sx.toFixed(1)); sunDot.setAttribute('cy', sy.toFixed(1));
      sunGlow.setAttribute('cx', sx.toFixed(1)); sunGlow.setAttribute('cy', sy.toFixed(1));
      sunRay.setAttribute('x1', sx.toFixed(1)); sunRay.setAttribute('y1', sy.toFixed(1));
      sunRay.setAttribute('x2', (sx + ux * 96).toFixed(1)); sunRay.setAttribute('y2', (sy + uy * 96).toFixed(1));

      hourEl.textContent = DAY.hhmm(h);
      altEl.textContent = alt < 1 ? 'sun below the horizon'
        : 'sun ' + Math.round(alt) + '\u00B0 above the horizon, to the ' +
          (az < -18 ? 'east' : az > 18 ? 'west' : 'south');
    }

    input.addEventListener('input', function () { render(+input.value); });
    var start = clamp(DAY.now(), 5, 21.5);
    input.value = start.toFixed(2);
    render(start);
  })();

  /* ── big dial (hours) ─────────────────────────────────────── */
  if (window.SOMBRA_HOURS) (function () {
    var host = $('#bigDial'); if (!host) return;
    var NS = 'http://www.w3.org/2000/svg';
    function el(t, a) { var n = document.createElementNS(NS, t); for (var k in a) n.setAttribute(k, a[k]); return n; }

    /* A shallow ellipse, not a semicircle: a true half-circle across 1000 units
       would be 474 units tall and spill straight out of the box. */
    var W = 1000, Hh = 210, pad = 30, cy = Hh - 26;
    var rx = (W - pad * 2) / 2, ry = 128, cx = W / 2;
    var pt = function (f) {
      var a = Math.PI * (1 - f);
      return { x: cx + rx * Math.cos(a), y: cy - ry * Math.sin(a) };
    };
    var arc = 'M' + pad + ' ' + cy + ' A' + rx + ' ' + ry + ' 0 0 1 ' + (W - pad) + ' ' + cy;

    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + Hh, preserveAspectRatio: 'xMidYMid meet' });
    svg.appendChild(el('line', { x1: pad, y1: cy, x2: W - pad, y2: cy,
      stroke: 'rgba(23,42,51,.14)', 'stroke-width': 1 }));
    svg.appendChild(el('path', { d: arc, fill: 'none', stroke: 'rgba(23,42,51,.18)', 'stroke-width': 1.5 }));
    var live = el('path', { d: arc, fill: 'none', stroke: '#1B6FA8', 'stroke-width': 1.5 });
    svg.appendChild(live);

    var lastLabelX = -999;
    DAY.marks.forEach(function (m, i) {
      var f = DAY.frac(m[0]); if (f <= 0 || f >= 1) return;
      var p = pt(f);
      svg.appendChild(el('line', { x1: p.x, y1: p.y, x2: p.x, y2: cy,
        stroke: 'rgba(23,42,51,.10)', 'stroke-width': 1 }));
      svg.appendChild(el('circle', { cx: p.x, cy: p.y, r: 2.8, fill: 'rgba(23,42,51,.34)' }));
      // stagger the labels, and drop any that would still sit on their neighbour
      if (p.x - lastLabelX < 52) return;
      lastLabelX = p.x;
      var t = el('text', { x: p.x, y: p.y - (i % 2 ? 22 : 11), 'text-anchor': 'middle',
        fill: 'rgba(23,42,51,.5)', 'font-size': 12, 'letter-spacing': '.05em' });
      t.textContent = DAY.hhmm(m[0]); svg.appendChild(t);
    });

    ['Sunrise', 'Sunset'].forEach(function (lab, i) {
      var t = el('text', { x: i ? W - pad : pad, y: cy + 20, 'text-anchor': i ? 'end' : 'start',
        fill: 'rgba(23,42,51,.42)', 'font-size': 11, 'letter-spacing': '.13em' });
      t.textContent = lab.toUpperCase(); svg.appendChild(t);
    });

    var glow = el('circle', { r: 15, fill: 'rgba(232,181,88,.22)' });
    var sun = el('circle', { r: 8, fill: '#E8B558', stroke: '#F2EEE7', 'stroke-width': 2 });
    svg.appendChild(glow); svg.appendChild(sun);
    host.appendChild(svg);

    var L = live.getTotalLength();
    live.style.strokeDasharray = L;

    function paint() {
      var h = DAY.now(), f = DAY.frac(h);
      live.style.strokeDashoffset = (L * (1 - f)).toFixed(1);
      var p = pt(f);
      [sun, glow].forEach(function (c) { c.setAttribute('cx', p.x.toFixed(1)); c.setAttribute('cy', p.y.toFixed(1)); });
      var up = h > DAY.rise && h < DAY.set;
      sun.style.opacity = up ? '1' : '.35';
      glow.style.opacity = up ? '1' : '0';

      var rows = $$('#hrs .hr'), best = null;
      rows.forEach(function (row) {
        var q = row.dataset.hour.split(':');
        if ((+q[0] + q[1] / 60) <= h) best = row;
      });
      rows.forEach(function (row) { row.classList.toggle('is-now', row === best); });
    }
    paint();
    setInterval(paint, 30000);
  })();

  /* ── room filter ──────────────────────────────────────────── */
  if (window.SOMBRA_FILTER) (function () {
    var btns = $$('.filter__b'), rooms = $$('.room'), count = $('#filterCount');
    if (!btns.length) return;
    var WORD = { 1: 'one room', 2: 'two rooms', 3: 'three rooms', 4: 'four rooms', 5: 'five rooms', 6: 'all six rooms' };
    function apply(f) {
      var n = 0;
      rooms.forEach(function (r) {
        var a = r.dataset.aspect;
        var show = f === 'all' || a.indexOf(f) === 0 || a === 'all';
        r.hidden = !show;
        if (show) n++;
      });
      count.textContent = 'Showing ' + (WORD[n] || n + ' rooms');
      btns.forEach(function (b) {
        var on = b.dataset.f === f;
        b.classList.toggle('is-on', on);
        b.setAttribute('aria-pressed', String(on));
      });
    }
    btns.forEach(function (b) { b.addEventListener('click', function () { apply(b.dataset.f); }); });
  })();

  /* ── FAQ + enquiry (visit) ────────────────────────────────── */
  if (window.SOMBRA_VISIT) {
    (function () {
      $$('.faq__q').forEach(function (q) {
        q.addEventListener('click', function () {
          var open = q.getAttribute('aria-expanded') === 'true';
          q.setAttribute('aria-expanded', String(!open));
          q.closest('.faq__i').classList.toggle('is-open', !open);
        });
      });
    })();

    (function () {
      var form = $('#enquiry'); if (!form) return;
      var ok = $('#formOk');
      // take over validation only now that we are certainly running; without us the
      // browser's own required/type checks stay in force
      form.setAttribute('novalidate', '');
      function bad(field, msg) {
        var p = field.closest('.f');
        p.classList.add('is-bad');
        field.setAttribute('aria-invalid', 'true');
        if (!p.querySelector('.err')) {
          var s = document.createElement('span');
          s.className = 'err'; s.textContent = msg; p.appendChild(s);
        }
      }
      function clear(field) {
        var p = field.closest('.f');
        p.classList.remove('is-bad');
        field.removeAttribute('aria-invalid');
        var e = p.querySelector('.err'); if (e) e.remove();
      }
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var name = $('#fName'), mail = $('#fMail'), first = null;
        [name, mail].forEach(clear);
        if (!name.value.trim()) { bad(name, 'We need a name to reply to.'); first = first || name; }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(mail.value.trim())) {
          bad(mail, 'That email does not look right.'); first = first || mail;
        }
        if (first) { first.focus(); return; }
        ok.hidden = false;
        ok.textContent = 'Thank you, ' + name.value.trim().split(' ')[0] +
          '. This is a concept site so nothing was actually sent — on the real one you would ' +
          'hear back from us the same day.';
        form.querySelector('.form__foot').hidden = true;
        ok.scrollIntoView({ block: 'nearest', behavior: reduce ? 'auto' : 'smooth' });
      });
      [$('#fName'), $('#fMail')].forEach(function (f) {
        f.addEventListener('input', function () { if (f.closest('.f').classList.contains('is-bad')) clear(f); });
      });
    })();
  }

  /* ── in-page anchors ──────────────────────────────────────── */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a || a.classList.contains('skip')) return;
    var id = a.getAttribute('href').slice(1); if (!id) return;
    var t = document.getElementById(id); if (!t) return;
    e.preventDefault();
    var top = t.getBoundingClientRect().top + scrollY -
      (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--bar-h')) + 20);
    scrollTo({ top: Math.max(0, top), behavior: reduce ? 'auto' : 'smooth' });
    if (history.replaceState) history.replaceState(null, '', '#' + id);
    if (!t.hasAttribute('tabindex')) t.setAttribute('tabindex', '-1');
    setTimeout(function () { t.focus({ preventScroll: true }); }, reduce ? 0 : 520);
  });

  kick();
})();
