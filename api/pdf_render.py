"""Portfolio uchun PDF generatsiya (WeasyPrint + Jinja2).

Frontend modal dizayniga yaqin chiqadigan vector PDF yaratadi.
"""
from typing import Any

from django.conf import settings
from jinja2 import Template

from core.models import Representative


# ─── UI labellar (3 til) ─────────────────────────────────────────────────

LABELS: dict[str, dict[str, str]] = {
    'uz_latn': {
        'title': 'PORTFOLIO',
        'personal': "SHAXSIY MA'LUMOTLAR",
        'lastName': 'Familiyasi',
        'firstName': 'Ismi',
        'middleName': 'Otasining ismi',
        'nationality': 'Millati',
        'birthDate': "Tug'ilgan sanasi",
        'birthPlace': "Tug'ilgan joyi",
        'residence': 'Hozirgi yashash joyi',
        'familyInfo': "Oilasi haqida ma'lumotlar",
        'maritalStatus': 'Oilaviy va ijtimoiy ahvoli',
        'familyMembers': "Oila a'zolari",
        'father': 'Otasi',
        'mother': 'Onasi',
        'spouse': "Turmush o'rtog'i",
        'child': 'Farzandi',
        'other': 'Boshqa',
        'education': "MA'LUMOTI",
        'university': 'Tamomlagan OTM',
        'specialty': 'Mutaxassisligi',
        'academicDegree': 'Ilmiy daraja (unvon)',
        'languages': 'Chet tillarni bilishi',
        'training': "Malaka oshirganligi (so'nggi 2 yilda)",
        'work': 'MEHNAT FAOLIYATI',
        'position': 'Egallab turgan lavozimi',
        'careerLevel': 'Martaba darajasi',
        'totalExperience': 'Umumiy mehnat staji',
        'leadershipExperience': 'Rahbarlik staji',
        'leadershipPositions': 'Faoliyat yuritgan rahbarlik lavozimlari',
        'health': "Sog'lig'i",
        'lastMedicalTreatment': 'Qachon tibbiy muolaja olgan',
        'medicalCheckup': "Tibbiy ko'rikdan o'tganligi",
        'healthProblems': "Sog'ligidagi muammolar",
        'achievements': 'MEHNAT FAOLIYATIDAGI YUTUQLAR',
        'description': 'MEHNAT FAOLIYATI HAQIDA QISQACHA TAVSIFNOMA',
        'stateEvents': "DAVLAT TADBIRLARIDAGI ISHTIROKI",
    },
    'uz_cyrl': {
        'title': 'ПОРТФОЛИО',
        'personal': 'ШАХСИЙ МАЪЛУМОТЛАР',
        'lastName': 'Фамилияси',
        'firstName': 'Исми',
        'middleName': 'Отасининг исми',
        'nationality': 'Миллати',
        'birthDate': 'Туғилган санаси',
        'birthPlace': 'Туғилган жойи',
        'residence': 'Ҳозирги яшаш жойи',
        'familyInfo': 'Оиласи ҳақида маълумотлар',
        'maritalStatus': 'Оилавий ва ижтимоий аҳволи',
        'familyMembers': 'Оила аъзолари',
        'father': 'Отаси',
        'mother': 'Онаси',
        'spouse': 'Турмуш ўртоғи',
        'child': 'Фарзанди',
        'other': 'Бошқа',
        'education': 'МАЪЛУМОТИ',
        'university': 'Тамомлаган ОТМ',
        'specialty': 'Мутахассислиги',
        'academicDegree': 'Илмий даража (унвон)',
        'languages': 'Чет тилларни билиши',
        'training': 'Малака оширганлиги (сўнгги 2 йилда)',
        'work': 'МЕҲНАТ ФАОЛИЯТИ',
        'position': 'Эгаллаб турган лавозими',
        'careerLevel': 'Мартаба даражаси',
        'totalExperience': 'Умумий меҳнат стажи',
        'leadershipExperience': 'Раҳбарлик стажи',
        'leadershipPositions': 'Фаолият юритган раҳбарлик лавозимлари',
        'health': 'Соғлиги',
        'lastMedicalTreatment': 'Қачон тиббий муолажа олган',
        'medicalCheckup': 'Тиббий кўрикдан ўтганлиги',
        'healthProblems': 'Соғлигидаги муаммолар',
        'achievements': 'МЕҲНАТ ФАОЛИЯТИДАГИ ЮТУҚЛАР',
        'description': 'МЕҲНАТ ФАОЛИЯТИ ҲАҚИДА ҚИСҚАЧА ТАВСИФНОМА',
        'stateEvents': 'ДАВЛАТ ТАДБИРЛАРИДАГИ ИШТИРОКИ',
    },
    'ru': {
        'title': 'ПОРТФОЛИО',
        'personal': 'ЛИЧНЫЕ ДАННЫЕ',
        'lastName': 'Фамилия',
        'firstName': 'Имя',
        'middleName': 'Отчество',
        'nationality': 'Национальность',
        'birthDate': 'Дата рождения',
        'birthPlace': 'Место рождения',
        'residence': 'Место проживания',
        'familyInfo': 'Сведения о семье',
        'maritalStatus': 'Семейное и социальное положение',
        'familyMembers': 'Члены семьи',
        'father': 'Отец',
        'mother': 'Мать',
        'spouse': 'Супруг(а)',
        'child': 'Ребёнок',
        'other': 'Другое',
        'education': 'ОБРАЗОВАНИЕ',
        'university': 'Оконченный вуз',
        'specialty': 'Специальность',
        'academicDegree': 'Учёная степень (звание)',
        'languages': 'Знание иностранных языков',
        'training': 'Повышение квалификации (за последние 2 года)',
        'work': 'ТРУДОВАЯ ДЕЯТЕЛЬНОСТЬ',
        'position': 'Занимаемая должность',
        'careerLevel': 'Карьерный уровень',
        'totalExperience': 'Общий трудовой стаж',
        'leadershipExperience': 'Руководящий стаж',
        'leadershipPositions': 'Руководящие должности',
        'health': 'Здоровье',
        'lastMedicalTreatment': 'Когда проходил лечение',
        'medicalCheckup': 'Прохождение медосмотра',
        'healthProblems': 'Проблемы со здоровьем',
        'achievements': 'ДОСТИЖЕНИЯ В ТРУДОВОЙ ДЕЯТЕЛЬНОСТИ',
        'description': 'КРАТКАЯ ХАРАКТЕРИСТИКА ТРУДОВОЙ ДЕЯТЕЛЬНОСТИ',
        'stateEvents': 'УЧАСТИЕ В ГОСУДАРСТВЕННЫХ МЕРОПРИЯТИЯХ',
    },
}


