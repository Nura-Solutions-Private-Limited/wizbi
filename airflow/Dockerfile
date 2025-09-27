# Use the official Apache Airflow image as the base
FROM apache/airflow:2.8.2

# Switch to root user to install dependencies
USER root

# Install dependencies
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

# Copy entrypoint script if needed
COPY extra/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch back to the airflow user
USER airflow

# Install Python dependencies
COPY dags/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set the working directory
WORKDIR /opt/airflow