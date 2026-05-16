"""Mukofotlar iyerarxiyasini to'ldiradi:
    AwardAffiliation (5)
        └── AwardType (Davlat mukofotlari ichida 5 ta)
                └── AwardName (jami 60 ta nom)

Foydalanish:
    python manage.py populate_awards
"""
from django.core.management.base import BaseCommand

from core.models import AwardAffiliation, AwardName, AwardType


# ─── Mansubliklar ─────────────────────────────────────────────────────────
AFFILIATIONS = [
    {
        'key': 'state', 'order': 1,
        'uz_latn': 'Davlat mukofotlari',
        'uz_cyrl': 'Давлат мукофотлари',
        'ru': 'Государственные награды',
    },
    {
        'key': 'karakalpakstan', 'order': 2,
        'uz_latn': "Qoraqalpog'iston Respublikasi mukofotlari",
        'uz_cyrl': 'Қорақалпоғистон Республикаси мукофотлари',
        'ru': 'Награды Республики Каракалпакстан',
    },
    {
        'key': 'ministry', 'order': 3,
        'uz_latn': "Vazirlik va idoralarning mukofotlari",
        'uz_cyrl': 'Вазирлик ва идораларнинг мукофотлари',
        'ru': 'Награды министерств и ведомств',
    },
    {
        'key': 'foreign', 'order': 4,
        'uz_latn': 'Turli davlatlar mukofotlari',
        'uz_cyrl': 'Турли давлатлар мукофотлари',
        'ru': 'Награды различных государств',
    },
    {
        'key': 'international', 'order': 5,
        'uz_latn': 'Xalqaro tashkilotlar mukofotlari',
        'uz_cyrl': 'Халқаро ташкилотлар мукофотлари',
        'ru': 'Награды международных организаций',
    },
]


# ─── Davlat mukofotlari turlari ───────────────────────────────────────────
STATE_TYPES = [
    {
        'key': 'hero', 'order': 1,
        'uz_latn': "«O'zbekiston Qahramoni» unvoni",
        'uz_cyrl': '«Ўзбекистон Қаҳрамони» унвони',
        'ru': 'Звание «Герой Узбекистана»',
    },
    {
        'key': 'honorary_titles', 'order': 2,
        'uz_latn': "O'zbekiston Respublikasining faxriy unvonlari",
        'uz_cyrl': 'Ўзбекистон Республикасининг фахрий унвонлари',
        'ru': 'Почётные звания Республики Узбекистан',
    },
    {
        'key': 'orders', 'order': 3,
        'uz_latn': "O'zbekiston Respublikasining ordenlari",
        'uz_cyrl': 'Ўзбекистон Республикасининг орденлари',
        'ru': 'Ордена Республики Узбекистан',
    },
    {
        'key': 'medals', 'order': 4,
        'uz_latn': "O'zbekiston Respublikasining medallari",
        'uz_cyrl': 'Ўзбекистон Республикасининг медаллари',
        'ru': 'Медали Республики Узбекистан',
    },
    {
        'key': 'honorary_diploma', 'order': 5,
        'uz_latn': "O'zbekiston Respublikasining Faxriy yorlig'i",
        'uz_cyrl': 'Ўзбекистон Республикасининг Фахрий ёрлиғи',
        'ru': 'Почётная грамота Республики Узбекистан',
    },
]


# ─── Mukofot nomlari (her tur uchun) ──────────────────────────────────────

HERO_NAMES = [
    ('hero_uzbekistan',
     "«O'zbekiston Qahramoni» unvoni",
     '«Ўзбекистон Қаҳрамони» унвони',
     'Звание «Герой Узбекистана»'),
]

