"""Hududiy bo'linish endpoints — viloyat, tuman, mahalla."""
from asgiref.sync import sync_to_async
from fastapi import APIRouter, HTTPException, Query

from core.models import District, Mahalla, Region

router = APIRouter(prefix='/api', tags=['locations'])


def _name(obj) -> dict:
    return {
        'uz_latn': obj.name_uz_latn or '',
        'uz_cyrl': obj.name_uz_cyrl or '',
        'ru': obj.name_ru or '',
    }


@router.get('/regions')
async def list_regions():
    """Barcha viloyatlar."""

    @sync_to_async
    def _fetch():
        return [
            {
                'soato': r.soato,
                'slug': r.slug,
                'name': _name(r),
                'districtsCount': r.districts.count(),
            }
            for r in Region.objects.all().order_by('name_uz_latn')
        ]

    return {'regions': await _fetch()}


@router.get('/districts')
async def list_districts(
    region: str | None = Query(None, description='Viloyat SOATO kodi'),
):
    """Tumanlar (viloyat bo'yicha filtrlanadi)."""

    @sync_to_async
    def _fetch():
        qs = District.objects.select_related('region').all()
        if region:
            qs = qs.filter(region_id=region)
        return [
            {
                'soato': d.soato,
                'slug': d.slug,
                'regionSoato': d.region_id,
                'name': _name(d),
            }
            for d in qs.order_by('region', 'name_uz_latn')
        ]

    return {'districts': await _fetch()}


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
        qs = Mahalla.objects.select_related('district').all()
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
                'name': _name(m),
            }
            for m in qs.order_by('name_uz_latn')[:limit]
        ]

    return {'mahallas': await _fetch()}


@router.get('/mahallas/{tin}')
async def get_mahalla(tin: str):
    """Bitta mahalla — viloyat va tuman ma'lumotlari bilan."""

    @sync_to_async
    def _fetch():
        try:
            m = Mahalla.objects.select_related(
                'district', 'district__region'
            ).get(pk=tin)
        except Mahalla.DoesNotExist:
            return None
        return {
            'tin': m.tin,
            'name': _name(m),
            'district': {
                'soato': m.district.soato,
                'name': _name(m.district),
            },
            'region': {
                'soato': m.district.region.soato,
                'slug': m.district.region.slug,
                'name': _name(m.district.region),
            },
        }

    data = await _fetch()
    if data is None:
        raise HTTPException(status_code=404, detail='Mahalla topilmadi')
    return data
