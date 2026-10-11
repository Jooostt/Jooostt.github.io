"""De apps op de site. Conceptapps (Forbidden Words, FactFlow, Aquarium, Butterfly Garden)
staan hier bewust niet in; hun pagina's worden met de hand bijgehouden."""

# slug = map op de site, dir = map met PlayStoreAssets, live = staat publiek op Google Play.
# genre: het soort spel in de paginatitel, per taal.
# color: accentkleur van de pagina, afgestemd op het icoon. cat: filter op de homepage.
# related: drie andere spellen onderaan de pagina, bij voorkeur spellen die al live zijn.
APPS = [
    {
        'slug': 'mergepuzzle', 'color': '#e3a33b', 'cat': 'puzzle', 'dir': '2048/MergePuzzle', 'id': 'com.joostmuijsenberg.mergepuzzle', 'live': False,
        'genre': {'en': 'Number Puzzle', 'nl': 'getallenpuzzel', 'de': 'Zahlenpuzzle', 'es': 'puzle numérico', 'fr': 'jeu de chiffres', 'pt': 'puzzle de números'},
        'related': ['blockpuzzle', 'sudoku', 'MineSweeper'],
    },
    {
        'slug': '30-seconds', 'color': '#1fb5a8', 'cat': 'party', 'dir': '30Seconds', 'id': 'com.joostmuijsenberg.thirtyseconds', 'live': True,
        'genre': {'en': 'Party Word Game', 'nl': 'partyspel', 'de': 'Partyspiel', 'es': 'juego de palabras para fiestas', 'fr': 'jeu de mots pour soirées', 'pt': 'jogo de palavras para festas', 'it': 'gioco di parole per feste', 'tr': 'parti kelime oyunu', 'pl': 'imprezowa gra słowna', 'ro': 'joc de cuvinte pentru petreceri'},
        'related': ['wordconnect', 'hartenjagen', 'wordsearch'],
    },
    {
        'slug': 'blockpuzzle', 'color': '#3fae6a', 'cat': 'puzzle', 'dir': 'BlockPuzzle/BlockPuzzle', 'id': 'com.joostmuijsenberg.blockpuzzle', 'live': True,
        'genre': {'en': 'Block Puzzle Game', 'nl': 'puzzelspel', 'de': 'Denkspiel', 'es': 'juego de lógica', 'fr': 'jeu de blocs', 'pt': 'jogo de lógica', 'it': 'gioco di logica', 'ru': 'головоломка', 'tr': 'zekâ oyunu'},
        'related': ['sudoku', 'nonogram', 'MineSweeper'],
    },
    {
        'slug': 'colorsort', 'color': '#e5484d', 'cat': 'puzzle', 'dir': 'ColorSort/ColorSort', 'id': 'com.joostmuijsenberg.colorsort', 'live': False,
        'genre': {'en': 'Color Sorting Puzzle', 'nl': 'sorteerpuzzel', 'de': 'Sortier-Puzzle', 'es': 'juego de lógica', 'fr': 'jeu de logique', 'pt': 'jogo de lógica'},
        'related': ['blockpuzzle', 'sudoku', 'nonogram'],
    },
    {
        'slug': 'countryquiz', 'color': '#2f9be0', 'cat': 'quiz', 'dir': 'CountryQuiz/CountryQuiz', 'id': 'com.joostmuijsenberg.countryquiz', 'live': False,
        'genre': {'en': 'Flag and Capital Quiz', 'nl': 'vlaggen- en hoofdstedenquiz', 'de': 'Flaggen- und Hauptstadtquiz', 'es': 'quiz de banderas y capitales', 'fr': 'quiz des drapeaux et capitales', 'pt': 'quiz de bandeiras e capitais'},
        'related': ['crossword', 'wordsearch', '30-seconds'],
        'howto_from_intro': True,
    },
    {
        'slug': 'crossword', 'color': '#f26b5b', 'cat': 'word', 'dir': 'Crossword/Crossword', 'id': 'com.joostmuijsenberg.crossword', 'live': True,
        'genre': {'en': 'Crossword Puzzle Game', 'nl': 'kruiswoordpuzzel', 'de': 'Worträtsel', 'es': 'juego de palabras', 'fr': 'jeu de lettres', 'pt': 'jogo de palavras', 'ca': 'joc de paraules', 'it': 'gioco di parole', 'tr': 'kelime oyunu'},
        'related': ['wordsearch', 'wordconnect', 'sudoku'],
    },
    {
        'slug': 'cryptogram', 'color': '#8b6cf0', 'cat': 'word', 'dir': 'Cryptogram/Cryptogram', 'id': 'com.joostmuijsenberg.cryptogram', 'live': False,
        'genre': {'en': 'Code Word Puzzle', 'nl': 'cijfercodepuzzel', 'de': 'Zahlenrätsel', 'es': 'juego de código secreto', 'fr': 'jeu de code chiffré', 'pt': 'jogo de código secreto'},
        'related': ['crossword', 'wordsearch', 'wordconnect'],
    },
    {
        'slug': 'hartenjagen', 'color': '#e8395a', 'cat': 'card', 'dir': 'Hartenjagen/Hartenjagen', 'id': 'com.joostmuijsenberg.hearts', 'live': True,
        'name_en': 'Hearts',
        'genre': {'en': 'Hearts Card Game', 'nl': 'kaartspel', 'de': 'Kartenspiel', 'es': 'juego de cartas', 'fr': 'jeu de cartes', 'pt': 'jogo de cartas', 'it': 'gioco di carte', 'pl': 'gra karciana', 'ro': 'joc de cărți', 'ru': 'карточная игра', 'tr': 'kart oyunu'},
        'related': ['sudoku', 'MineSweeper', '30-seconds'],
    },
    {
        'slug': 'MineSweeper', 'color': '#6fb33a', 'cat': 'puzzle', 'dir': 'MineSweeper/MineSweeper', 'id': 'com.joostmuijsenberg.minesweeper', 'live': True,
        'genre': {'en': 'Minesweeper Game', 'nl': 'puzzelspel', 'de': 'Logikspiel', 'es': 'juego de lógica', 'fr': 'jeu de logique', 'pt': 'jogo de lógica', 'it': 'gioco di logica', 'tr': 'zekâ oyunu'},
        'related': ['sudoku', 'nonogram', 'blockpuzzle'],
    },
    {
        'slug': 'nonogram', 'color': '#f0a830', 'cat': 'puzzle', 'dir': 'Nonogram/Nonogram', 'id': 'com.joostmuijsenberg.nonogram', 'live': True,
        'genre': {'en': 'Picture Logic Puzzle', 'nl': 'logische puzzel', 'de': 'Logikrätsel', 'es': 'juego de lógica', 'fr': 'jeu de logique', 'pt': 'jogo de lógica', 'it': 'gioco di logica', 'ro': 'joc de logică', 'tr': 'mantık bulmacası'},
        'related': ['sudoku', 'MineSweeper', 'crossword'],
    },
    {
        'slug': 'numbermatch', 'color': '#2b7de0', 'cat': 'puzzle', 'dir': 'NumberMatch/NumberMatch', 'id': 'com.joostmuijsenberg.numbermatch', 'live': False,
        'genre': {'en': 'Number Puzzle', 'nl': 'getallenpuzzel', 'de': 'Zahlenrätsel', 'es': 'puzle numérico', 'fr': 'jeu de chiffres', 'pt': 'puzzle de números'},
        'related': ['sudoku', 'blockpuzzle', 'nonogram'],
    },
    {
        'slug': 'pipeconnect', 'color': '#3a6fd8', 'cat': 'puzzle', 'dir': 'PipeConnect/PipeConnect', 'id': 'com.joostmuijsenberg.pipeconnect', 'live': False,
        'genre': {'en': 'Pipe Puzzle Game', 'nl': 'leidingpuzzel', 'de': 'Rohr-Puzzle', 'es': 'puzle de tuberías', 'fr': 'jeu de tuyaux', 'pt': 'puzzle de canos'},
        'related': ['blockpuzzle', 'nonogram', 'MineSweeper'],
    },
    {
        'slug': 'sudoku', 'color': '#ef6c57', 'cat': 'puzzle', 'dir': 'Sudoku/Sudoku', 'id': 'com.joostmuijsenberg.sudoku', 'live': True,
        'genre': {'en': 'Sudoku Puzzle Game', 'nl': 'puzzelspel', 'de': 'Rätselspiel', 'es': 'juego de lógica', 'fr': 'jeu de logique', 'pt': 'jogo de lógica', 'it': 'gioco di logica', 'pl': 'gra logiczna', 'tr': 'bulmaca oyunu'},
        'related': ['nonogram', 'MineSweeper', 'blockpuzzle'],
    },
    {
        'slug': 'wordconnect', 'color': '#e8546d', 'cat': 'word', 'dir': 'WordConnect/WordConnect', 'id': 'com.joostmuijsenberg.wordconnect', 'live': True,
        'genre': {'en': 'Word Puzzle Game', 'nl': 'woordpuzzel', 'de': 'Worträtsel', 'es': 'juego de palabras', 'fr': 'jeu de mots', 'pt': 'jogo de palavras', 'ca': 'joc de paraules', 'it': 'gioco di parole', 'tr': 'kelime oyunu'},
        'related': ['wordsearch', 'crossword', '30-seconds'],
    },
    {
        'slug': 'wordsearch', 'color': '#d9734e', 'cat': 'word', 'dir': 'WordSearch/WordSearch', 'id': 'com.joostmuijsenberg.wordsearch', 'live': True,
        'genre': {'en': 'Word Search Puzzle', 'nl': 'woordpuzzel', 'de': 'Wörterrätsel', 'es': 'juego de palabras', 'fr': 'jeu de mots', 'pt': 'jogo de letras', 'ca': 'joc de paraules', 'it': 'gioco di parole', 'tr': 'kelime bulmacası'},
        'related': ['wordconnect', 'crossword', 'nonogram'],
    },
]

BY_SLUG = {a['slug']: a for a in APPS}

# Het uitgelichte spel bovenaan de homepage (moet live zijn en een video hebben).
FEATURED = '30-seconds'

# Drie schermafbeeldingen in de kop van de homepage: (slug, nummer).
HERO_SHOTS = [('sudoku', 2), ('wordsearch', 2), ('hartenjagen', 2)]

CATEGORIES = ['puzzle', 'word', 'card', 'party', 'quiz']
