# 📹 Video Tools (`videotools`)

**Video Tools** is a web application and background task management system built with **Django** and **Django REST Framework (DRF)**. It leverages **Celery** and **Redis** for asynchronous task execution, such as extracting metadata, handling video downloading streams, and processing media tasks without blocking the main web application thread.

---

## 📐 Architecture & Design Patterns

The project follows a modular, multi-layered architecture separating data persistence, business logic, and background processing:

```text
videotools/
├── manage.py                   # Django management CLI script
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Multi-container service orchestration
├── .dockerignore               # Files excluded from Docker context
├── videotools/                 # Core project configuration module
│   ├── __init__.py
│   ├── settings.py             # Global settings, Celery & Redis configs
│   ├── urls.py                 # Root URL routing
│   ├── wsgi.py / asgi.py       # WSGI/ASGI entrypoints
│   └── celerybeat-schedule     # Local Celery Beat schedule database
├── jobs/                       # Main app for managing media download jobs
│   ├── models.py               # Database schema (Job entity)
│   ├── views.py                # REST API views / endpoints
│   ├── urls.py                 # Application route definitions
│   ├── serializer.py           # DRF Serializers for JSON parsing/validation
│   ├── task.py                 # Asynchronous background tasks managed by Celery
│   ├── repositories/           # Data Access Layer
│   │   └── job_repository.py   # Direct database operations & queries
│   └── services/               # Business Logic Layer
│       └── job_service.py      # Core rules and processing logic
└── staticfiles/                # Collected static assets
```
🧩 Key Components:
Model (models.py): Defines the Job schema to track video requests (URL, current status, detected website/platform name, selected quality/format IDs, and error tracking).

Repository Pattern (repositories/): Encapsulates database queries to decouple data persistence from domain logic.

Service Layer (services/): Implements business validation, payload processing, and job queuing logic.

Celery Tasks (task.py): Executes long-running and resource-intensive media retrieval tasks asynchronously in background worker processes.

🛠️ Tech Stack
Language: Python 3.x

Web Framework: Django & Django REST Framework (DRF)

Task Queue & Scheduler: Celery & Celery Beat

Message Broker / Cache: Redis

Containerization: Docker & Docker Compose

Media Handling: yt-dlp / Media Download Helpers

Database: SQLite / PostgreSQL

🐳 Running with Docker (Recommended)
The easiest way to run the entire stack (Django Web App, Redis, Celery Worker, and Celery Beat) is using Docker Compose.

Prerequisites
Docker Desktop installed and running.

1. Build and Start Services
Run the following command in the project root directory:

Bash
docker-compose up --build -d
This will build the Docker images and start all services in the background:

Web Server: http://localhost:8000

Redis: Internal broker service

Celery Worker: Background task processor

Celery Beat: Periodic task scheduler

2. Run Database Migrations Inside Container
Bash
docker-compose exec web python manage.py migrate
3. Create Superuser (Admin)
Bash
docker-compose exec web python manage.py createsuperuser
4. View Logs
Bash
# View logs for all services
docker-compose logs -f

# View logs for a specific service (e.g., celery worker)
docker-compose logs -f celery_worker
5. Stop the Containers
Bash
docker-compose down
💻 Manual Setup & Installation (Without Docker)
1. Clone the Repository & Setup Virtual Environment
Bash
# Navigate to the project directory
cd videotools

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Run Database Migrations & Create Superuser
Bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
4. Run the Services Separately
Start Redis Server:

Bash
redis-server
Start Django Web Server:

Bash
python manage.py runserver
Start Celery Worker:

Bash
celery -A videotools worker -l info
Start Celery Beat:

Bash
celery -A videotools beat -l info
💻 Workflow & Usage
Submit a Download Job:
Send a POST request with the video URL to the jobs API endpoint.

Background Processing:
The job is recorded with an initial state (PENDING or PROCESSING), and the processing task is dispatched to Celery.

Fetch Status & Results:
Query the job status endpoint (GET) to check whether processing is completed (COMPLETED) or failed (FAILED), and retrieve available media formats or output details.

🛠️ Management & Administration
Django Admin:
Manage all job records and database entries directly via:
http://localhost:8000/admin/