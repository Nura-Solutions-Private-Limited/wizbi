import json
import os
from datetime import datetime
from typing import Dict

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import constants
from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.dbutils.createDatawarehouse import CreateDatawarehouse
from db.dbutils.etljson import EtlJson
from db.dbutils.etlload import EtlLoad
from db.dbutils.migratejson import MigrateJson
from db.dbutils.mysqldatabase import MySQLDatabase

# from db.dbutils.SQLalchemydatawarehouse import GenericDatawarehouse
from db.dbutils.postgresDatawarehouse import PostGresDatawarehouse
from db.dbutils.sourcejson import SourceJson
from db.models.models import Db_Conn, Job, Pipeline, User
from db.session import get_db
from db.views.job import add_update_job_status
from db.views.migration import MigrationMetadata
from db.views.utility import (
    create_update_db_source_mapping,
    gen_dw_from_source,
    run_datapipeline,
)
from schemas.database import DatabaseConn
from schemas.utility import (
    DatawarehouseStatus,
    ShowDimFactJson,
    ShowMappedJson,
    ShowSourceDbMapping,
    ShowSourceJson,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/gen-source-json", response_model=ShowSourceJson)
def generate_source_json(databaseConn: DatabaseConn,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate json file for source database

    '''
    mysqldatbase = DatabaseConnection(database_type=databaseConn.database_type,
                                      username=databaseConn.username,
                                      password=databaseConn.password,
                                      host=databaseConn.host,
                                      port=databaseConn.port,
                                      schemas=databaseConn.schemas)
    connection = mysqldatbase.get_connection()

    sourceJson = SourceJson(connection=connection,
                            db_type=databaseConn.database_type,
                            databaseName=databaseConn.schemas,
                            engine=mysqldatbase.get_engine())
    file_name, sourceJsonData = sourceJson.generate_source_json()

    return {"source_json_file": file_name}


async def get_body(request: Request):
    # return await request.body()
    return await request.json()


@router.post("/gen-migration-json")
async def generate_migration_json(body: bytes = Depends(get_body),
                               db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate mapped json from source json
    '''
    # data = body.decode('UTF-8')
    data = body

    json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                             constants.SOURCE_JSON_FILE)
    migJson = MigrateJson(source_json_file=json_file,
                            data=data)
    file_name,migrateJsonData =migJson.generate_migration_json()

    return {"migrate_json_file": file_name}



@router.post("/gen-dw-schema", response_model=DatawarehouseStatus)
def generate_dw_schema(databaseCon: DatabaseConn,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    '''
    Create datawarehouse schema
    '''
    mysqldatbase = DatabaseConnection(database_type=databaseCon.database_type,
                                      username=databaseCon.username,
                                      password=databaseCon.password,
                                      host=databaseCon.host,
                                      port=databaseCon.port,
                                      schemas=databaseCon.schemas)
    connection = mysqldatbase.get_connection()
    file_name = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                             constants.MIGRATE_JSON_FILE)
    database = MySQLDatabase(connection=connection,
                                  migrate_json_file=file_name)
    database.create_database_obj()

    return {"status": True}
@router.get("/migration_metadata/{pipeline_id}", response_model=list)
def generate_migration_metadata(pipeline_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate metadata from source database
    '''
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if pipeline:
        source_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()
        if source_db_conn:
            if source_db_conn.db_type == "sqlserver":
                schema = source_db_conn.db_name
            else:
                schema = pipeline.source_schema_name

            datbaseconnection = DatabaseConnection(database_type=source_db_conn.db_type,
                                                   username=source_db_conn.db_username,
                                                   password=source_db_conn.db_password,
                                                   host=source_db_conn.db_host,
                                                   port=source_db_conn.db_port,
                                                   # schemas=pipeline.source_schema_name
                                                   # schemas=source_db_conn.db_name
                                                   schemas=schema)
            engine = datbaseconnection.get_engine()
            metadata = MigrationMetadata(pipeline_id=pipeline_id,
                                db=db,
                                chosen_schema=pipeline.source_schema_name,
                                database_type=source_db_conn.db_type,
                                engine=engine,
                                )

            data = metadata.get_migrate_db_metadata()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Invalid pipeline, source db connection not found")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")

    return data

@router.post("/gen-migrated_db-from-source/{pipeline_id}")
def migrate_database_from_source(pipeline_id: int,
                                       # sourcedatabaseConn: DatabaseConn,
                                       # targetdatabaseConn: DatabaseConn,
                                       # body: bytes = Depends(get_body),
                                       # mappedData: JSONObject,
                                       background_tasks: BackgroundTasks,
                                       mappedData: list,
                                       db: Session = Depends(get_db),
                                       current_user: User = Depends(get_current_user_from_token)):
    # TODO commented this part to rollback asynchronous changes because of issues
    # Query job against pipeline_id
    # jobs = db.query(Job).filter(Job.pipeline_id == pipeline_id).all()

    # for job in jobs:
    #     if job.status == 'Running':
    #         raise Exception(f"Existing job:{job.job_id} is in running status for the pipeline:{pipeline_id}")

    # job_status = 'Running'
    # current_time = datetime.now()
    # time_stamp = current_time.timestamp()
        
    # job_id = str(time_stamp).replace('.', '_') + '_' + current_user.username + '_api'

    # # Create job id for the run and insert into job table for the pipeline id
    # add_update_job_status(db=db,
    #                     status=job_status,
    #                     job_id=job_id,
    #                     pipeline_id=pipeline_id,
    #                     job_date_time=current_time)

    # background_tasks.add_task(gen_dw_from_source,
    #                           pipeline_id=pipeline_id,
    #                           job_id=job_id,
    #                           db=db,
    #                           current_user=current_user,
    #                           mappedData=mappedData)

    # return {"job_id": job_id, "message": "job started"}

    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    source_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()

    dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()


    # Source json
    if source_db_conn.db_type == "mysql" or source_db_conn.db_type == "postgres" :
        schema = pipeline.source_schema_name
    else:
        schema = source_db_conn.db_name
    mysqldatbase = DatabaseConnection(database_type=source_db_conn.db_type,
                                      username=source_db_conn.db_username,
                                      password=source_db_conn.db_password,
                                      host=source_db_conn.db_host,
                                      port=source_db_conn.db_port,
                                      # schemas=pipeline.source_schema_name
                                      schemas=schema)
    connection = mysqldatbase.get_connection()

    sourceJson = SourceJson(connection=connection,
                            db_type=source_db_conn.db_type,
                            databaseName=pipeline.source_schema_name,
                            engine=mysqldatbase.get_engine())
    file_name, sourceJsonData = sourceJson.generate_source_json()

    logger.info('Source json:- {}'.format(file_name))

    # Mapped json
    # print(mappedData.get('mappedData'))
    json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                             constants.SOURCE_JSON_FILE)
    # json_file='/Users/shahbaz/rebiz1/json_files/newsource.json'
    migrateJson = MigrateJson(source_json_file=json_file,
                            data=mappedData)
    file_name,migrateJsonData = migrateJson.generate_migration_json()
    logger.info('Migrate json:- {}'.format(file_name))

    '''
    Generate etl json from mapped json
    '''
    migrate_json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                    constants.MIGRATE_JSON_FILE)
    etl_json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                 constants.ETL_JSON_FILE)
    etlJson = EtlJson(mapped_json_file=migrate_json_file,
                      etl_json_file=etl_json_file)
    etljson_status, etlJsonData = etlJson.gen_etl_json()

    logger.info(f"Etl json status:{etljson_status}")
    # store json file data in source_db_mapping
    sourceDbMapping = create_update_db_source_mapping(pipeline_id=pipeline_id,
                                                      user_input=mappedData,
                                                      sourcejsondata=sourceJsonData,
                                                      migratejsondata=migrateJsonData,
                                                      etljsondata=etlJsonData,
                                                      db=db)

    logger.info('Loaded data in source_data_mapping :{}'.format(sourceDbMapping.id))

    # Create Datawarehouse
    
    mysqldatbase = DatabaseConnection(database_type=dest_db_conn.db_type,
                                      username=dest_db_conn.db_username,
                                      password=dest_db_conn.db_password,
                                      host=dest_db_conn.db_host,
                                      port=dest_db_conn.db_port,
                                      schemas=pipeline.dest_schema_name)
    url = mysqldatbase.get_url()
    newDW = CreateDatawarehouse(url=url)
    newDW.createDW(pipeline.dest_schema_name)
    connection = mysqldatbase.get_connection()
    engine = mysqldatbase.get_engine()
    #raw_connection = engine.raw_connection()
    migrate_json_filename = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                          constants.MIGRATE_JSON_FILE)
    etl_json_filename = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                     constants.ETL_JSON_FILE)
    if dest_db_conn.db_type == "mysql":
        database = MySQLDatabase(pipeline_id=pipeline_id,
                                      db=db,
                                      user=current_user,
                                      connection=connection,
                                      engine=engine,
                                      migrate_json_file=migrate_json_filename,
                                      dw_name=pipeline.dest_schema_name)
    """  elif dest_db_conn.db_type == "postgres":
        datawarehouse = PostGresDatawarehouse(pipeline_id=pipeline_id,
                                              db=db,
                                              user=current_user,
                                              connection=connection,
                                              raw_connection=raw_connection,
                                              engine=engine,
                                              dimfact_json_file=dim_fact_json_filename,
                                              etl_json_file=etl_json_filename,
                                              dw_name=pipeline.dest_schema_name) """
    
    database.create_database_obj()
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    pipeline.status = 'Ready for Migration'

    # Commit changes to database and return the dataset
    db.commit()

    db.refresh(pipeline)

    return {"status": True}


@router.post("/gen-etl-json", response_model=DatawarehouseStatus)
def generate_etl_json(db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    
    #Generate etl json from mapped json
    
    migrate_json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                    constants.MIGRATE_JSON_FILE)
    etl_json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                 constants.ETL_JSON_FILE)
    etlJson = EtlJson(mapped_json_file=migrate_json_file,
                      etl_json_file=etl_json_file)
    etljson_status, etlJsonData = etlJson.gen_etl_json()
    
    return {"status": etljson_status}
    #return{"status": True}
'''
@router.post("/run-etl", response_model=DatawarehouseStatus)
def run_etl(sourcedatabaseCon: DatabaseConn,
            targetdatabaseCon: DatabaseConn,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user_from_token)):
    
    Create datawarehouse schema
    
    json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                             constants.ETL_JSON_FILE)

    sourcedbcon = DatabaseConnection(database_type=sourcedatabaseCon.database_type,
                                     username=sourcedatabaseCon.username,
                                     password=sourcedatabaseCon.password,
                                     host=sourcedatabaseCon.host,
                                     port=sourcedatabaseCon.port,
                                     schemas=sourcedatabaseCon.schemas)
    source_con = sourcedbcon.get_connection()
    source_engine = sourcedbcon.get_engine()

    targetdbcon = DatabaseConnection(database_type=targetdatabaseCon.database_type,
                                     username=targetdatabaseCon.username,
                                     password=targetdatabaseCon.password,
                                     host=targetdatabaseCon.host,
                                     port=targetdatabaseCon.port,
                                     schemas=targetdatabaseCon.schemas)
    target_con = targetdbcon.get_connection()
    target_engine = targetdbcon.get_engine()
    etlload = EtlLoad(source_con=source_con,
                      target_con=target_con,
                      source_engine=source_engine,
                      target_engine=target_engine,
                      etl_json_file=json_file)
    etl_status = etlload.load_data()

    return {"status": etl_status}


#@router.post("/run-pipeline/{id}")
@router.post("/run-pipeline/{id}", response_model=DatawarehouseStatus)

def run_data_pipeline(id: int,
                      background_tasks: BackgroundTasks,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    
    Run data pipeline
    
    # return run_datapipeline(pipeline_id=id, db=db)
    return run_datapipeline(pipeline_id=id,
                            background_tasks=background_tasks,
                            db=db,
                            user_name=current_user.username)


# @router.post("/run-pipeline-airflow/{id}", response_model=DatawarehouseStatus)
# def run_data_pipeline_from_airflow(id: int,
#                                    db: Session = Depends(get_db),
#                                    current_user='testuser'):
#     '''
#     Run data pipeline
#     '''
#     # return run_datapipeline(pipeline_id=id, db=db)
#     return run_datapipeline(pipeline_id=id, db=db, user_name=current_user)
 