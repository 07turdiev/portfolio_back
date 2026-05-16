"""Vakillar endpoint."""
from asgiref.sync import sync_to_async
from fastapi import APIRouter, HTTPException, Query

from core.models import Representative

router = APIRouter(prefix='/api', tags=['representatives'])


def _serialize(rep: Representative) -> dict:
    awards = [
        {
            'year': ra.year,
            'key': ra.award.key,
            'name': {
                'uz_latn': ra.award.name_uz_latn,
                'uz_cyrl': ra.award.name_uz_cyrl,
                'ru': ra.award.name_ru,
            },
            'type_key': ra.award.type.key,
            'affiliation_key': ra.award.type.affiliation.key,
        }
        for ra in rep.representative_awards.select_related(
            'award__type__affiliation'
        ).order_by('-year')
    ]
    return {
        'id': rep.id,
        'directionKey': rep.direction.key,
        'lastName': rep.last_name,
        'firstName': rep.first_name,
        'middleName': rep.middle_name,
        'fullName': rep.full_name,
        'gender': rep.gender,
        'nationality': rep.nationality,
        'birthDate': rep.birth_date.isoformat() if rep.birth_date else None,
        'birthPlace': rep.birth_place,
        'residencePlace': rep.residence_place,
        'position': rep.position,
        'photo': rep.photo.url if rep.photo else None,
        'awards': awards,
    }


@router.get('/people')
async def list_people(
    direction: str | None = Query(None, description="Yo'nalish kaliti"),
    gender: str | None = Query(None, regex='^(male|female)$'),
):
    """Vakillar ro'yxati (filtrlanadigan)."""

    @sync_to_async
    def _fetch():
        qs = Representative.objects.filter(is_active=True).select_related('direction')
        if direction:
            qs = qs.filter(direction__key=direction)
        if gender:
            qs = qs.filter(gender=gender)
        return [_serialize(r) for r in qs]

    return {'results': await _fetch()}


@router.get('/people/{pk}')
async def get_person(pk: int):
    @sync_to_async
    def _fetch():
        try:
            return _serialize(Representative.objects.get(pk=pk, is_active=True))
        except Representative.DoesNotExist:
            return None

    data = await _fetch()
    if data is None:
        raise HTTPException(status_code=404, detail='Vakil topilmadi')
    return data
