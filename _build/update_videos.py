"""Werkt videos.py bij: de promovideo per app en taal uit het portaal (PlayLocaleStatus) en de
uploaddatum van elke video van YouTube (nodig voor de VideoObject-gegevens).

Gebruik (vanuit de root van de site):  py -3 _build/update_videos.py
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from apps import APPS  # noqa: E402
from i18n import LANGS  # noqa: E402

# Welke Play-locale per taal telt (de eerste die een video heeft).
LOCALES = {
    'en': ['en-US'], 'nl': ['nl-NL'], 'de': ['de-DE'], 'es': ['es-ES', 'es-419'], 'fr': ['fr-FR'],
    'pt': ['pt-BR', 'pt-PT'], 'it': ['it-IT'], 'tr': ['tr-TR'], 'pl': ['pl-PL'], 'ro': ['ro', 'ro-RO'],
    'ru': ['ru-RU'], 'ca': ['ca', 'ca-ES'],
}

QUERY = """SET NOCOUNT ON;
WITH s AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY PackageName ORDER BY Id DESC) rn FROM PlayStatuses)
SELECT s.PackageName, l.Locale, l.VideoUrl FROM s JOIN PlayLocaleStatus l ON l.AppStatusId = s.Id
WHERE rn = 1 AND l.VideoUrl LIKE '%v=%'"""


def main():
    out = subprocess.run(['sqlcmd', '-S', 'localhost', '-d', 'PlayStoreListings', '-E', '-C', '-W', '-h-1', '-s', '|',
                          '-Q', QUERY], capture_output=True, text=True, check=True).stdout
    found = {}
    for line in out.splitlines():
        parts = line.strip().split('|')
        if len(parts) == 3:
            found[(parts[0], parts[1])] = parts[2].split('v=')[1].split('&')[0]

    videos = {}
    for a in APPS:
        for lang in LANGS:
            vid = next((found[(a['id'], loc)] for loc in LOCALES[lang] if (a['id'], loc) in found), None)
            if vid:
                videos.setdefault(a['slug'], {})[lang] = vid

    dates = {}
    for vid in sorted({v for per in videos.values() for v in per.values()}):
        # curl in plaats van urllib: dat gaat via dezelfde netwerkinstellingen als de rest van het systeem.
        page = ''
        for _ in range(3):
            r = subprocess.run(['curl', '-s', '--max-time', '30', '-A', 'Mozilla/5.0', '-H', 'Accept-Language: en',
                                f'https://www.youtube.com/watch?v={vid}'], capture_output=True, text=True, encoding='utf-8', errors='replace')
            page = r.stdout
            if 'uploadDate' in page:
                break
        m = re.search(r'itemprop="uploadDate" content="([^"]+)"', page) or re.search(r'"uploadDate":"([^"]+)"', page)
        if m:
            dates[vid] = m.group(1)
        else:
            print(f'geen uploaddatum voor {vid}')

    lines = ['"""YouTube-promovideo per app en taal (uit de Play-listings) en de uploaddatum per video.',
             'Bijwerken met: py -3 _build/update_videos.py"""', '', 'VIDEOS = {']
    for slug, per in videos.items():
        lines.append(f'    {slug!r}: {{' + ', '.join(f'{l!r}: {v!r}' for l, v in per.items()) + '},')
    lines += ['}', '', 'UPLOADED = {']
    lines += [f'    {vid!r}: {d!r},' for vid, d in dates.items()]
    lines += ['}', '']
    with open(os.path.join(os.path.dirname(__file__), 'videos.py'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print(f'{sum(len(p) for p in videos.values())} video-koppelingen, {len(dates)} uploaddatums.')


if __name__ == '__main__':
    main()
