# Multi-stage build for College ERP

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies file
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --user --no-cache-dir ".[dev]" || pip install --user --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    sqlalchemy==2.0.23 \
    alembic==1.12.1 \
    pymysql==1.1.0 \
    python-jose[cryptography]==3.3.0 \
    bcrypt==4.1.1 \
    python-multipart==0.0.6 \
    httpx==0.25.2 \
    python-dotenv==1.0.0 \
    email-validator==2.1.0 \
    python-json-logger==2.0.7

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set Python path
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY backend ./backend
COPY .env.example ./.env

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
