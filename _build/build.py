"""Bouwt de app-pagina's en de homepage in alle talen, plus sitemap.xml en llms.txt.

Gebruik (vanuit de root van de site):  py -3 _build/build.py

De teksten van de spellen komen uit de Play-listings in PlayStoreAssets/metadata van elke app;
de vertaalde schermafbeeldingen uit PlayStoreAssets/screenshots. Een app krijgt een pagina in elke
taal die in de app aan staat en waarvoor listingteksten en schermafbeeldingen bestaan.
Privacybeleid en voorwaarden worden niet aangeraakt, net als de pagina's van de conceptapps.
"""
import datetime
import glob
import html
import json
import os
import re
import subprocess
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from apps import APPS, BY_SLUG, CATEGORIES, FEATURED, HERO_SHOTS  # noqa: E402
from i18n import AUTONYM, DESIGN, FAQ, LANGS, MORE_IN_EN, OG_LOCALE, SHOT, UI, heading  # noqa: E402
from listing import ROOT, app_language_switches, has_listing, meta_file, parse_description  # noqa: E402
from videos import UPLOADED, VIDEOS  # noqa: E402

SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BASE = 'https://jooostt.github.io/'
MAIL = 'joostmuijsenberg.dev@gmail.com'
TODAY = datetime.date.today().isoformat()

# Conceptapps die op de Engelse homepage blijven staan zoals ze waren.
EN_CONCEPT_CARDS = [
    ('Forbidden Words', '''        <a class="card" href="forbidden-words/" data-cat="party">
          <img class="card-icon" src="assets/apps/forbidden-words/icon.png" width="64" height="64" alt="" loading="lazy" />
          <h3>Forbidden Words</h3>
          <p>Explain the word without saying it! A fast and funny party word game for friends and family.</p>
          <span class="tag tag-soon">Coming soon</span>
        </a>'''),
    ('FactFlow', '''        <a class="card" href="factflow/" data-cat="quiz">
          <img class="card-icon" src="assets/apps/factflow/icon.png" width="64" height="64" alt="" loading="lazy" />
          <h3>FactFlow</h3>
          <p>Swipe through facts like shorts, but fully offline.</p>
          <span class="tag tag-soon">Coming soon</span>
        </a>'''),
]

# Pagina's die niet gegenereerd worden maar wel in de sitemap horen.
EXTRA_SITEMAP = [
    ('forbidden-words/', '0.8'),
    ('forbidden-words/privacy.html', '0.3'),
    ('forbidden-words/terms.html', '0.3'),
]

e = html.escape

# Talen per app (slug -> lijst), gevuld in main().
APP_LANGS = {}


def apps_in(lang):
    return [a for a in APPS if lang in APP_LANGS[a['slug']]]


def page_path(lang, slug=None):
    """URL-pad zonder domein, bv. 'nl/sudoku/' of '' voor de Engelse homepage."""
    p = '' if lang == 'en' else f'{lang}/'
    return p + (f'{slug}/' if slug else '')


def prefix(lang, slug=None):
    depth = (0 if lang == 'en' else 1) + (1 if slug else 0)
    return '../' * depth


def play_url(app, lang, campaign):
    ref = f'utm_source=jooostt.github.io&utm_medium=website&utm_campaign={campaign}'
    hl = '' if lang == 'en' else f'&hl={lang}'
    return f'https://play.google.com/store/apps/details?id={app["id"]}{hl}&referrer={quote(ref, safe="")}'


def short_name(app_name):
    return re.split(r'\s+[-·]\s+|:\s+', app_name)[0].strip()


def plain(blocks):
    parts = []
    for kind, val in blocks:
        parts.append(val if kind == 'p' else '; '.join(val) + '.')
    return ' '.join(parts)


def load(app, lang):
    d = app['dir']
    full_name = meta_file(d, lang, 'app-name')
    intro, sections, _ = parse_description(meta_file(d, lang, 'full-description'))
    shots = sorted(glob.glob(os.path.join(ROOT, d, 'PlayStoreAssets', 'screenshots', lang, f'{lang}_0[1-4]-*.png')))
    if len(shots) != 4:
        raise SystemExit(f'{d} {lang}: verwacht 4 schermafbeeldingen, gevonden {len(shots)}')
    name = app.get('name_en') if lang == 'en' and app.get('name_en') else short_name(full_name)
    return {
        'full_name': full_name,
        'name': name,
        'short': meta_file(d, lang, 'short-description'),
        'intro': intro,
        'sections': sections,
        'shots': shots,
    }


