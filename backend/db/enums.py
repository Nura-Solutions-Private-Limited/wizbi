from enum import Enum


class PipelineType(Enum):
    ETL = "ETL"
    ELT = "ELT"
    SPARK = "SPARK"
    MIGRATION = "MIGRATION"
    DATALAKE = "DATALAKE"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"


class PipelineStatus(Enum):
    ACTIVE = "ACTIVE"
    DESIGN = "DESIGN"
    SAVED = "SAVED"
    READY_FOR_ETL = "READY_FOR_ETL"


class JobStatus(Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


class DbType(Enum):
    MYSQL = "MYSQL"
    POSTGRES = "POSTGRES"
    MSSQL = "MSSQL"
    REDSHIFT = "REDSHIFT"
    LFS = "LFS"
    S3 = "S3"
    GDRIVE = "GDRIVE"
    GA = "GA"
    ICEBERG = "ICEBERG"
    DUCKDB = "DUCKDB"
    ORACLE = "ORACLE"
    RESTAPI = "RESTAPI"
    X = "X"
    FACEBOOK = "FACEBOOK"
    INSTAGRAM = "INSTAGRAM"
    LINKEDIN = "LINKEDIN"


class PermissionType(Enum):
    PIPELINES = "PIPELINES"
    ETLS = "ETLS"
    CONNECTIONS = "CONNECTIONS"
    DASHBOARDS = "DASHBOARDS"
    AUDITS = "AUDITS"
    JOBS = "JOBS"
    REPORTS = "REPORTS"
    GENAI = "GENAI"


class DbtHostAuthType(Enum):
    PASSWORD = 'PASSWORD'
    KEY = 'KEY'