HONORARY_TITLES_NAMES = [
    ('art_arbob',
     "«O'zbekiston Respublikasi san'at arbobi»",
     '«Ўзбекистон Республикаси санъат арбоби»',
     '«Деятель искусств Республики Узбекистан»'),
    ('science_arbob',
     "«O'zbekiston Respublikasi fan arbobi»",
     '«Ўзбекистон Республикаси фан арбоби»',
     '«Деятель науки Республики Узбекистан»'),
    ('iftihor',
     "«O'zbekiston iftixori»",
     '«Ўзбекистон ифтихори»',
     '«Гордость Узбекистана»'),
    ('xalq_artisti',
     "«O'zbekiston Respublikasi xalq artisti»",
     '«Ўзбекистон Республикаси халқ артисти»',
     '«Народный артист Республики Узбекистан»'),
    ('xalq_baxshi',
     "«O'zbekiston Respublikasi xalq baxshisi»",
     '«Ўзбекистон Республикаси халқ бахшиси»',
     '«Народный бахши Республики Узбекистан»'),
    ('xalq_yozuvchi',
     "«O'zbekiston Respublikasi xalq yozuvchisi»",
     '«Ўзбекистон Республикаси халқ ёзувчиси»',
     '«Народный писатель Республики Узбекистан»'),
    ('xalq_rassom',
     "«O'zbekiston Respublikasi xalq rassomi»",
     '«Ўзбекистон Республикаси халқ рассоми»',
     '«Народный художник Республики Узбекистан»'),
    ('xalq_usta',
     "«O'zbekiston Respublikasi xalq ustasi»",
     '«Ўзбекистон Республикаси халқ устаси»',
     '«Народный мастер Республики Узбекистан»'),
    ('xalq_shoir',
     "«O'zbekiston Respublikasi xalq shoiri»",
     '«Ўзбекистон Республикаси халқ шоири»',
     '«Народный поэт Республики Узбекистан»'),
    ('xalq_oqituvchi',
     "«O'zbekiston Respublikasi xalq o'qituvchisi»",
     '«Ўзбекистон Республикаси халқ ўқитувчиси»',
     '«Народный учитель Республики Узбекистан»'),
    ('xalq_hofiz',
     "«O'zbekiston Respublikasi xalq hofizi»",
     '«Ўзбекистон Республикаси халқ ҳофизи»',
     '«Народный хофиз Республики Узбекистан»'),
    ('kommunal_xodim',
     "«O'zbekiston Respublikasida kommunal, maishiy va savdo sohasida xizmat ko'rsatgan xodim»",
     '«Ўзбекистон Республикасида коммунал, маиший ва савдо соҳасида хизмат кўрсатган ходим»',
     '«Заслуженный работник коммунально-бытового обслуживания и торговли Республики Узбекистан»'),
    ('aloqa_xodim',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan aloqa xodimi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган алоқа ходими»',
     '«Заслуженный работник связи Республики Узбекистан»'),
    ('xizmat_artisti',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan artist»",
     '«Ўзбекистон Республикасида хизмат кўрсатган артист»',
     '«Заслуженный артист Республики Узбекистан»'),
    ('geolog',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan geolog»",
     '«Ўзбекистон Республикасида хизмат кўрсатган геолог»',
     '«Заслуженный геолог Республики Узбекистан»'),
    ('yoshlar_murabbiy',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan yoshlar murabbiysi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган ёшлар мураббийси»',
     '«Заслуженный наставник молодёжи Республики Узбекистан»'),
    ('jurnalist',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan jurnalist»",
     '«Ўзбекистон Республикасида хизмат кўрсатган журналист»',
     '«Заслуженный журналист Республики Узбекистан»'),
    ('irrigator',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan irrigator»",
     '«Ўзбекистон Республикасида хизмат кўрсатган ирригатор»',
     '«Заслуженный ирригатор Республики Узбекистан»'),
    ('ixtirochi',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan ixtirochi va ratsionalizator»",
     '«Ўзбекистон Республикасида хизмат кўрсатган ихтирочи ва рационализатор»',
     '«Заслуженный изобретатель и рационализатор Республики Узбекистан»'),
    ('iqtisodchi',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan iqtisodchi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган иқтисодчи»',
     '«Заслуженный экономист Республики Узбекистан»'),
    ('madaniyat_xodim',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan madaniyat xodimi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган маданият ходими»',
     '«Заслуженный работник культуры Республики Узбекистан»'),
    ('memor',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan me'mor»",
     '«Ўзбекистон Республикасида хизмат кўрсатган меъмор»',
     '«Заслуженный архитектор Республики Узбекистан»'),
    ('paxtakor',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan paxtakor»",
     '«Ўзбекистон Республикасида хизмат кўрсатган пахтакор»',
     '«Заслуженный хлопкороб Республики Узбекистан»'),
    ('pillachi',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan pillachi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган пиллачи»',
     '«Заслуженный шелковод Республики Узбекистан»'),
    ('sanoat_xodim',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan sanoat xodimi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган саноат ходими»',
     '«Заслуженный работник промышленности Республики Узбекистан»'),
    ('soglik_xodim',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan sog'liqni saqlash xodimi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган соғлиқни сақлаш ходими»',
     '«Заслуженный работник здравоохранения Республики Узбекистан»'),
    ('sport_ustoz',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan sport ustozi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган спорт устози»',
     '«Заслуженный тренер Республики Узбекистан»'),
    ('sportchi',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan sportchi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган спортчи»',
     '«Заслуженный спортсмен Республики Узбекистан»'),
    ('tadbirkor',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan tadbirkor»",
     '«Ўзбекистон Республикасида хизмат кўрсатган тадбиркор»',
     '«Заслуженный предприниматель Республики Узбекистан»'),
    ('transport_xodim',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan transport xodimi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган транспорт ходими»',
     '«Заслуженный работник транспорта Республики Узбекистан»'),
    ('aviatsiya_xodim',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan fuqaro aviatsiyasi xodimi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган фуқаро авиацияси ходими»',
     '«Заслуженный работник гражданской авиации Республики Узбекистан»'),
    ('talim_xodim',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan xalq ta'limi xodimi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган халқ таълими ходими»',
     '«Заслуженный работник народного образования Республики Узбекистан»'),
    ('chorvador',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan chorvador»",
     '«Ўзбекистон Республикасида хизмат кўрсатган чорвадор»',
     '«Заслуженный животновод Республики Узбекистан»'),
    ('ekolog',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan ekolog»",
     '«Ўзбекистон Республикасида хизмат кўрсатган эколог»',
     '«Заслуженный эколог Республики Узбекистан»'),
    ('yurist',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan yurist»",
     '«Ўзбекистон Республикасида хизмат кўрсатган юрист»',
     '«Заслуженный юрист Республики Узбекистан»'),
    ('qishloq_xodim',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan qishloq xo'jalik xodimi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган қишлоқ хўжалик ходими»',
     '«Заслуженный работник сельского хозяйства Республики Узбекистан»'),
    ('quruvchi',
     "«O'zbekiston Respublikasida xizmat ko'rsatgan quruvchi»",
     '«Ўзбекистон Республикасида хизмат кўрсатган қурувчи»',
     '«Заслуженный строитель Республики Узбекистан»'),
]

