# EduCore_ERP System

Modern college ERP system with a FastAPI backend, Reflex (Python) frontend, and MySQL database using SQLAlchemy ORM.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Reflex (Python frontend framework)
- **Database**: MySQL
- **ORM**: SQLAlchemy (with Alembic for migrations)

## High-Level Features

- **Role-based login**: student, faculty, admin
- **Student dashboard**
- **Faculty dashboard**
- **Admin dashboard**
- **Attendance system**
- **Assignments system**
- **Results management**
- **Notices**
- **Timetable**

## Project Structure

```text
College_ERP/
  backend/
    app/
      api/
        v1/
      core/
      db/
        models/
      schemas/
  frontend/
    rxconfig.py
    college_erp/
      pages/
      components/
      state/
```

## Getting Started

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows PowerShell
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file in the project root based on `.env.example` and update the values for your local MySQL instance and secrets.

### 4. Running the backend (FastAPI)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### 5. Running the frontend (Reflex)

```bash
cd frontend
reflex run
```

The frontend will be available at `http://localhost:3000` (or the port configured in Reflex).

## Next Steps

- Implement authentication (JWT-based) and role-based access control.
- Flesh out database models for students, faculty, admins, attendance, assignments, results, notices, and timetables.
- Build dashboards and pages in Reflex consuming the FastAPI backend.
- Add tests, CI/CD, and production-ready configuration.
- Secure login

