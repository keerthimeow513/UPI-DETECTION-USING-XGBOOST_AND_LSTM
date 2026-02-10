# Multi-stage build for UPI Fraud Detection API
# Stage 1: Builder stage - compiles and installs Python dependencies
# Stage 2: Production stage - minimal image with only runtime necessities

# ============================================================================
# STAGE 1: BUILDER
# ============================================================================
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies required for compiling Python packages
# gcc and build-essential are needed for packages like numpy, scipy, xgboost
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
# This layer only rebuilds when requirements.txt changes
COPY requirements.txt .

# Install Python dependencies to user directory (no root access needed)
# --no-cache-dir reduces image size by not caching pip downloads
# --user installs to /root/.local which we'll copy in production stage
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 2: PRODUCTION
# ============================================================================
FROM python:3.12-slim

# Security: Create non-root user for running the application
# This reduces attack surface if container is compromised
RUN groupadd -r fraudshield && useradd -r -g fraudshield fraudshield

# Install netcat for entrypoint script to check Redis connectivity
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
# Only the installed packages, not the build tools
COPY --from=builder /root/.local /home/fraudshield/.local

# Add user-local bin to PATH
ENV PATH=/home/fraudshield/.local/bin:$PATH

# Copy entrypoint script first (needed for startup checks)
COPY --chown=fraudshield:fraudshield scripts/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy application code with correct ownership
# Using --chown ensures files are owned by non-root user
COPY --chown=fraudshield:fraudshield . .

# Switch to non-root user for security
# All subsequent commands run as fraudshield user
USER fraudshield

# Expose the API port
EXPOSE 8000

# Health check to verify API is responding
# Docker will restart container if health check fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Use entrypoint script for pre-startup checks
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command to run the API
# Uvicorn runs the FastAPI application
CMD ["python", "-m", "uvicorn", "04_inference.api:app", "--host", "0.0.0.0", "--port", "8000"]