ORDERS_NAMES = [
    ('mustaqillik', '«Mustaqillik» ordeni', '«Мустақиллик» ордени', 'Орден «Мустакиллик»'),
    ('amir_temur', '«Amir Temur» ordeni', '«Амир Темур» ордени', 'Орден «Амир Темур»'),
    ('jaloliddin_manguberdi',
     '«Jaloliddin Manguberdi» ordeni',
     '«Жалолиддин Мангуберди» ордени',
     'Орден «Джалалиддин Мангуберды»'),
    ('buyuk_xizmat',
     '«Buyuk xizmatlari uchun» ordeni',
     '«Буюк хизматлари учун» ордени',
     'Орден «За большие заслуги»'),
    ('el_yurt_hurmati',
     '«El-yurt hurmati» ordeni',
     '«Эл-юрт ҳурмати» ордени',
     'Орден «Эл-юрт хурмати»'),
    ('fidokorona_xizmat',
     '«Fidokorona xizmatlari uchun» ordeni',
     '«Фидокорона хизматлари учун» ордени',
     'Орден «За самоотверженный труд»'),
    ('mehnat_shuhrati',
     '«Mehnat shuhrati» ordeni',
     '«Меҳнат шуҳрати» ордени',
     'Орден «Мехнат шухрати»'),
    ('faxriy_murabbiy',
     '«Faxriy murabbiy» ordeni',
     '«Фахрий мураббий» ордени',
     'Орден «Почётный наставник»'),
    ('soglom_avlod',
     "I va II darajali «Sog'lom avlod uchun» ordeni",
     'I ва II даражали «Соғлом авлод учун» ордени',
     'Орден «Соглом авлод учун» I и II степени'),
    ('shon_sharaf',
     'I va II darajali «Shon-sharaf» ordeni',
     'I ва II даражали «Шон-шараф» ордени',
     'Орден «Шон-шараф» I и II степени'),
    ('dostlik', "«Do'stlik» ordeni", '«Дўстлик» ордени', 'Орден «Дустлик»'),
    ('salomatlik',
     'I va II darajali «Salomatlik» ordeni',
     'I ва II даражали «Саломатлик» ордени',
     'Орден «Саломатлик» I и II степени'),
    ('mardlik', '«Mardlik» ordeni', '«Мардлик» ордени', 'Орден «Мардлик»'),
    ('oliy_dostlik',
     "«Oliy Darajali Do'stlik» ordeni",
     '«Олий Даражали Дўстлик» ордени',
     'Орден «Олий Даражали Дустлик»'),
    ('oliy_imom_buxoriy',
     '«Oliy Darajali Imom Buxoriy» ordeni',
     '«Олий Даражали Имом Бухорий» ордени',
     'Орден «Олий Даражали Имам Бухари»'),
    ('imom_buxoriy',
     '«Imom Buxoriy» ordeni',
     '«Имом Бухорий» ордени',
     'Орден «Имам Бухари»'),
]

