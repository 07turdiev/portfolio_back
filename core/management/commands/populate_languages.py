"""Language jadvalini boshlang'ich tillar bilan to'ldiradi.

Foydalanish:
    python manage.py populate_languages
"""
from django.core.management.base import BaseCommand

from core.models import Language

# (code, name, order) — eng kerakli tillar yuqorida
LANGUAGES = [
    ('ozbek', "O'zbek tili", 1),
    ('rus', 'Rus tili', 2),
    ('ingliz', 'Ingliz tili', 3),
    ('tojik', 'Tojik tili', 4),
    ('qozoq', 'Qozoq tili', 5),
    ('qirgiz', "Qirg'iz tili", 6),
    ('turkman', 'Turkman tili', 7),
    ('qoraqalpoq', "Qoraqalpoq tili", 8),
    ('tatar', 'Tatar tili', 9),
    ('uygur', "Uyg'ur tili", 10),
    ('koreys', 'Koreys tili', 11),
    ('turk', 'Turk tili', 12),
    ('arab', 'Arab tili', 13),
    ('fors', 'Fors tili', 14),
    ('urdu', 'Urdu tili', 15),
    ('hind', 'Hind tili', 16),
    ('xitoy', 'Xitoy tili', 17),
    ('yapon', 'Yapon tili', 18),
    ('nemis', 'Nemis tili', 19),
    ('fransuz', 'Fransuz tili', 20),
    ('italyan', 'Italyan tili', 21),
    ('ispan', 'Ispan tili', 22),
    ('portugal', 'Portugal tili', 23),
    ('polyak', 'Polyak tili', 24),
    ('ukrain', 'Ukrain tili', 25),
    ('belorus', 'Belorus tili', 26),
    ('latish', 'Latish tili', 27),
    ('eston', 'Eston tili', 28),
    ('litva', 'Litva tili', 29),
    ('chex', 'Chex tili', 30),
    ('slovak', 'Slovak tili', 31),
    ('vengr', 'Vengr tili', 32),
    ('rumin', 'Rumin tili', 33),
    ('bolgar', 'Bolgar tili', 34),
    ('grek', 'Grek tili', 35),
    ('niderland', 'Niderland tili', 36),
    ('shved', 'Shved tili', 37),
    ('norveg', 'Norveg tili', 38),
    ('dat', 'Dat tili', 39),
    ('finlyandiya', 'Finlyandiya tili', 40),
    ('ibroniy', 'Ibroniy tili', 41),
    ('vyetnam', 'Vyetnam tili', 42),
    ('indonez', 'Indoneziya tili', 43),
    ('malay', 'Malay tili', 44),
    ('tay', 'Tay tili', 45),
    ('birma', 'Birma tili', 46),
    ('lotin', 'Lotin tili', 47),
]


class Command(BaseCommand):
    help = "Language jadvaliga boshlang'ich tillarni qo'shadi"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        for code, name, order in LANGUAGES:
            obj, created = Language.objects.update_or_create(
                code=code,
                defaults={'name': name, 'order': order},
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  + {name}'))
            else:
                updated_count += 1
                self.stdout.write(f'  · {name}')
        self.stdout.write(
            self.style.SUCCESS(
                f"\nTayyor: {created_count} ta yangi qo'shildi, "
                f"{updated_count} ta yangilandi."
            )
        )
