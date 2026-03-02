# Vianue — Venue Marketplace (Django + DRF)

This repository contains a scaffolded Django + DRF project for a Venue Marketplace.

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