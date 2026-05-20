"""Mahalla nomlarini Cyrillicdan to'g'ri Lotinga aylantiradi (Uzbek 2019 standarti).

Lotin maydoni `name_uz_latn` ba'zi mahallalarda ingliz uslubida (diakritikasiz)
saqlangan. Masalan: "Bo'ston" → "Boston", "Qo'rg'on" → "Korgon". Bu komanda
Cyrillicdagi ў/ғ/қ/ҳ harflaridan to'g'ri lotin diakritikalarini tiklaydi.

Foydalanish:
    python manage.py fix_mahalla_translit            # ko'rsatish (dry-run)
    python manage.py fix_mahalla_translit --apply    # bazani yangilash
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Mahalla


# Cyrillic → Latin (Uzbek 2019 lotin)
# Diakritika uchun curly apostrof ' (U+2018) ishlatamiz — bu rasmiy standart
APO = '‘'

# Bigramlar (avval tekshiriladi)
DIGRAM = {
    'ё': 'yo', 'Ё': 'Yo',
    'ю': 'yu', 'Ю': 'Yu',
    'я': 'ya', 'Я': 'Ya',
    'ч': 'ch', 'Ч': 'Ch',
    'ш': 'sh', 'Ш': 'Sh',
    'ц': 'ts', 'Ц': 'Ts',
    'ў': f'o{APO}', 'Ў': f'O{APO}',
    'ғ': f'g{APO}', 'Ғ': f'G{APO}',
}

# Bir harfli o'tkazishlar
MONO = {
    'а': 'a', 'А': 'A',
    'б': 'b', 'Б': 'B',
    'в': 'v', 'В': 'V',
    'г': 'g', 'Г': 'G',
    'д': 'd', 'Д': 'D',
    'е': 'e', 'Е': 'E',
    'ж': 'j', 'Ж': 'J',
    'з': 'z', 'З': 'Z',
    'и': 'i', 'И': 'I',
    'й': 'y', 'Й': 'Y',
    'к': 'k', 'К': 'K',
    'л': 'l', 'Л': 'L',
    'м': 'm', 'М': 'M',
    'н': 'n', 'Н': 'N',
    'о': 'o', 'О': 'O',
    'п': 'p', 'П': 'P',
    'р': 'r', 'Р': 'R',
    'с': 's', 'С': 'S',
    'т': 't', 'Т': 'T',
    'у': 'u', 'У': 'U',
    'ф': 'f', 'Ф': 'F',
    'х': 'x', 'Х': 'X',
    'ъ': APO, 'Ъ': APO,
    'ь': '', 'Ь': '',
    'ы': 'i', 'Ы': 'I',
    'э': 'e', 'Э': 'E',
    'қ': 'q', 'Қ': 'Q',
    'ҳ': 'h', 'Ҳ': 'H',
    'ё': 'yo', 'Ё': 'Yo',
}


def cyr_to_lat(text: str) -> str:
    """Uzbek Cyrillic'ni Lotin (2019) standartiga aylantirish."""
    if not text:
        return ''
    out = []
    for ch in text:
        if ch in DIGRAM:
            out.append(DIGRAM[ch])
        elif ch in MONO:
            out.append(MONO[ch])
        else:
            out.append(ch)
    return ''.join(out)


def needs_fix(cyr: str, lat: str) -> bool:
    """Tekshirish: Cyrillicda diakritika kerak bo'lgan harf bor, lekin
    Lotinda mos diakritika yo'q.
    """
    if not cyr:
        return False
    cyr_lo = cyr.lower()
    apos = ("'", '‘', '’', 'ʻ', 'ʼ', '`')
    has_apo = any(a in lat for a in apos)
    if 'ў' in cyr_lo and not has_apo:
        return True
    if 'ғ' in cyr_lo and not has_apo:
        return True
    if 'қ' in cyr_lo and 'q' not in lat.lower():
        return True
    if 'ҳ' in cyr_lo and 'h' not in lat.lower() and 'x' not in lat.lower():
        return True
    return False


class Command(BaseCommand):
    help = "Mahalla name_uz_latn maydonini Cyrillic'dan to'g'ri transliteratsiya bilan tiklaydi"

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help="Bazani yangilash. Bu yo'q bo'lsa, faqat ko'rsatadi (dry-run)."
        )
        parser.add_argument(
            '--all', action='store_true',
            help="Hammasini regeneratsiya qilish (mavjud Lotin nomlarini almashtirish)"
        )

    def handle(self, *args, **options):
        apply_changes = options['apply']
        fix_all = options['all']

        to_fix = []
        for m in Mahalla.objects.all().only('tin', 'name_uz_cyrl', 'name_uz_latn'):
            cyr = m.name_uz_cyrl or ''
            lat = m.name_uz_latn or ''
            if not cyr:
                continue

            new_lat = cyr_to_lat(cyr)
            if fix_all:
                if new_lat != lat:
                    to_fix.append((m.tin, cyr, lat, new_lat))
            else:
                if needs_fix(cyr, lat):
                    to_fix.append((m.tin, cyr, lat, new_lat))

        self.stdout.write(f"Topilgan tuzatish kerak: {len(to_fix)} ta mahalla")
        if not to_fix:
            self.stdout.write(self.style.SUCCESS("Hammasi to'g'ri, hech narsa qilish kerak emas."))
            return

        # Birinchi 20 ta misol
        self.stdout.write("\nBirinchi 20 misol:")
        for tin, cyr, old, new in to_fix[:20]:
            self.stdout.write(f"  [{tin}] {cyr}  →  {old!r}  =>  {new!r}")

        if not apply_changes:
            self.stdout.write(self.style.WARNING(
                f"\nDRY-RUN: bazaga yozilmadi. Qo'llash uchun --apply qo'shing."
            ))
            return

        # Yangilash
        with transaction.atomic():
            for tin, cyr, old, new in to_fix:
                Mahalla.objects.filter(tin=tin).update(name_uz_latn=new)

        self.stdout.write(self.style.SUCCESS(
            f"\nBazada yangilandi: {len(to_fix)} ta mahalla."
        ))