# Yo'nalish nomlari (frontend directions.* dan)
DIRECTIONS: dict[str, dict[str, str]] = {
    'uz_latn': {
        'theater_circus': 'TEATR VA SIRK SOHASI VAKILLARI',
        'education': "TA'LIM SOHASI VAKILLARI",
        'heritage': 'NOMODDIY MADANIY MEROS SOHASI VAKILLARI',
        'cinema': 'KINO SOHASI VAKILLARI',
        'concert': 'KONSERT-TOMOSHA SOHASI VAKILLARI',
    },
    'uz_cyrl': {
        'theater_circus': 'ТЕАТР ВА СИРК СОҲАСИ ВАКИЛЛАРИ',
        'education': 'ТАЪЛИМ СОҲАСИ ВАКИЛЛАРИ',
        'heritage': 'НОМОДДИЙ МАДАНИЙ МЕРОС СОҲАСИ ВАКИЛЛАРИ',
        'cinema': 'КИНО СОҲАСИ ВАКИЛЛАРИ',
        'concert': 'КОНЦЕРТ-ТОМОША СОҲАСИ ВАКИЛЛАРИ',
    },
    'ru': {
        'theater_circus': 'ПРЕДСТАВИТЕЛИ СФЕРЫ ТЕАТРА И ЦИРКА',
        'education': 'ПРЕДСТАВИТЕЛИ СФЕРЫ ОБРАЗОВАНИЯ',
        'heritage': 'ПРЕДСТАВИТЕЛИ СФЕРЫ НЕМАТЕРИАЛЬНОГО КУЛЬТУРНОГО НАСЛЕДИЯ',
        'cinema': 'ПРЕДСТАВИТЕЛИ СФЕРЫ КИНО',
        'concert': 'ПРЕДСТАВИТЕЛИ КОНЦЕРТНО-ЗРЕЛИЩНОЙ СФЕРЫ',
    },
}


