import json
import os
from datetime import datetime
from typing import Dict

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.orm import Session

import constants
from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.dbutils.createDatawarehouse import CreateDatawarehouse
from db.dbutils.datawarehouse import Datawarehouse
from db.dbutils.dimfactjson import DimFactJson
from db.dbutils.etljson import EtlJson
from db.dbutils.etlload import EtlLoad
from db.dbutils.mappedjson import MappedJson
from db.dbutils.postgresDatawarehouse import PostGresDatawarehouse
from db.dbutils.redshiftdatawarehouse import RedshiftDatawarehouse
from db.dbutils.sourcejson import SourceJson
from db.enums import DbType
from db.models.models import Db_Conn, Job, Pipeline, User
from db.session import get_db
from db.views.job import add_update_job_status
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


@router.post("/gen-mapped-json", response_model=ShowMappedJson)
async def generate_mapped_json(body: bytes = Depends(get_body),
                               db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate mapped json from source json
    '''
    # data = body.decode('UTF-8')
    data = body

    json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                             constants.SOURCE_JSON_FILE)
    mappedJson = MappedJson(source_json_file=json_file,
                            data=data)
    file_name, mappedJsonData = mappedJson.generate_mapped_json()

    return {"mapped_json_file": file_name}


@router.post("/gen-dimfact-json", response_model=ShowDimFactJson)
def generate_dimfact_json(db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate dimfact json from mapped json
    '''
    json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                             constants.MAPPED_JSON_FILE)
    dimFactJson = DimFactJson(mapped_json_file=json_file)
    file_name, dimFactJsonData = dimFactJson.generate_dimfact_json()

    return {"dimfact_json_file": file_name}


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
                             constants.DIMFACT_JSON_FILE)
    datawarehouse = Datawarehouse(connection=connection,
                                  dimfact_json_file=file_name)
    datawarehouse.create_database_with_obj()

    return {"status": True}