def asset_dir(app, lang):
    """Map met de beelden van een app in een taal; Engels staat direct in de app-map."""
    return f'assets/apps/{app["slug"]}/' + ('' if lang == 'en' else f'{lang}/')


def _image(src, dst, size, fmt='WEBP', quality=80):
    from PIL import Image
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return
    im = Image.open(src).convert('RGB')
    if size[1] is None:
        size = (size[0], round(im.height * size[0] / im.width))
    extra = {'method': 6} if fmt == 'WEBP' else {'optimize': True, 'progressive': True}
    im.resize(size, Image.LANCZOS).save(dst, fmt, quality=quality, **extra)


def convert_images(app, lang, data):
    """Schermafbeeldingen klein (340x604, de Engelse bestaan al) en groot (540x960, voor de
    vergroting), de feature graphic als voorbeeldbeeld voor de video en als deelplaatje."""
    out_dir = os.path.join(SITE, asset_dir(app, lang))
    os.makedirs(out_dir, exist_ok=True)
    for i, src in enumerate(data['shots'], 1):
        if lang != 'en':
            _image(src, os.path.join(out_dir, f'shot-{i}.webp'), (340, 604))
        _image(src, os.path.join(out_dir, f'shot-{i}-lg.webp'), (540, 960), quality=78)
    feature = os.path.join(ROOT, app['dir'], 'PlayStoreAssets', 'screenshots', lang, f'{lang}_feature-graphic.png')
    data['has_feature'] = os.path.exists(feature)
    if data['has_feature']:
        _image(feature, os.path.join(out_dir, 'feature.webp'), (960, None), quality=82)
        if lang != 'en':
            # Het Engelse og.jpg bestond al; de andere talen krijgen hun eigen deelplaatje.
            _image(feature, os.path.join(out_dir, 'og.jpg'), (1024, 500), fmt='JPEG', quality=85)
    data['og'] = BASE + asset_dir(app, lang) + 'og.jpg' if lang == 'en' or data['has_feature'] else BASE + asset_dir(app, 'en') + 'og.jpg'


def shot_alt(lang, name, src):
    key = os.path.basename(src).split('-', 1)[1].rsplit('.', 1)[0]
    return f'{name} – {SHOT[key][lang]}'


def video_id(app, lang):
    """Alleen openbare video's (met een uploaddatum); privévideo's slaan we over."""
    vid = VIDEOS.get(app['slug'], {}).get(lang)
    return vid if vid in UPLOADED else None


def hreflang_links(langs, slug):
    lines = [f'  <link rel="alternate" hreflang="{l}" href="{BASE}{page_path(l, slug)}" />' for l in langs]
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{BASE}{page_path("en", slug)}" />')
    return '\n'.join(lines)


def lang_switch(lang, slug, langs):
    pre = prefix(lang, slug)
    items = []
    for l in langs:
        if l == lang:
            items.append(f'<strong>{AUTONYM[l]}</strong>')
        else:
            items.append(f'<a href="{pre}{page_path(l, slug)}" hreflang="{l}" lang="{l}">{AUTONYM[l]}</a>')
    return f'<nav class="lang-switch" aria-label="{UI[lang]["language"]}">' + ' · '.join(items) + '</nav>'


