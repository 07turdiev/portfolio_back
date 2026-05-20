"""Sahifa pastidagi info kartochkalari uchun endpoint."""
from asgiref.sync import sync_to_async
from fastapi import APIRouter

from core.models import InfoCard

router = APIRouter(prefix='/api', tags=['info-cards'])


def _i18n(obj, field: str) -> dict:
    """Tarjima qilinadigan maydonni 3 tilli dict ga aylantirish."""
    return {
        'uz_latn': getattr(obj, f'{field}_uz_latn', '') or '',
        'uz_cyrl': getattr(obj, f'{field}_uz_cyrl', '') or '',
        'ru': getattr(obj, f'{field}_ru', '') or '',
    }


def _serialize(card: InfoCard) -> dict:
    return {
        'id': card.id,
        'title': _i18n(card, 'title'),
        'body': _i18n(card, 'body'),
        'icon': card.icon.url if card.icon else None,
        'order': card.order,
    }


@router.get('/info-cards')
async def list_info_cards():
    """Faol info kartochkalari ro'yxati (sahifa pastida ko'rsatish uchun)."""

    @sync_to_async
    def _fetch():
        return [
            _serialize(c)
            for c in InfoCard.objects.filter(is_active=True).order_by('order', 'id')
        ]

    return {'results': await _fetch()}
