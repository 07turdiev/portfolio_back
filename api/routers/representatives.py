"""Vakillar endpoint."""
from asgiref.sync import sync_to_async
from fastapi import APIRouter, HTTPException, Query

from core.models import Representative

router = APIRouter(prefix='/api', tags=['representatives'])


def _i18n(obj, field: str) -> dict:
    """Bitta tarjima qilinadigan maydonni 3 tilli dict ga aylantirish."""
    return {
        'uz_latn': getattr(obj, f'{field}_uz_latn', '') or '',
        'uz_cyrl': getattr(obj, f'{field}_uz_cyrl', '') or '',
        'ru': getattr(obj, f'{field}_ru', '') or '',
    }


def _loc_name(obj) -> dict:
    return {
        'uz_latn': obj.name_uz_latn or '',
        'uz_cyrl': obj.name_uz_cyrl or '',
        'ru': obj.name_ru or '',
    }


def _residence(rep) -> dict | None:
    """Hozirgi yashash joyi — mahalla + tuman + viloyat."""
    if not rep.residence_mahalla_id:
        return None
    m = rep.residence_mahalla
    d = m.district
    r = d.region
    return {
        'mahalla': {'tin': m.tin, 'name': _loc_name(m)},
        'district': {'soato': d.soato, 'slug': d.slug, 'name': _loc_name(d)},
        'region': {'soato': r.soato, 'slug': r.slug, 'name': _loc_name(r)},
        'extra': rep.residence_place or '',
    }


def _serialize(rep: Representative) -> dict:
    awards = [
        {
            'year': ra.year,
            'key': ra.award.key,
            'name': _i18n(ra.award, 'name'),
            'type_key': ra.award.type.key,
            'affiliation_key': ra.award.type.affiliation.key,
        }
        for ra in rep.representative_awards.select_related(
            'award__type__affiliation'
        ).order_by('-year')
    ]
    family = [
        {
            'relation': m.relation,
            'name': _i18n(m, 'name'),
            'info': _i18n(m, 'info'),
            'note': _i18n(m, 'note'),
        }
        for m in rep.family_members.order_by('order', 'id')
    ]
    languages = [
        {'code': lang.code, 'name': lang.name}
        for lang in rep.languages.all().order_by('order', 'name')
    ]
    return {
        'id': rep.id,
        'directionKey': rep.direction.key,
        'lastName': _i18n(rep, 'last_name'),
        'firstName': _i18n(rep, 'first_name'),
        'middleName': _i18n(rep, 'middle_name'),
        'fullName': rep.full_name,
        'gender': rep.gender,
        'nationality': rep.nationality,
        'nationalityDisplay': rep.get_nationality_display() if rep.nationality else '',
        'birthDate': rep.birth_date.isoformat() if rep.birth_date else None,
        'birthPlace': _i18n(rep, 'birth_place'),
        'residence': _residence(rep),
        'photo': rep.photo.url if rep.photo else None,
        # Family
        'maritalStatus': _i18n(rep, 'marital_status'),
        'family': family,
        # Education
        'education': {
            'university': _i18n(rep, 'university'),
            'specialty': _i18n(rep, 'specialty'),
            'academicDegree': _i18n(rep, 'academic_degree'),
            'languages': languages,
            'training': _i18n(rep, 'training'),
        },
        # Work
        'work': {
            'position': _i18n(rep, 'position'),
            'careerLevel': _i18n(rep, 'career_level'),
            'totalExperience': _i18n(rep, 'total_experience'),
            'leadershipExperience': _i18n(rep, 'leadership_experience'),
            'leadershipPositions': _i18n(rep, 'leadership_positions'),
            'health': rep.health,
            'healthDisplay': rep.get_health_display() if rep.health else '',
            'lastMedicalTreatment': _i18n(rep, 'last_medical_treatment'),
            'medicalCheckup': _i18n(rep, 'medical_checkup'),
            'healthProblems': _i18n(rep, 'health_problems'),
        },
        # Activity
        'activity': {
            'description': _i18n(rep, 'description'),
            'stateEvents': _i18n(rep, 'state_events'),
        },
        'awards': awards,
    }


@router.get('/people')
async def list_people(
    direction: str | None = Query(None, description="Yo'nalish kaliti"),
    gender: str | None = Query(None, pattern='^(male|female)$'),
):
    """Vakillar ro'yxati (filtrlanadigan)."""

    @sync_to_async
    def _fetch():
        qs = Representative.objects.filter(is_active=True).select_related(
            'direction', 'residence_mahalla__district__region',
        )
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
            return _serialize(
                Representative.objects.select_related(
                    'direction', 'residence_mahalla__district__region',
                ).get(pk=pk, is_active=True)
            )
        except Representative.DoesNotExist:
            return None

    data = await _fetch()
    if data is None:
        raise HTTPException(status_code=404, detail='Vakil topilmadi')
    return data
