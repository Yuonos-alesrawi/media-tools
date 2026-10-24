# Media Tools

A web application and background-job system for downloading videos and audio in the quality you choose, built with **Django**, **Django REST Framework**, **Celery** and **Redis**.

**Why I built it:** my internet connection is weak and unreliable, and I wanted to watch courses and videos offline. Downloads run in background workers so the web server never blocks, and progress is pushed live over WebSockets.

> **Responsible use:** this tool is for downloading content you have the right to access. Respect the terms of the sites you use and the rights of the content owners.

## Features
- Submit a download job with a URL, a type and a quality/format, and check its status.
- List the available formats for a URL before downloading.
- Asynchronous processing with Celery and Redis; live progress via Django Channels.
- Jobs move through the states `pending`, `processing`, `done` and `error`; failed jobs keep their error message.
- Django admin for browsing and managing jobs.
- Docker Compose stack: backend, Redis, Celery worker, Celery Beat and a simple front-end.

## Architecture

```text
mediatool/
├── docker-compose.yml
├── .env.example               # copy to .env and fill in
├── frontend/                  # simple web interface
└── backend/
    ├── Dockerfile
    ├── entrypoint.sh
    ├── requirements.txt
    └── videotools/
        ├── manage.py
        ├── videotools/        # settings, URLs, Celery app
        ├── jobs/              # jobs app
        │   ├── models.py          # Jobs entity
        │   ├── views.py           # REST API views
        │   ├── serializer.py
        │   ├── task.py            # Celery tasks
        │   ├── repositories/      # data access layer
        │   ├── services/          # business logic layer
        │   └── tests.py           # unit and API tests
        └── videodownloader/   # download and format services (yt-dlp)
```

The code is layered: **views** handle HTTP, **services** hold the business rules, **repositories** talk to the database, and **Celery tasks** run the long jobs. The services receive their dependencies through the constructor, which keeps them easy to test with mocks.

## API

| Method | Endpoint | Body | Purpose |
|---|---|---|---|
| POST | `/jobs/create/` | `url`, `type` (`VID` or `Mp3`), optional `format_id` | Create a job and queue it |
| GET | `/jobs/<id>/` | none | Get a job and its status |
| POST | `/jobs/get_formats/` | `url` | List the available formats for a URL |

## Configuration

Settings are read from environment variables. Copy `.env.example` to `.env`:

| Variable | Meaning |
|---|---|
| `DJANGO_SECRET_KEY` | Required. Generate one with `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"` |
| `DJANGO_DEBUG` | `1` for development, `0` (default) otherwise |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts, default `localhost,127.0.0.1` |
| `REDIS_URL` | Broker URL, e.g. `redis://redis:6379/0` with Docker |

Never commit `.env`, cookie files or the database. They are listed in `.gitignore`.

## Run with Docker (recommended)

```bash
cp .env.example .env          # then edit the values
docker-compose up --build -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

- Backend API and admin: http://localhost:8000 (admin at `/admin/`)
- Front-end: http://localhost:3000
- Logs: `docker-compose logs -f celery_worker`
- Stop: `docker-compose down`

## Run without Docker

```bash
cd backend/videotools
python -m venv venv
venv\Scripts\activate          # Windows (use: source venv/bin/activate on Linux/macOS)
pip install -r ../requirements.txt
# set DJANGO_SECRET_KEY (or use a .env file), then:
python manage.py migrate
redis-server                                   # terminal 1
python manage.py runserver                     # terminal 2
celery -A videotools worker -l info            # terminal 3
celery -A videotools beat -l info              # terminal 4
```

## Tests

```bash
python manage.py test
# or: docker-compose exec backend python manage.py test
```

13 tests cover the model, the repository, the service layer and the API endpoints. Celery and the download services are mocked, so no Redis or internet is needed.

## Tech stack
Python, Django, Django REST Framework, Celery, Celery Beat, Redis, Django Channels, yt-dlp, Docker, Docker Compose, SQLite.
