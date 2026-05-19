"""GeoJSON dan har tumanga lat/lng (centroid) hisoblab District modeliga yozadi.

Foydalanish:
    python manage.py compute_district_coords
    python manage.py compute_district_coords --dry-run
"""
import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import District


# Russian → English transliteration variants (ko'p variant — Ж=J yoki Dj)
CYR_LAT_VARIANTS = {
    'ж': ['j', 'zh', 'dj'],
    'х': ['x', 'kh', 'h'],
    'ё': ['yo', 'e'],
    'й': ['y', 'i', ''],
    'ц': ['ts', 'c'],
    'ч': ['ch'],
    'ш': ['sh'],
    'щ': ['shch', 'sh'],
    'ъ': [''],
    'ы': ['i', 'y'],
    'ь': [''],
    'э': ['e'],
    'ю': ['yu', 'u'],
    'я': ['ya', 'a'],
}
CYR_LAT_SIMPLE = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'з': 'z',
    'и': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
    'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
}


def translit_variants(text):
    """Bir necha transliteratsiya variantini qaytaradi."""
    text = text.lower().strip()
    # Suffixlarni olib tashlash
    text = re.sub(r'ского|ский|ская|район|г\.|город', '', text).strip()
    text = re.sub(r'\s+', '', text)

    variants = ['']
    for ch in text:
        if ch in CYR_LAT_SIMPLE:
            variants = [v + CYR_LAT_SIMPLE[ch] for v in variants]
        elif ch in CYR_LAT_VARIANTS:
            new_variants = []
            for opt in CYR_LAT_VARIANTS[ch]:
                for v in variants:
                    new_variants.append(v + opt)
            variants = new_variants
        else:
            variants = [v + ch for v in variants]
    return list(set(variants))


def centroid(geometry):
    """GeoJSON geometriyasidan centroid (o'rtacha lat/lng) hisoblash."""
    polys = (
        geometry['coordinates']
        if geometry['type'] == 'MultiPolygon'
        else [geometry['coordinates']]
    )
    s_lat, s_lng, n = 0.0, 0.0, 0
    for poly in polys:
        for ring in poly:
            for lng, lat in ring:
                s_lat += lat
                s_lng += lng
                n += 1
    return (s_lat / n, s_lng / n) if n else (0, 0)


def normalize(s):
    return re.sub(r'[\s\-_\']', '', s.lower())


# SOATO → GeoJSON shapeName (qo'lda mos kelmagan tumanlar uchun)
MANUAL_MAP = {
    # Andijon
    '1703209': 'Bo\'ston', '1703211': 'Djalalkuduk', '1703214': 'Izboskan',
    '1703217': 'Ulugnar', '1703220': 'Kurgantepa', '1703224': 'Asaka',
    '1703227': 'Markhamat', '1703230': 'Shakhrixan', '1703236': 'Khadjaabad',
    # Buxoro
    '1706204': 'Alat', '1706219': 'Kagan', '1706230': 'Karakul',
    '1706232': 'Karaulbazar', '1706242': 'Rаmitan',
    # Jizzax
    '1708207': 'Bakhmal', '1708214': 'Sharof Rashidov',
    '1708218': 'Zaаmin', '1708220': 'Zarbdar',
    # Navoiy
    '1712234': 'Karmana',
    # Fargona
    '1730206': 'Kushtepa', '1730212': 'Buvayda',
    '1730218': 'Kuva', '1730236': 'Dangara',
    # Qashqadaryo
    '1710213': 'Dehkanabad', '1710233': 'Mirishkar', '1710240': 'Nishan',
    # Navoiy
    '1712216': 'Kiziltepa', '1712238': 'Nurata',
    # Namangan
    '1714217': 'Kasansay',
    # Samarqand
    '1718203': 'Akdarya', '1718230': 'Pastdargom', '1718233': 'Pakhtachi',
    # Surxondaryo
    '1722220': 'Dzharkurgan', '1722232': 'Sariasiya', '1722238': 'Sherabad',
    # Sirdaryo
    '1724226': 'Sardoba', '1724231': 'Sirdarya', '1724413': 'Yangiyer city',
    # Toshkent shahri
    '1726262': 'Uchtepa', '1726277': 'Shaykhantokhur', '1726290': 'Yashnobod',
    # Toshkent viloyati
    '1727228': 'Buka', '1727237': 'Zangiata', '1727239': 'Yukarichirchik',
    # Xorazm
    '1733221': 'Tuprokkala', '1733223': 'Khanka', '1733226': 'Khiva',
    # Qoraqalpog'iston
    '1735204': 'Amudarya', '1735236': 'Khojeyli', '1735250': 'Ellikkala',
    '1735228': 'Takhiatash', '1735230': 'Takhtakupir',
}


