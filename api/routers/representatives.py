"""Vakillar endpoint."""
from io import BytesIO

from asgiref.sync import sync_to_async
from django.db.models import Q
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from core.models import Representative

from ..utils import build_search_q, i18n, loc_name

router = APIRouter(prefix='/api', tags=['representatives'])


# Qidiruv bo'yicha skanerlanadigan barcha maydonlar (3 til x har bir field).
# Yangi maydon qo'shmoqchi bo'lsangiz, ro'yxatga bitta nom qo'shing — qolgani
# `build_search_q` ichida AND/OR mantig'i bilan avtomatik bog'lanadi.
SEARCH_FIELDS = (
    'last_name_uz_latn', 'last_name_uz_cyrl', 'last_name_ru',
    'first_name_uz_latn', 'first_name_uz_cyrl', 'first_name_ru',
    'middle_name_uz_latn', 'middle_name_uz_cyrl', 'middle_name_ru',
    'position_uz_latn', 'position_uz_cyrl', 'position_ru',
    'birth_place_uz_latn', 'birth_place_uz_cyrl', 'birth_place_ru',
    'residence_mahalla__name_uz_latn',
    'residence_mahalla__name_uz_cyrl',
    'residence_mahalla__name_ru',
    'residence_mahalla__district__name_uz_latn',
    'residence_mahalla__district__name_uz_cyrl',
    'residence_mahalla__district__name_ru',
    'residence_mahalla__district__region__name_uz_latn',
    'residence_mahalla__district__region__name_uz_cyrl',
    'residence_mahalla__district__region__name_ru',
)


def _residence(rep) -> dict | None:
    """Hozirgi yashash joyi — mahalla + tuman + viloyat."""
    if not rep.residence_mahalla_id:
        return None
    m = rep.residence_mahalla
    d = m.district
    r = d.region
    return {
        'mahalla': {'tin': m.tin, 'name': loc_name(m)},
        'district': {
            'soato': d.soato,
            'slug': d.slug,
            'name': loc_name(d),
            'lat': d.lat,
            'lng': d.lng,
        },
        'region': {'soato': r.soato, 'slug': r.slug, 'name': loc_name(r)},
        'extra': rep.residence_place or '',
    }


def _serialize(rep: Representative) -> dict:
    awards = [
        {
            'year': ra.year,
            'key': ra.award.key,
            'name': i18n(ra.award, 'name'),
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
            'name': i18n(m, 'name'),
            'info': i18n(m, 'info'),
            'note': i18n(m, 'note'),
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
        'lastName': i18n(rep, 'last_name'),
        'firstName': i18n(rep, 'first_name'),
        'middleName': i18n(rep, 'middle_name'),
        'fullName': rep.full_name,
        'gender': rep.gender,
        'nationality': rep.nationality,
        'nationalityDisplay': rep.get_nationality_display() if rep.nationality else '',
        'birthDate': rep.birth_date.isoformat() if rep.birth_date else None,
        'birthPlace': i18n(rep, 'birth_place'),
        'residence': _residence(rep),
        'photo': rep.photo.url if rep.photo else None,
        # Family
        'maritalStatus': i18n(rep, 'marital_status'),
        'family': family,
        # Education
        'education': {
            'university': i18n(rep, 'university'),
            'specialty': i18n(rep, 'specialty'),
            'academicDegree': i18n(rep, 'academic_degree'),
            'languages': languages,
            'training': i18n(rep, 'training'),
        },
        # Work
        'work': {
            'position': i18n(rep, 'position'),
            'careerLevel': i18n(rep, 'career_level'),
            'totalExperience': i18n(rep, 'total_experience'),
            'leadershipExperience': i18n(rep, 'leadership_experience'),
            'leadershipPositions': i18n(rep, 'leadership_positions'),
            'health': rep.health,
            'healthDisplay': rep.get_health_display() if rep.health else '',
            'lastMedicalTreatment': i18n(rep, 'last_medical_treatment'),
            'medicalCheckup': i18n(rep, 'medical_checkup'),
            'healthProblems': i18n(rep, 'health_problems'),
        },
        # Activity
        'activity': {
            'description': i18n(rep, 'description'),
            'stateEvents': i18n(rep, 'state_events'),
        },
        'awards': awards,
    }


@router.get('/people')
async def list_people(
    direction: str | None = Query(None, description="Yo'nalish kaliti"),
    gender: str | None = Query(None, pattern='^(male|female)$'),
    region: str | None = Query(None, description="Viloyat slug yoki SOATO"),
    district: str | None = Query(None, description="Tuman slug yoki SOATO"),
    q: str | None = Query(None, description="Qidiruv (F.I.O., lavozim, tuman, viloyat) — 3 til"),
    skip: int = Query(0, ge=0, description='Boshlang\'ich offset (pagination)'),
    limit: int = Query(200, ge=1, le=1000, description='Maksimum natijalar soni'),
):
    """Vakillar ro'yxati. Filtrlash: yo'nalish, jins, viloyat, tuman, qidiruv (q)."""

    @sync_to_async
    def _fetch():
        qs = Representative.objects.filter(is_active=True).select_related(
            'direction', 'residence_mahalla__district__region',
        )
        if direction:
            qs = qs.filter(direction__key=direction)
        if gender:
            qs = qs.filter(gender=gender)
        if region:
            qs = qs.filter(
                Q(residence_mahalla__district__region__slug=region)
                | Q(residence_mahalla__district__region__soato=region)
            )
        if district:
            qs = qs.filter(
                Q(residence_mahalla__district__slug=district)
                | Q(residence_mahalla__district__soato=district)
            )
        if q:
            # Token-asosli ko'p tilli qidiruv (build_search_q):
            # har so'z barcha maydonlardan kamida bittasida bo'lishi kerak.
            qs = qs.filter(build_search_q(q, SEARCH_FIELDS)).distinct()

        total = qs.count()
        page = list(qs[skip:skip + limit])
        return total, [_serialize(r) for r in page]

    total, results = await _fetch()
    return {
        'results': results,
        'total': total,
        'skip': skip,
        'limit': limit,
    }


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


@router.get('/people/{pk}/pdf')
async def get_person_pdf(
    pk: int,
    lang: str = Query('uz_latn', pattern='^(uz_latn|uz_cyrl|ru)$'),
):
    """Vakil portfoliosini PDF formatida yuklab olish.

    `lang`: uz_latn | uz_cyrl | ru
    """

    @sync_to_async
    def _generate():
        try:
            rep = Representative.objects.select_related(
                'direction', 'residence_mahalla__district__region',
            ).get(pk=pk, is_active=True)
        except Representative.DoesNotExist:
            return None

        # PDF generator import shu yerda — agar WeasyPrint o'rnatilmagan bo'lsa,
        # boshqa endpoint'lar ishlashda davom etadi.
        from api.pdf_render import render_portfolio_pdf

        pdf_bytes = render_portfolio_pdf(rep, lang)
        # Fayl nomi uchun xavfsiz ism
        safe_name = ''.join(
            c if c.isalnum() or c in ' _-' else '_'
            for c in rep.full_name
        ).strip() or 'portfolio'
        return pdf_bytes, safe_name

    result = await _generate()
    if result is None:
        raise HTTPException(status_code=404, detail='Vakil topilmadi')
    pdf_bytes, safe_name = result
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{safe_name}.pdf"',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
        },
    )
