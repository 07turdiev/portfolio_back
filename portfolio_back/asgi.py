"""Birlashtirilgan ASGI — Django (admin) + FastAPI (REST API + Swagger).

Yo'naltirish:
  /admin, /static, /media, /jsi18n   → Django
  /api, /docs, /redoc, /openapi.json → FastAPI

Ishga tushirish:
    uvicorn portfolio_back.asgi:application --reload --port 8000
"""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_back.settings')

import django  # noqa: E402

django.setup()

from django.core.asgi import get_asgi_application  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402

# Django ASGI (admin va static uchun)
django_app = get_asgi_application()

# FastAPI app (Django setup'dan keyin import qilinadi)
from api.main import app as fastapi_app  # noqa: E402


async def application(scope, receive, send):
    """Path bo'yicha Django yoki FastAPI ga yo'naltirish."""
    if scope['type'] == 'lifespan':
        # Lifespan eventlari FastAPI ga yuboriladi
        await fastapi_app(scope, receive, send)
        return

    path = scope.get('path', '')
    django_paths = ('/admin', '/static', '/media', '/jsi18n')

    if any(path.startswith(p) for p in django_paths):
        await django_app(scope, receive, send)
    else:
        await fastapi_app(scope, receive, send)