@router.post("/gen-dw-from-source/{pipeline_id}")
def generate_datawarehouse_from_source(pipeline_id: int,
                                       # sourcedatabaseConn: DatabaseConn,
                                       # targetdatabaseConn: DatabaseConn,
                                       # body: bytes = Depends(get_body),
                                       # mappedData: JSONObject,
                                       background_tasks: BackgroundTasks,
                                       mappedData: Dict,
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
    if source_db_conn.db_type == "mysql" or source_db_conn.db_type == DbType.MYSQL.value:
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
    mappedJson = MappedJson(source_json_file=json_file,
                            data=mappedData)
    file_name, mappedJsonData = mappedJson.generate_mapped_json()
    logger.info('Mapped json:- {}'.format(file_name))

    # DimFact Json
    json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                             constants.MAPPED_JSON_FILE)
    dimFactJson = DimFactJson(mapped_json_file=json_file)
    file_name, dimFactJsonData = dimFactJson.generate_dimfact_json()

    logger.info('DimFact json:- {}'.format(file_name))

    '''
    Generate etl json from mapped json
    '''
    mapped_json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                    constants.MAPPED_JSON_FILE)
    etl_json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                 constants.ETL_JSON_FILE)
    etlJson = EtlJson(mapped_json_file=mapped_json_file,
                      etl_json_file=etl_json_file)
    etljson_status, etlJsonData = etlJson.gen_etl_json()

    logger.info(f"Etl json status:{etljson_status}")
    # store json file data in source_db_mapping
    sourceDbMapping = create_update_db_source_mapping(pipeline_id=pipeline_id,
                                                      user_input=mappedData,
                                                      sourcejsondata=sourceJsonData,
                                                      mappedjsondata=mappedJsonData,
                                                      dimfactjsondata=dimFactJsonData,
                                                      etljsondata=etlJsonData,
                                                      db=db)

    logger.info('Loaded data in source_data_mapping :{}'.format(sourceDbMapping.id))

    # Create Datawarehouse
    if dest_db_conn.db_type == 'redshift' or dest_db_conn.db_type == DbType.REDSHIFT.value:
        schemas = dest_db_conn.db_name
    else:
        schemas = pipeline.dest_schema_name
    mysqldatbase = DatabaseConnection(database_type=dest_db_conn.db_type,
                                      username=dest_db_conn.db_username,
                                      password=dest_db_conn.db_password,
                                      host=dest_db_conn.db_host,
                                      port=dest_db_conn.db_port,
                                      schemas=schemas)
    url = mysqldatbase.get_url()
    newDW = CreateDatawarehouse(url=url)
    newDW.createDW(pipeline.dest_schema_name)
    """  if  dest_db_conn.db_type == 'redshift':
        mysqldatbase = DatabaseConnection(database_type=dest_db_conn.db_type,
                                        username=dest_db_conn.db_username,
                                        password=dest_db_conn.db_password,
                                        host=dest_db_conn.db_host,
                                        port=dest_db_conn.db_port,
                                        schemas=pipeline.dest_schema_name) """
    connection = mysqldatbase.get_connection()
    engine = mysqldatbase.get_engine()
    raw_connection = engine.raw_connection()
    dim_fact_json_filename = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                          constants.DIMFACT_JSON_FILE)
    etl_json_filename = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                     constants.ETL_JSON_FILE)
    if dest_db_conn.db_type == "mysql" or dest_db_conn.db_type == DbType.MYSQL.value:
        datawarehouse = Datawarehouse(pipeline_id=pipeline_id,
                                      db=db,
                                      user=current_user,
                                      connection=connection,
                                      raw_connection=raw_connection,
                                      dimfact_json_file=dim_fact_json_filename,
                                      etl_json_file=etl_json_filename,
                                      dw_name=pipeline.dest_schema_name)
    elif dest_db_conn.db_type == "postgres" or dest_db_conn.db_type == DbType.POSTGRES.value:
        datawarehouse = PostGresDatawarehouse(pipeline_id=pipeline_id,
                                              db=db,
                                              user=current_user,
                                              connection=connection,
                                              raw_connection=raw_connection,
                                              engine=engine,
                                              dimfact_json_file=dim_fact_json_filename,
                                              etl_json_file=etl_json_filename,
                                              dw_name=pipeline.dest_schema_name)
    elif dest_db_conn.db_type == "redshift" or dest_db_conn.db_type == DbType.REDSHIFT.value:
        datawarehouse = RedshiftDatawarehouse(pipeline_id=pipeline_id,
                                              db=db,
                                              user=current_user,
                                              connection=connection,
                                              raw_connection=raw_connection,
                                              engine=engine,
                                              dimfact_json_file=dim_fact_json_filename,
                                              etl_json_file=etl_json_filename,
                                              dw_name=pipeline.dest_schema_name)

    datawarehouse.create_database_with_obj()
    datawarehouse.create_sqlquery_for_reports()
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    pipeline.status = 'Ready for ETL'

    # Commit changes to database and return the dataset
    db.commit()

    db.refresh(pipeline)

    return {"status": True}


@router.post("/gen-etl-json", response_model=DatawarehouseStatus)
def generate_etl_json(db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate etl json from mapped json
    '''
    mapped_json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                    constants.MAPPED_JSON_FILE)
    etl_json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                 constants.ETL_JSON_FILE)
    etlJson = EtlJson(mapped_json_file=mapped_json_file,
                      etl_json_file=etl_json_file)
    etljson_status, etlJsonData = etlJson.gen_etl_json()

    return {"status": etljson_status}


@router.post("/run-etl", response_model=DatawarehouseStatus)
def run_etl(sourcedatabaseCon: DatabaseConn,
            targetdatabaseCon: DatabaseConn,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user_from_token)):
    '''
    Create datawarehouse schema
    '''
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


@router.post("/run-pipeline/{id}", response_model=DatawarehouseStatus)
def run_data_pipeline(id: int,
                      background_tasks: BackgroundTasks,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    '''
    Run data pipeline
    '''
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