def head(lang, slug, langs, title, desc, og_image, extra_ld):
    pre = prefix(lang, slug)
    url = BASE + page_path(lang, slug)
    ld = '\n'.join(
        f'  <script type="application/ld+json">\n{json.dumps(obj, indent=2, ensure_ascii=False)}\n  </script>'
        for obj in extra_ld)
    # Verificatie voor Pinterest en Bing Webmaster Tools, alleen op de Engelse homepage.
    verify = ('  <meta name="p:domain_verify" content="8a36ac90cfb680cd9bb29832ba4d842f" />\n'
              '  <meta name="msvalidate.01" content="2741EB10E13850E4C3A199FA09C2F3E7" />\n') if lang == 'en' and not slug else ''
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
{verify}  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}" />
  <link rel="canonical" href="{url}" />
{hreflang_links(langs, slug)}
  <meta name="author" content="Joost Muijsenberg" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Joost Muijsenberg" />
  <meta property="og:title" content="{e(title)}" />
  <meta property="og:description" content="{e(desc)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{og_image}" />
  <meta property="og:locale" content="{OG_LOCALE[lang]}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{e(title)}" />
  <meta name="twitter:description" content="{e(desc)}" />
  <meta name="twitter:image" content="{og_image}" />
  <meta name="theme-color" content="#3557e8" />
  <link rel="icon" href="{pre}favicon.png" type="image/png" />
  <link rel="stylesheet" href="{pre}assets/style.css" />
{ld}
</head>'''


def render_blocks(blocks, indent):
    out = []
    for kind, val in blocks:
        if kind == 'p':
            out.append(f'{indent}<p>{e(val)}</p>')
        else:
            out.append(f'{indent}<ul>')
            out.extend(f'{indent}  <li>{e(item)}</li>' for item in val)
            out.append(f'{indent}</ul>')
    return '\n'.join(out)


def faq_items(app, lang, data):
    f = FAQ[lang]
    n = data['name']
    items = [(f['free_q'], f['free_a']), (f['offline_q'], f['offline_a']), (f['account_q'], f['account_a'])]
    howto = data['intro'] if app.get('howto_from_intro') else plain(data['sections'][0]['blocks'])
    items.append((f['howto_q'], howto))
    daily = next((s for s in data['sections'] if s['emoji'] == '📅'), None)
    if daily:
        items.append((f['daily_q'], plain(daily['blocks'])))
    items.append((f['where_q'], f['where_a']) if app['live'] else (f['when_q'], f['when_a']))
    return [(q.format(name=n), a.format(name=n)) for q, a in items]


def related_slugs(app, lang):
    """Drie andere spellen in deze taal: eerst de vaste keuze, dan dezelfde categorie, dan live spellen."""
    pool = [a for a in apps_in(lang) if a['slug'] != app['slug']]
    chosen = [s for s in app['related'] if any(a['slug'] == s for a in pool)]
    for a in sorted(pool, key=lambda a: (a['cat'] != app['cat'], not a['live'])):
        if len(chosen) >= 3:
            break
        if a['slug'] not in chosen:
            chosen.append(a['slug'])
    return chosen[:3]


def card(lang, slug_from, a, all_data):
    pre = prefix(lang, slug_from)
    d = all_data[a['slug']][lang]
    u = UI[lang]
    tag = f'<span class="tag">{u["tag_play"]}</span>' if a['live'] else f'<span class="tag tag-soon">{u["tag_soon"]}</span>'
    href = pre + page_path(lang, a['slug']) if slug_from else page_path(lang, a['slug'])[len(page_path(lang)):]
    return f'''        <a class="card" href="{href}" data-cat="{a["cat"]}">
          <img class="card-icon" src="{pre}assets/apps/{a["slug"]}/icon.png" width="64" height="64" alt="" loading="lazy" />
          <h3>{e(d["name"])}</h3>
          <p>{e(d["short"])}</p>
          {tag}
        </a>'''


def video_block(app, lang, data, pre):
    """Video die pas bij een klik van YouTube laadt (youtube-nocookie); tot dan alleen een eigen beeld."""
    vid = video_id(app, lang)
    dz = DESIGN[lang]
    poster = f'{pre}{asset_dir(app, lang)}feature.webp' if data.get('has_feature') else f'{pre}assets/apps/{app["slug"]}/og.jpg'
    return f'''      <div class="video" data-yt="{vid}" data-hl="{lang}">
        <a class="video-play" href="https://www.youtube.com/watch?v={vid}" rel="noopener" target="_blank" aria-label="{e(dz["play_video"].format(name=data["name"]))}">
          <img src="{poster}" alt="" loading="lazy" decoding="async" />
          <span class="video-icon" aria-hidden="true"></span>
        </a>
      </div>
      <p class="video-note">{dz["video_note"]}</p>'''


def video_ld(app, lang, data):
    vid = video_id(app, lang)
    thumb = BASE + asset_dir(app, lang) + 'feature.webp' if data.get('has_feature') else data['og']
    return {
        '@context': 'https://schema.org',
        '@type': 'VideoObject',
        'name': data['full_name'],
        'description': data['short'],
        'thumbnailUrl': [data['og'], thumb],
        'uploadDate': UPLOADED[vid],
        'embedUrl': f'https://www.youtube.com/embed/{vid}',
        'contentUrl': f'https://www.youtube.com/watch?v={vid}',
        'inLanguage': lang,
    }


def app_page(app, lang, all_data):
    data = all_data[app['slug']][lang]
    u = UI[lang]
    dz = DESIGN[lang]
    slug = app['slug']
    langs = APP_LANGS[slug]
    pre = prefix(lang, slug)
    name = data['name']
    title = u['title'].format(name=name, genre=app['genre'][lang])
    desc = f'{data["short"]} {u["meta_suffix"]}'
    shot_dir = pre + asset_dir(app, lang)
    faqs = faq_items(app, lang, data)
    has_video = app['live'] and video_id(app, lang)

    soft = {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': data['full_name'],
        'alternateName': name,
        'description': data['short'],
        'url': BASE + page_path(lang, slug),
        'image': data['og'],
        'screenshot': [BASE + asset_dir(app, lang) + f'shot-{i}.webp' for i in range(1, 5)],
        'inLanguage': lang,
        'operatingSystem': 'Android',
        'applicationCategory': 'GameApplication',
        'author': {'@type': 'Person', 'name': 'Joost Muijsenberg', 'url': BASE},
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'},
    }
    if app['live']:
        soft['installUrl'] = f'https://play.google.com/store/apps/details?id={app["id"]}'
    crumbs = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': u['games'], 'item': BASE + page_path(lang)},
            {'@type': 'ListItem', 'position': 2, 'name': name, 'item': BASE + page_path(lang, slug)},
        ],
    }
    faq_ld = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs],
    }
    lds = [soft, crumbs, faq_ld] + ([video_ld(app, lang, data)] if has_video else [])

    if app['live']:
        cta = f'''      <a class="play-badge" href="{e(play_url(app, lang, f"{slug}-{lang}"))}" rel="noopener" target="_blank">
        <img src="{pre}assets/google-play-badge.png" width="323" height="125" alt="{e(u["badge_alt"].format(title=data["full_name"]))}" />
      </a>'''
    else:
        cta = f'      <p class="pill">{u["soon_pill"]}</p>'

    shots = '\n'.join(
        f'''        <a class="shot" href="{shot_dir}shot-{i}-lg.webp" aria-label="{e(dz["enlarge"])}">
          <img src="{shot_dir}shot-{i}.webp" width="340" height="604" alt="{e(shot_alt(lang, name, src))}" loading="lazy" decoding="async" />
        </a>'''
        for i, src in enumerate(data['shots'], 1))

    video = ''
    if has_video:
        video = f'''
      <h2>{dz["video_h"]}</h2>
{video_block(app, lang, data, pre)}
'''

    sticky = ''
    if app['live']:
        sticky = f'''
  <div class="sticky-cta">
    <img src="{pre}assets/apps/{slug}/icon.png" width="40" height="40" alt="" />
    <div class="sticky-text"><strong>{e(name)}</strong><span>{dz["sticky_sub"]}</span></div>
    <a class="sticky-btn" href="{e(play_url(app, lang, f"{slug}-{lang}-sticky"))}" rel="noopener" target="_blank">{dz["install"]}</a>
  </div>'''

    features = '\n'.join(f'''      <section class="feature">
        <h3><span class="feature-emoji" aria-hidden="true">{s["emoji"]}</span>{e(heading(lang, s["title"]))}</h3>
{render_blocks(s["blocks"], "        ")}
      </section>''' for s in data['sections'])

    faq_html = '\n'.join(f'''        <details>
          <summary>{e(q)}</summary>
          <p>{e(a)}</p>
        </details>''' for q, a in faqs)

    rel = related_slugs(app, lang)
    related = ''
    if rel:
        cards = '\n'.join(card(lang, slug, BY_SLUG[r], all_data) for r in rel)
        related = f'''
      <h2>{u["more_h"]}</h2>
      <div class="card-grid">
{cards}
      </div>
