# College ERP - Production-Ready Enterprise Resource Planning System

**Version:** 1.0.0  
**Last Updated:** September 2026  
**Status:** ✅ Production Ready

## Overview

**College ERP** is a comprehensive, scalable, and secure Enterprise Resource Planning (ERP) system designed for educational institutions of any size. It provides role-based access control, multi-tenant architecture support, and a modern REST API with a Reflex-based frontend.

This is a **complete, out-of-the-box deployable system** that any college, university, or educational organization can use immediately with minimal configuration.

---

## Quick Start

### Prerequisites
- **Python 3.11+**
- **Docker & Docker Compose** (recommended)
- **Git**

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/ATHARV-MALWADKAR/College_ERP.git
cd College_ERP

# Copy environment template
cp .env.example .env

# Build and start all services
make run

# Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
# Admin: http://localhost:8000/api/redoc
```

### Option 2: Local Development

```bash
# Install dependencies
make setup

# Create database and run migrations
cd backend
alembic upgrade head
python -c "from app.db.init_db import seed_database; from app.db.session import SessionLocal; db = SessionLocal(); seed_database(db)"

# Start backend
make dev

# In another terminal, start frontend
cd frontend
reflex run
```

### Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@college.edu` | `admin123` |
| **Faculty** | `prof.alan@college.edu` | `faculty123` |
| **Student** | `student.john@college.edu` | `student123` |

---

## Architecture

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Reflex (Python) + React | User interface, real-time state management |
| **Backend** | FastAPI (Python) | RESTful API, business logic |
| **Database** | SQLite (dev), MySQL (prod) | Data persistence |
| **Auth** | JWT + Refresh Tokens | Secure authentication & session management |
| **Deployment** | Docker + Docker Compose | Containerized deployment |

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Browser)                     │
│              (Reflex React Application)                 │
└────────────────┬────────────────────────────────────────┘
                 │ HTTPS
                 ↓
┌─────────────────────────────────────────────────────────┐
│               FastAPI Backend (Port 8000)               │
│  ┌─────────────────────────────────────────────────────┐
│  │         Authentication & Authorization              │
│  │    (JWT + Role-Based Access Control)                │
│  └─────────────────────────────────────────────────────┘
│  ┌─────────────────────────────────────────────────────┐
│  │          REST API Routes (v1)                       │
│  │  - /auth           (Login, Refresh, Logout)         │
│  │  - /admin          (Users, Departments, Courses)    │
│  │  - /students       (Student management)             │
│  │  - /faculty        (Faculty management)             │
│  │  - /attendance     (Mark & track attendance)        │
│  │  - /assignments    (Assignment mgmt)                │
│  │  - /results        (Grade management)               │
│  │  - /notices        (Announcements)                  │
│  │  - /timetable      (Class scheduling)               │
│  └─────────────────────────────────────────────────────┘
│  ┌─────────────────────────────────────────────────────┐
│  │          CRUD Business Logic Layer                  │
│  │    (Entities: User, Student, Faculty, etc.)         │
│  └─────────────────────────────────────────────────────┘
└────────────────┬────────────────────────────────────────┘
                 │ SQL
                 ↓
