"""Sahifa pastidagi info kartochkalari uchun endpoint."""
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.cache import cache
from fastapi import APIRouter

from core.models import InfoCard

from ..utils import i18n

router = APIRouter(prefix='/api', tags=['info-cards'])

CACHE_KEY = 'info_cards:list:v1'


def _serialize(card: InfoCard) -> dict:
    return {
        'id': card.id,
        'title': i18n(card, 'title'),
        'body': i18n(card, 'body'),
        'icon': card.icon.url if card.icon else None,
        'order': card.order,
    }


def _build_cards() -> list[dict]:
    return [
        _serialize(c)
        for c in InfoCard.objects.filter(is_active=True).order_by('order', 'id')
    ]


@router.get('/info-cards')
async def list_info_cards():
    """Faol info kartochkalari ro'yxati (sahifa pastida ko'rsatish uchun)."""
    results = await sync_to_async(cache.get_or_set, thread_sensitive=True)(
        CACHE_KEY, _build_cards, settings.CACHE_TTL,
    )
    return {'results': results}
