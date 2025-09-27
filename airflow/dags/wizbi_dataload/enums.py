from enum import Enum


class PipelineType(Enum):
    ETL = "ETL"
    ELT = "ELT"
    DATALAKE = "DATALAKE"
    SPARK = "SPARK"
    MIGRATION = "MIGRATION"


class JobStatus(Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


class DbType(Enum):
    MYSQL = "MYSQL"
    POSTGRES = "POSTGRES"
    MSSQL = "MSSQL"
    REDSHIFT = "REDSHIFT"
