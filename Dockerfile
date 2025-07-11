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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories with proper permissions
RUN mkdir -p /opt/airflow/data/raw \
    /opt/airflow/data/processed \
    /opt/airflow/downloads \
    /opt/airflow/logs \
    /opt/airflow/plugins \
    /opt/airflow/logs/dag_processor_manager \
    /opt/airflow/logs/scheduler

# Set proper permissions for Airflow directories
RUN chown -R airflow:root /opt/airflow && \
    chmod -R 755 /opt/airflow

# Switch back to airflow user
USER airflow

# Copy requirements files
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set the entrypoint
ENTRYPOINT ["python", "entrypoint.py"]

# The default command will be overridden by docker-compose
# This Dockerfile is used to build a custom Airflow image with ENEM ETL dependencies 