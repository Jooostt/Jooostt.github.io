"""Bouwt de app-pagina's en de homepage in alle talen, plus sitemap.xml.

Gebruik (vanuit de root van de site):  py -3 _build/build.py

De teksten van de spellen komen uit de Play-listings in PlayStoreAssets/metadata van elke app;
de vertaalde schermafbeeldingen uit PlayStoreAssets/screenshots. Privacybeleid en voorwaarden
worden niet aangeraakt, net als de pagina's van de conceptapps.
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
from apps import APPS, BY_SLUG  # noqa: E402
from i18n import AUTONYM, FAQ, LANGS, OG_LOCALE, SHOT, UI, heading  # noqa: E402
from listing import ROOT, meta_file, parse_description  # noqa: E402

SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BASE = 'https://jooostt.github.io/'
MAIL = 'joostmuijsenberg.dev@gmail.com'
TODAY = datetime.date.today().isoformat()

# Conceptapps die op de Engelse homepage blijven staan zoals ze waren.
EN_CONCEPT_CARDS = [
    ('Forbidden Words', '''        <a class="card" href="forbidden-words/">
          <img class="card-icon" src="assets/apps/forbidden-words/icon.png" width="64" height="64" alt="" loading="lazy" />
          <h3>Forbidden Words</h3>
          <p>Explain the word without saying it! A fast and funny party word game for friends and family.</p>
          <span class="tag tag-soon">Coming soon</span>
        </a>'''),
    ('FactFlow', '''        <a class="card" href="factflow/">
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


def convert_shots(app, lang, data):
    """Vertaalde schermafbeeldingen in hetzelfde formaat als de Engelse (340x604 webp)."""
    from PIL import Image
    out_dir = os.path.join(SITE, 'assets', 'apps', app['slug'], lang)
    os.makedirs(out_dir, exist_ok=True)
    for i, src in enumerate(data['shots'], 1):
        dst = os.path.join(out_dir, f'shot-{i}.webp')
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        im = Image.open(src).convert('RGB').resize((340, 604), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=80, method=6)


def shot_alt(lang, name, src):
    key = os.path.basename(src).split('-', 1)[1].rsplit('.', 1)[0]
    return f'{name} – {SHOT[key][lang]}'


def hreflang_links(slug):
    lines = [f'  <link rel="alternate" hreflang="{l}" href="{BASE}{page_path(l, slug)}" />' for l in LANGS]
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{BASE}{page_path("en", slug)}" />')
    return '\n'.join(lines)


def lang_switch(lang, slug):
    pre = prefix(lang, slug)
    items = []
    for l in LANGS:
        if l == lang:
            items.append(f'<strong>{AUTONYM[l]}</strong>')
        else:
            items.append(f'<a href="{pre}{page_path(l, slug)}" hreflang="{l}" lang="{l}">{AUTONYM[l]}</a>')
    return f'<nav class="lang-switch" aria-label="{UI[lang]["language"]}">' + ' · '.join(items) + '</nav>'


def head(lang, slug, title, desc, og_image, extra_ld):
    pre = prefix(lang, slug)
    url = BASE + page_path(lang, slug)
    ld = '\n'.join(
        f'  <script type="application/ld+json">\n{json.dumps(obj, indent=2, ensure_ascii=False)}\n  </script>'
        for obj in extra_ld)
    verify = '  <meta name="p:domain_verify" content="8a36ac90cfb680cd9bb29832ba4d842f" />\n' if lang == 'en' and not slug else ''
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
{verify}  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}" />
  <link rel="canonical" href="{url}" />
{hreflang_links(slug)}
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


def related_card(lang, slug, rel, all_data):
    pre = prefix(lang, slug)
    d = all_data[rel][lang]
    app = BY_SLUG[rel]
    u = UI[lang]
    tag = f'<span class="tag">{u["tag_play"]}</span>' if app['live'] else f'<span class="tag tag-soon">{u["tag_soon"]}</span>'
    return f'''        <a class="card" href="{pre}{page_path(lang, rel)}">
          <img class="card-icon" src="{pre}assets/apps/{rel}/icon.png" width="64" height="64" alt="" loading="lazy" />
          <h3>{e(d["name"])}</h3>
          <p>{e(d["short"])}</p>
          {tag}
        </a>'''


def app_page(app, lang, all_data):
    data = all_data[app['slug']][lang]
    u = UI[lang]
    slug = app['slug']
    pre = prefix(lang, slug)
    name = data['name']
    title = u['title'].format(name=name, genre=app['genre'][lang])
    desc = f'{data["short"]} {u["meta_suffix"]}'
    og = f'{BASE}assets/apps/{slug}/og.jpg'
    shot_dir = f'{pre}assets/apps/{slug}/' + ('' if lang == 'en' else f'{lang}/')
    faqs = faq_items(app, lang, data)

    soft = {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': data['full_name'],
        'alternateName': name,
        'description': data['short'],
        'url': BASE + page_path(lang, slug),
        'image': og,
        'screenshot': [f'{BASE}assets/apps/{slug}/' + ('' if lang == 'en' else f'{lang}/') + f'shot-{i}.webp' for i in range(1, 5)],
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

    if app['live']:
        cta = f'''      <a class="play-badge" href="{e(play_url(app, lang, f"{slug}-{lang}"))}" rel="noopener" target="_blank">
        <img src="{pre}assets/google-play-badge.png" width="323" height="125" alt="{e(u["badge_alt"].format(title=data["full_name"]))}" />
      </a>'''
    else:
        cta = f'      <p class="pill">{u["soon_pill"]}</p>'

    shots = '\n'.join(
        f'        <img src="{shot_dir}shot-{i}.webp" width="340" height="604" alt="{e(shot_alt(lang, name, src))}" loading="lazy" decoding="async" />'
        for i, src in enumerate(data['shots'], 1))

    features = '\n'.join(f'''      <section class="feature">
        <h3><span class="feature-emoji" aria-hidden="true">{s["emoji"]}</span>{e(heading(lang, s["title"]))}</h3>
{render_blocks(s["blocks"], "        ")}
      </section>''' for s in data['sections'])

    faq_html = '\n'.join(f'''        <details>
          <summary>{e(q)}</summary>
          <p>{e(a)}</p>
        </details>''' for q, a in faqs)

    related = '\n'.join(related_card(lang, slug, r, all_data) for r in app['related'])
    legal_pre = pre + slug + '/' if lang != 'en' else ''
    mail = f'<a href="mailto:{MAIL}">{MAIL}</a>'

    return f'''{head(lang, slug, title, desc, og, [soft, crumbs, faq_ld])}
<body>
  <div class="container">
    <div class="topbar">
      <nav class="crumbs"><a href="{pre}{page_path(lang)}">{u["games"]}</a> &nbsp;/&nbsp; {e(name)}</nav>
      {lang_switch(lang, slug)}
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
      <div class="shots">
{shots}
      </div>

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

      <h2>{u["more_h"]}</h2>
      <div class="card-grid">
{related}
      </div>

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
      <p>&copy; <span id="year">{TODAY[:4]}</span> Joost Muijsenberg. <a href="{pre}{page_path(lang)}">{u["all_games"]}</a></p>
      {lang_switch(lang, slug)}
    </footer>
  </div>
  <script src="{pre}assets/site.js" defer></script>
</body>
</html>
'''


def home_page(lang, all_data):
    u = UI[lang]
    pre = prefix(lang)
    live = [a for a in APPS if a['live']]
    cards = []
    for a in APPS:
        d = all_data[a['slug']][lang]
        tag = f'<span class="tag">{u["tag_play"]}</span>' if a['live'] else f'<span class="tag tag-soon">{u["tag_soon"]}</span>'
        cards.append((d['name'], f'''        <a class="card" href="{page_path(lang, a["slug"])[len(page_path(lang)):]}">
          <img class="card-icon" src="{pre}assets/apps/{a["slug"]}/icon.png" width="64" height="64" alt="" loading="lazy" />
          <h3>{e(d["name"])}</h3>
          <p>{e(d["short"])}</p>
          {tag}
        </a>'''))
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
            for i, a in enumerate(sorted(APPS, key=lambda a: all_data[a['slug']][lang]['name'].lower()), 1)
        ],
    }
    mail = f'<a href="mailto:{MAIL}">{MAIL}</a>'
    return f'''{head(lang, None, u["home_title"], u["home_desc"], BASE + "assets/og-default.jpg", [website, items])}
<body>
  <div class="container">
    <header class="site">
      {lang_switch(lang, None)}
      <h1>Joost Muijsenberg</h1>
      <p>{u["home_tagline"]}</p>
    </header>

    <main>
      <h2 style="margin-top:0">{u["play_strip_h"]}</h2>
      <div class="play-strip">
{strip}
      </div>

      <h2>{u["games_h"]}</h2>
      <p class="lead">{u["games_lead"].format(live=len(live))}</p>
      <div class="card-grid">
{chr(10).join(c[1] for c in cards)}
      </div>

      <h2>{u["about_site_h"]}</h2>
      <p>{u["about_site_p"]}</p>

      <h2>{u["contact_h"]}</h2>
      <p>{u["home_contact_p"].format(mail=mail)}</p>
    </main>

    <footer class="site">
      <p>&copy; <span id="year">{TODAY[:4]}</span> Joost Muijsenberg.</p>
    </footer>
  </div>
  <script src="{pre}assets/site.js" defer></script>
</body>
</html>
'''


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

    def url(rel, prio, alternates_slug=False, slug=None):
        out.append('  <url>')
        out.append(f'    <loc>{BASE}{rel}</loc>')
        if alternates_slug:
            for l in LANGS:
                out.append(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{BASE}{page_path(l, slug)}" />')
            out.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{page_path("en", slug)}" />')
        out.append(f'    <lastmod>{lastmod(rel or "index.html")}</lastmod>')
        out.append(f'    <priority>{prio}</priority>')
        out.append('  </url>')

    for l in LANGS:
        url(page_path(l), '1.0' if l == 'en' else '0.9', True, None)
    for a in APPS:
        for l in LANGS:
            url(page_path(l, a['slug']), '0.8', True, a['slug'])
    for a in APPS:
        url(f'{a["slug"]}/privacy.html', '0.3')
        url(f'{a["slug"]}/terms.html', '0.3')
    for rel, prio in EXTRA_SITEMAP:
        url(rel, prio)
    out.append('</urlset>')
    write('sitemap.xml', '\n'.join(out) + '\n')


def main():
    all_data = {a['slug']: {l: load(a, l) for l in LANGS} for a in APPS}
    for a in APPS:
        for l in LANGS:
            if l != 'en':
                convert_shots(a, l, all_data[a['slug']][l])
            write(page_path(l, a['slug']) + 'index.html', app_page(a, l, all_data))
    for l in LANGS:
        write(page_path(l) + 'index.html', home_page(l, all_data))
    sitemap()
    print(f'{len(APPS) * len(LANGS)} app-pagina\'s en {len(LANGS)} homepages geschreven.')


if __name__ == '__main__':
    main()
