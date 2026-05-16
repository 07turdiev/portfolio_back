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

    position = models.CharField('Egallab turgan lavozimi', max_length=300, blank=True)

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
