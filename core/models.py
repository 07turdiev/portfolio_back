"""Portfolio backend modellari.

Iyerarxiya:
    Direction (yo'nalish) — Vakil shu yo'nalishga tegishli.

    AwardAffiliation (mansublik: davlat, viloyat, vazirlik, ...)
        └── AwardType (turi: hero, faxriy unvonlar, ordenlar, medallar, ...)
                └── AwardName (mukofotning aniq nomi)

    Representative (vakil) — bitta Direction, ko'p AwardName (through model bilan)
"""
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField('Yaratilgan vaqt', auto_now_add=True)
    updated_at = models.DateTimeField("O'zgartirilgan vaqt", auto_now=True)

    class Meta:
        abstract = True


# ── Yo'nalishlar ──────────────────────────────────────────────────────────

class Direction(TimestampedModel):
    """Sanat sohasi yo'nalishi (teatr/sirk, ta'lim, kino, ...)."""

    key = models.SlugField(
        'Kalit (slug)', max_length=64, unique=True,
        help_text="URL slug. Masalan: theater_circus, education, cinema, ..."
    )
    name_uz_latn = models.CharField('Nomi (lotin)', max_length=200)
    name_uz_cyrl = models.CharField('Nomi (krill)', max_length=200)
    name_ru = models.CharField('Название (рус)', max_length=200)
    icon = models.CharField(
        'Ikon nomi', max_length=50, blank=True,
        help_text='Frontend DirectionIcon kalit: theater, education, heritage, cinema, concert'
    )
    order = models.PositiveIntegerField('Tartib', default=0)

    class Meta:
        verbose_name = "Yo'nalish"
        verbose_name_plural = "Yo'nalishlar"
        ordering = ['order', 'key']

    def __str__(self):
        return self.name_uz_latn


# ── Mukofotlar iyerarxiyasi ───────────────────────────────────────────────

class AwardAffiliation(TimestampedModel):
    """Mukofot mansubligi — eng yuqori kategoriya.

    Misol: Davlat mukofotlari, Qoraqalpog'iston Respublikasi mukofotlari, ...
    """

    key = models.SlugField('Kalit (slug)', max_length=64, unique=True)
    name_uz_latn = models.CharField('Nomi (lotin)', max_length=200)
    name_uz_cyrl = models.CharField('Nomi (krill)', max_length=200)
    name_ru = models.CharField('Название (рус)', max_length=200)
    order = models.PositiveIntegerField('Tartib', default=0)

    class Meta:
        verbose_name = "Mukofot mansubligi"
        verbose_name_plural = "Mukofot mansubliklari"
        ordering = ['order', 'key']

    def __str__(self):
        return self.name_uz_latn


class AwardType(TimestampedModel):
    """Mukofot turi — mansublik ichidagi tur (Hero, Ordenlar, Medallar, ...)."""

    affiliation = models.ForeignKey(
        AwardAffiliation, on_delete=models.CASCADE, related_name='types',
        verbose_name='Mansubligi'
    )
    key = models.SlugField('Kalit (slug)', max_length=64)
    name_uz_latn = models.CharField('Nomi (lotin)', max_length=200)
    name_uz_cyrl = models.CharField('Nomi (krill)', max_length=200)
    name_ru = models.CharField('Название (рус)', max_length=200)
    order = models.PositiveIntegerField('Tartib', default=0)

    class Meta:
        verbose_name = "Mukofot turi"
        verbose_name_plural = "Mukofot turlari"
        ordering = ['affiliation', 'order', 'key']
        constraints = [
            models.UniqueConstraint(
                fields=['affiliation', 'key'], name='unique_type_per_affiliation'
            )
        ]

    def __str__(self):
        return f'{self.affiliation.name_uz_latn} → {self.name_uz_latn}'


