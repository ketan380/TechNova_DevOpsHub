# ==============================================================================
# DevOpsHub - Production Dockerfile
# TechNova Cloud Computing Internship Task 4: Docker Containerization
# Base Image: Python 3.12 Slim (Debian-based, minimal footprint & attack surface)
# ==============================================================================

FROM python:3.12-slim

# Set environment variables to optimize Python runtime in container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FLASK_ENV=production

# Set working directory inside container
WORKDIR /app

# Create a dedicated non-root user and group for security compliance
# Security Best Practice: Never run container workloads as root (UID 0)
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -m -s /bin/bash appuser

# Copy dependency definition first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies without caching build artifacts
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code with non-root ownership
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser templates/ ./templates/
COPY --chown=appuser:appuser static/ ./static/

# Switch to the non-root application user
USER appuser

# Expose standard container port
EXPOSE 5000

# Container Healthcheck using Python's standard library (no curl dependency required)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health', timeout=3)" || exit 1

# Production WSGI Server: Start via Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
