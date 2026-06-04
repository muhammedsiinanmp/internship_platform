# Internship Platform API — v1.0.0

Base URL: `http://localhost:8000/api/v1/`
Interactive docs: `http://localhost:8000/api/docs/`

## Authentication
All endpoints except `register` and `login` require: Authorization: Bearer <access_token>

## Endpoints

### Auth
| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/auth/register/` | No | Register student or company |
| POST | `/auth/login/` | No | Login, receive JWT |
| POST | `/auth/logout/` | Yes | Blacklist refresh token |
| POST | `/auth/token/refresh/` | No | Refresh access token |
| GET/PATCH | `/auth/profile/` | Yes | Get or update profile |
| POST | `/auth/change-password/` | Yes | Change password |

### Internships
| Method | URL | Auth | Role |
|--------|-----|------|------|
| GET | `/internships/` | Yes | Any |
| POST | `/internships/` | Yes | Company |
| GET | `/internships/{id}/` | Yes | Any |
| PATCH | `/internships/{id}/` | Yes | Owning Company |
| DELETE | `/internships/{id}/` | Yes | Owning Company |

### Applications
| Method | URL | Auth | Role |
|--------|-----|------|------|
| POST | `/applications/apply/` | Yes | Student |
| GET | `/applications/` | Yes | Student (own) / Company (theirs) |
| GET/PATCH | `/applications/{id}/` | Yes | Student (view) / Company (update status) |