'''
    legal_pre = pre + slug + '/' if lang != 'en' else ''
    mail = f'<a href="mailto:{MAIL}">{MAIL}</a>'

    return f'''{head(lang, slug, langs, title, desc, data["og"], lds)}
<body class="app-page{' has-sticky' if app['live'] else ''}" style="--app: {app['color']}">
  <div class="container">
    <div class="topbar">
      <nav class="crumbs"><a href="{pre}{page_path(lang)}">{u["games"]}</a> &nbsp;/&nbsp; {e(name)}</nav>
      {lang_switch(lang, slug, langs)}
    </div>

    <header class="hero">
      <img class="hero-icon" src="{pre}assets/apps/{slug}/icon.png" width="96" height="96" alt="{e(u["icon_alt"].format(name=name))}" />
      <div class="hero-text">
        <h1>{e(name)}</h1>
        <p class="lead">{e(data["short"])}</p>
      </div>
    </header>

    <div class="cta">
{cta}
    </div>

    <main>
      <div class="shots" data-close="{e(dz["close"])}" data-prev="{e(dz["prev"])}" data-next="{e(dz["next"])}">
{shots}
      </div>
{video}
      <h2>{e(u["about_h"].format(name=name))}</h2>
      <p>{e(data["intro"])}</p>

      <div class="features">
{features}
      </div>

      <p class="note">{u["note"]}</p>

      <h2>{u["faq_h"]}</h2>
      <div class="faq">
{faq_html}
      </div>
{related}
      <h2>{u["legal_h"]}</h2>
      <p>{e(u["legal_p"].format(name=name))}</p>

      <div class="doc-links">
        <a href="{legal_pre}privacy.html">{u["privacy"]}{u["in_english"]}</a>
        <a href="{legal_pre}terms.html">{u["terms"]}{u["in_english"]}</a>
      </div>

      <h2>{u["contact_h"]}</h2>
      <p>{u["contact_p"].format(mail=mail)}</p>
    </main>

    <footer class="site">
      <p>&copy; <span id="year">{TODAY[:4]}</span> Joost Muijsenberg. {u["hobby"]} <a href="{pre}{page_path(lang)}">{u["all_games"]}</a></p>
      {lang_switch(lang, slug, langs)}
    </footer>
  </div>{sticky}
  <script src="{pre}assets/site.js" defer></script>
