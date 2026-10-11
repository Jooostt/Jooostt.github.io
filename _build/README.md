# Site-generator

Bouwt de app-pagina's en homepages in zes talen (en, nl, de, es, fr, pt) plus `sitemap.xml`.
Jekyll slaat deze map over omdat de naam met `_` begint.

```
py -3 _build/build.py
```

- **Teksten** komen uit de Play-listings: `PlayStoreAssets/metadata/<taal>/` van elke app
  (app-naam, korte en volledige beschrijving). Pas je een listing aan, draai dan de build opnieuw.
- **Schermafbeeldingen** voor de vertaalde pagina's komen uit `PlayStoreAssets/screenshots/<taal>/`
  (01 t/m 04) en worden als 340x604 webp in `assets/apps/<slug>/<taal>/` gezet.
- **Vaste teksten** (FAQ, knoppen, titels) staan in `i18n.py`; welke apps meedoen, of ze live
  zijn, het genre in de titel en de gerelateerde spellen in `apps.py`.
- Live gaat een app door `live: True` te zetten: dan verschijnt de Play-knop met referrer
  (`utm_campaign=<slug>-<taal>`), zodat installs via de site in Play Console zichtbaar zijn.
- Komt een bezoeker binnen met `?utm_source=...` (Pinterest, Instagram), dan geeft
  `assets/site.js` die door aan de Play-link.

Niet gegenereerd: `privacy.html` en `terms.html` (vaste URL's voor Play Console) en de pagina's
van de conceptapps (Forbidden Words, FactFlow, Aquarium, Butterfly Garden).

**Ontwerp-instellingen** in `apps.py`: `color` (accentkleur van de app-pagina), `cat` (filter op de
homepage), `FEATURED` (uitgelicht spel met video) en `HERO_SHOTS` (de drie telefoons in de kop).
De video-ID's staan in `videos.py` (uit de Play-listings); de video laadt pas na een klik, via youtube-nocookie.

**Talen per spel**: een spel krijgt een pagina in elke taal die in de app aan staat (dezelfde
taalschakelaar die het portaal leest) en waarvoor listingteksten en vier schermafbeeldingen bestaan.
Vaste teksten voor de zes extra talen (it, tr, pl, ro, ru, ca) staan in `i18n_more.py`.

**Na het pushen**:
- `py -3 _build/update_videos.py` werkt de video's en uploaddatums bij (privévideo's worden overgeslagen).
- `py -3 _build/indexnow.py` meldt de gewijzigde pagina's van de laatste commit bij Bing/IndexNow
  (`--all` voor de hele sitemap). De sleutel staat als bestand in de root.
- `llms.txt` (overzicht voor AI-zoekmachines) wordt door de build zelf geschreven.
