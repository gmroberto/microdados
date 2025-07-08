# Use Apache Airflow 2.8.1 as base image
FROM apache/airflow:2.8.1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Switch to root to install system dependencies
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Copy requirements files
COPY requirements.txt requirements-test.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed downloads logs plugins

# Set the entrypoint
ENTRYPOINT ["python", "entrypoint.py"]

# The default command will be overridden by docker-compose
# This Dockerfile is used to build a custom Airflow image with ENEM ETL dependencies 