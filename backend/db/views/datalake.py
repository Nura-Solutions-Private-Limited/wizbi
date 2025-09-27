import structlog
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.enums import DbType
from db.models.models import Db_Conn, Permissions, Pipeline, User, UserRole
from db.views.iceberg_dataload import IcebergDataload
from db.views.permission_checker import PermissionChecker
from schemas.datalake import IcebergTableConnection


def validate_iceberg_table(db: Session, user_id: int, icebergTableConnection: IcebergTableConnection):
    '''
    Validate Iceberg table connection and return metadata.json file location
    '''
    icebergDataload = IcebergDataload(aws_access_key=icebergTableConnection.aws_access_key,
                                      aws_secret_key=icebergTableConnection.aws_secret_key,
                                      s3_bucket=icebergTableConnection.s3_bucket,
                                      s3_region=icebergTableConnection.s3_region)

    return icebergDataload.validate_iceberg_table(iceberg_database=icebergTableConnection.iceberg_database,
                                                  iceberg_table=icebergTableConnection.iceberg_table)


def iceberg_table_preview(db: Session, user_id: int, pipeline_id: int):
    '''
    Iceberg table preview
    '''
    # query pipeline
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if not pipeline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")

    # query source database connection
    iceberg_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()

    # get iceberg table preview
    if iceberg_db_conn.db_type == DbType.ICEBERG.value:
        icebergDataload = IcebergDataload(aws_access_key=iceberg_db_conn.s3_access_key_id,
                                          aws_secret_key=iceberg_db_conn.s3_secret_access_key,
                                          s3_bucket=iceberg_db_conn.s3_bucket,
                                          s3_region=iceberg_db_conn.s3_bucket_region)
        return icebergDataload.table_previews(iceberg_database=iceberg_db_conn.iceberg_database,
                                              iceberg_table=iceberg_db_conn.iceberg_table,
                                              db=db,
                                              user_id=user_id,
                                              pipeline_id=pipeline_id)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Database type not {iceberg_db_conn.database_type} supported")
