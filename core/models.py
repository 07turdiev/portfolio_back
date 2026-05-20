"""Portfolio backend modellari.

Iyerarxiya:
    Direction (yo'nalish) — Vakil shu yo'nalishga tegishli.

    AwardAffiliation (mansublik: davlat, viloyat, vazirlik, ...)
        └── AwardType (turi: hero, faxriy unvonlar, ordenlar, medallar, ...)
                └── AwardName (mukofotning aniq nomi)

    Representative (vakil) — bitta Direction, ko'p AwardName (through model bilan)
"""
from django.core.validators import FileExtensionValidator
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
    name = models.CharField('Nomi', max_length=200)
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
        return self.name


# ── Mukofotlar iyerarxiyasi ───────────────────────────────────────────────

class AwardAffiliation(TimestampedModel):
    """Mukofot mansubligi — eng yuqori kategoriya.

    Misol: Davlat mukofotlari, Qoraqalpog'iston Respublikasi mukofotlari, ...
    """

    key = models.SlugField('Kalit (slug)', max_length=64, unique=True)
    name = models.CharField('Nomi', max_length=200)
    order = models.PositiveIntegerField('Tartib', default=0)

    class Meta:
        verbose_name = "Mukofot mansubligi"
        verbose_name_plural = "Mukofot mansubliklari"
        ordering = ['order', 'key']

    def __str__(self):
        return self.name


class AwardType(TimestampedModel):
    """Mukofot turi — mansublik ichidagi tur (Hero, Ordenlar, Medallar, ...)."""

    affiliation = models.ForeignKey(
        AwardAffiliation, on_delete=models.CASCADE, related_name='types',
        verbose_name='Mansubligi'
    )
    key = models.SlugField('Kalit (slug)', max_length=64)
    name = models.CharField('Nomi', max_length=200)
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
        return f'{self.affiliation.name} → {self.name}'


class AwardName(TimestampedModel):
    """Mukofot nomi — aniq mukofot (Mustaqillik ordeni, Amir Temur, ...)."""

    type = models.ForeignKey(
        AwardType, on_delete=models.CASCADE, related_name='names',
        verbose_name='Turi'
    )
    key = models.SlugField('Kalit (slug)', max_length=128)
    name = models.CharField('Nomi', max_length=300)
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
        return self.name

    @property
    def affiliation(self):
        return self.type.affiliation


# ── Hududiy bo'linish (Viloyat → Tuman → Mahalla) ─────────────────────────

class Region(TimestampedModel):
    """Viloyat (yoki shahar). SOATO kodi PrimaryKey sifatida."""

    soato = models.CharField(
        'SOATO kodi', max_length=10, primary_key=True,
        help_text='Masalan: 1703 (Andijon), 1726 (Toshkent shahri)'
    )
    slug = models.SlugField(
        'Slug (frontend xarita kaliti)', max_length=64, blank=True,
        help_text="Frontend SVG xaritasi uchun, masalan: 'andijon', 'toshkent-shahri'"
    )
    name_uz_latn = models.CharField("Nomi (uz-latn)", max_length=150)
    name_uz_cyrl = models.CharField("Nomi (uz-cyrl)", max_length=150, blank=True)
    name_ru = models.CharField("Nomi (ru)", max_length=150, blank=True)

    class Meta:
        verbose_name = 'Viloyat'
        verbose_name_plural = 'Viloyatlar'
        ordering = ('name_uz_latn',)

    def __str__(self):
        return self.name_uz_latn


class District(TimestampedModel):
    """Tuman/shahar. SOATO kodi PrimaryKey."""

    soato = models.CharField('SOATO kodi', max_length=10, primary_key=True)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE,
        related_name='districts', verbose_name='Viloyati'
    )
    slug = models.SlugField('Slug', max_length=64, blank=True)
    name_uz_latn = models.CharField("Nomi (uz-latn)", max_length=200)
    name_uz_cyrl = models.CharField("Nomi (uz-cyrl)", max_length=200, blank=True)
    name_ru = models.CharField("Nomi (ru)", max_length=200, blank=True)
    lat = models.FloatField('Centroid kenglik (lat)', null=True, blank=True)
    lng = models.FloatField('Centroid uzunlik (lng)', null=True, blank=True)

    class Meta:
        verbose_name = 'Tuman'
        verbose_name_plural = 'Tumanlar'
        ordering = ('region', 'name_uz_latn')
        indexes = [models.Index(fields=['region'])]

    def __str__(self):
        return f'{self.name_uz_latn} ({self.region.name_uz_latn})'


class Mahalla(TimestampedModel):
    """Mahalla. TIN kodi PrimaryKey."""

    tin = models.CharField('TIN kodi', max_length=20, primary_key=True)
    district = models.ForeignKey(
        District, on_delete=models.CASCADE,
        related_name='mahallas', verbose_name='Tumani'
    )
    code = models.CharField('Mahalla kodi', max_length=20, blank=True)
    name_uz_latn = models.CharField("Nomi (uz-latn)", max_length=200)
    name_uz_cyrl = models.CharField("Nomi (uz-cyrl)", max_length=200, blank=True)
    name_ru = models.CharField("Nomi (ru)", max_length=200, blank=True)
    name_en = models.CharField("Nomi (en)", max_length=200, blank=True)

    class Meta:
        verbose_name = 'Mahalla'
        verbose_name_plural = 'Mahallalar'
        ordering = ('district', 'name_uz_latn')
        indexes = [models.Index(fields=['district'])]

    def __str__(self):
        return f'{self.name_uz_latn} — {self.district.name_uz_latn}'


