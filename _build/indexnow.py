"""Meldt gewijzigde pagina's bij IndexNow (Bing, Yandex, Seznam, Naver), zodat ze snel opnieuw
gecrawld worden. Draai dit nadat de wijzigingen gepusht zijn en GitHub Pages ze serveert.

Gebruik (vanuit de root van de site):
  py -3 _build/indexnow.py            pagina's uit de laatste commit
  py -3 _build/indexnow.py HEAD~3     pagina's die sinds die commit veranderd zijn
  py -3 _build/indexnow.py --all      alle pagina's uit sitemap.xml
"""
import json
import os
import re
import subprocess
import sys

SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BASE = 'https://jooostt.github.io/'
HOST = 'jooostt.github.io'
# De sleutel staat ook als bestand in de root van de site: <sleutel>.txt
KEY = '629bac05e3b0321da41fa693e47b3814'


def changed_urls(since):
    out = subprocess.run(['git', 'diff', '--name-only', since, 'HEAD'], cwd=SITE,
                         capture_output=True, text=True, check=True).stdout.split()
    urls = []
    for path in out:
        if path.startswith('_') or not path.endswith(('.html', 'llms.txt')):
            continue
        if not os.path.exists(os.path.join(SITE, path)):
            continue
        urls.append(BASE + (path[:-len('index.html')] if path.endswith('index.html') else path))
    return urls


def sitemap_urls():
    with open(os.path.join(SITE, 'sitemap.xml'), encoding='utf-8') as f:
        return re.findall(r'<loc>([^<]+)</loc>', f.read())


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else 'HEAD~1'
    urls = sitemap_urls() if arg == '--all' else changed_urls(arg)
    if not urls:
        print('Geen gewijzigde pagina\'s.')
        return
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'{BASE}{KEY}.txt', 'urlList': urls[:10000]})
    # curl in plaats van urllib: dat gaat via dezelfde netwerkinstellingen als de rest van het systeem.
    r = subprocess.run(['curl', '-s', '-o', '-', '-w', '\n%{http_code}', '-X', 'POST',
                        '-H', 'Content-Type: application/json; charset=utf-8',
                        '--data-binary', '@-', 'https://api.indexnow.org/indexnow'],
                       input=body, capture_output=True, text=True, encoding='utf-8')
    status = r.stdout.strip().rsplit('\n', 1)[-1]
    print(f'{len(urls)} URL\'s gemeld bij IndexNow, antwoord: HTTP {status}')
    if status not in ('200', '202'):
        print(r.stdout)
        sys.exit(1)


if __name__ == '__main__':
    main()
