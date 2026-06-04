# Internship Management Platform

Django REST Framework backend for IQRAA MARK PVT LTD.

## Stack

Python 3.12 · Django 5.0.6 · DRF 3.15.2 · SimpleJWT 5.3.1 · PostgreSQL / SQLite

## Setup

```bash
python -m venv venv && source venv/bin/activate
cp .env.example .env        # edit SECRET_KEY
make install && make migrate && make run
```

## API

Base: `http://localhost:8000/api/v1/` — Auth: `Authorization: Bearer <token>`

### Auth
| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/auth/register/` | — |
| POST | `/auth/login/` | — |
| POST | `/auth/logout/` | JWT |
| POST | `/auth/token/refresh/` | — |
| GET/PATCH | `/auth/profile/` | JWT |
| POST | `/auth/change-password/` | JWT |

### Internships
| Method | Endpoint | Role |
|--------|----------|------|
| GET | `/internships/` | Any |
| POST | `/internships/` | Company |
| GET | `/internships/{id}/` | Any |
| PATCH | `/internships/{id}/` | Owner |
| DELETE | `/internships/{id}/` | Owner |

Supports `?search=`, `?status=`, `?internship_type=`, `?stipend_min=`, `?stipend_max=`, `?location=`, `?page=`, `?page_size=`.

### Applications
| Method | Endpoint | Role |
|--------|----------|------|
| POST | `/applications/apply/` | Student |
| GET | `/applications/` | Student/Company |
| GET | `/applications/{id}/` | Student/Company |
| PATCH | `/applications/{id}/` | Company (update status) |

Statuses: `pending` → `reviewed` → `shortlisted` → `accepted` / `rejected`

Interactive docs at `/api/docs/` (Swagger) or `/api/redoc/`.

## Commands

| Command | Description |
|---------|-------------|
| `make test` | Run tests with coverage |
| `make lint` | flake8 |
| `make format` | black + isort |

## Postman

Import `postman/` collection — pre-configured with auto-auth and sample payloads.

---