# ── Tillar (vakil bilgan tillar) ──────────────────────────────────────────

class Language(TimestampedModel):
    """Til — vakil bilishi mumkin bo'lgan til."""

    code = models.SlugField('Kod', max_length=30, unique=True)
    name = models.CharField('Nomi', max_length=100)
    order = models.PositiveIntegerField('Tartib', default=100)

    class Meta:
        verbose_name = 'Til'
        verbose_name_plural = 'Tillar'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name


# ── Vakillar ──────────────────────────────────────────────────────────────

class Representative(TimestampedModel):
    """Madaniyat sohasi vakili (sanat arbobi, ijodkor)."""

    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_CHOICES = [
        (GENDER_MALE, 'Erkak'),
        (GENDER_FEMALE, 'Ayol'),
    ]

    # ── Millati (eng kerakli millatlar yuqorida) ──────────────────────
    NATIONALITY_CHOICES = [
        ('ozbek', "O'zbek"),
        ('qozoq', 'Qozoq'),
        ('tojik', 'Tojik'),
        ('rus', 'Rus'),
        ('qoraqalpoq', 'Qoraqalpoq'),
        ('qirgiz', "Qirg'iz"),
        ('turkman', 'Turkman'),
        ('tatar', 'Tatar'),
        ('koreys', 'Koreys'),
        ('uygur', "Uyg'ur"),
        ('ukrain', 'Ukrain'),
        ('belorus', 'Belorus'),
        ('armani', 'Armani'),
        ('ozarbayjon', 'Ozarbayjon'),
        ('yahudiy', 'Yahudiy'),
        ('bashqird', 'Bashqird'),
        ('chuvash', 'Chuvash'),
        ('lazgin', 'Lazgin'),
        ('dungan', 'Dungan'),
        ('turk', 'Turk'),
        ('arab', 'Arab'),
        ('eron', 'Eron'),
        ('afgon', "Afg'on"),
        ('hind', 'Hind'),
        ('boshqa', 'Boshqa'),
    ]

    direction = models.ForeignKey(
        Direction, on_delete=models.PROTECT,
        related_name='representatives', verbose_name="Yo'nalishi"
    )

    last_name = models.CharField('Familiyasi', max_length=100)
    first_name = models.CharField('Ismi', max_length=100)
    middle_name = models.CharField('Otasining ismi', max_length=100, blank=True)

    gender = models.CharField('Jinsi', max_length=10, choices=GENDER_CHOICES)
    nationality = models.CharField(
        'Millati', max_length=30, choices=NATIONALITY_CHOICES, blank=True
    )
    birth_date = models.DateField("Tug'ilgan sanasi", null=True, blank=True)

    birth_place = models.CharField("Tug'ilgan joyi", max_length=200, blank=True)

    residence_mahalla = models.ForeignKey(
        Mahalla, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='residents', verbose_name='Hozirgi yashash joyi (mahalla)',
        help_text='Viloyat → tuman → mahalla tanlanadi. Xaritada marker shu tumanga qo\'yiladi.'
    )
    residence_place = models.CharField(
        "Yashash manzili (qo'shimcha)", max_length=200, blank=True,
        help_text="Mahalladan tashqari aniqlashtirish: ko'cha, uy raqami"
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
    languages = models.ManyToManyField(
        Language, blank=True, related_name='speakers',
        verbose_name='Chet tillarni bilishi'
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


# ── Sahifa pastidagi info kartochkalari (Saylovchilar/Partiyalar uchun va h.k.) ─

class InfoCard(TimestampedModel):
    """Asosiy sahifa pastida ko'rsatiladigan info kartochkalari.

    Misol: \"Siyosiy partiyalar uchun\", \"Nomzodlar uchun\" va h.k.
    Kartochkani bosganda pop-up ochiladi va to'liq matn ko'rsatiladi.
    """

    title = models.CharField(
        'Sarlavha', max_length=200,
        help_text="Masalan: \"Siyosiy partiyalar uchun\""
    )
    icon = models.FileField(
        'Ikon (SVG, PNG, JPG)', upload_to='info_cards/icons/',
        validators=[FileExtensionValidator(
            allowed_extensions=['svg', 'png', 'jpg', 'jpeg', 'webp']
        )],
        help_text="SVG (tavsiya etiladi) yoki PNG. Taxminan 64x64 px"
    )
    body = models.TextField(
        'Matni',
        help_text="Pop-up oynada ko'rsatiladigan to'liq matn"
    )
    order = models.PositiveIntegerField(
        'Tartib', default=0,
        help_text="Kichik raqam birinchi ko'rinadi"
    )
    is_active = models.BooleanField('Faol', default=True)

    class Meta:
        verbose_name = 'Info kartochka'
        verbose_name_plural = 'Info kartochkalar'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title
