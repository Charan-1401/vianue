# Vianue — Venue Marketplace (Django + DRF)

Vianue is a full-stack venue marketplace built with Django and Django REST Framework. It supports multi-role workflows including customers, venue owners, service vendors, and admin moderators. The platform includes venue discovery, service listings, booking/order management, availability blocking, and approval workflows.

## Features

- Role-based access for `CUSTOMER`, `OWNER`, `VENDOR`, and `STAFF`
- Venue search and availability checking
- Service listings with categories, pricing models, packages, and add-ons
- Booking/order lifecycle with order items, payments, refunds, and status tracking
- Admin moderation for venue/service approvals
- JWT authentication and protected dashboards
- Celery + Redis for background task support
- Docker Compose setup for Postgres and Redis

## Tech stack

- Python 3.11
- Django 4.x
- Django REST Framework
- JWT auth via `djangorestframework-simplejwt`
- Celery with Redis
- PostgreSQL
- Stripe integration
- Docker + Docker Compose
- `drf-spectacular` for API schema
- `django-storages` and `python-dotenv`

Quick start (dev):

1. Create venv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set environment variables (see `.env.example`) and run migrations:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_sample
python manage.py runserver
```

3. Run Celery worker (requires Redis):

```bash
celery -A vianue worker -l info
celery -A vianue beat -l info
```

Docker compose (Postgres + Redis):

```bash
docker-compose up --build
```
Username: Vianue
Email address: charanmarrapu9@gmail.com
Password: 9494541032