"""Uzbek Cyrillic → Latin (2019 rasmiy lotin) transliteratsiyasi.

Yagona manba — admin buyruqlari, PDF render va boshqalar shu yerdan oladi.
Frontenddagi `src/utils/translit.js` bilan bir xil jadval.
"""
from __future__ import annotations

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