# Sog'lig'i ranglari (key → (bg, border, text))
HEALTH_COLORS = {
    'good':     ('#ecfdf5', '#16a34a', '#166534'),
    'average':  ('#fefce8', '#ca8a04', '#854d0e'),
    'poor':     ('#fef2f2', '#dc2626', '#991b1b'),
    'deceased': ('#f3f4f6', '#6b7280', '#374151'),
}


# ─── HTML shablon ────────────────────────────────────────────────────────

TEMPLATE_SRC = r"""<!DOCTYPE html>
<html lang="{{ html_lang }}">
<head>
<meta charset="UTF-8">
<title>{{ full_name }}</title>
<style>
  @page {
    size: A4 landscape;
    margin: 5mm;
  }

  * { box-sizing: border-box; }

  html, body {
    margin: 0;
    padding: 0;
    font-family: "Public Sans", "Segoe UI", Tahoma, sans-serif;
    color: #172b4d;
    font-size: 7.5pt;
    line-height: 1.35;
    background: white;
  }

  .root {
    {% if deceased %}filter: grayscale(100%);{% endif %}
  }

  /* ─── Hero ─────────────────────────────────────────────── */
  .hero {
    background: linear-gradient(to right, #1e325c 0%, #4775ff 100%);
    color: white;
    padding: 3mm 6mm;
    border-radius: 2mm 2mm 0 0;
  }
  .hero-label {
    font-size: 6pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3em;
    color: rgba(255,255,255,0.65);
  }
  .hero-name {
    font-size: 13pt;
    font-weight: 700;
    margin: 0.5mm 0 1mm 0;
    line-height: 1.2;
  }
  .deceased-tag {
    font-weight: 400;
    color: rgba(255,255,255,0.82);
    font-size: 0.7em;
  }
  .hero-meta {
    font-size: 8pt;
    color: rgba(255,255,255,0.92);
    line-height: 1.3;
  }
  .hero-meta > span { margin-right: 4mm; }
  .hero-position {
    background: rgba(255,255,255,0.16);
    padding: 0.3mm 2.5mm;
    border-radius: 99px;
    font-size: 7pt;
    font-weight: 500;
    display: inline-block;
  }

  /* ─── 3-ustun: TABLE layout (WeasyPrint uchun ishonchli) */
  .grid {
    width: 100%;
    border-collapse: collapse;
    margin-top: 3mm;
    table-layout: fixed;
  }
  .grid > tbody > tr > td {
    vertical-align: top;
    width: 33.33%;
    padding: 0 1.5mm;
  }
  .grid > tbody > tr > td:first-child { padding-left: 0; }
  .grid > tbody > tr > td:last-child  { padding-right: 0; }

  /* ─── Bo'lim kartochkasi ───────────────────────────────── */
  .section {
    border: 0.25mm solid #e5e7eb;
    border-radius: 1.5mm;
    margin-bottom: 3mm;
  }
  .section-header {
    padding: 1.5mm 3mm;
    border-left-width: 0.8mm;
    border-left-style: solid;
    border-top-left-radius: 1.5mm;
    border-top-right-radius: 1.5mm;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 7pt;
  }
  .sh-blue   { background: #eef3f9; border-left-color: #5b87b3; color: #3f6286; }
  .sh-green  { background: #eef3e9; border-left-color: #7d9b6e; color: #536b46; }
  .sh-orange { background: #fbefe4; border-left-color: #e0935f; color: #a8602f; }
  .sh-amber  { background: #fef3e2; border-left-color: #c98135; color: #8b5a25; }

  /* ─── Shaxsiy ma'lumotlar (rasm + qatorlar) ──────────── */
  .personal-body {
    padding: 3mm;
  }
  .photo-row {
    display: table;
    width: 100%;
  }
  .photo-cell {
    display: table-cell;
    width: 22mm;
    vertical-align: top;
    padding-right: 3mm;
  }
  .photo {
    width: 22mm;
    height: 29mm;
    object-fit: cover;
    border: 0.25mm solid #e5e7eb;
    border-radius: 1mm;
    background: #f3f4f6;
    display: block;
  }
  .rows-wrap {
    display: table-cell;
    vertical-align: top;
  }
  .row {
    display: table;
    width: 100%;
    padding: 0.6mm 0;
    border-bottom: 0.2mm solid #f3f4f6;
    font-size: 7.5pt;
  }
  .row:last-child { border-bottom: none; }
  .row .label {
    display: table-cell;
    width: 38%;
    color: #6b778c;
    padding-right: 1.5mm;
  }
  .row .value {
    display: table-cell;
    width: 62%;
    color: #1e325c;
    font-weight: 500;
  }
  .place-rows { margin-top: 0.5mm; }

  /* ─── Ta'lim / Mehnat qatorlari ──────────────────────── */
  .rows-section {
    padding: 1.5mm 3mm;
  }
  .rows-section .row {
    padding: 0.8mm 0;
  }

  /* ─── Oilasi haqida ──────────────────────────────────── */
  .family-info-body {
    padding: 2mm 3mm;
    font-size: 7.5pt;
  }
  .fi-label {
    color: #6b778c;
    margin-bottom: 0.5mm;
  }
  .fi-value {
    color: #1e325c;
    font-weight: 500;
  }

  /* ─── Oila a'zolari ──────────────────────────────────── */
  .family-member {
    padding: 1.5mm 3mm;
    border-bottom: 0.2mm solid #f3f4f6;
    font-size: 7.5pt;
  }
  .family-member:last-child { border-bottom: none; }
  .fm-relation {
    color: #6b778c;
    font-size: 6.5pt;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.3mm;
  }
  .fm-name {
    color: #1e325c;
    font-weight: 500;
  }
  .fm-info {
    color: #6b778c;
    font-size: 7pt;
  }

  /* ─── Mukofotlar ─────────────────────────────────────── */
  .achievements {
    padding: 1.5mm 3mm;
  }
  .ach-item {
    display: table;
    width: 100%;
    padding: 1mm 0;
    border-bottom: 0.2mm solid #f3f4f6;
  }
  .ach-item:last-child { border-bottom: none; }
  .ach-year {
    display: table-cell;
    width: 11mm;
    vertical-align: top;
    background: #eef3e9;
    color: #536b46;
    font-size: 6.5pt;
    font-weight: 700;
    padding: 0.8mm 1.5mm;
    border-radius: 1mm;
    text-align: center;
    line-height: 1.1;
  }
  .ach-spacer {
    display: table-cell;
    width: 2mm;
  }
  .ach-title {
    display: table-cell;
    vertical-align: top;
    font-size: 7.5pt;
    color: #1e325c;
    line-height: 1.35;
  }

  /* ─── Erkin matn (tavsifnoma, davlat tadbirlari) ────── */
  .free-text {
    padding: 2mm 3mm;
    font-size: 7pt;
    color: #172b4d;
    line-height: 1.4;
    text-align: justify;
    word-wrap: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
  }
</style>
</head>
<body>
<div class="root">

  <!-- Hero -->
  <div class="hero">
    <div class="hero-label">{{ L.title }}</div>
    <div class="hero-name">
      {{ full_name }}{% if deceased and health_text %} <span class="deceased-tag">— {{ health_text }}</span>{% endif %}
    </div>
    <div class="hero-meta">
      <span>{{ direction_name }}</span>
      {% if region_name %}<span>{{ region_name }}{% if district_name %}, {{ district_name }}{% endif %}</span>{% endif %}
      {% if position %}<span class="hero-position">{{ position }}</span>{% endif %}
    </div>
  </div>

  <!-- 3-ustun layout: TABLE (WeasyPrint flex'dan ko'ra ishonchli) -->
  <table class="grid">
    <tr>

      <!-- ─── Ustun 1 ─────────────────────────────── -->
      <td>

        <div class="section">
          <div class="section-header sh-blue">{{ L.personal }}</div>
          <div class="personal-body">
            <div class="photo-row">
              <div class="photo-cell">
                {% if photo_path %}<img class="photo" src="{{ photo_path }}" />
                {% else %}<div class="photo"></div>{% endif %}
              </div>
              <div class="rows-wrap">
                {% for r in personal_rows %}
                <div class="row">
                  <div class="label">{{ r.l }}</div>
                  <div class="value">{{ r.v }}</div>
                </div>
                {% endfor %}
              </div>
            </div>
            {% if place_rows %}
            <div class="place-rows">
              {% for r in place_rows %}
              <div class="row">
                <div class="label">{{ r.l }}</div>
                <div class="value">{{ r.v }}</div>
              </div>
              {% endfor %}
            </div>
            {% endif %}
          </div>
        </div>

        {% if marital_status %}
        <div class="section">
          <div class="section-header sh-blue">{{ L.familyInfo }}</div>
          <div class="family-info-body">
            <div class="fi-label">{{ L.maritalStatus }}</div>
            <div class="fi-value">{{ marital_status }}</div>
          </div>
        </div>
        {% endif %}

        {% if family_members %}
        <div class="section">
          <div class="section-header sh-blue">{{ L.familyMembers }}</div>
          {% for m in family_members %}
          <div class="family-member">
            <div class="fm-relation">{{ L.get(m.relation, m.relation) }}</div>
            {% if m.name %}<div class="fm-name">{{ m.name }}</div>{% endif %}
            {% if m.info or m.note %}
            <div class="fm-info">
              {% if m.info %}{{ m.info }}{% endif %}{% if m.info and m.note %} — {% endif %}{% if m.note %}{{ m.note }}{% endif %}
            </div>
            {% endif %}
          </div>
          {% endfor %}
        </div>
        {% endif %}
      </td>

      <!-- ─── Ustun 2 ─────────────────────────────── -->
      <td>

        {% if education_rows %}
        <div class="section">
          <div class="section-header sh-green">{{ L.education }}</div>
          <div class="rows-section">
            {% for r in education_rows %}
            <div class="row">
              <div class="label">{{ r.l }}</div>
              <div class="value">{{ r.v }}</div>
            </div>
            {% endfor %}
          </div>
        </div>
        {% endif %}

        {% if work_rows %}
        <div class="section">
          <div class="section-header sh-green">{{ L.work }}</div>
          <div class="rows-section">
            {% for r in work_rows %}
            <div class="row">
              <div class="label">{{ r.l }}</div>
              <div class="value">{{ r.v }}</div>
            </div>
            {% endfor %}
          </div>
        </div>
        {% endif %}

        {% if health_text %}
        <div class="section" style="background: {{ health_bg }};">
          <div class="section-header" style="background: {{ health_bg }}; border-left-color: {{ health_border }}; color: {{ health_text_color }};">
            {{ L.health }}: {{ health_text }}
          </div>
        </div>
        {% endif %}
      </td>

      <!-- ─── Ustun 3 ─────────────────────────────── -->
      <td>

        {% if achievements %}
        <div class="section">
          <div class="section-header sh-green">{{ L.achievements }}</div>
          <div class="achievements">
            {% for a in achievements %}
            <div class="ach-item">
              <div class="ach-year">{{ a.year }}</div>
              <div class="ach-spacer"></div>
              <div class="ach-title">{{ a.title }}</div>
            </div>
            {% endfor %}
          </div>
        </div>
        {% endif %}

        {% if description %}
        <div class="section">
          <div class="section-header sh-orange">{{ L.description }}</div>
          <div class="free-text">{{ description }}</div>
        </div>
        {% endif %}

        {% if state_events %}
        <div class="section">
          <div class="section-header sh-amber">{{ L.stateEvents }}</div>
          <div class="free-text">{{ state_events }}</div>
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

</div>
</body>
</html>
"""

