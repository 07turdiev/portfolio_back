"""Viloyat / Tuman / Mahalla ma'lumotlarini /data papkasidan to'ldiradi.

Manbalar:
    data/mahalla.json — 8992 mahalla (4 til: uz_latn, uz_cyrl, ru, en)
    data/tuman.json   — 205 tuman (faqat ruscha)

Foydalanish:
    python manage.py populate_locations
    python manage.py populate_locations --data-dir ../data
"""
import io
import json
import sys
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import District, Mahalla, Region


# 14 ta viloyat: SOATO → (slug, uz_latn, uz_cyrl, ru)
REGIONS = {
    '1703': ('andijon',          'Andijon viloyati',         'Андижон вилояти',           'Андижанская область'),
    '1706': ('buxoro',           'Buxoro viloyati',          'Бухоро вилояти',            'Бухарская область'),
    '1708': ('jizzax',           'Jizzax viloyati',          'Жиззах вилояти',            'Джизакская область'),
    '1710': ('qashqadaryo',      'Qashqadaryo viloyati',     'Қашқадарё вилояти',         'Кашкадарьинская область'),
    '1712': ('navoiy',           'Navoiy viloyati',          'Навоий вилояти',            'Навоийская область'),
    '1714': ('namangan',         'Namangan viloyati',        'Наманган вилояти',          'Наманганская область'),
    '1718': ('samarqand',        'Samarqand viloyati',       'Самарқанд вилояти',         'Самаркандская область'),
    '1722': ('surxondaryo',      'Surxondaryo viloyati',     'Сурхондарё вилояти',        'Сурхандарьинская область'),
    '1724': ('sirdaryo',         'Sirdaryo viloyati',        'Сирдарё вилояти',           'Сырдарьинская область'),
    '1726': ('toshkent-shahri',  'Toshkent shahri',          'Тошкент шаҳри',             'г. Ташкент'),
    '1727': ('toshkent-viloyati','Toshkent viloyati',        'Тошкент вилояти',           'Ташкентская область'),
    '1730': ('fargona',          "Farg'ona viloyati",        'Фарғона вилояти',           'Ферганская область'),
    '1733': ('xorazm',           'Xorazm viloyati',          'Хоразм вилояти',            'Хорезмская область'),
    '1735': ('qoraqalpogiston',  "Qoraqalpog'iston Respublikasi", 'Қорақалпоғистон Республикаси', 'Республика Каракалпакстан'),
}


class Command(BaseCommand):
    help = "Viloyat / Tuman / Mahalla ma'lumotlarini /data papkasidan to'ldiradi"

    def add_arguments(self, parser):
        default_dir = Path(__file__).resolve().parent.parent.parent / 'data'
        parser.add_argument(
            '--data-dir', default=str(default_dir),
            help="JSON fayllar joylashgan papka (default: core/data/)"
        )

    def handle(self, *args, **options):
        # Windows konsoli uchun UTF-8 stdout
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass

        data_dir = Path(options['data_dir']).resolve()
        mahalla_file = data_dir / 'mahalla.json'
        tuman_file = data_dir / 'tuman.json'

        if not mahalla_file.exists():
            self.stderr.write(f'Fayl topilmadi: {mahalla_file}')
            return
        if not tuman_file.exists():
            self.stderr.write(f'Fayl topilmadi: {tuman_file}')
            return

        # ─── Viloyatlar ─────────────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING('1) Viloyatlar:'))
        for soato, (slug, uz_latn, uz_cyrl, ru) in REGIONS.items():
            Region.objects.update_or_create(
                soato=soato,
                defaults={
                    'slug': slug,
                    'name_uz_latn': uz_latn,
                    'name_uz_cyrl': uz_cyrl,
                    'name_ru': ru,
                },
            )
            self.stdout.write(f'  +{soato} — {uz_latn}')

        # ─── Tumanlar (tuman.json'dan ruscha nomlar) ────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING('\n2) Tumanlar:'))
        with open(tuman_file, encoding='utf-8-sig') as f:
            tu_data = json.load(f)

        # Tuman SOATO → uning viloyat SOATO si (qisqaroq prefix moslashish)
        region_soatos = set(REGIONS.keys())
        tuman_count = 0
        with transaction.atomic():
            for t in tu_data:
                sid = t['RegionID']
                if sid in region_soatos:
                    continue  # bu viloyat, tuman emas

                # Viloyat SOATO ni topish (eng uzun moslashuvchi prefiks)
                region_soato = None
                for r in region_soatos:
                    if sid.startswith(r):
                        region_soato = r
                        break
                if not region_soato:
                    self.stderr.write(f'  WARNViloyatsiz tuman: {sid} — {t["RegionNane"]}')
                    continue

                ru_name = t['RegionNane'].strip()
                District.objects.update_or_create(
                    soato=sid,
                    defaults={
                        'region_id': region_soato,
                        'name_uz_latn': ru_name,  # boshlang'ich qiymat; admin keyin tuzatadi
                        'name_uz_cyrl': ru_name,
                        'name_ru': ru_name,
                    },
                )
                tuman_count += 1
        self.stdout.write(f'  +{tuman_count} ta tuman qo\'shildi/yangilandi')

        # ─── Mahallalar (4 tilli) ───────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING('\n3) Mahallalar:'))
        with open(mahalla_file, encoding='utf-8-sig') as f:
            ms_data = json.load(f)

        existing_districts = set(District.objects.values_list('soato', flat=True))
        existing_mahallas = set(Mahalla.objects.values_list('tin', flat=True))

        to_create = []
        to_update = []
        skipped = 0
        for m in ms_data:
            tin = m['tin']
            district_soato = m['district_soato']
            if district_soato not in existing_districts:
                # mahalla.json'da bor tumanlar tuman.json'da bo'lmagan holatlar
                # avtomatik tuman yarataylik (faqat mahalla'dagi viloyat ma'lumotlari bo'yicha)
                region_soato = m['region_soato']
                if region_soato not in REGIONS:
                    skipped += 1
                    continue
                District.objects.create(
                    soato=district_soato,
                    region_id=region_soato,
                    name_uz_latn=f'{district_soato} tumani',
                    name_uz_cyrl=f'{district_soato} тумани',
                    name_ru=f'район {district_soato}',
                )
                existing_districts.add(district_soato)

            mahalla = Mahalla(
                tin=tin,
                district_id=district_soato,
                code=m.get('code', '') or '',
                name_uz_latn=m.get('name_uz_latin', '') or '',
                name_uz_cyrl=m.get('name_uz', '') or '',
                name_ru=m.get('name_ru', '') or '',
                name_en=m.get('name_en', '') or '',
            )
            if tin in existing_mahallas:
                to_update.append(mahalla)
            else:
                to_create.append(mahalla)

        if to_create:
            Mahalla.objects.bulk_create(to_create, batch_size=1000)
        if to_update:
            Mahalla.objects.bulk_update(
                to_update,
                ['district_id', 'code', 'name_uz_latn', 'name_uz_cyrl', 'name_ru', 'name_en'],
                batch_size=1000,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTayyor: {len(REGIONS)} viloyat, {District.objects.count()} tuman, "
                f"{Mahalla.objects.count()} mahalla. Yangi: {len(to_create)}, "
                f"yangilangan: {len(to_update)}, o'tkazib yuborilgan: {skipped}."
            )
        )