MEDALS_NAMES = [
    ('jasorat', '«Jasorat» medali', '«Жасорат» медали', 'Медаль «Жасорат»'),
    ('sodiq_xizmat',
     '«Sodiq xizmatlari uchun» medali',
     '«Содиқ хизматлари учун» медали',
     'Медаль «За преданную службу»'),
    ('soglom_turmush',
     "«Sog'lom turmush» medali",
     '«Соғлом турмуш» медали',
     'Медаль «Соглом турмуш»'),
    ('kelajak_bunyodkori',
     '«Kelajak bunyodkori» medali',
     '«Келажак бунёдкори» медали',
     'Медаль «Созидатель будущего»'),
    ('shuhrat', '«Shuhrat» medali', '«Шуҳрат» медали', 'Медаль «Шухрат»'),
]

HONORARY_DIPLOMA_NAMES = [
    ('faxriy_yorliq_uz',
     "«O'zbekiston Respublikasining Faxriy yorlig'i»",
     '«Ўзбекистон Республикасининг Фахрий ёрлиғи»',
     '«Почётная грамота Республики Узбекистан»'),
]

# Mapping: type key → list of names
NAMES_BY_TYPE = {
    'hero': HERO_NAMES,
    'honorary_titles': HONORARY_TITLES_NAMES,
    'orders': ORDERS_NAMES,
    'medals': MEDALS_NAMES,
    'honorary_diploma': HONORARY_DIPLOMA_NAMES,
}


class Command(BaseCommand):
    help = "Mukofot mansubliklari, turlari va nomlarini frontend bilan bir xil to'ldiradi"

    def handle(self, *args, **options):
        # ─── Affiliations ──────────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING('Mansubliklar:'))
        affiliations = {}
        for aff in AFFILIATIONS:
            obj, created = AwardAffiliation.objects.update_or_create(
                key=aff['key'],
                defaults={
                    'order': aff['order'],
                    'name': aff['uz_latn'],
                    'name_uz_latn': aff['uz_latn'],
                    'name_uz_cyrl': aff['uz_cyrl'],
                    'name_ru': aff['ru'],
                },
            )
            affiliations[aff['key']] = obj
            mark = '+' if created else '·'
            self.stdout.write(f'  {mark} {aff["uz_latn"]}')

        # ─── Types (faqat 'state' uchun) ───────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING('\nMukofot turlari (state):'))
        state_aff = affiliations['state']
        types_by_key = {}
        for tp in STATE_TYPES:
            obj, created = AwardType.objects.update_or_create(
                affiliation=state_aff, key=tp['key'],
                defaults={
                    'order': tp['order'],
                    'name': tp['uz_latn'],
                    'name_uz_latn': tp['uz_latn'],
                    'name_uz_cyrl': tp['uz_cyrl'],
                    'name_ru': tp['ru'],
                },
            )
            types_by_key[tp['key']] = obj
            mark = '+' if created else '·'
            self.stdout.write(f'  {mark} {tp["uz_latn"]}')

        # ─── Names (har tur ichida) ────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING('\nMukofot nomlari:'))
        total = 0
        for type_key, names in NAMES_BY_TYPE.items():
            tp = types_by_key[type_key]
            self.stdout.write(f'  [{type_key}]')
            for order, (key, uz_latn, uz_cyrl, ru) in enumerate(names, start=1):
                obj, created = AwardName.objects.update_or_create(
                    type=tp, key=key,
                    defaults={
                        'order': order,
                        'name': uz_latn,
                        'name_uz_latn': uz_latn,
                        'name_uz_cyrl': uz_cyrl,
                        'name_ru': ru,
                    },
                )
                mark = '+' if created else '·'
                self.stdout.write(f'      {mark} {uz_latn}')
                total += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTayyor: {len(AFFILIATIONS)} mansublik, '
                f'{len(STATE_TYPES)} tur, {total} nom.'
            )
        )