┌─────────────────────────────────────────────────────────┐
│         Database (SQLite/MySQL)                         │
│  ┌─────────────────────────────────────────────────────┐
│  │  14 Core Tables:                                    │
│  │  • Users, Roles, Departments, Courses, Subjects     │
│  │  • Students, Faculty, Enrollments, Attendance       │
│  │  • Assignments, Submissions, Results, Timetable     │
│  │  • Notices, RefreshTokens                           │
│  └─────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────┘
```

---

## Core Features

### 1. **User Management & Authentication**
- Multi-role support (Admin, Faculty, Student)
- Secure JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- Account activation/deactivation
- Password reset flow

### 2. **Academic Management**
- Department & Course Management
- Subject & Curriculum Design
- Student Enrollment Tracking
- Faculty Assignment to Courses

### 3. **Attendance System**
- Real-time attendance marking by faculty
- Student attendance tracking per subject
- Automated attendance reports & summaries
- Attendance percentage calculation
- Low-attendance student alerts

### 4. **Assignment & Submissions**
- Faculty creates and publishes assignments
- Students submit work (file or inline content)
- Faculty grades submissions with feedback
- Submission deadline tracking
- Status workflow (draft, published, closed)

### 5. **Grading & Results**
- Exam result entry (mid-term, final, internal)
- Grade calculation & storage
- Student transcript/report generation
- Performance analytics

### 6. **Timetable Management**
- Class schedule creation (day, time, room)
- Faculty assignment to classes
- Conflict detection (future enhancement)
- Student view of their schedule

### 7. **Notices & Communications**
- Admin/Faculty can post notices
- Target audience filtering (all, students, faculty)
- Department-specific announcements
- Notification system (future enhancement)

### 8. **Dashboard Analytics**
- Admin: System overview (users, departments, attendance trends)
- Faculty: Assigned courses, pending submissions, class schedule
- Student: Enrolled courses, attendance status, grades, assignments

---

## Role-Based Access Control (RBAC)

| Feature | Admin | Faculty | Student |
|---------|:-----:|:-------:|:-------:|
| Manage Users | ✅ | ❌ | ❌ |
| Manage Departments & Courses | ✅ | ❌ | ❌ |
| Create Assignments | ✅ | ✅ | ❌ |
| Mark Attendance | ✅ | ✅ | ❌ |
| View All Attendance | ✅ | ✅ | View Own |
| Enter Grades | ✅ | ✅ | ❌ |
| View Own Grades | ✅ | ✅ | ✅ |
| Post Notices | ✅ | ✅ | ❌ |
| View Timetable | ✅ | ✅ | ✅ |
| Submit Assignments | ❌ | ❌ | ✅ |
| View Dashboard | ✅ | ✅ | ✅ |

---

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Interactive API Docs
- **Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`

### Authentication
All endpoints (except `/auth/login`) require a valid JWT access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Sample Endpoints

#### Login
```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@college.edu&password=admin123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "hashed_token...",
  "token_type": "bearer",
  "expires_in": 900,
  "user_id": 1,
  "role": "admin",
  "full_name": "System Administrator"
}
```

#### List Students
```bash
GET /students?skip=0&limit=100
Authorization: Bearer <access_token>
```

#### Mark Attendance
```bash
POST /attendance/mark
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "student_id": 1,
  "subject_id": 5,
  "date": "2026-09-13",
  "status": "present",
  "remarks": "Regular attendance"
}
```

#### Get Admin Dashboard Data
```bash
GET /admin/departments
GET /admin/courses
GET /admin/users?role=student
GET /attendance/report/overall
Authorization: Bearer <access_token>
```

---

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# Application
APP_ENV=production
SECRET_KEY=your-super-secret-key-change-in-production

# Database
DB_TYPE=mysql          # sqlite or mysql
DB_HOST=mysql
DB_PORT=3306
DB_USER=college_erp_user
DB_PASSWORD=secure_password
DB_NAME=college_erp

# Backend
BACKEND_PORT=8000

# Frontend
FRONTEND_PORT=3000

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# File Uploads
MAX_UPLOAD_SIZE_MB=10

# Email (for password resets)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app-specific-password
SMTP_FROM=noreply@collegeerp.local
```

---

## Deployment

### Using Docker Compose (Recommended)

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Kubernetes (Advanced)

Pre-built Kubernetes manifests are provided in the `k8s/` directory:

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get svc
```

### Database Migrations

```bash
# Run migrations
make db-migrate

# Rollback last migration
make db-rollback

# View migration status
cd backend && alembic current
```

---

## Development

### Project Structure