_TEMPLATE = Template(TEMPLATE_SRC)


# ─── Yordamchi funksiyalar ───────────────────────────────────────────────

def _tr(obj: Any, field: str, lang: str) -> str:
    """Modeltranslation maydonidan tarjima qiymatini olish."""
    value = getattr(obj, f'{field}_{lang}', None)
    if not value:
        # Fallback: uz_cyrl, then uz_latn
        value = getattr(obj, f'{field}_uz_cyrl', None)
    if not value:
        value = getattr(obj, f'{field}_uz_latn', None)
    return (value or '').strip()


def _format_date(d) -> str:
    if not d:
        return ''
    return f'{d.day:02d}.{d.month:02d}.{d.year}'


def _build_full_name(rep: Representative, lang: str) -> str:
    parts = [
        _tr(rep, 'last_name', lang),
        _tr(rep, 'first_name', lang),
        _tr(rep, 'middle_name', lang),
    ]
    return ' '.join(p for p in parts if p)


def _build_residence(rep: Representative, lang: str) -> tuple[str, str, str]:
    """(region_name, district_name, residence_full)."""
    extra = (rep.residence_place or '').strip()
    if rep.residence_district_id:
        d = rep.residence_district
        r = d.region
        region_name = _tr(r, 'name', lang)
        district_name = _tr(d, 'name', lang)
        parts = [district_name, region_name]
        if extra:
            parts.append(extra)
        return region_name, district_name, ', '.join(p for p in parts if p)
    # Chet el — qo'lda kiritilgan joy
    foreign = (rep.residence_place_foreign or '').strip()
    if foreign:
        parts = [foreign]
        if extra:
            parts.append(extra)
        return '', '', ', '.join(parts)
    return '', '', ''


