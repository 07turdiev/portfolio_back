"""FastAPI routers uchun umumiy yordamchi funksiyalar."""
from __future__ import annotations

from typing import Any, Iterable

from django.db.models import Q


# ── i18n helpers ─────────────────────────────────────────────────────────

def i18n(obj: Any, field: str) -> dict[str, str]:
    """Bitta tarjima maydonini 3 tilli dict ga aylantirish.

    Misol: i18n(rep, 'last_name') →
        {'uz_latn': '...', 'uz_cyrl': '...', 'ru': '...'}
    """
    return {
        'uz_latn': getattr(obj, f'{field}_uz_latn', '') or '',
        'uz_cyrl': getattr(obj, f'{field}_uz_cyrl', '') or '',
        'ru': getattr(obj, f'{field}_ru', '') or '',
    }


def loc_name(obj: Any) -> dict[str, str]:
    """Hudud (Region/District/Mahalla) name ni 3 tilli dict ga aylantirish."""
    return {
        'uz_latn': obj.name_uz_latn or '',
        'uz_cyrl': obj.name_uz_cyrl or '',
        'ru': obj.name_ru or '',
    }


# ── Search Q helper ──────────────────────────────────────────────────────

def build_search_q(query: str, fields: Iterable[str]) -> Q:
    """Qidiruv so'rovini ko'p tilli OR-zanjirga aylantirish.

    Har bir so'z (token) AND bilan birlashtiriladi — har tokenning kamida bittasi
    biror maydonda topilishi kerak. Bu oddiy icontains'dan ko'ra aniqroq natija
    beradi: "ali valiyev" → faqat ham "ali", ham "valiyev" topilgan yozuvlar.
    """
    query = (query or '').strip()
    if not query:
        return Q()

    tokens = [t for t in query.split() if t]
    if not tokens:
        return Q()

    field_list = list(fields)
    combined = Q()
    for token in tokens:
        token_q = Q()
        for field in field_list:
            token_q |= Q(**{f'{field}__icontains': token})
        combined &= token_q
    return combined
