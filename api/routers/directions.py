"""Yo'nalishlar endpoint."""
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q
from fastapi import APIRouter

from core.models import Direction, Representative

router = APIRouter(prefix='/api', tags=['directions'])

CACHE_KEY = 'directions:list:v1'


def _build_directions() -> list[dict]:
    """Bitta SQL — annotate orqali har direction uchun erkak/ayol sonlari."""
    qs = Direction.objects.annotate(
        men=Count(
            'representatives',
            filter=Q(
                representatives__is_active=True,
                representatives__gender=Representative.GENDER_MALE,
            ),
        ),
        women=Count(
            'representatives',
            filter=Q(
                representatives__is_active=True,
                representatives__gender=Representative.GENDER_FEMALE,
            ),
        ),
    ).order_by('order', 'key')

    return [
        {
            'key': d.key,
            'icon': d.icon,
            'order': d.order,
            'name': {
                'uz_latn': d.name_uz_latn,
                'uz_cyrl': d.name_uz_cyrl,
                'ru': d.name_ru,
            },
            'count': d.men + d.women,
            'men': d.men,
            'women': d.women,
        }
        for d in qs
    ]


@router.get('/directions')
async def list_directions():
    """Barcha yo'nalishlar va ulardagi faol vakillar soni."""
    items = await sync_to_async(cache.get_or_set, thread_sensitive=True)(
        CACHE_KEY, _build_directions, settings.CACHE_TTL,
    )
    return {'directions': items}
