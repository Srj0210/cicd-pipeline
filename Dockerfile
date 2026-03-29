# ---- Build Stage ----
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Production Stage ----
FROM python:3.11-slim

# Security: run as non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app.py .

# Metadata
LABEL maintainer="Suraj Maitra <surajmaitra@gmail.com>"
LABEL description="Containerized Flask API with CI/CD pipeline"
LABEL version="1.0.0"

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Switch to non-root user
USER appuser

# Run the application
CMD ["python", "app.py"]