</body>
</html>
'''


def hero_shots(lang):
    """De drie telefoons in de kop: de vaste keuze waar die in deze taal bestaat, aangevuld met
    andere live spellen en, als er te weinig spellen zijn, met meer beelden van dezelfde spellen."""
    apps = apps_in(lang)
    avail = {a['slug'] for a in apps}
    shots = [(slug, n) for slug, n in HERO_SHOTS if slug in avail]
    used = {slug for slug, _ in shots}
    for a in apps:
        if len(shots) < 3 and a['live'] and a['slug'] not in used:
            shots.append((a['slug'], 2))
            used.add(a['slug'])
    for n in (3, 1, 4):
        for a in apps:
            if len(shots) < 3 and (a['slug'], n) not in shots:
                shots.append((a['slug'], n))
    return shots[:3]


def featured_app(lang):
    candidates = [BY_SLUG[FEATURED]] + [a for a in APPS if a['slug'] != FEATURED]
    return next((a for a in candidates if lang in APP_LANGS[a['slug']] and a['live'] and video_id(a, lang)), None)


def home_page(lang, all_data):
    u = UI[lang]
    dz = DESIGN[lang]
    pre = prefix(lang)
    apps = apps_in(lang)
    live = [a for a in apps if a['live']]

    cards = [(all_data[a['slug']][lang]['name'], card(lang, None, a, all_data)) for a in apps]
    if lang == 'en':
        cards.extend(EN_CONCEPT_CARDS)
    cards.sort(key=lambda c: c[0].lower())

    strip = '\n'.join(
        f'''        <a class="play-chip" href="{e(play_url(a, lang, f"home-{lang}"))}" rel="noopener" target="_blank">
          <img src="{pre}assets/apps/{a["slug"]}/icon.png" width="40" height="40" alt="" loading="lazy" />
          <span>{e(all_data[a["slug"]][lang]["name"])}</span>
        </a>''' for a in sorted(live, key=lambda a: all_data[a['slug']][lang]['name'].lower()))

    website = {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        'name': 'Joost Muijsenberg',
        'url': BASE + page_path(lang),
        'inLanguage': lang,
        'description': u['home_desc'],
        'author': {'@type': 'Person', 'name': 'Joost Muijsenberg', 'email': MAIL},
    }
    items = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': u['games_by'],
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': all_data[a['slug']][lang]['full_name'], 'url': BASE + page_path(lang, a['slug'])}
            for i, a in enumerate(sorted(apps, key=lambda a: all_data[a['slug']][lang]['name'].lower()), 1)
        ],
    }
    lds = [website, items]

    filters = '\n'.join(
        f'        <button type="button" class="filter" data-cat="{c}" aria-pressed="{"true" if c == "all" else "false"}">{dz["cat"][c]}</button>'
        for c in ['all'] + CATEGORIES)
    pills = ''.join(f'<li>{p}</li>' for p in dz['pills'])
    phones = '\n'.join(
        f'          <img src="{pre}{asset_dir(BY_SLUG[s], lang)}shot-{n}.webp" width="340" height="604" alt="" />'
        for s, n in hero_shots(lang))

    featured = ''
    fa = featured_app(lang)
    if fa:
        fd = all_data[fa['slug']][lang]
        lds.append(video_ld(fa, lang, fd))
        featured = f'''
      <h2>{dz["featured_h"]}</h2>
      <section class="featured" style="--app: {fa["color"]}">
{video_block(fa, lang, fd, pre)}
        <div class="featured-text">
          <img class="card-icon" src="{pre}assets/apps/{fa["slug"]}/icon.png" width="64" height="64" alt="" />
          <h3>{e(fd["name"])}</h3>
          <p>{e(fd["short"])}</p>
          <div class="featured-actions">
            <a class="play-badge" href="{e(play_url(fa, lang, f"featured-{lang}"))}" rel="noopener" target="_blank">
              <img src="{pre}assets/google-play-badge.png" width="323" height="125" alt="{e(u["badge_alt"].format(title=fd["full_name"]))}" />
            </a>
            <a href="{page_path(lang, fa["slug"])[len(page_path(lang)):]}">{e(dz["more_about"].format(name=fd["name"]))}</a>
          </div>
        </div>
      </section>
