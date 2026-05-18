"""Test uchun har yo'nalishga 5 ta vakil yaratadi.

Foydalanish:
    python manage.py populate_test_representatives
    python manage.py populate_test_representatives --clear  # avval o'chiradi
"""
import random
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    AwardName,
    Direction,
    FamilyMember,
    Language,
    Mahalla,
    Representative,
    RepresentativeAward,
)


# Direction key → (lavozim_uz_latn, lavozim_uz_cyrl, lavozim_ru, ta'lim)
DIRECTION_DATA = {
    'theater_circus': {
        'positions': [
            ('Bosh rejissyor', 'Бош режиссёр', 'Главный режиссёр'),
            ('Sirk artisti', 'Цирк артисти', 'Артист цирка'),
            ('Teatr aktyori', 'Театр актёри', 'Актёр театра'),
            ('Sahna ustasi', 'Саҳна устаси', 'Мастер сцены'),
            ('Dramaturgiya muallifi', 'Драматургия муаллифи', 'Автор драматургии'),
        ],
        'university': (
            "O'zbekiston davlat san'at va madaniyat instituti",
            'Ўзбекистон давлат санъат ва маданият институти',
            'Узбекский государственный институт искусств и культуры',
        ),
        'specialty': ('Rejissura', 'Режиссура', 'Режиссура'),
    },
    'education': {
        'positions': [
            ('Maktab direktori', 'Мактаб директори', 'Директор школы'),
            ('Universitet professori', 'Университет профессори', 'Профессор университета'),
            ("Ta'lim uslubchisi", 'Таълим услубчиси', 'Методист образования'),
            ("Maktabgacha ta'lim pedagogi", 'Мактабгача таълим педагоги', 'Педагог дошкольного образования'),
            ('Akademik litsey direktori', 'Академик лицей директори', 'Директор академического лицея'),
        ],
        'university': (
            "Nizomiy nomidagi TDPU",
            'Низомий номидаги ТДПУ',
            'ТГПУ имени Низами',
        ),
        'specialty': ("Pedagogika", 'Педагогика', 'Педагогика'),
    },
    'heritage': {
        'positions': [
            ('Folklor jamoasi rahbari', 'Фольклор жамоаси раҳбари', 'Руководитель фольклорного ансамбля'),
            ('Hunarmandchilik ustasi', 'Ҳунармандчилик устаси', 'Мастер ремесла'),
            ('Baxshi', 'Бахши', 'Бахши'),
            ("An'anaviy musiqachi", "Анъанавий мусиқачи", 'Традиционный музыкант'),
            ('Etnograf', 'Этнограф', 'Этнограф'),
        ],
        'university': (
            "O'zbekiston davlat konservatoriyasi",
            'Ўзбекистон давлат консерваторияси',
            'Государственная консерватория Узбекистана',
        ),
        'specialty': ("Xalq cholg'ulari", "Халқ чолғулари", 'Народные инструменты'),
    },
    'cinema': {
        'positions': [
            ('Kinorejissyor', 'Кинорежиссёр', 'Кинорежиссёр'),
            ('Operator', 'Оператор', 'Оператор'),
            ('Kinoaktyor', 'Киноактёр', 'Киноактёр'),
            ('Kinoprodyuser', 'Кинопродюсер', 'Кинопродюсер'),
            ('Kinodramaturg', 'Кинодраматург', 'Кинодраматург'),
        ],
        'university': (
            "O'zbekiston davlat san'at va madaniyat instituti",
            'Ўзбекистон давлат санъат ва маданият институти',
            'Узбекский государственный институт искусств и культуры',
        ),
        'specialty': ('Kinodramaturgiya', 'Кинодраматургия', 'Кинодраматургия'),
    },
    'concert': {
        'positions': [
            ('Estrada hofizi', 'Эстрада ҳофизи', 'Эстрадный исполнитель'),
            ('Dirijor', 'Дирижёр', 'Дирижёр'),
            ('Bastakor', 'Бастакор', 'Композитор'),
            ('Konsertmeyster', 'Концертмейстер', 'Концертмейстер'),
            ('Solist', 'Солист', 'Солист'),
        ],
        'university': (
            "O'zbekiston davlat konservatoriyasi",
            'Ўзбекистон давлат консерваторияси',
            'Государственная консерватория Узбекистана',
        ),
        'specialty': ('Vokal', 'Вокал', 'Вокал'),
    },
}