class Command(BaseCommand):
    help = "Har tumanga lat/lng (centroid) hisoblab District modeliga yozadi"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        # 1) Avval oldindan hisoblangan centroidlar JSON ni tekshirish
        centroids_json = (
            Path(__file__).resolve().parent.parent.parent / 'data' / 'district_centroids.json'
        )
        if centroids_json.exists():
            with open(centroids_json, encoding='utf-8') as f:
                cached = json.load(f)
            count = 0
            for d in District.objects.all():
                c = cached.get(d.soato)
                if c:
                    d.lat = c['lat']
                    d.lng = c['lng']
                    if not options['dry_run']:
                        d.save(update_fields=['lat', 'lng'])
                    count += 1
            self.stdout.write(self.style.SUCCESS(
                f'Cached centroids dan {count} ta tuman yangilandi'
            ))
            return

        # 2) Aks holda GeoJSON dan hisoblash
        bases = [
            Path(__file__).resolve().parent.parent.parent / 'data' / 'geojson',
            Path(__file__).resolve().parent.parent.parent.parent.parent / 'data' / 'geojson',
        ]
        geo_path = None
        for base in bases:
            p = base / 'uzbekistan.geojson'
            if p.exists():
                geo_path = p
                break
        if geo_path is None:
            self.stderr.write(
                'GeoJSON yoki district_centroids.json topilmadi.'
            )
            return

        with open(geo_path, encoding='utf-8') as f:
            geo = json.load(f)

        # GeoJSON xususiyatlarini normallashtirilgan English nomi bo'yicha indekslash
        geo_by_norm = {}
        for feat in geo['features']:
            name = feat['properties']['shapeName']
            # 'Andijan city' → 'andijan' + 'city' alohida
            norm = normalize(re.sub(r' city$', '', name, flags=re.IGNORECASE))
            geo_by_norm[norm] = (name, feat['geometry'])

        matched = 0
        unmatched = []

        # GeoJSON ni shapeName bo'yicha ham indexlash
        geo_by_exact = {feat['properties']['shapeName']: feat['geometry']
                        for feat in geo['features']}

        for d in District.objects.all().select_related('region'):
            # 1) Manual map ni avval tekshiramiz
            best = None
            if d.soato in MANUAL_MAP:
                shape = MANUAL_MAP[d.soato]
                if shape in geo_by_exact:
                    best = (shape, geo_by_exact[shape])

            if best is None:
                # 2) name_ru asosida transliteratsiya variantlarini olamiz
                variants = translit_variants(d.name_ru or d.name_uz_latn or '')
                for v in variants:
                    v_norm = normalize(v)
                    if not v_norm:
                        continue
                    if v_norm in geo_by_norm:
                        best = geo_by_norm[v_norm]
                        break
                    for k, val in geo_by_norm.items():
                        if v_norm in k or k in v_norm:
                            if abs(len(v_norm) - len(k)) <= 3:
                                best = val
                                break
                    if best:
                        break

            if best:
                lat, lng = centroid(best[1])
                d.lat = lat
                d.lng = lng
                if not options['dry_run']:
                    d.save(update_fields=['lat', 'lng'])
                matched += 1
                self.stdout.write(
                    f'  +{d.soato} {d.name_ru[:30]:30}  →  {best[0]:25} ({lat:.4f}, {lng:.4f})'
                )
            else:
                unmatched.append(f'{d.soato} = {d.name_ru}')

        self.stdout.write(self.style.SUCCESS(
            f"\nMatched: {matched}/{District.objects.count()}"
        ))
        if unmatched:
            self.stdout.write(self.style.WARNING(
                f"\nUnmatched ({len(unmatched)}):"
            ))
            for u in unmatched:
                self.stdout.write('  ' + u)