class AwardName(TimestampedModel):
    """Mukofot nomi — aniq mukofot (Mustaqillik ordeni, Amir Temur, ...)."""

    type = models.ForeignKey(
        AwardType, on_delete=models.CASCADE, related_name='names',
        verbose_name='Turi'
    )
    key = models.SlugField('Kalit (slug)', max_length=128)
    name_uz_latn = models.CharField('Nomi (lotin)', max_length=300)
    name_uz_cyrl = models.CharField('Nomi (krill)', max_length=300)
    name_ru = models.CharField('Название (рус)', max_length=300)
    order = models.PositiveIntegerField('Tartib', default=0)

    class Meta:
        verbose_name = "Mukofot nomi"
        verbose_name_plural = "Mukofot nomlari"
        ordering = ['type', 'order', 'key']
        constraints = [
            models.UniqueConstraint(
                fields=['type', 'key'], name='unique_name_per_type'
            )
        ]

    def __str__(self):
        return self.name_uz_latn

    @property
    def affiliation(self):
        return self.type.affiliation


# ── Vakillar ──────────────────────────────────────────────────────────────

class Representative(TimestampedModel):
    """Madaniyat sohasi vakili (sanat arbobi, ijodkor)."""

    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_CHOICES = [
        (GENDER_MALE, 'Erkak'),
        (GENDER_FEMALE, 'Ayol'),
    ]

    direction = models.ForeignKey(
        Direction, on_delete=models.PROTECT,
        related_name='representatives', verbose_name="Yo'nalishi"
    )

    last_name = models.CharField('Familiyasi', max_length=100)
    first_name = models.CharField('Ismi', max_length=100)
    middle_name = models.CharField('Otasining ismi', max_length=100, blank=True)

    gender = models.CharField('Jinsi', max_length=10, choices=GENDER_CHOICES)
    nationality = models.CharField('Millati', max_length=64, blank=True)
    birth_date = models.DateField("Tug'ilgan sanasi", null=True, blank=True)

    birth_place = models.CharField("Tug'ilgan joyi", max_length=200, blank=True)
    residence_place = models.CharField(
        'Hozirgi yashash joyi', max_length=200, blank=True,
        help_text='Xaritada marker shu manzilga qo\'yiladi'
    )

    photo = models.ImageField(
        'Surati', upload_to='representatives/', null=True, blank=True
    )

    # ── Oilasi haqida ──────────────────────────────────────────────────
    marital_status = models.CharField(
        'Oilaviy va ijtimoiy ahvoli', max_length=300, blank=True,
        help_text="Masalan: \"Oilali, 2 nafar farzandi bor\""
    )

    # ── Ma'lumoti (ta'lim) ─────────────────────────────────────────────
    university = models.CharField(
        'Tamomlagan OTM', max_length=300, blank=True,
        help_text="Masalan: \"1971 y. Toshkent teatr instituti (kunduzgi)\""
    )
    specialty = models.CharField(
        'Mutaxassisligi', max_length=300, blank=True
    )
    academic_degree = models.CharField(
        'Ilmiy darajasi (unvoni)', max_length=200, blank=True,
        help_text="Masalan: \"san'atshunoslik fanlari nomzodi\" yoki \"Yo'q\""
    )
    languages = models.CharField(
        'Chet tillarni bilishi', max_length=200, blank=True
    )
    training = models.CharField(
        "Malaka oshirganligi (so'nggi 2 yilda)", max_length=300, blank=True
    )

    # ── Mehnat faoliyati ──────────────────────────────────────────────
    position = models.CharField('Egallab turgan lavozimi', max_length=300, blank=True)
    career_level = models.CharField(
        'Martaba darajasi', max_length=100, blank=True
    )
    total_experience = models.CharField(
        'Umumiy mehnat staji', max_length=50, blank=True,
        help_text="Masalan: \"33 yil\""
    )
    leadership_experience = models.CharField(
        'Rahbarlik staji', max_length=50, blank=True,
        help_text="Masalan: \"6 yil\" yoki \"Yo'q\""
    )
    leadership_positions = models.TextField(
        'Faoliyat yuritgan rahbarlik lavozimlari', blank=True
    )

    # ── Sog'ligi ───────────────────────────────────────────────────────
    HEALTH_GOOD = 'good'
    HEALTH_AVERAGE = 'average'
    HEALTH_POOR = 'poor'
    HEALTH_DECEASED = 'deceased'
    HEALTH_CHOICES = [
        (HEALTH_GOOD, 'Yaxshi'),
        (HEALTH_AVERAGE, "O'rtacha"),
        (HEALTH_POOR, 'Qoniqarsiz'),
        (HEALTH_DECEASED, 'Vafot etgan'),
    ]

    health = models.CharField(
        "Sog'lig'i", max_length=20, choices=HEALTH_CHOICES, blank=True
    )
    last_medical_treatment = models.CharField(
        'Qachon tibbiy muolaja olgan', max_length=300, blank=True
    )
    medical_checkup = models.CharField(
        "Tibbiy ko'rikdan o'tganligi (so'nggi 2 yilda)", max_length=200, blank=True
    )
    health_problems = models.TextField(
        "Sog'ligidagi muammolar", blank=True
    )

    # ── Faoliyati ──────────────────────────────────────────────────────
    description = models.TextField(
        'Mehnat faoliyati haqida qisqacha tavsifnoma', blank=True
    )
    state_events = models.TextField(
        'Davlat tadbirlaridagi ishtiroki', blank=True
    )

    # ── Mukofotlar bog'lanishi ────────────────────────────────────────
    awards = models.ManyToManyField(
        AwardName, through='RepresentativeAward', blank=True,
        related_name='holders', verbose_name='Mukofotlari'
    )

    is_active = models.BooleanField(
        'Faol', default=True,
        help_text="Olib tashlangan bo'lsa ham, ma'lumotlar saqlanadi"
    )

    class Meta:
        verbose_name = 'Vakil'
        verbose_name_plural = 'Vakillar'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['direction', 'is_active']),
            models.Index(fields=['gender']),
        ]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return ' '.join(p for p in [self.last_name, self.first_name, self.middle_name] if p)


