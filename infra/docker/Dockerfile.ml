FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install ML Python packages globally
RUN pip install --no-cache-dir \
    numpy==1.26.2 \
    pandas==2.1.3 \
    scikit-learn==1.3.2 \
    tensorflow==2.14.0 \
    sqlalchemy==2.0.23 \
    psycopg2-binary==2.9.9 \
    asyncpg==0.29.0 \
    pydantic==2.5.0 \
    python-dotenv==1.0.0 \
    requests==2.31.0

# Dev mode: source code bind-mounted at /app via docker-compose
CMD ["python", "-m", "inference.service"]
