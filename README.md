# Task Manager API

A production-grade RESTful Task Manager API built with Django REST Framework, JWT authentication, and MySQL.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 4.2 + Django REST Framework 3.15 |
| Auth | Simple JWT (access + refresh tokens, blacklisting) |
| Database | MySQL 8 |
| Docs | drf-spectacular (Swagger UI + ReDoc) |
| Tests | pytest + pytest-django + factory-boy |
| Dev environment | Docker + docker-compose |

---

## Project Structure

```
task_manager/
├── config/               # Django settings, root URLs, WSGI
│   └── settings/
│       ├── base.py       # Shared settings
│       ├── development.py
│       └── production.py
├── apps/
│   ├── core/             # Shared utilities (exception handler, response helper)
│   ├── users/            # Custom User model + auth endpoints
│   └── tasks/            # Task CRUD endpoints
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── docker-compose.yml
└── Dockerfile
```

---

## Quick Start (Docker — Recommended)

### 1. Clone and configure environment

```bash
git clone <your-repo-url>
cd task_manager
cp .env.example .env
# Edit .env with your preferred credentials if needed
```

### 2. Start services

```bash
docker-compose up --build
```

This starts MySQL and the Django dev server. Migrations run automatically on startup.

### 3. Create a superuser (optional, for Django Admin)

```bash
docker-compose exec api python manage.py createsuperuser
```

### 4. Open the API docs

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Django Admin: http://localhost:8000/admin/

---

## Manual Setup (without Docker)

### Prerequisites

- Python 3.11+
- MySQL 8 running locally
- MySQL C headers: `sudo apt install default-libmysqlclient-dev gcc pkg-config`

### Steps

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements/development.txt

# 3. Configure environment
cp .env.example .env
# Edit .env: set DB_HOST=localhost and your MySQL credentials

# 4. Create the MySQL database
mysql -u root -p -e "CREATE DATABASE taskdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "CREATE USER 'taskuser'@'localhost' IDENTIFIED BY 'taskpass';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON taskdb.* TO 'taskuser'@'localhost';"

# 5. Run migrations
python manage.py migrate

# 6. Start the server
python manage.py runserver
```

---

## Running Tests

```bash
# All tests with coverage report
pytest --cov=apps --cov-report=term-missing

# Specific app
pytest apps/users/tests/
pytest apps/tasks/tests/

# Single test file
pytest apps/tasks/tests/test_tasks.py -v

# With Docker
docker-compose exec api pytest --cov=apps --cov-report=term-missing
```

---

## API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | No | Create account |
| POST | `/api/auth/login/` | No | Get JWT tokens |
| POST | `/api/auth/logout/` | Yes | Blacklist refresh token |
| POST | `/api/auth/token/refresh/` | No | Get new access token |

### Tasks

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/tasks/` | No | List tasks (paginated) |
| POST | `/api/tasks/` | Yes | Create task |
| GET | `/api/tasks/{id}/` | No | Get task detail |
| PUT | `/api/tasks/{id}/` | Yes (owner) | Full update |
| PATCH | `/api/tasks/{id}/` | Yes (owner) | Partial update |
| DELETE | `/api/tasks/{id}/` | Yes (owner) | Delete task |

### Docs

| Endpoint | Description |
|----------|-------------|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | Raw OpenAPI JSON |

---

## Query Parameters (Task List)

| Parameter | Example | Description |
|-----------|---------|-------------|
| `completed` | `?completed=true` | Filter by completion status |
| `title` | `?title=bug` | Case-insensitive title match |
| `search` | `?search=deploy` | Full-text search (title + description) |
| `ordering` | `?ordering=-created_at` | Sort field (prefix `-` for descending) |
| `page` | `?page=2` | Page number |
| `page_size` | `?page_size=20` | Results per page (max 100) |

---

## Example cURL Requests

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"Secure123!","password2":"Secure123!"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Secure123!"}'
```

### Create Task

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"My first task","description":"Getting started"}'
```

### List Tasks (filtered)

```bash
curl "http://localhost:8000/api/tasks/?completed=false&search=deploy&ordering=-created_at" \
  -H "Authorization: Bearer <access_token>"
```

### Mark Task Complete

```bash
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'
```

### Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

---

## Key Production Patterns

| Pattern | Where |
|---------|-------|
| Custom `AbstractUser` with email login | `apps/users/models.py` |
| Split settings (base/dev/prod) | `config/settings/` |
| Secrets via `django-environ` | `config/settings/base.py` |
| JWT with token blacklisting on logout | `apps/users/views.py` |
| Uniform API response envelope | `apps/core/exceptions.py` |
| `select_related` to avoid N+1 queries | `apps/tasks/views.py` |
| Object-level ownership permissions | `apps/tasks/permissions.py` |
| Factory-based test data | `*/tests/factories.py` |
| OpenAPI auto-generated docs | `drf-spectacular` |
| Docker-compose for reproducible dev | `docker-compose.yml` |

---

## User Roles

| Role | Permissions |
|------|-------------|
| `user` (default) | Create tasks, read/update/delete own tasks only |
| `admin` | Read/update/delete any task |

Set role during registration by passing `"role": "admin"` in the request body, or update via Django Admin.
