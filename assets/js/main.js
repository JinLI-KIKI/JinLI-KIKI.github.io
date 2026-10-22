/* Jin Li, personal site. No dependencies. */
(function () {
  'use strict';

  /* Mechanism figure tabs (research pages) */
  document.querySelectorAll('.mech').forEach(function (mech) {
    var tabs = mech.querySelectorAll('[role="tab"]');
    function select(t) {
      mech.dataset.mode = t.dataset.mode;
      tabs.forEach(function (x) {
        var on = x === t;
        x.setAttribute('aria-selected', String(on));
        x.tabIndex = on ? 0 : -1;
      });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t); });
      t.addEventListener('keydown', function (e) {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        e.preventDefault();
        var n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
        select(n); n.focus();
      });
    });
    select(mech.querySelector('[aria-selected="true"]') || tabs[0]);
  });

  /* Spectrum readout, same emission model used to draw the curve */
  document.querySelectorAll('.spectrum-plot').forEach(function (plot) {
    var probe = plot.querySelector('.probe');
    var readout = plot.querySelector('.readout');
    var LMIN = 230, LMAX = 330, PEAK = 280;
    var norm = 1 + 0.035 * Math.exp(-0.5 * Math.pow(20 / 9, 2));
    function intensity(l) {
      var s = l < PEAK ? 4.7 : 5.6;
      return (Math.exp(-0.5 * Math.pow((l - PEAK) / s, 2)) + 0.035 * Math.exp(-0.5 * Math.pow((l - 300) / 9, 2))) / norm;
    }
    function band(l) { return l < 280 ? 'UV-C' : (l < 315 ? 'UV-B' : 'UV-A'); }
    function show(x) {
      var r = plot.getBoundingClientRect();
      var f = Math.min(1, Math.max(0, (x - r.left) / r.width));
      var l = LMIN + f * (LMAX - LMIN);
      var pct = intensity(l) * 100;
      probe.setAttribute('x1', f * 1200); probe.setAttribute('x2', f * 1200);
      readout.textContent = Math.round(l) + ' nm, ' + band(l) + ', ' + (pct >= 1 ? Math.round(pct) : '<1') + '% of peak';
      var w = readout.offsetWidth, left = f * r.width + 12;
      if (left + w > r.width) left = f * r.width - w - 12;
      readout.style.left = left + 'px';
      plot.classList.add('probing');
    }
    plot.addEventListener('pointermove', function (e) { show(e.clientX); });
    plot.addEventListener('pointerdown', function (e) { show(e.clientX); });
    plot.addEventListener('pointerleave', function () { plot.classList.remove('probing'); });
  });

  /* Menu closes after choosing a page, on outside click and on Escape */
  var menu = document.querySelector('.menu');
  if (menu) {
    menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { menu.open = false; }); });
    document.addEventListener('click', function (e) { if (menu.open && !menu.contains(e.target)) menu.open = false; });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary').focus(); }
    });
  }

  /* Résumé page: print button */
  document.querySelectorAll('[data-print]').forEach(function (b) {
    b.addEventListener('click', function () { window.print(); });
  });
})();
