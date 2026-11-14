# ==============================================================================
# TruVex AI - Production Docker Container
# Multi-stage lightweight Python image with non-root security execution
# ==============================================================================

FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY run.py ./
COPY data/ ./data/

# Create non-root user and assign permissions
RUN useradd -m -u 1000 truvex && \
    mkdir -p /app/data && \
    chown -R truvex:truvex /app

USER truvex

# Expose API & Dashboard port
EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start production server
CMD ["python", "run.py"]
