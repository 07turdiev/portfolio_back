"""Mavjud vakillarga test uchun yashash va tug'ilgan joylarni (tuman darajasida)
variativ to'ldirish.

Xarita rejimi (`Yashash` / `Tug'ilgan`) animatsiyasini tekshirish uchun ataylab
quyidagi taqsimot bilan:

  30% — yashash va tug'ilish bir xil tumanda     → animatsiyasiz
  50% — yashash va tug'ilish butunlay boshqa tumanda → ko'rinarli surilish
  20% — birth_district = null                    → birth rejimda yashirinadi

Foydalanish:
    python manage.py seed_test_locations
    python manage.py seed_test_locations --dry-run       # saqlamaydi
    python manage.py seed_test_locations --seed 42       # qaytariluvchi natija
    python manage.py seed_test_locations --only-empty    # faqat null joyni to'ldiradi
    python manage.py seed_test_locations --null-ratio 0  # birth null bo'lmasin
    python manage.py seed_test_locations --only-birth    # PROD UCHUN: faqat birth_district
                                                          # ni to'ldiradi, residence ga tegmaydi
"""
from __future__ import annotations

import random
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import District, Representative


class Command(BaseCommand):
    help = "Mavjud vakillarga yashash + tug'ilgan tumanni variativ to'ldirish"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help="Ma'lumotni saqlamasdan, faqat statistikani chiqaradi",
        )
        parser.add_argument(
            '--seed', type=int, default=None,
            help='Random urug\'i — bir xil natija olish uchun',
        )
        parser.add_argument(
            '--only-empty', action='store_true',
            help="Faqat residence_district yoki birth_district null bo'lgan vakillarni yangilaydi",
        )
        parser.add_argument(
            '--only-birth', action='store_true',
            help="PROD UCHUN XAVFSIZ: faqat birth_district ni to'ldiradi, "
                 "residence_district ga tegmaydi. Faqat birth_district null bo'lganlarga yozadi.",
        )
        parser.add_argument(
            '--null-ratio', type=float, default=0.20,
            help='birth_district null bo\'lishi ehtimoli (0..1, default 0.20)',
        )
        parser.add_argument(
            '--same-district-ratio', type=float, default=0.30,
            help='Tug\'ilish va yashash bir tumanda bo\'lishi ehtimoli (0..1, default 0.30)',
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts['seed'] is not None:
            random.seed(opts['seed'])

        null_ratio = max(0.0, min(1.0, opts['null_ratio']))
        same_ratio = max(0.0, min(1.0, opts['same_district_ratio']))
        diff_ratio = max(0.0, 1.0 - null_ratio - same_ratio)
        if diff_ratio == 0.0:
            same_ratio = 1.0 - null_ratio  # 100% same, hech qanday boshqa tuman bo'lmasin

        # Barcha tumanlarni xotirada saqlaymiz — har vakil uchun random tanlash
        districts = list(District.objects.select_related('region').all())
        if not districts:
            self.stderr.write(self.style.ERROR(
                "Hech qanday tuman yo'q. Avval `populate_locations` ni ishga tushiring."
            ))
            return

        only_birth = opts['only_birth']
        qs = Representative.objects.select_related('residence_district').all()
        if only_birth:
            # Faqat birth null bo'lganlarni yangilaymiz, residence ga tegmaymiz
            qs = qs.filter(birth_district__isnull=True)
        elif opts['only_empty']:
            from django.db.models import Q
            qs = qs.filter(Q(residence_district__isnull=True) | Q(birth_district__isnull=True))

        total = qs.count()
        if not total:
            self.stdout.write("Yangilashga vakil yo'q.")
            return

        mode_label = (
            "FAQAT BIRTH (residence ga tegilmaydi)" if only_birth
            else "TO'LIQ (residence + birth)"
        )
        self.stdout.write(self.style.HTTP_INFO(
            f"Rejim: {mode_label}"
        ))
        self.stdout.write(self.style.HTTP_INFO(
            f"Vakillar: {total} | tumanlar: {len(districts)}"
        ))
        self.stdout.write(self.style.HTTP_INFO(
            f"Taqsimot: bir xil tuman {same_ratio:.0%}, "
            f"boshqa tuman {diff_ratio:.0%}, birth null {null_ratio:.0%}"
        ))

        stats = Counter()
        updated = []

        for rep in qs.iterator(chunk_size=200):
            if only_birth:
                # PROD-safe: mavjud residence dan foydalanamiz, yangi qo'ymaymiz
                residence = rep.residence_district
                # Agar residence ham null bo'lsa — birth uchun "same district" mantig'i
                # ishlamaydi, oddiy random tanlaymiz
                if residence is None:
                    rep.birth_district = random.choice(districts) if random.random() > null_ratio else None
                    stats['null' if rep.birth_district is None else 'no_residence'] += 1
                    updated.append(rep)
                    continue
            else:
                # Yashash tumanini ham tasodifiy qo'yamiz
                residence = random.choice(districts)
                rep.residence_district = residence

            # Tug'ilgan tuman — taqsimot bo'yicha
            roll = random.random()
            if roll < null_ratio:
                rep.birth_district = None
                stats['null'] += 1
            elif roll < null_ratio + same_ratio:
                rep.birth_district = residence
                stats['same'] += 1
            else:
                # Boshqa tumandan tanlash (residence tumanidan emas)
                while True:
                    candidate = random.choice(districts)
                    if candidate.pk != residence.pk:
                        rep.birth_district = candidate
                        break
                stats['diff'] += 1

            updated.append(rep)

        # Bulk update — bitta SQL
        if not opts['dry_run']:
            fields = ['birth_district'] if only_birth else ['residence_district', 'birth_district']
            Representative.objects.bulk_update(updated, fields, batch_size=500)

        prefix = '[DRY-RUN] ' if opts['dry_run'] else ''
        self.stdout.write(self.style.SUCCESS(
            f"\n{prefix}Yangilandi: {len(updated)} ta vakil"
        ))
        self.stdout.write(f"  • bir xil tuman (animatsiyasiz): {stats['same']}")
        self.stdout.write(f"  • boshqa tuman (animatsiya ko'rinadi): {stats['diff']}")
        self.stdout.write(f"  • birth = null (birth rejimda yashirin): {stats['null']}")
        if stats.get('no_residence'):
            self.stdout.write(self.style.WARNING(
                f"  • residence ham null (random birth): {stats['no_residence']}"
            ))

        if opts['dry_run']:
            self.stdout.write(self.style.WARNING(
                "\nDIQQAT: --dry-run rejimi — DB o'zgarmadi."
            ))