# Real Uzbek names
MALE_NAMES = [
    ('Karimov', 'Каримов', 'Каримов', 'Alisher', 'Алишер', 'Алишер', 'Bahromovich'),
    ('Yusupov', 'Юсупов', 'Юсупов', 'Sherzod', 'Шерзод', 'Шерзод', 'Rustamovich'),
    ('Rahmonov', 'Раҳмонов', 'Рахмонов', 'Bobur', 'Бобур', 'Бобур', 'Toxirovich'),
    ('Tursunov', 'Турсунов', 'Турсунов', 'Jasur', 'Жасур', 'Жасур', 'Anvarovich'),
    ('Mirzayev', 'Мирзаев', 'Мирзаев', "Ulug'bek", 'Улуғбек', 'Улугбек', 'Komilovich'),
]

FEMALE_NAMES = [
    ('Karimova', 'Каримова', 'Каримова', 'Dilnoza', 'Дилноза', 'Дилноза', 'Bahromovna'),
    ('Yusupova', 'Юсупова', 'Юсупова', 'Madina', 'Мадина', 'Мадина', 'Rustamovna'),
    ('Rahmonova', 'Раҳмонова', 'Рахмонова', 'Gulnora', 'Гулнора', 'Гулнора', 'Toxirovna'),
    ('Tursunova', 'Турсунова', 'Турсунова', 'Nilufar', 'Нилуфар', 'Нилуфар', 'Anvarovna'),
    ('Saidova', 'Саидова', 'Саидова', 'Shahnoza', 'Шаҳноза', 'Шахноза', 'Komilovna'),
]


