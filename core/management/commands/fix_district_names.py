"""Tuman nomlarini ruschadan o'zbek (latin va kirill) ga konvertatsiya qiladi.

tuman.json faylida faqat ruscha nomlar bo'lgani uchun barcha 206 tumanda
name_uz_latn, name_uz_cyrl, name_ru maydonlari bir xil rus matnga ega edi.
Bu skript ularni avtomatik transliteratsiya qiladi.

Foydalanish:
    python manage.py fix_district_names
    python manage.py fix_district_names --dry-run     # faqat ko'rsatadi
    python manage.py fix_district_names --force       # mavjud uz nomlarini ham o'zgartiradi
"""
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import District


# Cyrillic → Latin transliteration (O'zbek standarti)
RU_TO_LATN = [
    ('Ё', 'Yo'), ('ё', 'yo'),
    ('Ю', 'Yu'), ('ю', 'yu'),
    ('Я', 'Ya'), ('я', 'ya'),
    ('Ч', 'Ch'), ('ч', 'ch'),
    ('Щ', 'Shch'), ('щ', 'shch'),
    ('Ш', 'Sh'), ('ш', 'sh'),
    ('Ў', "O'"), ('ў', "o'"),
    ('Қ', 'Q'), ('қ', 'q'),
    ('Ғ', "G'"), ('ғ', "g'"),
    ('Ҳ', 'H'), ('ҳ', 'h'),
    ('Ж', 'J'), ('ж', 'j'),
    ('Ц', 'Ts'), ('ц', 'ts'),
    ('Й', 'Y'), ('й', 'y'),
    ('Э', 'E'), ('э', 'e'),
    ('Ъ', "'"), ('ъ', "'"),
    ('Ы', 'I'), ('ы', 'i'),
    ('Ь', ''), ('ь', ''),
    ('А', 'A'), ('а', 'a'),
    ('Б', 'B'), ('б', 'b'),
    ('В', 'V'), ('в', 'v'),
    ('Г', 'G'), ('г', 'g'),
    ('Д', 'D'), ('д', 'd'),
    ('Е', 'E'), ('е', 'e'),
    ('З', 'Z'), ('з', 'z'),
    ('И', 'I'), ('и', 'i'),
    ('К', 'K'), ('к', 'k'),
    ('Л', 'L'), ('л', 'l'),
    ('М', 'M'), ('м', 'm'),
    ('Н', 'N'), ('н', 'n'),
    ('О', 'O'), ('о', 'o'),
    ('П', 'P'), ('п', 'p'),
    ('Р', 'R'), ('р', 'r'),
    ('С', 'S'), ('с', 's'),
    ('Т', 'T'), ('т', 't'),
    ('У', 'U'), ('у', 'u'),
    ('Ф', 'F'), ('ф', 'f'),
    ('Х', 'X'), ('х', 'x'),
]


def ru_to_uz_cyrl(text):
    """Russian Cyrillic → O'zbek Kirill (suffix va so'z tartibi bilan)."""
    if not text:
        return ''
    t = text.strip()

    # "город X" → "X шаҳри" (so'z tartibini almashtirish)
    m = re.match(r'^город\s+(.+)$', t, flags=re.IGNORECASE)
    if m:
        t = f'{m.group(1).strip()} шаҳри'
    else:
        m = re.match(r'^г\.\s*(.+)$', t, flags=re.IGNORECASE)
        if m:
            t = f'{m.group(1).strip()} шаҳри'

    # "X-ский район" → "X тумани"
    t = re.sub(r'(\w+?)\s*ский\s+район\b', r'\1 тумани', t, flags=re.IGNORECASE)
    t = re.sub(r'(\w+?)\s*ская\s+область\b', r'\1 вилояти', t, flags=re.IGNORECASE)
    t = re.sub(r'(\w+?)\s*ский\s+р-н\b', r'\1 тумани', t, flags=re.IGNORECASE)
    t = re.sub(r'(\w+?)\s*ская\s+обл\.?', r'\1 вилояти', t, flags=re.IGNORECASE)
    # Mustaqil "район" so'zi
    t = re.sub(r'\bрайон\b', 'тумани', t, flags=re.IGNORECASE)
    # Qoldiq "ский" / "ская" / "цкий"
    t = re.sub(r'(\w+?)цкий\b', r'\1', t, flags=re.IGNORECASE)
    t = re.sub(r'(\w+?)ский\b', r'\1', t, flags=re.IGNORECASE)
    t = re.sub(r'(\w+?)ская\b', r'\1', t, flags=re.IGNORECASE)

    # Russian-specific letters → O'zbek Kirill
    t = t.replace('ы', 'и').replace('Ы', 'И')
    t = t.replace('щ', 'ш').replace('Щ', 'Ш')
    t = t.replace('э', 'е').replace('Э', 'Е')
    t = t.replace('ё', 'ё').replace('Ё', 'Ё')  # qoladi
    # 'ъ' va 'ь' belgilarini olib tashlash
    t = t.replace('ъ', '').replace('Ъ', '')
    t = t.replace('ь', '').replace('Ь', '')

    # Ortiqcha bo'shliqlar
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def uz_cyrl_to_latn(text):
    """O'zbek Kirill → O'zbek Lotin."""
    if not text:
        return ''
    for cyr, lat in RU_TO_LATN:
        text = text.replace(cyr, lat)
    return text


def ru_to_uz_latn(text):
    """Russian → O'zbek Lotin (kirill orqali)."""
    return uz_cyrl_to_latn(ru_to_uz_cyrl(text))


class Command(BaseCommand):
    help = "Tuman nomlarini ruschadan o'zbek (latin/kirill) ga konvertatsiya qiladi"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help="Bazaga yozmasdan faqat ko'rsatadi")
        parser.add_argument('--force', action='store_true',
                            help="Mavjud uz nomlarini ham qayta yozadi")

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        total = 0
        updated = 0
        for d in District.objects.all().order_by('region', 'name_uz_latn'):
            total += 1
            ru = d.name_ru.strip()
            if not ru:
                continue

            new_cyrl = ru_to_uz_cyrl(ru)
            new_latn = uz_cyrl_to_latn(new_cyrl)

            # Agar force bo'lmasa va uz nomlari allaqachon farq qilsa, o'tkazib yuborish
            if not force:
                if d.name_uz_cyrl != d.name_ru and d.name_uz_latn != d.name_ru:
                    continue

            changed = False
            if d.name_uz_cyrl != new_cyrl:
                d.name_uz_cyrl = new_cyrl
                changed = True
            if d.name_uz_latn != new_latn:
                d.name_uz_latn = new_latn
                changed = True

            if changed:
                updated += 1
                self.stdout.write(f"  {d.soato}: {ru[:30]}  →  {new_latn}  /  {new_cyrl}")
                if not dry_run:
                    d.save(update_fields=['name_uz_latn', 'name_uz_cyrl'])

        mode = ' (DRY RUN)' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f"\nTayyor: {updated}/{total} ta tuman yangilandi{mode}"
        ))
