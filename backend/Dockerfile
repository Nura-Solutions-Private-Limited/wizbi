<<<<<<< HEAD
# Use the base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Install libaio1 and other dependencies
RUN apt-get update && apt-get install -y libaio1 wget unzip && rm -rf /var/lib/apt/lists/*

# Install Oracle Instant Client
RUN wget https://download.oracle.com/otn_software/linux/instantclient/1926000/instantclient-basic-linux.x64-19.26.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.x64-19.26.0.0.0dbru.zip -d /opt/oracle && \
    rm instantclient-basic-linux.x64-19.26.0.0.0dbru.zip && \
    echo "/opt/oracle/instantclient_19_26" > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

# Set environment variables for Oracle Instant Client
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_19_26:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/opt/oracle/instantclient_19_26

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /backend
WORKDIR /backend
=======
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> f51b7047a2043655136d40320d507721426366cb
