"""Mukofotlar taxonomy endpoint."""
from asgiref.sync import sync_to_async
from fastapi import APIRouter

from core.models import AwardAffiliation

router = APIRouter(prefix='/api', tags=['awards'])


@router.get('/award-taxonomy')
async def award_taxonomy():
    """Cascading taxonomy: affiliation → type → name."""

    @sync_to_async
    def _fetch():
        affiliations = []
        qs = (
            AwardAffiliation.objects
            .order_by('order', 'key')
            .prefetch_related('types__names')
        )
        for aff in qs:
            types = []
            for tp in aff.types.order_by('order', 'key'):
                names = [
                    {
                        'key': n.key,
                        'name': {
                            'uz_latn': n.name_uz_latn,
                            'uz_cyrl': n.name_uz_cyrl,
                            'ru': n.name_ru,
                        },
                    }
                    for n in tp.names.order_by('order', 'key')
                ]
                types.append({
                    'key': tp.key,
                    'name': {
                        'uz_latn': tp.name_uz_latn,
                        'uz_cyrl': tp.name_uz_cyrl,
                        'ru': tp.name_ru,
                    },
                    'names': names,
                })
            affiliations.append({
                'key': aff.key,
                'name': {
                    'uz_latn': aff.name_uz_latn,
                    'uz_cyrl': aff.name_uz_cyrl,
                    'ru': aff.name_ru,
                },
                'types': types,
            })
        return affiliations

    return {'affiliations': await _fetch()}
