"""Yo'nalishlar endpoint."""
from asgiref.sync import sync_to_async
from fastapi import APIRouter

from core.models import Direction

router = APIRouter(prefix='/api', tags=['directions'])


@router.get('/directions')
async def list_directions():
    """Barcha yo'nalishlar va ulardagi faol vakillar soni."""

    @sync_to_async
    def _fetch():
        items = []
        for d in Direction.objects.order_by('order', 'key'):
            active_qs = d.representatives.filter(is_active=True)
            men = active_qs.filter(gender=Direction.representatives.field.model.GENDER_MALE).count() \
                if hasattr(Direction.representatives.field.model, 'GENDER_MALE') else \
                active_qs.filter(gender='male').count()
            women = active_qs.filter(gender='female').count()
            items.append({
                'key': d.key,
                'icon': d.icon,
                'order': d.order,
                'name': {
                    'uz_latn': d.name_uz_latn,
                    'uz_cyrl': d.name_uz_cyrl,
                    'ru': d.name_ru,
                },
                'count': men + women,
                'men': men,
                'women': women,
            })
        return items

    return {'directions': await _fetch()}