'''

    more_en = ''
    if lang != 'en' and len(apps) < len(APPS):
        link = f'<a href="{pre}" hreflang="en" lang="en">English</a>'
        more_en = f'\n      <p class="note">{MORE_IN_EN[lang].format(link=link)}</p>'

    mail = f'<a href="mailto:{MAIL}">{MAIL}</a>'
    return f'''{head(lang, None, LANGS, u["home_title"], u["home_desc"], BASE + "assets/og-default.jpg", lds)}
<body>
  <div class="container">
    <header class="home-hero">
      {lang_switch(lang, None, LANGS)}
      <div class="home-hero-grid">
        <div class="home-hero-text">
          <p class="eyebrow">Joost Muijsenberg</p>
          <h1>{dz["hero_h"]}</h1>
          <p class="hero-tagline">{dz["hero_sub"]}</p>
          <ul class="pills">{pills}</ul>
        </div>
        <div class="hero-phones" aria-hidden="true">
{phones}
        </div>
      </div>
    </header>

    <main>
      <h2 style="margin-top:0">{u["play_strip_h"]}</h2>
      <div class="play-strip">
{strip}
      </div>
{featured}
      <h2>{u["games_h"]}</h2>
      <p class="lead">{u["games_lead"].format(live=len(live))}</p>
      <div class="filters" role="group" aria-label="{dz["filter_label"]}" hidden>
{filters}
      </div>
      <div class="card-grid" id="games">
{chr(10).join(c[1] for c in cards)}
      </div>{more_en}

      <h2>{u["about_site_h"]}</h2>
      <p>{u["about_site_p"]}</p>

      <h2>{u["contact_h"]}</h2>
      <p>{u["home_contact_p"].format(mail=mail)}</p>
    </main>

    <footer class="site">
      <p>&copy; <span id="year">{TODAY[:4]}</span> Joost Muijsenberg. {u["hobby"]}</p>
    </footer>
  </div>
  <script src="{pre}assets/site.js" defer></script>