```
College_ERP/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API route handlers
│   │   ├── crud/            # CRUD business logic
│   │   ├── db/              # Database models & session
│   │   ├── core/            # Core utilities (auth, config, logging)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business services
│   │   └── main.py          # FastAPI application entry point
│   ├── alembic/             # Database migrations
│   ├── tests/               # Backend tests
│   └── requirements.txt
├── frontend/
│   ├── college_erp/
│   │   ├── pages/           # Reflex pages
│   │   ├── components/      # Reusable UI components
│   │   ├── state/           # Global state management
│   │   ├── services/        # API client
│   │   └── __init__.py
│   ├── rxconfig.py          # Reflex config
│   └── app.py               # Reflex app entry point
├── docs/                    # Documentation
├── docker-compose.yml       # Multi-container setup
├── Dockerfile               # Backend containerization
├── Makefile                 # Development shortcuts
├── pyproject.toml           # Python dependencies & config
└── README.md                # This file
```

### Running Tests

```bash
# Run all tests with coverage
make test

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage report
make test-coverage
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make mypy

# Security scans
make security
```

---

## Security Features

### Authentication & Authorization
✅ JWT-based stateless authentication  
✅ Bcrypt password hashing  
✅ Refresh token rotation support  
✅ Role-based access control (RBAC)  
✅ Token expiration (15 min access, 7 days refresh)  

### API Security
✅ CORS policy enforcement  
✅ Rate limiting (200 req/min per IP)  
✅ Secure HTTP headers (CSP, X-Frame-Options, etc.)  
✅ Input validation (Pydantic)  
✅ SQL injection prevention (SQLAlchemy ORM)  
✅ XSS protection  

### Database Security
✅ Foreign key constraints  
✅ Unique indexes on emails, roll numbers  
✅ Soft-delete capability (via status field)  
✅ Audit timestamps (created_at, updated_at)  

### Scanning & Compliance
```bash
# Run security scans
make security

# Bandit (static analysis)
bandit -r backend

# Safety (dependency vulnerabilities)
safety check

# OWASP ZAP (dynamic scanning)
# Configured in CI/CD pipeline (.github/workflows/security.yml)
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Database Connection Error
```bash
# Check MySQL is running
docker-compose logs mysql

# Reset database
make reset-db
```

### Authentication Failures
- Verify `.env` variables are set correctly
- Check `SECRET_KEY` is consistent across service restarts
- Ensure refresh tokens haven't expired (see logs)

### Slow API Response
- Check database indexes are created: `alembic upgrade head`
- Monitor logs for N+1 queries (use `joinedload` in CRUD)
- Verify CORS headers not blocking requests

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 (Python style guide)
- Write tests for new features
- Update documentation
- Run linters before committing: `make lint format`

---

## Roadmap

### Completed ✅
- [x] Core ERP data model (14 tables)
- [x] User authentication & RBAC
- [x] CRUD APIs for all entities
- [x] Attendance tracking system
- [x] Assignment & submission management
- [x] Grading & results
- [x] Timetable management
- [x] Admin/Faculty/Student dashboards
- [x] Docker deployment
- [x] Security hardening

### Planned 🚀
- [ ] Multi-tenant support (per institution isolation)
- [ ] Email notifications
- [ ] SMS alerts (attendance, grades)
- [ ] Mobile app (React Native)
- [ ] Analytics & reporting (charts, graphs)
- [ ] SAML/OAuth2 SSO integration
- [ ] File upload with virus scanning
- [ ] Audit logging
- [ ] Performance dashboards
- [ ] Advanced scheduling algorithm

---

## Support

### Documentation
- 📖 [API Reference](./docs/API.md)
- 📋 [User Guide](./docs/USER_GUIDE.md)
- 🚀 [Deployment Guide](./docs/DEPLOYMENT.md)
- 🔒 [Security Best Practices](./docs/SECURITY.md)

### Help & Issues
- 🐛 [GitHub Issues](https://github.com/ATHARV-MALWADKAR/College_ERP/issues)
- 💬 [Discussions](https://github.com/ATHARV-MALWADKAR/College_ERP/discussions)

---

## License

MIT License - see [LICENSE](./LICENSE) file for details.

---

## Acknowledgments

Built with ❤️ using:
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM for database operations
- **Reflex** - Python framework for reactive UIs
- **Docker** - Container orchestration
- **Pydantic** - Data validation

---

**Ready to deploy? Start with `make run` and follow the demo credentials above!**
