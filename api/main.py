"""FastAPI ilovasi — Django ORM yordamida REST endpoints.

Ishga tushirish:
    uvicorn api.main:app --reload --port 8001
"""
import os

import django

# Django ni FastAPI da ishlatish uchun avval setup qilinadi
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_back.settings')
django.setup()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from .routers import awards, directions, info_cards, locations, representatives  # noqa: E402

app = FastAPI(
    title='Madaniyat portfolio API',
    description='Sanat sohasi vakillari Portfolio platformasi REST API',
    version='0.1.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://localhost:5174',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5174',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(directions.router)
app.include_router(awards.router)
app.include_router(locations.router)
app.include_router(representatives.router)
app.include_router(info_cards.router)


@app.get('/health', tags=['system'])
def health():
    return {'status': 'ok'}
