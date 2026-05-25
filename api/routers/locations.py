"""Hududiy bo'linish endpoints — viloyat, tuman, mahalla."""
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count
from fastapi import APIRouter, HTTPException, Query

from core.models import District, Mahalla, Region

from ..utils import loc_name

router = APIRouter(prefix='/api', tags=['locations'])

REGIONS_KEY = 'locations:regions:v1'
DISTRICTS_KEY_PREFIX = 'locations:districts:v1'  # + ':<region>'
MAHALLA_KEY_PREFIX = 'locations:mahalla:v1'      # + ':<tin>'


# ── /regions ──────────────────────────────────────────────────────────────

def _build_regions() -> list[dict]:
    qs = Region.objects.annotate(
        _districts=Count('districts', distinct=True),
    ).order_by('name_uz_latn')
    return [
        {
            'soato': r.soato,
            'slug': r.slug,
            'name': loc_name(r),
            'districtsCount': r._districts,
        }
        for r in qs
    ]


@router.get('/regions')
async def list_regions():
    """Barcha viloyatlar."""
    regions = await sync_to_async(cache.get_or_set, thread_sensitive=True)(
        REGIONS_KEY, _build_regions, settings.CACHE_TTL,
    )
    return {'regions': regions}


# ── /districts ────────────────────────────────────────────────────────────

def _build_districts(region: str | None) -> list[dict]:
    qs = District.objects.select_related('region')
    if region:
        qs = qs.filter(region_id=region)
    qs = qs.order_by('region', 'name_uz_latn')
    return [
        {
            'soato': d.soato,
            'slug': d.slug,
            'regionSoato': d.region_id,
            'name': loc_name(d),
        }
        for d in qs
    ]


@router.get('/districts')
async def list_districts(
    region: str | None = Query(None, description='Viloyat SOATO kodi'),
):
    """Tumanlar (viloyat bo'yicha filtrlanadi)."""
    cache_key = f'{DISTRICTS_KEY_PREFIX}:{region or "all"}'
    districts = await sync_to_async(cache.get_or_set, thread_sensitive=True)(
        cache_key, lambda: _build_districts(region), settings.CACHE_TTL,
    )
    return {'districts': districts}


# ── /mahallas ─────────────────────────────────────────────────────────────
# Bu endpoint search va limit qabul qiladi — har kombinatsiyani cache qilish
# foyda bermaydi (juda ko'p variant). Faqat select_related + cheklov bilan
# qoldiramiz; cache shu yerda asossiz.

@router.get('/mahallas')
async def list_mahallas(
    district: str | None = Query(None, description='Tuman SOATO kodi'),
    region: str | None = Query(None, description='Viloyat SOATO kodi'),
    search: str | None = Query(None, description='Nom bo\'yicha qidirish'),
    limit: int = Query(200, le=2000, description='Maksimum natijalar soni'),
):
    """Mahallalar (tuman/viloyat/qidiruv bo'yicha filtrlanadi)."""

    @sync_to_async
    def _fetch():
        qs = Mahalla.objects.select_related('district')
        if district:
            qs = qs.filter(district_id=district)
        elif region:
            qs = qs.filter(district__region_id=region)
        if search:
            qs = qs.filter(name_uz_latn__icontains=search)
        return [
            {
                'tin': m.tin,
                'districtSoato': m.district_id,
                'name': loc_name(m),
            }
            for m in qs.order_by('name_uz_latn')[:limit]
        ]

    return {'mahallas': await _fetch()}


# ── /mahallas/{tin} ───────────────────────────────────────────────────────

def _build_mahalla(tin: str) -> dict | None:
    try:
        m = Mahalla.objects.select_related(
            'district', 'district__region',
        ).get(pk=tin)
    except Mahalla.DoesNotExist:
        return None
    return {
        'tin': m.tin,
        'name': loc_name(m),
        'district': {
            'soato': m.district.soato,
            'name': loc_name(m.district),
        },
        'region': {
            'soato': m.district.region.soato,
            'slug': m.district.region.slug,
            'name': loc_name(m.district.region),
        },
    }


@router.get('/mahallas/{tin}')
async def get_mahalla(tin: str):
    """Bitta mahalla — viloyat va tuman ma'lumotlari bilan."""
    cache_key = f'{MAHALLA_KEY_PREFIX}:{tin}'
    data = await sync_to_async(cache.get_or_set, thread_sensitive=True)(
        cache_key, lambda: _build_mahalla(tin), settings.CACHE_TTL,
    )
    if data is None:
        raise HTTPException(status_code=404, detail='Mahalla topilmadi')
    return data
