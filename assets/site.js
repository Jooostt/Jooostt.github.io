(function () {
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  // Komt een bezoeker binnen met utm-parameters (bijvoorbeeld via Pinterest of Instagram),
  // dan gaan die mee naar Google Play, zodat Play Console de installatie aan die bron koppelt.
  var params = new URLSearchParams(location.search);
  if (!params.get('utm_source')) return;
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
})();
