"""Mavjud vakillarga test uchun yashash va tug'ilgan joylarni variativ
to'ldirish.

Xarita rejimi (`Yashash` / `Tug'ilgan`) animatsiyasini tekshirish uchun ataylab
quyidagi taqsimot bilan:

  30% — yashash va tug'ilish bir xil tumandagi mahallada → animatsiyasiz
  50% — yashash va tug'ilish butunlay boshqa tumanda     → ko'rinarli surilish
  20% — birth_mahalla = null                              → birth rejimda yashirinadi

Foydalanish:
    python manage.py seed_test_locations
    python manage.py seed_test_locations --dry-run       # saqlamaydi
    python manage.py seed_test_locations --seed 42       # qaytariluvchi natija
    python manage.py seed_test_locations --only-empty    # faqat null joyni to'ldiradi
    python manage.py seed_test_locations --null-ratio 0  # birth null bo'lmasin
    python manage.py seed_test_locations --only-birth    # PROD UCHUN: faqat birth_mahalla
                                                          # ni to'ldiradi, residence ga tegmaydi
"""
from __future__ import annotations

import random
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Mahalla, Representative


class Command(BaseCommand):
    help = "Mavjud vakillarga yashash + tug'ilgan mahallani variativ to'ldirish"

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
            help="Faqat residence_mahalla yoki birth_mahalla null bo'lgan vakillarni yangilaydi",
        )
        parser.add_argument(
            '--only-birth', action='store_true',
            help="PROD UCHUN XAVFSIZ: faqat birth_mahalla ni to'ldiradi, "
                 "residence_mahalla ga tegmaydi. Faqat birth_mahalla null bo'lganlarga yozadi.",
        )
        parser.add_argument(
            '--null-ratio', type=float, default=0.20,
            help='birth_mahalla null bo\'lishi ehtimoli (0..1, default 0.20)',
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

        # Barcha mahallalarni xotirada saqlaymiz — har vakil uchun random tanlash
        mahallas = list(
            Mahalla.objects.select_related('district__region').all()
        )
        if not mahallas:
            self.stderr.write(self.style.ERROR(
                "Hech qanday mahalla yo'q. Avval `populate_locations` ni ishga tushiring."
            ))
            return

        # Tuman bo'yicha indeks — bir tumandagi mahallalarni tez topish uchun
        by_district: dict[str, list[Mahalla]] = {}
        for m in mahallas:
            by_district.setdefault(m.district_id, []).append(m)

        only_birth = opts['only_birth']
        qs = Representative.objects.select_related('residence_mahalla').all()
        if only_birth:
            # Faqat birth null bo'lganlarni yangilaymiz, residence ga tegmaymiz
            qs = qs.filter(birth_mahalla__isnull=True)
        elif opts['only_empty']:
            from django.db.models import Q
            qs = qs.filter(Q(residence_mahalla__isnull=True) | Q(birth_mahalla__isnull=True))

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
            f"Vakillar: {total} | mahallalar: {len(mahallas)} | tumanlar: {len(by_district)}"
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
                residence = rep.residence_mahalla
                # Agar residence ham null bo'lsa — birth uchun "same district" mantig'i
                # ishlamaydi, oddiy random tanlaymiz
                if residence is None:
                    rep.birth_mahalla = random.choice(mahallas) if random.random() > null_ratio else None
                    stats['null' if rep.birth_mahalla is None else 'no_residence'] += 1
                    updated.append(rep)
                    continue
            else:
                # Yashash mahallasini ham tasodifiy qo'yamiz
                residence = random.choice(mahallas)
                rep.residence_mahalla = residence

            # Tug'ilgan mahalla — taqsimot bo'yicha
            roll = random.random()
            if roll < null_ratio:
                rep.birth_mahalla = None
                stats['null'] += 1
            elif roll < null_ratio + same_ratio:
                same_pool = by_district.get(residence.district_id, [residence])
                rep.birth_mahalla = random.choice(same_pool)
                stats['same'] += 1
            else:
                # Boshqa tumandan tanlash (residence tumanidan emas)
                while True:
                    candidate = random.choice(mahallas)
                    if candidate.district_id != residence.district_id:
                        rep.birth_mahalla = candidate
                        break
                stats['diff'] += 1

            updated.append(rep)

        # Bulk update — bitta SQL
        if not opts['dry_run']:
            fields = ['birth_mahalla'] if only_birth else ['residence_mahalla', 'birth_mahalla']
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
