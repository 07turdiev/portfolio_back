"""Uzbek Cyrillic → Latin (2019 rasmiy lotin) transliteratsiyasi.

Yagona manba — admin buyruqlari, PDF render va boshqalar shu yerdan oladi.
Frontenddagi `src/utils/translit.js` bilan bir xil jadval.
"""
from __future__ import annotations

import re

# Diakritika uchun rasmiy curly apostrof ' (U+2018)
APO = '‘'

# Bigramlar (avval tekshiriladi)
DIGRAM = {
    'ё': 'yo', 'Ё': 'Yo',
    'ю': 'yu', 'Ю': 'Yu',
    'я': 'ya', 'Я': 'Ya',
    'ч': 'ch', 'Ч': 'Ch',
    'ш': 'sh', 'Ш': 'Sh',
    'ц': 'ts', 'Ц': 'Ts',
    'ў': f'o{APO}', 'Ў': f'O{APO}',
    'ғ': f'g{APO}', 'Ғ': f'G{APO}',
}

# Bir harfli o'tkazishlar
MONO = {
    'а': 'a', 'А': 'A',
    'б': 'b', 'Б': 'B',
    'в': 'v', 'В': 'V',
    'г': 'g', 'Г': 'G',
    'д': 'd', 'Д': 'D',
    'е': 'e', 'Е': 'E',
    'ж': 'j', 'Ж': 'J',
    'з': 'z', 'З': 'Z',
    'и': 'i', 'И': 'I',
    'й': 'y', 'Й': 'Y',
    'к': 'k', 'К': 'K',
    'л': 'l', 'Л': 'L',
    'м': 'm', 'М': 'M',
    'н': 'n', 'Н': 'N',
    'о': 'o', 'О': 'O',
    'п': 'p', 'П': 'P',
    'р': 'r', 'Р': 'R',
    'с': 's', 'С': 'S',
    'т': 't', 'Т': 'T',
    'у': 'u', 'У': 'U',
    'ф': 'f', 'Ф': 'F',
    'х': 'x', 'Х': 'X',
    'ъ': APO, 'Ъ': APO,
    'ь': '', 'Ь': '',
    'ы': 'i', 'Ы': 'I',
    'э': 'e', 'Э': 'E',
    'қ': 'q', 'Қ': 'Q',
    'ҳ': 'h', 'Ҳ': 'H',
}


def cyr_to_lat(text: str) -> str:
    """Uzbek Cyrillic'ni Lotin (2019) standartiga aylantirish."""
    if not text:
        return ''
    out = []
    for ch in text:
        if ch in DIGRAM:
            out.append(DIGRAM[ch])
        elif ch in MONO:
            out.append(MONO[ch])
        else:
            out.append(ch)
    return ''.join(out)


# ── Lotin → Kirill (teskari yo'nalish) ─────────────────────────────────────
# Frontenddagi `src/utils/translit.js` (latinToCyrl) bilan bir xil.

# Bitta harflar
_SINGLE = {
    'A': 'А', 'a': 'а',
    'B': 'Б', 'b': 'б',
    'V': 'В', 'v': 'в',
    'G': 'Г', 'g': 'г',
    'D': 'Д', 'd': 'д',
    'E': 'Е', 'e': 'е',
    'J': 'Ж', 'j': 'ж',
    'Z': 'З', 'z': 'з',
    'I': 'И', 'i': 'и',
    'Y': 'Й', 'y': 'й',
    'K': 'К', 'k': 'к',
    'L': 'Л', 'l': 'л',
    'M': 'М', 'm': 'м',
    'N': 'Н', 'n': 'н',
    'O': 'О', 'o': 'о',
    'P': 'П', 'p': 'п',
    'Q': 'Қ', 'q': 'қ',
    'R': 'Р', 'r': 'р',
    'S': 'С', 's': 'с',
    'T': 'Т', 't': 'т',
    'U': 'У', 'u': 'у',
    'F': 'Ф', 'f': 'ф',
    'X': 'Х', 'x': 'х',
    'H': 'Ҳ', 'h': 'ҳ',
    'W': 'В', 'w': 'в',
    # Undoshdan keyingi apostrof (O' va G' dan tashqari) — ayirish belgisi
    "'": 'ъ',
}

# Ko'p harfli kombinatsiyalar (barcha registr variantlari)
_MULTI = {
    "Yo'": 'Йў', "YO'": 'ЙЎ', "yo'": 'йў',
    'Sh': 'Ш', 'SH': 'Ш', 'sh': 'ш',
    'Ch': 'Ч', 'CH': 'Ч', 'ch': 'ч',
    "O'": 'Ў', "o'": 'ў',
    "G'": 'Ғ', "g'": 'ғ',
    'Yo': 'Ё', 'YO': 'Ё', 'yo': 'ё', 'yO': 'ё',
    'Yu': 'Ю', 'YU': 'Ю', 'yu': 'ю', 'yU': 'ю',
    'Ya': 'Я', 'YA': 'Я', 'ya': 'я', 'yA': 'я',
    'Ye': 'Е', 'YE': 'Е', 'ye': 'е', 'yE': 'е',
    'Ts': 'Ц', 'TS': 'Ц', 'ts': 'ц',
}

_MAX_MULTI = max(len(k) for k in _MULTI)
_APOS_RE = re.compile('[‘’ʹʻʼʽˊˋ`´′]')
_VOWELS = set('aeiouAEIOU')


def _normalize_apostrophes(text: str) -> str:
    return _APOS_RE.sub("'", text)


def lat_to_cyr(text: str) -> str:
    """Uzbek lotin matnini kirill yozuviga aylantirish."""
    if not text:
        return text
    text = _normalize_apostrophes(text)

    out = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        # Ko'p harfli kombinatsiyalarni tekshirish (uzundan qisqaga)
        for size in range(min(_MAX_MULTI, n - i), 1, -1):
            chunk = text[i:i + size]
            if chunk in _MULTI:
                out.append(_MULTI[chunk])
                i += size
                matched = True
                break
        if matched:
            continue

        ch = text[i]
        if ch in ('e', 'E'):
            # E/e: so'z boshida yoki unlidan keyin → Э/э, undoshdan keyin → Е/е
            prev = text[i - 1] if i > 0 else ''
            prev_is_letter = prev.isalpha() and prev.isascii()
            prev_is_vowel = prev in _VOWELS
            use_eh = (not prev_is_letter) or prev_is_vowel
            if ch == 'E':
                out.append('Э' if use_eh else 'Е')
            else:
                out.append('э' if use_eh else 'е')
        else:
            out.append(_SINGLE.get(ch, ch))
        i += 1

    return ''.join(out)
