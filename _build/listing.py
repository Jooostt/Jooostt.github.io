"""Leest de Play-listingteksten (PlayStoreAssets/metadata) van de apps in."""
import glob
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

BULLET = '•'


def _read(path):
    with open(path, encoding='utf-8-sig') as f:
        return f.read().replace('\r\n', '\n').strip()


def meta_file(app_dir, lang, kind):
    """kind: app-name, short-description of full-description."""
    d = os.path.join(ROOT, app_dir, 'PlayStoreAssets', 'metadata', lang)
    for name in (f'{lang}_{kind}.txt', f'{kind}.txt'):
        p = os.path.join(d, name)
        if os.path.exists(p):
            # Een paar bestanden bevatten per ongeluk twee varianten achter elkaar; neem de eerste regel.
            text = _read(p)
            return text if kind == 'full-description' else text.split('\n')[0]
    raise FileNotFoundError(f'{app_dir} {lang} {kind}')


def _is_heading(line):
    # "🧩 HOW TO PLAY": begint met een symbool en de rest staat in hoofdletters.
    if not line or line[0].isalnum() or line.startswith(BULLET):
        return False
    rest = line.split(' ', 1)[1] if ' ' in line else ''
    letters = [c for c in rest if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def parse_description(text):
    """Geeft (intro, secties) terug. Een sectie is {emoji, title, blocks}; een block is
    ('p', tekst) of ('ul', [punten]). De afsluitende alinea's (gratis/advertenties, groet)
    vallen weg; die tekst staat op de site in een eigen, actuele zin."""
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    intro = paras[0]
    rest = paras[1:]
    # Alinea's zonder kop aan het eind zijn de afsluiter.
    end = len(rest)
    while end > 0 and not _is_heading(rest[end - 1].split('\n')[0]):
        end -= 1
    # De laatste sectie kan zelf nog een losse slotalinea bevatten (geen opsomming, wel "gratis").
    sections = []
    for para in rest[:end] + []:
        lines = para.split('\n')
        if _is_heading(lines[0]):
            emoji, title = lines[0].split(' ', 1)
            sections.append({'emoji': emoji, 'title': title.strip(), 'blocks': []})
            lines = lines[1:]
        target = sections[-1]['blocks']
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(BULLET):
                item = line[1:].strip()
                if target and target[-1][0] == 'ul':
                    target[-1][1].append(item)
                else:
                    target.append(('ul', [item]))
            else:
                target.append(('p', line))
    trailer = rest[end:]
    return intro, sections, trailer


_SKIP = {'bin', 'obj', 'node_modules', 'PlayStoreAssets', '.git', '.vs'}


def _switch_files(project_dir, max_depth=4):
    out = []
    for dirpath, dirs, files in os.walk(project_dir):
        rel = os.path.relpath(dirpath, project_dir)
        depth = 0 if rel == '.' else rel.count(os.sep) + 1
        dirs[:] = [d for d in dirs if d not in _SKIP and not d.startswith('.')] if depth < max_depth else []
        out += [os.path.join(dirpath, f) for f in files if f in ('LocalizationManager.cs', 'LanguageSettings.cs')]
    return out


def app_language_switches(app_dir):
    """Talen die in de app aan staan, gelezen zoals het portaal dat doet (AppLanguageSwitchReader):
    eerst de LanguageEnabled-tabel, dan LanguageSettings, anders de vertaalblokken zelf."""
    project_dir = os.path.join(ROOT, app_dir)
    files = _switch_files(project_dir)
    code = r'"([a-z]{2,3}(?:-[A-Za-z]{2,4})?)"'
    for f in files:
        if f.endswith('LocalizationManager.cs'):
            text = _read(f)
            start = text.find('LanguageEnabled')
            if start >= 0:
                block = text[start:text.find('};', start)]
                table = {c: v == 'true' for c, v in re.findall(r'\[' + code + r'\]\s*=\s*(true|false)', block)}
                if table:
                    return table
    for f in files:
        if f.endswith('LanguageSettings.cs'):
            table = {c: v == 'true' for c, v in re.findall(r'new\s+LanguageInfo\(\s*' + code + r'[^)]*?Enabled:\s*(true|false)', _read(f))}
            if table:
                return table
    for f in files:
        if f.endswith('LocalizationManager.cs'):
            table = {c: True for c in re.findall(r'\[' + code + r'\]\s*=\s*new\s+Dictionary<string,\s*string>', _read(f))}
            if table:
                return table
    return None


def has_listing(app_dir, lang):
    base = os.path.join(ROOT, app_dir, 'PlayStoreAssets')
    return (bool(glob.glob(os.path.join(base, 'metadata', lang, '*full-description.txt')))
            and len(glob.glob(os.path.join(base, 'screenshots', lang, f'{lang}_0[1-4]-*.png'))) == 4)
