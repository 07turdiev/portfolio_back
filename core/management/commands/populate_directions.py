"""5 ta yo'nalishni Direction jadvaliga qo'shadi (frontend i18n bilan bir xil).

Foydalanish:
    python manage.py populate_directions
"""
from django.core.management.base import BaseCommand

from core.models import Direction

DIRECTIONS = [
    {
        'key': 'theater_circus',
        'icon': 'theater',
        'order': 1,
        'uz_latn': "TEATR VA SIRK YO'NALISHI SOHA VAKILLARI",
        'uz_cyrl': 'ТЕАТР ВА СИРК ЙЎНАЛИШИ СОҲА ВАКИЛЛАРИ',
        'ru': 'ПРЕДСТАВИТЕЛИ СФЕРЫ ТЕАТРА И ЦИРКА',
    },
    {
        'key': 'education',
        'icon': 'education',
        'order': 2,
        'uz_latn': "TA'LIM YO'NALISHI SOHA VAKILLARI",
        'uz_cyrl': 'ТАЪЛИМ ЙЎНАЛИШИ СОҲА ВАКИЛЛАРИ',
        'ru': 'ПРЕДСТАВИТЕЛИ СФЕРЫ ОБРАЗОВАНИЯ',
    },
    {
        'key': 'heritage',
        'icon': 'heritage',
        'order': 3,
        'uz_latn': "NOMODDIY MADANIY MEROS YO'NALISHI BO'YICHA SOHA VAKILLARI",
        'uz_cyrl': 'НОМОДДИЙ МАДАНИЙ МЕРОС ЙЎНАЛИШИ БЎЙИЧА СОҲА ВАКИЛЛАРИ',
        'ru': 'ПРЕДСТАВИТЕЛИ СФЕРЫ НЕМАТЕРИАЛЬНОГО КУЛЬТУРНОГО НАСЛЕДИЯ',
    },
    {
        'key': 'cinema',
        'icon': 'cinema',
        'order': 4,
        'uz_latn': 'KINO SOHASI VAKILLARI',
        'uz_cyrl': 'КИНО СОҲАСИ ВАКИЛЛАРИ',
        'ru': 'ПРЕДСТАВИТЕЛИ СФЕРЫ КИНО',
    },
    {
        'key': 'concert',
        'icon': 'concert',
        'order': 5,
        'uz_latn': "KONSERT-TOMOSHA YO'NALISHI SOHA VAKILLARI",
        'uz_cyrl': 'КОНЦЕРТ-ТОМОША ЙЎНАЛИШИ СОҲА ВАКИЛЛАРИ',
        'ru': 'ПРЕДСТАВИТЕЛИ КОНЦЕРТНО-ЗРЕЛИЩНОЙ СФЕРЫ',
    },
]


class Command(BaseCommand):
    help = "5 ta yo'nalishni Direction jadvaliga qo'shadi"

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for d in DIRECTIONS:
            obj, was_created = Direction.objects.update_or_create(
                key=d['key'],
                defaults={
                    'icon': d['icon'],
                    'order': d['order'],
                    'name_uz_latn': d['uz_latn'],
                    'name_uz_cyrl': d['uz_cyrl'],
                    'name_ru': d['ru'],
                },
            )
            mark = '+' if was_created else '·'
            self.stdout.write(f'  {mark} {d["uz_latn"]}')
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"\nTayyor: {created} yangi qo'shildi, {updated} yangilandi."
            )
        )