def _build_birth_place(rep: Representative, lang: str) -> str:
    """Strukturali tug'ilgan joy: tuman, viloyat (yoki chet el)."""
    if rep.birth_district_id:
        d = rep.birth_district
        r = d.region
        parts = [
            _tr(d, 'name', lang),
            _tr(r, 'name', lang),
        ]
        return ', '.join(p for p in parts if p)
    return (rep.birth_place_foreign or '').strip()


def _filter_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r['v']]


# ─── Asosiy render funksiyasi ────────────────────────────────────────────

def render_portfolio_pdf(rep: Representative, lang: str = 'uz_cyrl') -> bytes:
    """Vakilning portfoliosini PDF formatida render qilish."""
    if lang not in LABELS:
        lang = 'uz_cyrl'
    L = LABELS[lang]

    # Asosiy ma'lumotlar
    full_name = _build_full_name(rep, lang)
    direction_name = DIRECTIONS[lang].get(rep.direction.key, rep.direction.key)
    region_name, district_name, residence_full = _build_residence(rep, lang)

    # Tug'ilgan joyi — strukturali (mahalla → tuman → viloyat)
    birth_place = _build_birth_place(rep, lang)

    # Personal rows (filtrlangan)
    personal_rows = _filter_rows([
        {'l': L['lastName'],   'v': _tr(rep, 'last_name', lang)},
        {'l': L['firstName'],  'v': _tr(rep, 'first_name', lang)},
        {'l': L['middleName'], 'v': _tr(rep, 'middle_name', lang)},
        {'l': L['nationality'], 'v': rep.get_nationality_display() if rep.nationality else ''},
        {'l': L['birthDate'],  'v': _format_date(rep.birth_date)},
    ])

    place_rows = _filter_rows([
        {'l': L['birthPlace'], 'v': birth_place},
        {'l': L['residence'],  'v': residence_full},
    ])

    # Ta'lim
    languages_str = ', '.join(
        lng.name for lng in rep.languages.all().order_by('order', 'name')
    )
    education_rows = _filter_rows([
        {'l': L['university'],     'v': _tr(rep, 'university', lang)},
        {'l': L['specialty'],      'v': _tr(rep, 'specialty', lang)},
        {'l': L['academicDegree'], 'v': _tr(rep, 'academic_degree', lang)},
        {'l': L['languages'],      'v': languages_str},
        {'l': L['training'],       'v': _tr(rep, 'training', lang)},
    ])

    # Mehnat
    work_rows = _filter_rows([
        {'l': L['position'],             'v': _tr(rep, 'position', lang)},
        {'l': L['careerLevel'],          'v': _tr(rep, 'career_level', lang)},
        {'l': L['totalExperience'],      'v': _tr(rep, 'total_experience', lang)},
        {'l': L['leadershipExperience'], 'v': _tr(rep, 'leadership_experience', lang)},
        {'l': L['leadershipPositions'],  'v': _tr(rep, 'leadership_positions', lang)},
        {'l': L['lastMedicalTreatment'], 'v': _tr(rep, 'last_medical_treatment', lang)},
        {'l': L['medicalCheckup'],       'v': _tr(rep, 'medical_checkup', lang)},
        {'l': L['healthProblems'],       'v': _tr(rep, 'health_problems', lang)},
    ])

    # Sog'lig'i
    health_text = rep.get_health_display() if rep.health else ''
    health_bg, health_border, health_text_color = HEALTH_COLORS.get(
        rep.health or '', ('#f9fafb', '#9ca3af', '#374151')
    )

    # Oila a'zolari
    family_members = []
    for m in rep.family_members.order_by('order', 'id'):
        family_members.append({
            'relation': m.relation,
            'name': _tr(m, 'name', lang),
            'info': _tr(m, 'info', lang),
            'note': _tr(m, 'note', lang),
        })

    # Mukofotlar
    achievements = []
    for ra in rep.representative_awards.select_related('award').order_by('-year'):
        achievements.append({
            'year': str(ra.year) if ra.year else '—',
            'title': _tr(ra.award, 'name', lang),
        })

    # Faoliyat
    description = _tr(rep, 'description', lang)
    state_events = _tr(rep, 'state_events', lang)

    # Surat (fayl yo'li)
    photo_path = ''
    if rep.photo and hasattr(rep.photo, 'path'):
        import os
        if os.path.exists(rep.photo.path):
            photo_path = 'file://' + rep.photo.path.replace('\\', '/')

    # HTML render
    html_str = _TEMPLATE.render(
        html_lang={'uz_latn': 'uz', 'uz_cyrl': 'uz', 'ru': 'ru'}[lang],
        L=L,
        full_name=full_name,
        direction_name=direction_name,
        region_name=region_name,
        district_name=district_name,
        position=_tr(rep, 'position', lang),
        deceased=(rep.health == 'deceased'),
        photo_path=photo_path,
        personal_rows=personal_rows,
        place_rows=place_rows,
        marital_status=_tr(rep, 'marital_status', lang),
        family_members=family_members,
        education_rows=education_rows,
        work_rows=work_rows,
        health_text=health_text,
        health_bg=health_bg,
        health_border=health_border,
        health_text_color=health_text_color,
        achievements=achievements,
        description=description,
        state_events=state_events,
    )

    # WeasyPrint orqali PDF generatsiya
    from weasyprint import HTML
    base_url = str(settings.BASE_DIR)
    return HTML(string=html_str, base_url=base_url).write_pdf()
