from datetime import datetime
from typing import List

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.enums import DbType
from db.models.models import Connection_Ext, Db_Conn, Pipeline, User
from db.session import get_db
from db.views.filedataload import FileDataUpload
from db.views.job import add_update_job_status
from schemas.fileupload import ColumnDatatype, CreateFileUpload

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/s3dataload/{pipeline_id}",
             description="Load file data from AWS S3 Bucket",
             summary="File Data Load from S3 Bucket")
async def s3dataload(createFileUpload: CreateFileUpload,
                     background_tasks: BackgroundTasks,
                     pipeline_id: int,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user_from_token)):
    '''
    Load data from aws s3 connection
    '''

    job_status = 'Running'
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    job_id = str(time_stamp).replace('.', '_') + '_' + current_user.username + '_manual'

    # Create job id for the run and insert into job table for the pipeline id
    add_update_job_status(db=db,
                          status=job_status,
                          job_id=job_id,
                          pipeline_id=pipeline_id,
                          job_date_time=current_time)

    try:
        s3file_conn = db.query(Db_Conn).filter(Db_Conn.id == createFileUpload.source_connection_id).first()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid S3 File Connection: {ex}")

    file_list = db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == s3file_conn.id).all()

    try:
        db_conn = db.query(Db_Conn).filter(Db_Conn.id == createFileUpload.destination_connection_id).first()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid staging database connection: {ex}")

    mysqldatbase = DatabaseConnection(database_type=db_conn.db_type,
                                      username=db_conn.db_username,
                                      password=db_conn.db_password,
                                      host=db_conn.db_host,
                                      port=db_conn.db_port,
                                      schemas=db_conn.db_name)
    engine = mysqldatbase.get_engine()

    filedataupload = FileDataUpload(db=db,
                                    pipeline_id=pipeline_id,
                                    file_conn=s3file_conn,
                                    db_conn=db_conn,
                                    engine=engine,
                                    file_list=file_list,
                                    source_type='s3')
    background_tasks.add_task(filedataupload.load_file_data)
    # background_tasks.add_task(load_data, createFileUpload, db)
    # filedataupload.load_file_data()

    # return {"message": f"Successfuly uploaded {[file.file_name for file in file_list]}"}
    return {"message": "Data upload for the files started"}


@router.post("/localdataload/{pipeline_id}",
             description="Load data from files from local file system",
             summary="File data load from local file system")
def lfdataload(createFileUpload: CreateFileUpload,
               pipeline_id: int,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user_from_token)):
    '''
    Load data from local connection
    '''
    job_status = 'Running'
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    job_id = str(time_stamp).replace('.', '_') + '_' + current_user.username + '_manual'

    # Create job id for the run and insert into job table for the pipeline id
    add_update_job_status(db=db,
                          status=job_status,
                          job_id=job_id,
                          pipeline_id=pipeline_id,
                          job_date_time=current_time)
    try:
        lfsfile_conn = db.query(Db_Conn).filter(Db_Conn.id == createFileUpload.source_connection_id).first()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid file system connection: {ex}")

    file_list = db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == lfsfile_conn.id).all()

    try:
        db_conn = db.query(Db_Conn).filter(Db_Conn.id == createFileUpload.destination_connection_id).first()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid staging database connection:{ex}")

    mysqldatbase = DatabaseConnection(database_type=db_conn.db_type,
                                      username=db_conn.db_username,
                                      password=db_conn.db_password,
                                      host=db_conn.db_host,
                                      port=db_conn.db_port,
                                      schemas=db_conn.db_name)
    engine = mysqldatbase.get_engine()

    filedataupload = FileDataUpload(db=db,
                                    pipeline_id=pipeline_id,
                                    file_conn=lfsfile_conn,
                                    db_conn=db_conn,
                                    engine=engine,
                                    file_list=file_list,
                                    source_type='lfs')
    filedataupload.load_file_data()

    return {"message": f"Successfuly uploaded {[file.file_name for file in file_list]}"}


@router.get("/filepreview/{pipeline_id}",
            description="File preview with column name, data type and sample data sets",
            summary="File preview",
            response_model=List[ColumnDatatype])
def filepreview(pipeline_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user_from_token)):
    '''
    '''
    try:
        pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid pipeline: {ex}")

    try:
        file_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid file connection: {ex}")

    if file_conn:
        if file_conn.db_type == DbType.S3.value or file_conn.db_type == 'Amazon S3':
            source_type = 's3'
            file_list = db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == file_conn.id).all()
        elif file_conn.db_type == DbType.LFS.value or file_conn.db_type == 'Local System':
            source_type = 'lfs'
            file_list = db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == file_conn.id).all()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid file connection: {file_conn.db_conn_name}")

        filedataupload = FileDataUpload(db=db,
                                        file_conn=file_conn,
                                        file_list=file_list,
                                        source_type=source_type,
                                        pipeline_id=pipeline_id)
        return filedataupload.get_file_preview()
