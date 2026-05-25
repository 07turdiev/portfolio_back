"""Mukofotlar taxonomy endpoint."""
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.cache import cache
from fastapi import APIRouter

from core.models import AwardAffiliation

router = APIRouter(prefix='/api', tags=['awards'])

CACHE_KEY = 'awards:taxonomy:v1'


def _build_taxonomy() -> list[dict]:
    """Cascading taxonomy: affiliation → type → name."""
    qs = (
        AwardAffiliation.objects
        .order_by('order', 'key')
        .prefetch_related('types__names')
    )
    affiliations = []
    for aff in qs:
        types = []
        for tp in aff.types.all():
            # `prefetch_related('types__names')` ishlatilganligi uchun
            # tp.names.all() yangi query yaratmaydi.
            sorted_types_names = sorted(
                tp.names.all(), key=lambda n: (n.order, n.key),
            )
            names = [
                {
                    'key': n.key,
                    'name': {
                        'uz_latn': n.name_uz_latn,
                        'uz_cyrl': n.name_uz_cyrl,
                        'ru': n.name_ru,
                    },
                }
                for n in sorted_types_names
            ]
            types.append({
                'key': tp.key,
                'order': tp.order,
                'name': {
                    'uz_latn': tp.name_uz_latn,
                    'uz_cyrl': tp.name_uz_cyrl,
                    'ru': tp.name_ru,
                },
                'names': names,
            })
        types.sort(key=lambda t: (t['order'], t['key']))
        affiliations.append({
            'key': aff.key,
            'name': {
                'uz_latn': aff.name_uz_latn,
                'uz_cyrl': aff.name_uz_cyrl,
                'ru': aff.name_ru,
            },
            'types': [{k: v for k, v in t.items() if k != 'order'} for t in types],
        })
    return affiliations


@router.get('/award-taxonomy')
async def award_taxonomy():
    """Cascading taxonomy: affiliation → type → name."""
    affiliations = await sync_to_async(cache.get_or_set, thread_sensitive=True)(
        CACHE_KEY, _build_taxonomy, settings.CACHE_TTL,
    )
    return {'affiliations': affiliations}
