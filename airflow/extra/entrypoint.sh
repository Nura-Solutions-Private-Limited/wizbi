#!/bin/bash
set -e

# Check if the MySQL connection exists
if airflow connections get wizbi; then
    echo "MySQL connection already exists."  
else
    echo "Creating MySQL connection."
    airflow connections add 'wizbi' \
        --conn-type 'mysql' \
        --conn-host 'mysql' \
        --conn-login 'wizbi_user' \
        --conn-password 'wizbi_password' \
        --conn-schema 'wizbi_db' \
        --conn-port '3306'
fi

# Execute the original entrypoint command
exec "$@"
