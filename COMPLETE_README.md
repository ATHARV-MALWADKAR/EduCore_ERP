# College ERP - Complete Production-Ready System

A full-stack Enterprise Resource Planning (ERP) system for educational institutions built with FastAPI, SQLAlchemy, and Jinja2 templates.

## Features

✅ **Complete Authentication**
- JWT-based authentication with role-based access control
- Secure password hashing with bcrypt
- Session management with HTTP cookies

✅ **Role-Based Dashboards**
- Admin Dashboard: Complete system oversight
- Faculty Dashboard: Course and assignment management
- Student Dashboard: Academic progress tracking

✅ **Light/Dark Theme**
- Persistent theme preference using localStorage
- Smooth transitions and Tailwind CSS styling

✅ **Database Support**
- SQLite (default, no setup required)
- MySQL (configured via environment variables)

✅ **API Documentation**
- Auto-generated Swagger UI at `/docs`
- Complete API endpoints with validation

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**

The `.env` file is configured for SQLite by default. For MySQL, update:
```
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=college_erp_user
DB_PASSWORD=college_erp_password
DB_NAME=college_erp
```

3. **Run the Application**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application will:
- Automatically create database tables
- Seed the database with default roles and admin user

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@college.edu | admin123 |

## Login Flow

1. Open `http://localhost:8000/login`
2. Enter credentials: `admin@college.edu` / `admin123`
3. Redirected to `/admin` dashboard
4. Token is stored in HTTP-only cookie

## Project Structure

```
college_erp/
├── backend/
│   └── app/
│       ├── api/v1/                    # API Routes
│       │   ├── routes_auth.py         # Authentication endpoints
│       │   ├── routes_students.py     # Student management
│       │   ├── routes_admin.py        # Admin endpoints
│       │   ├── routes_faculty.py      # Faculty endpoints
│       │   └── ...
│       ├── db/
│       │   ├── models/                # SQLAlchemy models
│       │   ├── session.py             # Database session
│       │   └── init_db.py             # Database seeding
│       ├── core/
│       │   ├── config.py              # Configuration
│       │   ├── security.py            # JWT & password hashing
│       │   ├── deps.py                # Dependency injection
│       │   └── middleware.py          # Custom middleware
│       ├── schemas/                   # Pydantic schemas
│       ├── crud/                      # Database operations
│       ├── services/                  # Business logic
│       ├── templates/                 # Jinja2 templates
│       ├── static/                    # CSS, JS, static files
│       └── main.py                    # FastAPI app
├── requirements.txt                   # Python dependencies
├── .env                              # Environment configuration
└── README.md                         # This file
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/json` - Login with email/password
- `GET /api/v1/auth/me` - Current user info (requires auth)
- `POST /api/v1/auth/logout` - Logout

### Admin Routes
- `GET /admin` - Admin dashboard
- `GET /students` - List all students

### Faculty Routes  
- `GET /faculty` - Faculty dashboard

### Student Routes
- `GET /student` - Student dashboard

### Utility
- `GET /health` - Health check
- `GET /docs` - Swagger API documentation
- `GET /redoc` - ReDoc documentation

## Security Features

✅ **Authentication & Authorization**
- JWT tokens with 1-hour expiration
- Role-based access control (RBAC)
- HTTP-only secure cookies

✅ **Password Security**
- bcrypt hashing with salt
- Minimum password requirements

✅ **HTTP Security Headers**
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security
- CORS properly configured

✅ **Rate Limiting**
- 200 requests per 60 seconds per IP
- Configurable limits

## Troubleshooting

### Token not persisting after refresh
- Ensure cookies are enabled in browser
- Check that the application is using the same domain/port

### Database errors
- Delete `college_erp.db` to reset database
- Tables will be recreated on next run

### CORS errors
- CORS is enabled for all origins in development
- Restrict in production by updating `CORSMiddleware`

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Restart Python environment after installing new packages

## Deployment

### Production Checklist

1. **Environment Variables**
   ```bash
   export APP_ENV=production
   export SECRET_KEY=<long-random-key>
   export DB_TYPE=mysql  # Use MySQL for production
   ```

2. **CORS Configuration**
   - Update `CORSMiddleware` in `main.py` with allowed origins

3. **HTTPS**
   - Set `secure=True` in cookie configuration
   - Use reverse proxy (nginx, Apache) with SSL

4. **Database**
   - Use managed MySQL service
   - Enable backups

5. **Run with Gunicorn**
   ```bash
   gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker app.main:app
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements
COPY backend/app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

## Support

For issues or questions, check:
- API Documentation: `http://localhost:8000/docs`
- Terminal logs for error messages
- Database schema: `docs/schema/SCHEMA.md`

## License

MIT License - See LICENSE file for details
