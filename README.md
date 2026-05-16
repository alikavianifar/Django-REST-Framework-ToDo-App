# <div align="center">ToDo App — Django REST Framework</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2_LTS-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15-red?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


</div>

<p align="center">
A full-featured <strong>task-management REST API</strong> built with <strong>Django 4.2 LTS</strong> and <strong>Django REST Framework 3.15</strong>.<br/>
Complete authentication flow from JWT and Token login to email verification and password reset — async email delivery via Celery, interactive Swagger docs, and a classic web UI, all containerised with Docker.
</p>

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture Overview](#-architecture-overview)
- [Getting Started](#-getting-started)
- [API Examples](#-api-examples-curl)
- [Running Tests](#-running-tests)
- [Project Structure](#-project-structure)
- [Security Practices](#-security-practices)
- [API & URL Endpoints](#-api--url-endpoints)
- [License](#-license)

---

## ✨ Key Features

### ✅ Tasks API
- **CRUD Operations** — Full create, read, update, and delete for tasks via a REST API, with proper owner-based permissions so users only access their own data
- **Filtering & Search** — Filter tasks by `priority` and `completed` status; full-text search on task fields; multi-field ordering support
- **Pagination** — Configurable page size via `?page_size=` query param for all list endpoints
- **Web UI** — Server-Side Rendered (SSR) classic Django templates for task management alongside the API, accessible in the browser without a separate frontend

### 🔐 Authentication & Users
- **Custom User Model** — Email-based authentication (no username field), used across both Token and JWT auth flows
- **Dual Auth Strategy** — DRF Token authentication for simple clients and JWT (access + refresh) for stateless API consumers, with blacklist-based logout for JWT
- **Email Verification** — Signed activation tokens sent via Celery; users confirm via link or `curl`; resend endpoint available
- **Password Reset** — Complete email-based recovery flow: request → email with signed link → confirm new password via API
- **Change Password** — Authenticated endpoint (`PUT`) for in-session password updates

### 📧 Email & Async Tasks
- **Celery + Redis** — All outbound emails (activation, password reset) dispatched asynchronously via Celery workers backed by Redis, keeping HTTP responses fast
- **Templated Emails** — HTML email templates for activation and password reset flows, testable locally via smtp4dev

### 📖 API Documentation
- **Swagger UI** — Auto-generated interactive docs at `/swagger/` via `drf-yasg`; can be disabled in production via `ENABLE_API_DOCS=False`
- **Postman Collection** — Ready-to-import collection at [`postman/ToDo-API.postman_collection.json`](postman/ToDo-API.postman_collection.json) covering all endpoints with example payloads

### 🛡️ Security Features
- **DRF Throttling** — Rate limiting on sensitive endpoints to prevent brute-force and abuse
- **Signed Tokens** — Activation and password reset tokens are cryptographically signed with expiry
- **Anti-Enumeration** — Auth responses are deliberately vague to prevent email discovery
- **Bandit in CI** — Static security analysis runs automatically on every push via GitHub Actions
- **Environment Variables** — All secrets managed via `.env` files; a utility script (`scripts/generate_secret_key.py`) generates strong keys

### 🔧 DevOps & Tooling
- **Docker Compose** — Multi-service setup: Django + Gunicorn, PostgreSQL, Redis, Celery worker, and smtp4dev
- **Health Check** — Dedicated `/health/` endpoint for container and load-balancer readiness probes
- **GitHub Actions CI** — Automated lint (flake8), security scan (Bandit), and test suite on every push and pull request
- **Makefile** — Convenience commands (`make up`, `make test`, `make lint`, `make format`, `make secret`) for local development

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11 |
| **Framework** | Django 4.2 LTS |
| **API** | Django REST Framework 3.15 |
| **Database** | PostgreSQL (Docker) |
| **Cache / Broker** | Redis |
| **Async Tasks** | Celery |
| **Authentication** | DRF Token + JWT (SimpleJWT with blacklist) |
| **API Docs** | drf-yasg (Swagger / ReDoc) |
| **Frontend** | Django Templates (SSR) |
| **Email** | smtp4dev (development SMTP server) |
| **Containerisation** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions (flake8 + Bandit + pytest) |
| **Testing** | pytest + pytest-django |
| **Security** | DRF Throttling, Bandit, python-decouple |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Client / Browser                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────────┐
│                 Gunicorn + Django 4.2                       │
│                                                             │
│  ┌─────────────────────────┐  ┌──────────────────────────┐  │
│  │        accounts         │  │          todo            │  │
│  │                         │  │                          │  │
│  │ • Register / Activate   │  │ • Task List / Create     │  │
│  │ • Token Login / Logout  │  │ • Task Detail / Update   │  │
│  │ • JWT Login / Refresh   │  │ • Filter / Search        │  │
│  │ • JWT Blacklist Logout  │  │ • Pagination             │  │
│  │ • Password Reset        │  │ • Owner Permissions      │  │
│  │ • Change Password       │  │ • Web UI (SSR)           │  │
│  │ • Profile               │  └──────────────────────────┘  │
│  └─────────────────────────┘                                │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Redis  │  Celery Worker  │  smtp4dev        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Register → Activate → Use API

```
POST /api/v1/registration/      ──► User created (inactive), activation email queued
Celery worker picks up task     ──► Activation email sent via smtp4dev
GET  /api/v1/activation/...     ──► Account activated
POST /api/v1/jwt/create/        ──► Access + Refresh tokens returned
POST /api/v1/  (Bearer token)   ──► Task created, scoped to owner
POST /api/v1/jwt/logout/        ──► Refresh token blacklisted
```

---

## 🚀 Getting Started

### Prerequisites

- **Docker** (recommended) OR **Python 3.11+**

### Clone the Repository

```bash
git clone https://github.com/alikavianifar/Django-REST-Framework-ToDo-App.git
cd Django-REST-Framework-ToDo-App
```

### 🐳 Option 1: Docker (Recommended)

```bash
# 1. Copy environment template and configure
cp .env.example .env

# 2. Generate a strong secret key
python scripts/generate_secret_key.py
# Paste output into .env as SECRET_KEY=

# 3. Build and start all services (Django + PostgreSQL + Redis + Celery + smtp4dev)
docker compose up --build

# 4. Create a superuser (admin account)
docker compose exec backend python manage.py createsuperuser
```

| Service | URL |
|---------|-----|
| **Web Application** | http://localhost:8000 |
| **Django Admin** | http://localhost:8000/admin |
| **Health Check** | http://localhost:8000/health/ |
| **Swagger UI** | http://localhost:8000/swagger/ |
| **smtp4dev (Email UI)** | http://localhost:5000 |

### 🖥️ Option 2: Local Development (Without Docker)

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
python scripts/generate_secret_key.py
# Paste output into .env as SECRET_KEY=

# 4. Apply database migrations
cd core
python manage.py migrate

# 5. Create a superuser
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

> **Note:** When running locally without Docker, configure your own Redis instance and start a Celery worker (`celery -A core worker -l info`) for email delivery. Without Redis/Celery, emails will not be sent.

---

## 🧪 API Examples (`curl`)

### Register

```bash
curl -X POST http://localhost:8000/api/v1/registration/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"StrongPassword123!","password1":"StrongPassword123!"}'
```

Check the activation email in smtp4dev, then open the link or confirm manually:

```bash
curl "http://localhost:8000/api/v1/activation/confirm/<uid>/<token>/"
```

### JWT Login

```bash
curl -X POST http://localhost:8000/api/v1/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"StrongPassword123!"}'
```

### Create Task

```bash
export ACCESS="<access_token_from_login>"

curl -X POST http://localhost:8000/api/v1/ \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"title":"Ship portfolio","priority":"high","description":"Publish on GitHub"}'
```

### Password Reset

```bash
# 1. Request reset email
curl -X POST http://localhost:8000/api/v1/password/reset/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'

# 2. Confirm new password with uid + token from the email link
curl -X POST http://localhost:8000/api/v1/password/reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{"uid":"<uid>","token":"<token>","new_password":"NewStrong456!","new_password1":"NewStrong456!"}'
```

---

## 🧪 Running Tests

```bash
cd core

# Run all tests
pytest

# Run with Docker
docker compose exec backend pytest
```

### Makefile Shortcuts

```bash
make up          # docker compose up --build
make test        # pytest with coverage
make lint        # flake8
make format      # black
make secret      # generate SECRET_KEY
```

---

## 📁 Project Structure

```
Django-ToDo-App-REST-Framework/
├── .github/
│   └── workflows/              # GitHub Actions CI (lint + Bandit + tests)
├── core/                       # Django project root
│   ├── accounts/               # Custom user model, auth API (Token + JWT)
│   │   ├── models.py           # Custom User model (email-based, no username)
│   │   ├── serializers.py      # Register, profile, password serializers
│   │   ├── views.py            # Auth endpoints (register, activate, reset, profile)
│   │   └── urls.py
│   ├── todo/                   # Tasks API + SSR web UI
│   │   ├── models.py           # Task model (title, description, priority, completed)
│   │   ├── serializers.py      # TaskSerializer with owner filtering
│   │   ├── views.py            # Task CRUD (DRF ViewSets + web views)
│   │   ├── filters.py          # Priority, completed, search filters
│   │   ├── permissions.py      # IsOwner permission class
│   │   └── urls.py
│   ├── templates/              # Django SSR templates (web UI)
│   └── core/                   # Settings, root URLs, WSGI/ASGI
├── postman/
│   └── ToDo-API.postman_collection.json   # Ready-to-import API collection
├── scripts/
│   └── generate_secret_key.py  # Utility: generate a strong SECRET_KEY
├── docker-compose.yml          # Django + PostgreSQL + Redis + Celery + smtp4dev
├── requirements.txt            # Pinned Python dependencies
├── Makefile                    # Dev shortcuts (up, test, lint, format, secret)
└── README.md
```

---

## 🔒 Security Practices

| Practice | Implementation |
|----------|---------------|
| **No Hardcoded Secrets** | All sensitive values loaded from `.env` via `python-decouple` |
| **`.env` Excluded from Git** | `.gitignore` blocks `.env`; only `.env.example` is tracked |
| **Rate Limiting** | DRF Throttling on auth and sensitive endpoints |
| **Signed Tokens** | Activation and password reset tokens use cryptographic signing with expiry |
| **Anti-Enumeration** | Auth responses are deliberately vague to prevent email discovery |
| **JWT Blacklist** | Refresh tokens blacklisted on logout via `djangorestframework-simplejwt` blacklist app |
| **Static Analysis** | Bandit runs in CI on every push to catch common security issues in Python code |
| **CSRF Protection** | Django's `CsrfViewMiddleware` active for all web (non-API) views |
| **API Docs Toggle** | Swagger/ReDoc disabled in production via `ENABLE_API_DOCS=False` |
| **DEBUG Default** | `DEBUG=False` by default — must be explicitly enabled in `.env` |
| **Secret Key Utility** | `scripts/generate_secret_key.py` encourages strong, unique keys from the start |

---

## 🌐 API & URL Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/registration/` | Register new user |
| GET/POST | `/api/v1/activation/confirm/<uid>/<token>/` | Activate account |
| POST | `/api/v1/activation/resend/` | Resend activation email |
| POST | `/api/v1/token/login/` | Token login |
| POST | `/api/v1/token/logout/` | Token logout |
| POST | `/api/v1/jwt/create/` | JWT login (returns access + refresh) |
| POST | `/api/v1/jwt/refresh/` | Refresh access token |
| POST | `/api/v1/jwt/verify/` | Verify access token |
| POST | `/api/v1/jwt/logout/` | Blacklist refresh token (`{"refresh":"..."}`) |
| PUT | `/api/v1/change/password/` | Change password (authenticated) |
| POST | `/api/v1/password/reset/` | Request password reset email |
| GET | `/api/v1/password/reset/confirm/<uid>/<token>/` | Validate reset link |
| POST | `/api/v1/password/reset/confirm/` | Confirm new password |
| GET/PATCH | `/api/v1/profile/` | View / update profile |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/v1/` | List tasks / create task |
| GET/PUT/PATCH/DELETE | `/api/v1/<id>/` | Retrieve / update / delete task |

**Query params:** `?search=`, `?ordering=`, `?priority=`, `?completed=`, `?page_size=`

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health/` | Health check (container readiness) |
| GET | `/swagger/` | Swagger interactive API docs |
| GET | `/redoc/` | ReDoc API docs |
| GET/POST | `/admin/` | Django admin panel |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).