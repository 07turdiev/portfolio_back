# Portfolio Backend — Madaniyat vazirligi

Sanat sohasi vakillari Portfolio platformasi uchun backend.

**Stack:**
- **Django** — ORM, model boshqaruvi, autentifikatsiya
- **Jazzmin** — chiroyli admin paneli
- **FastAPI** — REST API (Django ORM bilan ishlatadi, alohida processda)

## O'rnatish

```bash
# Virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# Paketlar
pip install -r requirements.txt

# Database
python manage.py makemigrations core
python manage.py migrate

# Admin foydalanuvchi
python manage.py createsuperuser
```

## Ishga tushirish

**Django admin** (porti 8000):
```bash
python manage.py runserver
```
→ http://localhost:8000/admin/

**FastAPI** (porti 8001):
```bash
uvicorn api.main:app --reload --port 8001
```
→ http://localhost:8001/docs (Swagger UI)
→ http://localhost:8001/redoc

Ikkala server bir vaqtda ishlashi mumkin (alohida terminallarda).

## Loyiha tuzilmasi

```
portfolio_back/
├── manage.py                   Django boshqaruv skripti
├── requirements.txt
├── db.sqlite3                  SQLite (.gitignore'da)
│
├── portfolio_back/             Django loyiha sozlamalari
│   ├── settings.py             Jazzmin + DB + sozlamalar
│   ├── urls.py                 /admin/, /media/
│   └── wsgi.py, asgi.py
│
├── core/                       Asosiy app — modellar va admin
│   ├── models.py               Direction, AwardAffiliation,
│   │                           AwardType, AwardName, Representative,
│   │                           RepresentativeAward
│   ├── admin.py                Jazzmin admin (inlines, autocomplete)
│   └── migrations/
│
└── api/                        FastAPI REST API
    ├── main.py                 FastAPI ilova + CORS
    └── routers/
        ├── directions.py       GET /api/directions
        ├── awards.py           GET /api/award-taxonomy
        └── representatives.py  GET /api/people, /api/people/{id}
```

## Model iyerarxiyasi

```
Direction (yo'nalish)
    └─ has many ─► Representative (vakil)

AwardAffiliation (mukofot mansubligi)
    └─ has many ─► AwardType (mukofot turi)
                       └─ has many ─► AwardName (mukofot nomi)
                                          └─ M2M ─► Representative
                                                    (RepresentativeAward + yili)
```

## Boshlang'ich ma'lumotlarni to'ldirish

Admin paneli orqali kiritish tartibi:

1. **Yo'nalishlar** (`Yo'nalishlar`)
   - Misol: `theater_circus` / `TEATR VA SIRK YO'NALISHI SOHA VAKILLARI` / icon: `theater`

2. **Mukofot mansubliklari** (`Mukofot mansubliklari`)
   - `state` / `Davlat mukofotlari`
   - `karakalpakstan` / `Qoraqalpog'iston Respublikasi mukofotlari`
   - `ministry`, `foreign`, `international`

3. **Mukofot turlari** (har mansublik ichida inline yoki alohida)
   - state → `hero`, `honorary_titles`, `orders`, `medals`, `honorary_diploma`

4. **Mukofot nomlari** (har tur ichida inline yoki alohida)
   - hero → `hero_uzbekistan`
   - honorary_titles → 37 ta unvon
   - orders → 16 ta orden
   - medals → 5 ta medal
   - honorary_diploma → 1 ta yorliq

5. **Vakillar** — to'liq Portfoliosi bilan, mukofotlar inline qo'shiladi (yili bilan)

## API endpointlari

| Method | URL | Tavsif |
|--------|-----|--------|
| GET | `/api/directions` | Yo'nalishlar ro'yxati (count bilan) |
| GET | `/api/award-taxonomy` | Mukofotlar iyerarxiyasi |
| GET | `/api/people?direction=&gender=` | Vakillar ro'yxati (filtrlanadigan) |
| GET | `/api/people/{id}` | Bitta vakil tafsiloti |
| GET | `/health` | Health check |

Frontend hozircha `public/api/*.json` fayllardan yuklaydi. Backend tayyor bo'lganda frontend [src/services/api.js](../portfolio_front/src/services/api.js) `baseURL` ni `http://localhost:8001/api` ga o'zgartiriladi.

## Keyingi qadamlar (rejada)

- [ ] Region, District modellari + map markerlari uchun lat/lng
- [ ] FamilyMember, Achievement modellari (Portfolio to'liq)
- [ ] Image upload + thumbnail
- [ ] Authentication (JWT) FastAPI uchun
- [ ] CSV/Excel import — bulk vakillar kiritish
- [ ] PostgreSQL + Docker compose
