(function () {
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  // Komt een bezoeker binnen met utm-parameters (bijvoorbeeld via Pinterest of Instagram),
  // dan gaan die mee naar Google Play, zodat Play Console de installatie aan die bron koppelt.
  var params = new URLSearchParams(location.search);
  if (params.get('utm_source')) {
    var links = document.querySelectorAll('a[href*="play.google.com/store/apps/details"]');
    for (var i = 0; i < links.length; i++) {
      var url = new URL(links[i].href);
      var referrer = new URLSearchParams(url.searchParams.get('referrer') || '');
      ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'].forEach(function (key) {
        if (params.get(key)) referrer.set(key, params.get(key));
      });
      url.searchParams.set('referrer', referrer.toString());
      links[i].href = url.toString();
    }
  }

  // Video: pas na een klik laden, via youtube-nocookie.
  document.querySelectorAll('.video[data-yt]').forEach(function (box) {
    var link = box.querySelector('.video-play');
    link.addEventListener('click', function (ev) {
      ev.preventDefault();
      var frame = document.createElement('iframe');
      frame.src = 'https://www.youtube-nocookie.com/embed/' + box.dataset.yt +
        '?autoplay=1&rel=0&playsinline=1&hl=' + box.dataset.hl;
      frame.title = link.getAttribute('aria-label');
      frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      frame.allowFullscreen = true;
      box.replaceChild(frame, link);
    });
  });

  // Schermafbeeldingen vergroten.
  var shots = document.querySelector('.shots[data-close]');
  if (shots && window.HTMLDialogElement) {
    var items = Array.prototype.slice.call(shots.querySelectorAll('a.shot'));
    var dlg = document.createElement('dialog');
    dlg.className = 'lightbox';
    dlg.innerHTML = '<div class="lightbox-inner"><img alt="" />' +
      '<button type="button" class="lb-prev">&#8249;</button>' +
      '<button type="button" class="lb-next">&#8250;</button>' +
      '<button type="button" class="lb-close">&times;</button></div>';
    document.body.appendChild(dlg);
    var img = dlg.querySelector('img');
    dlg.querySelector('.lb-close').setAttribute('aria-label', shots.dataset.close);
    dlg.querySelector('.lb-prev').setAttribute('aria-label', shots.dataset.prev);
    dlg.querySelector('.lb-next').setAttribute('aria-label', shots.dataset.next);
    var current = 0;
    var show = function (n) {
      current = (n + items.length) % items.length;
      img.src = items[current].href;
      img.alt = items[current].querySelector('img').alt;
    };
    items.forEach(function (a, n) {
      a.addEventListener('click', function (ev) {
        ev.preventDefault();
        show(n);
        dlg.showModal();
      });
    });
    dlg.querySelector('.lb-prev').addEventListener('click', function () { show(current - 1); });
    dlg.querySelector('.lb-next').addEventListener('click', function () { show(current + 1); });
    dlg.querySelector('.lb-close').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (ev) {
      if (ev.target === dlg || ev.target.className === 'lightbox-inner') dlg.close();
    });
    dlg.addEventListener('keydown', function (ev) {
      if (ev.key === 'ArrowLeft') show(current - 1);
      if (ev.key === 'ArrowRight') show(current + 1);
    });
  }

  // Filters op de homepage.
  var filters = document.querySelector('.filters');
  var grid = document.getElementById('games');
  if (filters && grid) {
    var cards = grid.querySelectorAll('.card[data-cat]');
    var buttons = filters.querySelectorAll('.filter');
    // Alleen categorieën tonen waar ook spellen in zitten.
    buttons.forEach(function (b) {
      if (b.dataset.cat !== 'all' && !grid.querySelector('.card[data-cat="' + b.dataset.cat + '"]')) b.hidden = true;
    });
    filters.hidden = false;
    filters.addEventListener('click', function (ev) {
      var btn = ev.target.closest('.filter');
      if (!btn) return;
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      cards.forEach(function (c) {
        c.hidden = btn.dataset.cat !== 'all' && c.dataset.cat !== btn.dataset.cat;
      });
    });
  }

  // Vaste downloadbalk op mobiel: verbergen zolang de gewone Play-knop in beeld is.
  var sticky = document.querySelector('.sticky-cta');
  var cta = document.querySelector('.cta');
  if (sticky && cta && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      sticky.classList.toggle('is-hidden', entries[0].isIntersecting);
    }).observe(cta);
  }
})();
