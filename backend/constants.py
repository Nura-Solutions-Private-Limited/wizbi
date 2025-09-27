import os
from os import environ

import dotenv

'''
Define all variables which needs to hardcoded in code and refer variable instead of values
'''

env_filename = ".env"
env_filepath = os.path.join(os.path.dirname(__file__), env_filename)
dotenv.load_dotenv(env_filepath)

JSON_FILE_PATH = "json_files"
SOURCE_JSON_FILE = "source.json"
MAPPED_JSON_FILE = "mapped.json"
DIMFACT_JSON_FILE = "dimfact.json"
ETL_JSON_FILE = "etl.json"
MIGRATE_JSON_FILE = "migrate.json"
USER_INPUT_FILE = "userinput.json"
SOURCE_DIAGRAM_JSON = "diagram_source.json"
DEST_DIAGRAM_JSON = "diagram_dest.json"
IMAGE_FILE_PATH = "images"
ER_DIAGRAM_SUFFIX = "er_diag"
REPORT_PATH = "reports"
TEMPLATES_PATH = "templates"

# Airflow
AIRFLOW_URL = environ.get('AIRFLOW_URL')
AIRFLOW_USERNAME = environ.get('AIRFLOW_USERNAME')
AIRFLOW_PASSWORD = environ.get('AIRFLOW_PASSWORD')

JOB_EXECUTOR = environ.get('JOB_EXECUTOR')
BATCH_SIZE = int(environ.get('BATCH_SIZE'))
GA_DAY_DATA = int(environ.get('GA_DAY_DATA'))

# Database
DB_USER = environ.get('DB_USER')
DB_PASSWORD = environ.get('DB_PASSWORD')
DB_SERVER = environ.get('DB_SERVER')
DB_PORT = environ.get('DB_PORT')
DB_DB = environ.get('DB_DB')
DB_DRIVER = environ.get('DB_DRIVER')

# Api
SECRET_KEY = environ.get('SECRET_KEY')
OPENAI_API_KEY = environ.get('OPENAI_API_KEY')

API_ACCESS_LOG = environ.get('API_ACCESS_LOG')
API_ERROR_LOG = environ.get('API_ERROR_LOG')

WIZBI_ENV = environ.get('WIZBI_ENV')
BACKDOOR_USER_REGISTER = environ.get('BACKDOOR_USER_REGISTER')

# DBT
DBT_HOSTNAME = environ.get('DBT_HOSTNAME')
DBT_HOST_PORT = environ.get('DBT_HOST_PORT')
DBT_HOST_USERNAME = environ.get('DBT_HOST_USERNAME')
DBT_HOST_PASSWORD = environ.get('DBT_HOST_PASSWORD')
DBT_PROFILE_NAME = environ.get('DBT_PROFILE_NAME')
DBT_PROJECT_PATH = environ.get('DBT_PROJECT_PATH')
DBT_PATH = environ.get('DBT_PATH')
DBT_HOST_PEM_FILE = environ.get('DBT_HOST_PEM_FILE')
# dbt host auth type (password/key)
DBT_HOST_AUTH_TYPE = environ.get('DBT_HOST_AUTH_TYPE')

ENCRYPTION_KEY = environ.get('ENCRYPTION_KEY')