class FamilyMember(TimestampedModel):
    """Vakilning oila a'zosi (otasi/onasi/turmush o'rtog'i/farzandi)."""

    RELATION_FATHER = 'father'
    RELATION_MOTHER = 'mother'
    RELATION_SPOUSE = 'spouse'
    RELATION_CHILD = 'child'
    RELATION_OTHER = 'other'
    RELATION_CHOICES = [
        (RELATION_FATHER, 'Otasi'),
        (RELATION_MOTHER, 'Onasi'),
        (RELATION_SPOUSE, "Turmush o'rtog'i"),
        (RELATION_CHILD, 'Farzandi'),
        (RELATION_OTHER, 'Boshqa'),
    ]

    representative = models.ForeignKey(
        'Representative', on_delete=models.CASCADE,
        related_name='family_members', verbose_name='Vakil'
    )
    relation = models.CharField(
        "Qarindoshlik darajasi", max_length=20, choices=RELATION_CHOICES
    )
    name = models.CharField('Ism sharifi', max_length=200)
    info = models.CharField(
        "Tug'ilgan yili va joyi", max_length=200, blank=True,
        help_text="Masalan: \"1910 yil, Toshkent shahri\""
    )
    note = models.CharField(
        'Qo\'shimcha izoh', max_length=300, blank=True,
        help_text="Masalan: \"Uy bekasi\" yoki \"1946 yil vafot etgan\""
    )
    order = models.PositiveIntegerField('Tartib', default=0)

    class Meta:
        verbose_name = "Oila a'zosi"
        verbose_name_plural = "Oila a'zolari"
        ordering = ('representative', 'order', 'id')

    def __str__(self):
        return f'{self.get_relation_display()} — {self.name}'


class RepresentativeAward(TimestampedModel):
    """Vakil ↔ Mukofot bog'lanishi (yil bilan)."""

    representative = models.ForeignKey(
        Representative, on_delete=models.CASCADE,
        related_name='representative_awards', verbose_name='Vakil'
    )
    award = models.ForeignKey(
        AwardName, on_delete=models.PROTECT,
        related_name='representative_awards', verbose_name='Mukofot'
    )
    year = models.PositiveIntegerField('Yili', null=True, blank=True)

    class Meta:
        verbose_name = 'Vakil mukofoti'
        verbose_name_plural = 'Vakil mukofotlari'
        ordering = ['-year']

    def __str__(self):
        y = self.year or '—'
        return f'{self.representative.full_name} — {self.award} ({y})'