</body>
</html>
'''


def llms_txt(all_data):
    """Kort, feitelijk overzicht voor AI-zoekmachines (llmstxt.org)."""
    en = {a['slug']: all_data[a['slug']]['en'] for a in APPS}
    lines = [
        '# Joost Muijsenberg — free puzzle and card games for Android',
        '',
        '> Small, classic Android games made by Joost Muijsenberg as a hobby project in his spare time. '
        'Every game is free, works fully offline and never asks for an account; progress stays on the device. '
        'The games show ads, which can be removed with one optional in-app purchase.',
        '',
        'Each game has its own page with screenshots, a description, frequently asked questions, '
        'its privacy policy and terms of service. Pages exist in several languages; the language versions are listed per game.',
        '',
        '## Games on Google Play',
        '',
    ]

    def entry(a):
        d = en[a['slug']]
        other = [f'[{AUTONYM[l]}]({BASE}{page_path(l, a["slug"])})' for l in APP_LANGS[a['slug']] if l != 'en']
        s = f'- [{d["full_name"]}]({BASE}{page_path("en", a["slug"])}): {d["short"]}'
        if a['live']:
            s += f' Google Play: https://play.google.com/store/apps/details?id={a["id"]}'
        if other:
            s += ' Also in: ' + ', '.join(other) + '.'
        return s

    lines += [entry(a) for a in APPS if a['live']]
    lines += ['', '## Coming soon to Google Play', '']
    lines += [entry(a) for a in APPS if not a['live']]
    lines += ['', '## Site in other languages', '']
    lines += [f'- [{AUTONYM[l]}]({BASE}{page_path(l)})' for l in LANGS if l != 'en']
    lines += ['', '## Contact', '', f'- Email: {MAIL}', f'- Sitemap: {BASE}sitemap.xml', '']
    write('llms.txt', '\n'.join(lines))


def write(rel, content):
    path = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def lastmod(rel):
    """Datum van de laatste commit als het bestand ongewijzigd is, anders vandaag."""
    path = os.path.join(SITE, rel)
    if os.path.isdir(path):
        path = os.path.join(path, 'index.html')
    r = subprocess.run(['git', 'status', '--porcelain', '--', path], cwd=SITE, capture_output=True, text=True)
    if r.stdout.strip():
        return TODAY
    r = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', path], cwd=SITE, capture_output=True, text=True)
    return r.stdout.strip() or TODAY


def sitemap():
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']

    def url(rel, prio, langs=None, slug=None):
        out.append('  <url>')
        out.append(f'    <loc>{BASE}{rel}</loc>')
        if langs:
            for l in langs:
                out.append(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{BASE}{page_path(l, slug)}" />')
            out.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{page_path("en", slug)}" />')
        out.append(f'    <lastmod>{lastmod(rel or "index.html")}</lastmod>')
        out.append(f'    <priority>{prio}</priority>')
        out.append('  </url>')

    for l in LANGS:
        url(page_path(l), '1.0' if l == 'en' else '0.9', LANGS, None)
    for a in APPS:
        for l in APP_LANGS[a['slug']]:
            url(page_path(l, a['slug']), '0.8', APP_LANGS[a['slug']], a['slug'])
    for a in APPS:
        url(f'{a["slug"]}/privacy.html', '0.3')
        url(f'{a["slug"]}/terms.html', '0.3')
    for rel, prio in EXTRA_SITEMAP:
        url(rel, prio)
    out.append('</urlset>')
    write('sitemap.xml', '\n'.join(out) + '\n')


def main():
    for a in APPS:
        switches = app_language_switches(a['dir']) or {}
        APP_LANGS[a['slug']] = [l for l in LANGS if l == 'en' or (switches.get(l) and has_listing(a['dir'], l))]
    all_data = {a['slug']: {l: load(a, l) for l in APP_LANGS[a['slug']]} for a in APPS}
    pages = 0
    for a in APPS:
        for l in APP_LANGS[a['slug']]:
            convert_images(a, l, all_data[a['slug']][l])
    for a in APPS:
        for l in APP_LANGS[a['slug']]:
            write(page_path(l, a['slug']) + 'index.html', app_page(a, l, all_data))
            pages += 1
    for l in LANGS:
        write(page_path(l) + 'index.html', home_page(l, all_data))
    sitemap()
    llms_txt(all_data)
    print(f'{pages} app-pagina\'s en {len(LANGS)} homepages geschreven, plus sitemap.xml en llms.txt.')


if __name__ == '__main__':
    main()
