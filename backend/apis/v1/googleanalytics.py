from datetime import datetime

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Connection_Ext, Db_Conn, User
from db.session import get_db
from db.views.gadataload import GoogleAnalyticsDataLoad
from db.views.job import add_update_job_status
from schemas.googleanalytics import CreateGaDataLoad

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/googleanalytics/{pipeline_id}",
             description="Load Google Analytics Data into database table",
             summary="Google Analytics Data")
async def gadataload(createGaDataLoad: CreateGaDataLoad,
                     pipeline_id: int,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user_from_token)):
    '''
    Load data from google analytics
    '''

    try:
        ga_conn = db.query(Db_Conn).filter(Db_Conn.id == createGaDataLoad.source_connection_id).first()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Google Analytics Connection: {ex}")

    conn_exts = db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == ga_conn.id).all()

    try:
        db_conn = db.query(Db_Conn).filter(Db_Conn.id == createGaDataLoad.destination_connection_id).first()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid staging database connection: {ex}")
    print(db_conn.id)
    destdatabase = DatabaseConnection(database_type=db_conn.db_type,
                                      username=db_conn.db_username,
                                      password=db_conn.db_password,
                                      host=db_conn.db_host,
                                      port=db_conn.db_port,
                                      schemas=db_conn.db_name)
    engine = destdatabase.get_engine()

    job_status = 'Running'
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    job_id = str(time_stamp).replace('.', '_') + '_' + current_user.username + '_fastapi_manual'

    # Create job id for the run and insert into job table for the pipeline id
    add_update_job_status(db=db,
                          status=job_status,
                          job_id=job_id,
                          pipeline_id=pipeline_id,
                          job_date_time=current_time)

    gadataload = GoogleAnalyticsDataLoad(db=db,
                                         pipeline_id=pipeline_id,
                                         ga_conn=ga_conn,
                                         dest_db_conn=db_conn,
                                         dest_db_engine=engine,
                                         connection_exts=conn_exts)

    gadataload.load_data(job_id=job_id)

    # return {"message": f"Successfuly uploaded {[file.file_name for file in file_list]}"}
    return {"message": "Data upload for the files started"}
