import structlog
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.enums import DbType
from db.models.models import Db_Conn, Permissions, Pipeline, User, UserRole
from db.views.iceberg_dataload import IcebergDataload
from db.views.permission_checker import PermissionChecker

logger = structlog.getLogger(__name__)


def database_type(db: Session, user_id: int):
    '''
    Return supported database type
    '''
    data = [
        {
            "id": 1,
            "database_type": DbType.MYSQL.value,
            "description": "MySQL",
            "type": "Database",
            "enabled": True,
        },
        {
            "id": 2,
            "database_type": DbType.POSTGRES.value,
            "description": "PostgreSQL",
            "type": "Database",
            "enabled": True,
        },
        {
            "id": 3,
            "database_type": DbType.MSSQL.value,
            "description": "Microsoft SQL Server",
            "type": "Database",
            "enabled": True
        },
        {
            "id": 4,
            "database_type": DbType.REDSHIFT.value,
            "description": "Amazon Redshift",
            "type": "Database",
            "enabled": True
        },
        {
            "id": 5,
            "database_type": DbType.GA.value,
            "description": "Google Analytics",
            "type": "Data Analytics",
            "enabled": True
        },
        {
            "id": 6,
            "database_type": DbType.S3.value,
            "description": "Amazon S3",
            "type": "Csv",
            "enabled": True
        },
        {
            "id": 7,
            "database_type": DbType.LFS.value,
            "description": "File System",
            "type": "Csv",
            "enabled": True
        },
        {
            "id": 8,
            "database_type": DbType.GDRIVE.value,
            "description": "Google Drive",
            "type": "Csv",
            "enabled": True
        },
        {
            "id": 9,
            "database_type": DbType.ICEBERG.value,
            "description": "Iceberg",
            "type": "Iceberg",
            "enabled": True
        },
        {
            "id": 10,
            "database_type": DbType.DUCKDB.value,
            "description": "DuckDB",
            "type": "DuckDB",
            "enabled": True
        },
        {
            "id": 11,
            "database_type": DbType.ORACLE.value,
            "description": "Oracle",
            "type": "Oracle",
            "enabled": True
        },
        {
            "id": 12,
            "database_type": DbType.RESTAPI.value,
            "description": "Rest API",
            "type": "RestAPI",
            "enabled": True
        },
        {
            "id": 13,
            "database_type": DbType.X.value,
            "description": "X (formerly Twitter)",
            "type": "X",
            "enabled": True
        },
        {
            "id": 14,
            "database_type": DbType.FACEBOOK.value,
            "description": "Facebook",
            "type": "Facebook",
            "enabled": True
        },
        {
            "id": 15,
            "database_type": DbType.INSTAGRAM.value,
            "description": "Instagram",
            "type": "Instagram",
            "enabled": True
        },
        {
            "id": 16,
            "database_type": DbType.LINKEDIN.value,
            "description": "LinkedIn",
            "type": "LinkedIn",
            "enabled": True
        },
    ]
    return data


def get_date_format(db: Session, user_id: int):
    '''
    Return date format
    '''
    data = [
        {
            "id": 1,
            "date_format": "%d/%m/%Y",
            "description": "dd/mm/yyyy",
            "type": "Date",
            "enabled": True,
        },
        {
            "id": 2,
            "date_format": '%d-%m-%Y',
            "description": "dd-mm-yyyy",
            "type": "Date",
            "enabled": True,
        },
    ]
    return data