class Command(BaseCommand):
    help = "Har yo'nalishga 5 ta test vakil yaratadi"

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                            help="Avval barcha vakillarni o'chiradi")
        parser.add_argument('--count', type=int, default=5,
                            help='Har yo\'nalishga necha vakil (default: 5)')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            n = Representative.objects.count()
            Representative.objects.all().delete()
            self.stdout.write(f"O'chirildi: {n} ta vakil")

        directions = list(Direction.objects.all().order_by('order'))
        if not directions:
            self.stderr.write("Avval populate_directions ishga tushiring")
            return

        mahallas = list(Mahalla.objects.select_related('district__region').all()[:500])
        if not mahallas:
            self.stderr.write("Avval populate_locations ishga tushiring")
            return

        award_names = list(AwardName.objects.all())
        languages = list(Language.objects.all()[:10])

        per = options['count']
        created = 0
        for direction in directions:
            data = DIRECTION_DATA.get(direction.key, DIRECTION_DATA['cinema'])
            for i in range(per):
                is_male = i % 2 == 0
                name_pool = MALE_NAMES if is_male else FEMALE_NAMES
                last_uz, last_cyr, last_ru, first_uz, first_cyr, first_ru, mid = name_pool[i % len(name_pool)]
                mid_uz = mid
                mid_cyr = mid.replace("'", '').replace('o', 'о').replace('a', 'а').replace('i', 'и').replace('v', 'в').replace('ch', 'ч').replace('y', 'й').replace('e', 'е')
                mid_ru = mid_cyr

                position_uz, position_cyr, position_ru = data['positions'][i % len(data['positions'])]
                univ_uz, univ_cyr, univ_ru = data['university']
                spec_uz, spec_cyr, spec_ru = data['specialty']
                mahalla = random.choice(mahallas)

                year = random.randint(1955, 1990)
                rep = Representative.objects.create(
                    direction=direction,
                    last_name=last_uz,
                    last_name_uz_latn=last_uz,
                    last_name_uz_cyrl=last_cyr,
                    last_name_ru=last_ru,
                    first_name=first_uz,
                    first_name_uz_latn=first_uz,
                    first_name_uz_cyrl=first_cyr,
                    first_name_ru=first_ru,
                    middle_name=mid_uz,
                    middle_name_uz_latn=mid_uz,
                    middle_name_uz_cyrl=mid_cyr,
                    middle_name_ru=mid_ru,
                    gender=Representative.GENDER_MALE if is_male else Representative.GENDER_FEMALE,
                    nationality='ozbek',
                    birth_date=date(year, random.randint(1, 12), random.randint(1, 28)),
                    birth_place=mahalla.district.region.name_uz_latn,
                    birth_place_uz_latn=mahalla.district.region.name_uz_latn,
                    birth_place_uz_cyrl=mahalla.district.region.name_uz_cyrl,
                    birth_place_ru=mahalla.district.region.name_ru,
                    residence_mahalla=mahalla,
                    residence_place='',
                    marital_status="Oilali, 2 nafar farzandi bor",
                    marital_status_uz_latn="Oilali, 2 nafar farzandi bor",
                    marital_status_uz_cyrl='Оилали, 2 нафар фарзанди бор',
                    marital_status_ru='Семейный, 2 детей',
                    university=univ_uz,
                    university_uz_latn=univ_uz,
                    university_uz_cyrl=univ_cyr,
                    university_ru=univ_ru,
                    specialty=spec_uz,
                    specialty_uz_latn=spec_uz,
                    specialty_uz_cyrl=spec_cyr,
                    specialty_ru=spec_ru,
                    academic_degree="Yo'q",
                    academic_degree_uz_latn="Yo'q",
                    academic_degree_uz_cyrl='Йўқ',
                    academic_degree_ru='Нет',
                    training="So'nggi 2 yilda malaka oshirgan",
                    training_uz_latn="So'nggi 2 yilda malaka oshirgan",
                    training_uz_cyrl="Сўнгги 2 йилда малака оширган",
                    training_ru='Повышал квалификацию за последние 2 года',
                    position=position_uz,
                    position_uz_latn=position_uz,
                    position_uz_cyrl=position_cyr,
                    position_ru=position_ru,
                    career_level='1-toifa',
                    career_level_uz_latn='1-toifa',
                    career_level_uz_cyrl='1-тоифа',
                    career_level_ru='1-я категория',
                    total_experience=f'{2026 - year - 22} yil',
                    total_experience_uz_latn=f'{2026 - year - 22} yil',
                    total_experience_uz_cyrl=f'{2026 - year - 22} йил',
                    total_experience_ru=f'{2026 - year - 22} лет',
                    leadership_experience='5 yil',
                    leadership_experience_uz_latn='5 yil',
                    leadership_experience_uz_cyrl='5 йил',
                    leadership_experience_ru='5 лет',
                    leadership_positions='',
                    leadership_positions_uz_latn='',
                    leadership_positions_uz_cyrl='',
                    leadership_positions_ru='',
                    health=Representative.HEALTH_GOOD,
                    last_medical_treatment="Yo'q",
                    last_medical_treatment_uz_latn="Yo'q",
                    last_medical_treatment_uz_cyrl='Йўқ',
                    last_medical_treatment_ru='Нет',
                    medical_checkup="O'tgan",
                    medical_checkup_uz_latn="O'tgan",
                    medical_checkup_uz_cyrl='Ўтган',
                    medical_checkup_ru='Прошёл',
                    health_problems="Yo'q",
                    health_problems_uz_latn="Yo'q",
                    health_problems_uz_cyrl='Йўқ',
                    health_problems_ru='Нет',
                    description=(
                        f"{last_uz} {first_uz} {mid_uz} — {direction.name_uz_latn.lower()} sohasidagi "
                        f"iste'dodli vakil. U {2026 - year - 22} yildan ortiq samarali mehnat qilib kelmoqda. "
                        f"Yaratgan ishlari soha mutaxassislari tomonidan yuqori baholangan."
                    ),
                    description_uz_latn=(
                        f"{last_uz} {first_uz} {mid_uz} — {direction.name_uz_latn.lower()} sohasidagi "
                        f"iste'dodli vakil. U {2026 - year - 22} yildan ortiq samarali mehnat qilib kelmoqda."
                    ),
                    description_uz_cyrl=(
                        f"{last_cyr} {first_cyr} {mid_cyr} — соҳада истеъдодли вакил. "
                        f"У {2026 - year - 22} йилдан ортиқ самарали меҳнат қилиб келмоқда."
                    ),
                    description_ru=(
                        f"{last_ru} {first_ru} {mid_ru} — талантливый представитель сферы. "
                        f"Работает в сфере более {2026 - year - 22} лет."
                    ),
                    state_events='Davlat tantanalarida muntazam ishtirok etadi',
                    state_events_uz_latn='Davlat tantanalarida muntazam ishtirok etadi',
                    state_events_uz_cyrl='Давлат тантаналарида мунтазам иштирок этади',
                    state_events_ru='Регулярно участвует в государственных мероприятиях',
                    is_active=True,
                )

                # Tillar (2 ta tasodifiy)
                if languages:
                    rep.languages.set(random.sample(languages, min(2, len(languages))))

                # Oila a'zolari (2 ta)
                FamilyMember.objects.create(
                    representative=rep,
                    relation=FamilyMember.RELATION_FATHER,
                    order=1,
                    name=f'{last_uz}ev Botir Karimovich',
                    name_uz_latn=f'{last_uz}ev Botir Karimovich',
                    name_uz_cyrl=f'{last_cyr}ев Ботир Каримович',
                    name_ru=f'{last_ru}ев Ботир Каримович',
                    info=f'{year - 28} yil, {mahalla.district.region.name_uz_latn}',
                    info_uz_latn=f'{year - 28} yil, {mahalla.district.region.name_uz_latn}',
                    info_uz_cyrl=f'{year - 28} йил, {mahalla.district.region.name_uz_cyrl}',
                    info_ru=f'{year - 28} г., {mahalla.district.region.name_ru}',
                    note='Nafaqada',
                    note_uz_latn='Nafaqada',
                    note_uz_cyrl='Нафақада',
                    note_ru='На пенсии',
                )
                FamilyMember.objects.create(
                    representative=rep,
                    relation=FamilyMember.RELATION_SPOUSE,
                    order=2,
                    name=f'{("Saidova","Yusupova")[i%2]} Nilufar Toxirovna',
                    name_uz_latn=f'{("Saidova","Yusupova")[i%2]} Nilufar Toxirovna',
                    name_uz_cyrl='Саидова Нилуфар Тоҳировна',
                    name_ru='Саидова Нилуфар Тохировна',
                    info='',
                    info_uz_latn='',
                    info_uz_cyrl='',
                    info_ru='',
                    note="O'qituvchi",
                    note_uz_latn="O'qituvchi",
                    note_uz_cyrl='Ўқитувчи',
                    note_ru='Учитель',
                )

                # Mukofotlar (2-3 ta tasodifiy)
                if award_names:
                    selected_awards = random.sample(award_names, min(3, len(award_names)))
                    for award in selected_awards:
                        RepresentativeAward.objects.create(
                            representative=rep,
                            award=award,
                            year=random.randint(2010, 2025),
                        )

                created += 1
                self.stdout.write(f'  +{rep.full_name} ({direction.key})')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTayyor: {created} ta test vakil yaratildi.'
            )
        )
