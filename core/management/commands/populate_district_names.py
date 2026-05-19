"""Tuman nomlarini 3 tilda + slug bilan to'liq to'ldiradi.

Manba: core/data/district_names.json (soatoMap.js dan generatsiya qilingan)

Foydalanish:
    python manage.py populate_district_names
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import District


class Command(BaseCommand):
    help = "Tuman nomlarini 3 tilda + slug bilan to'ldiradi"

    @transaction.atomic
    def handle(self, *args, **options):
        names_path = Path(__file__).resolve().parent.parent.parent / 'data' / 'district_names.json'
        if not names_path.exists():
            self.stderr.write(f'Fayl topilmadi: {names_path}')
            return

        with open(names_path, encoding='utf-8') as f:
            data = json.load(f)

        updated = 0
        skipped = 0
        for d in District.objects.all():
            entry = data.get(d.soato)
            if not entry:
                skipped += 1
                continue
            d.slug = entry['slug']
            d.name_uz_latn = entry['uz_latn']
            d.name_uz_cyrl = entry['uz_cyrl']
            d.name_ru = entry['ru']
            d.save(update_fields=['slug', 'name_uz_latn', 'name_uz_cyrl', 'name_ru'])
            updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Yangilandi: {updated}/{District.objects.count()} tuman '
            f"(o'tkazib yuborilgan: {skipped})"
        ))
