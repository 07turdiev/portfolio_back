"""Django sozlamalari — Portfolio backend."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Productionda environment variable orqali bering
SECRET_KEY = 'django-insecure-change-me-in-production-d8x2k9m4p1q3v6h7'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # modeltranslation va Jazzmin contrib.admin dan oldin bo'lishi shart
    'modeltranslation',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Loyiha
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'portfolio_back.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'portfolio_back.wsgi.application'
ASGI_APPLICATION = 'portfolio_back.asgi.application'

import os

if os.environ.get('USE_SQLITE') == '1':
    # Vaqtinchalik — eski SQLite dan dumpdata qilish uchun
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'portfolio_db',
            'USER': 'portfolio',
            'PASSWORD': '2002',
            'HOST': '127.0.0.1',
            'PORT': '5432',
            # Persistent connections — har thread/worker da 60 soniya ushlab turiladi
            'CONN_MAX_AGE': 60,
            # Django 4.1+: har request boshida `SELECT 1` bilan ulanish tirikligini
            # tekshiradi va yopilgan bo'lsa qayta ochadi. ASGI + sync_to_async muhitida
            # uzoq vaqt ishlayotgan workerlarda "the connection is closed" xatosini
            # oldini oladi.
            'CONN_HEALTH_CHECKS': True,
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz-latn'
LANGUAGES = [
    ('uz-latn', "O'zbekcha (lotin)"),
    ('uz-cyrl', 'Ўзбекча (крил)'),
    ('ru', 'Русский'),
]
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# ── modeltranslation ─────────────────────────────────────────────────────
# Field nomlari: name → name_uz_latn, name_uz_cyrl, name_ru
MODELTRANSLATION_DEFAULT_LANGUAGE = 'uz-latn'
MODELTRANSLATION_LANGUAGES = ('uz-latn', 'uz-cyrl', 'ru')
MODELTRANSLATION_FALLBACK_LANGUAGES = ('uz-latn', 'uz-cyrl', 'ru')
MODELTRANSLATION_AUTO_POPULATE = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Jazzmin admin teması ───────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    'site_title': 'Madaniyat portfolio',
    'site_header': 'Madaniyat portfolio',
    'site_brand': 'Portfolio',
    'welcome_sign': 'Boshqaruv paneliga xush kelibsiz',
    'copyright': "O'zbekiston Respublikasi Madaniyat vazirligi",
    'search_model': ['core.Representative', 'core.AwardName'],
    'language_chooser': False,
    'show_ui_builder': False,
    'custom_css': 'admin/css/jazzmin_light.css',
    'topmenu_links': [
        {'name': 'Bosh sahifa', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'name': 'API hujjatlari', 'url': '/docs', 'new_window': True},
    ],
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'auth.group': 'fas fa-users',
        'core.direction': 'fas fa-compass',
        'core.representative': 'fas fa-user-tie',
        'core.awardaffiliation': 'fas fa-landmark',
        'core.awardtype': 'fas fa-trophy',
        'core.awardname': 'fas fa-award',
        'core.region': 'fas fa-map',
        'core.district': 'fas fa-map-marked-alt',
        'core.mahalla': 'fas fa-map-pin',
    },
    'order_with_respect_to': [
        'core.representative',
        'core.direction',
        'core.awardaffiliation',
        'core.awardtype',
        'core.awardname',
        'core.region',
        'core.district',
        'core.mahalla',
        'auth',
    ],
}

JAZZMIN_UI_TWEAKS = {
    'theme': 'flatly',
    'dark_mode_theme': None,
    'navbar': 'navbar-white navbar-light',
    'sidebar': 'sidebar-light-primary',
    'brand_colour': 'navbar-white',
    'accent': 'accent-primary',
    'body_small_text': False,
    'navbar_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_small_text': False,
    'sidebar_nav_flat_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_compact_style': False,
    'no_navbar_border': True,
}
