import json
import os
import time
import traceback
from datetime import datetime
from enum import Enum
from typing import Dict

import requests
import structlog
from fastapi import BackgroundTasks
from requests.auth import HTTPBasicAuth
from sqlalchemy.orm import Session

import constants
from db.auth.dbconnection import DatabaseConnection
from db.dbutils.createDatawarehouse import CreateDatawarehouse
from db.dbutils.datawarehouse import Datawarehouse
from db.dbutils.dimfactjson import DimFactJson
from db.dbutils.etljson import EtlJson
from db.dbutils.etlload import EtlLoad
from db.dbutils.mappedjson import MappedJson
from db.dbutils.postgresDatawarehouse import PostGresDatawarehouse
from db.dbutils.sourcejson import SourceJson
from db.enums import PipelineType
from db.models.models import (
    Connection_Ext,
    Db_Conn,
    Job,
    Pipeline,
    Source_Db_Mapping,
    User,
)
from db.views.filedataload import FileDataUpload
from db.views.gadataload import GoogleAnalyticsDataLoad
from db.views.job import add_update_job_status
from db.views.restapi import RestApiConnector
from db.views.xdataload import XDataLoad

logger = structlog.getLogger(__name__)


class JobExecutor(Enum):
    fastapi = 'FASTAPI'
    airflow = 'AIRFLOW'


# def create_new_db_source_mapping(createSourceDbMapping: CreateSourceDbMapping, db: Session):
def create_update_db_source_mapping(pipeline_id,
                                    user_input,
                                    sourcejsondata,
                                    mappedjsondata=None,
                                    dimfactjsondata=None,
                                    migratejsondata=None,
                                    etljsondata=None,
                                    db=Session):

    # Query source database mapping againt pipeline id to check if already exist
    source_db_mapping = db.query(Source_Db_Mapping).filter(Source_Db_Mapping.pipeline_id == pipeline_id).first()

    # If source database mapping exist then update
    if source_db_mapping:
        source_db_mapping.user_input = user_input
        source_db_mapping.dim_fact = dimfactjsondata
        source_db_mapping.source_target_mapping = mappedjsondata
        source_db_mapping.etl_json = etljsondata
        source_db_mapping.migrate_json = migratejsondata
        source_db_mapping.source_json = sourcejsondata

    # If source database mapping does not exist then create new
    else:
        source_db_mapping = Source_Db_Mapping(pipeline_id=pipeline_id,
                                              user_input=user_input,
                                              dim_fact=dimfactjsondata,
                                              source_target_mapping=mappedjsondata,
                                              etl_json=etljsondata,
                                              migrate_json=migratejsondata,
                                              source_json=sourcejsondata)
        db.add(source_db_mapping)

    # Commit changes to database and return the dataset
    db.commit()
    db.refresh(source_db_mapping)
    return source_db_mapping


def run_datapipeline(pipeline_id,
                     background_tasks: BackgroundTasks,
                     db: Session,
                     user_name):
    '''
    Run data pipeline
    '''

    # Query pipeline table to get all details
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    jobs = db.query(Job).filter(Job.pipeline_id == pipeline_id).all()

    for job in jobs:
        if job.status == 'Running':
            raise Exception(f"Existing job:{job.job_id} is in running status for the pipeline:{pipeline_id}")

    job_status = 'Running'
    current_time = datetime.now()
    time_stamp = current_time.timestamp()

    job_executor = constants.JOB_EXECUTOR.upper()

    if job_executor == JobExecutor.fastapi.value:
        job_id = str(time_stamp).replace('.', '_') + '_' + user_name + '_fastapi'
    elif job_executor == JobExecutor.airflow.value:
        job_id = str(time_stamp).replace('.', '_') + '_' + user_name + '_airflow'

    # Create job id for the run and insert into job table for the pipeline id
    add_update_job_status(db=db,
                          status=job_status,
                          job_id=job_id,
                          pipeline_id=pipeline_id,
                          job_date_time=current_time)

    try:
        if job_executor == JobExecutor.fastapi.value:
            # dataload = DataLoad(pipeline_id=pipeline_id,
            #                     user_name=user_name)
            # dataload.load_data(job_id=job_id)
            if str(pipeline.pipeline_type).upper() == PipelineType.ETL.value:  # 'ETL'
                # Query da_conn table using source db conn id
                source_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()

                # Query da_conn table using dest db conn id
                dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()

                # Get source db mapping using pipeline id
                source_db_mapping = db.query(Source_Db_Mapping).filter(
                    Source_Db_Mapping.pipeline_id == pipeline_id).first()
                if str(source_db_conn.db_type).upper() == 'SQLSERVER':
                    schema = source_db_conn.db_name
                else:
                    schema = pipeline.source_schema_name
                # Create source database connection
                sourcedbcon = DatabaseConnection(database_type=source_db_conn.db_type,
                                                 username=source_db_conn.db_username,
                                                 password=source_db_conn.db_password,
                                                 host=source_db_conn.db_host,
                                                 port=source_db_conn.db_port,
                                                 # schemas=pipeline.source_schema_name
                                                 schemas=schema)
                source_con = sourcedbcon.get_connection()
                source_engine = sourcedbcon.get_engine()
                if str(dest_db_conn.db_type).upper() == 'REDSHIFT':
                    schema = dest_db_conn.db_name
                else:
                    schema = pipeline.dest_schema_name
                # Create target database connection
                targetdbcon = DatabaseConnection(database_type=dest_db_conn.db_type,
                                                 username=dest_db_conn.db_username,
                                                 password=dest_db_conn.db_password,
                                                 host=dest_db_conn.db_host,
                                                 port=dest_db_conn.db_port,
                                                 schemas=schema)
                target_con = targetdbcon.get_connection()
                target_engine = targetdbcon.get_engine()

                # Set etlload variable with connection and json
                etlload = EtlLoad(source_con=source_con,
                                  source_schema=pipeline.source_schema_name,
                                  source_db_type=source_db_conn.db_type,
                                  target_con=target_con,
                                  dest_schema=pipeline.dest_schema_name,
                                  dest_db_type=dest_db_conn.db_type,
                                  source_engine=source_engine,
                                  target_engine=target_engine,
                                  etl_json_data=source_db_mapping.etl_json,
                                  pipeline_id=pipeline_id,
                                  db=db,
                                  user_name=user_name,
                                  json_data_yn=True)
                # Run data load
                # status = etlload.load_data(job_id=job_id)
                background_tasks.add_task(etlload.load_data, job_id)
                # pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
                # pipeline.status = 'Active'

                # Commit changes to database and return the dataset
                # db.commit()
                # db.refresh(pipeline)
                return {"status": "Data load started.", "job_id": job_id}

            elif str(pipeline.pipeline_type).upper() in [PipelineType.ELT.value, PipelineType.SOCIAL_MEDIA.value]:
                # source and destination connection

                # source connection
                try:
                    source_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()
                except Exception as ex:
                    raise Exception(f"Invalid source connection: {ex}")

                # connection ext data
                conn_exts = db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == source_conn.id).all()

                # destination connection
                try:
                    db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()
                except Exception as ex:
                    raise Exception(f"Invalid staging database connection: {ex}")

                mysqldatbase = DatabaseConnection(database_type=db_conn.db_type,
                                                  username=db_conn.db_username,
                                                  password=db_conn.db_password,
                                                  host=db_conn.db_host,
                                                  port=db_conn.db_port,
                                                  schemas=db_conn.db_name)
                engine = mysqldatbase.get_engine()

                # Upload data from s3 bucket files
                if source_conn.s3_access_key_id:
                    filedataupload = FileDataUpload(db=db,
                                                    pipeline_id=pipeline_id,
                                                    file_conn=source_conn,
                                                    db_conn=db_conn,
                                                    engine=engine,
                                                    file_list=conn_exts,
                                                    source_type='s3')
                    background_tasks.add_task(filedataupload.load_file_data, job_id)

                    # return {"message": f"Successfuly uploaded {[file.file_name for file in file_list]}"}
                    return {"status": "Data upload for the files started", "job_id": job_id}

                # Upload data from local file system files
                elif source_conn.lfs_path:
                    filedataupload = FileDataUpload(db=db,
                                                    pipeline_id=pipeline_id,
                                                    file_conn=source_conn,
                                                    db_conn=db_conn,
                                                    engine=engine,
                                                    file_list=conn_exts,
                                                    source_type='lfs')
                    background_tasks.add_task(filedataupload.load_file_data, job_id)
                    return {"status": "Data upload for the files started", "job_id": job_id}

                elif source_conn.ga_property_id:
                    googleAnalyticsDataLoad = GoogleAnalyticsDataLoad(db=db,
                                                                      pipeline_id=pipeline_id,
                                                                      ga_conn=source_conn,
                                                                      dest_db_conn=db_conn,
                                                                      dest_db_engine=engine,
                                                                      connection_exts=conn_exts)
                    background_tasks.add_task(googleAnalyticsDataLoad.load_data, job_id)
                    return {"status": "Data upload for the google analytics started", "job_id": job_id}
                elif str(source_conn.db_type).upper() == 'RESTAPI':
                    restApiConnector = RestApiConnector(db=db,
                                                        pipeline_id=pipeline_id,
                                                        source_db_conn=source_conn,
                                                        dest_db_conn=db_conn,
                                                        dest_db_engine=engine)
                    # background_tasks.add_task(restApiConnector.load_data, job_id)
                    restApiConnector.load_data(job_id)
                    return {"status": "Data upload for restapi started", "job_id": job_id}
                elif str(source_conn.db_type).upper() == 'X':
                    xDataLoad = XDataLoad(db=db,
                                          pipeline_id=pipeline_id,
                                          source_db_conn=source_conn,
                                          dest_db_conn=db_conn,
                                          dest_db_engine=engine)
                    xDataLoad.load_data(job_id=job_id)
                    return {"status": "Data loaded for x", "job_id": job_id}

        elif job_executor == JobExecutor.airflow.value:
            try:
                airflow_username = constants.AIRFLOW_USERNAME
                airflow_password = constants.AIRFLOW_PASSWORD
                airflow_url = constants.AIRFLOW_URL
                dag_id = f'{str(pipeline.name).replace(" ", "_")}_{str(pipeline_id)}'
                url = f'{airflow_url}/api/v1/dags/{dag_id}/dagRuns'

                payload = json.dumps({"conf": {"job_id": job_id}})
                headers = {'Content-Type': 'application/json'}

                response = requests.request("POST",
                                            url,
                                            headers=headers,
                                            auth=HTTPBasicAuth(airflow_username, airflow_password),
                                            data=payload)
                if response.status_code == 200:
                    logger.info(f'response from airflow:{response.text}')
                    return {"status": "Data upload for the files started", "job_id": job_id}
                elif response.status_code == 404:
                    logger.info(f'Error in runing pipeline:{pipeline_id}, system will wait for 60 sec and retry again')
                    time.sleep(60)
                    response = requests.request("POST",
                                                url,
                                                headers=headers,
                                                auth=HTTPBasicAuth(airflow_username, airflow_password),
                                                data=payload)
                    if response.status_code == 200:
                        logger.info(f'response from airflow:{response.text}')
                        return {"status": "Data upload for the files started", "job_id": job_id}
                    else:
                        logger.info(f'response from airflow:{response.text}')
                        return {"status": "Data load job failed to start", "job_id": job_id}
                else:
                    logger.info(f'response from airflow:{response.text}')
                    return {"status": "Data load job failed to start", "job_id": job_id}
            except Exception as ex:
                logger.error(f"Error in running airflow job:{ex}")
                raise Exception(f"Error in running airflow job:{ex}")
    except Exception as ex:
        job_status = 'Completed with errors'
        current_time = datetime.now()
        add_update_job_status(db=db,
                              status=job_status,
                              job_id=job_id,
                              pipeline_id=pipeline_id,
                              job_date_time=current_time)
        # logger.error(f"Error in running job:{ex}")
        print(traceback.format_exc())
        raise Exception(f"Error in running job:{ex}")


def gen_dw_from_source(pipeline_id,
                       job_id,
                       db: Session,
                       current_user: User,
                       mappedData: Dict):
    '''
    generate datawarehouse from source
    '''
    # Query pipeline
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    # job_status = 'Running'
    # current_time = datetime.now()

    # # Create job id for the run and insert into job table for the pipeline id
    # add_update_job_status(db=db,
    #                       status=job_status,
    #                       job_id=job_id,
    #                       pipeline_id=pipeline_id,
    #                       job_date_time=current_time)

    source_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()

    dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()

    try:
        # Source json
        if source_db_conn.db_type == "mysql":
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
        json_file = os.path.join(os.path.join(os.getcwd(),
                                              constants.JSON_FILE_PATH),
                                 constants.SOURCE_JSON_FILE)
        # json_file='/Users/shahbaz/rebiz1/json_files/newsource.json'
        mappedJson = MappedJson(source_json_file=json_file,
                                data=mappedData)
        file_name, mappedJsonData = mappedJson.generate_mapped_json()
        logger.info('Mapped json:- {}'.format(file_name))

        # DimFact Json
        json_file = os.path.join(os.path.join(os.getcwd(),
                                              constants.JSON_FILE_PATH),
                                 constants.MAPPED_JSON_FILE)
        dimFactJson = DimFactJson(mapped_json_file=json_file)
        file_name, dimFactJsonData = dimFactJson.generate_dimfact_json()

        logger.info('DimFact json:- {}'.format(file_name))

        '''
        Generate etl json from mapped json
        '''
        mapped_json_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
                                        constants.MAPPED_JSON_FILE)
        etl_json_file = os.path.join(os.path.join(os.getcwd(),
                                                  constants.JSON_FILE_PATH),
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
        raw_connection = engine.raw_connection()
        dim_fact_json_filename = os.path.join(os.path.join(os.getcwd(),
                                                           constants.JSON_FILE_PATH),
                                              constants.DIMFACT_JSON_FILE)
        etl_json_filename = os.path.join(os.path.join(os.getcwd(),
                                                      constants.JSON_FILE_PATH),
                                         constants.ETL_JSON_FILE)
        if dest_db_conn.db_type == "mysql":

            datawarehouse = Datawarehouse(pipeline_id=pipeline_id,
                                          db=db,
                                          user=current_user,
                                          connection=connection,
                                          raw_connection=raw_connection,
                                          dimfact_json_file=dim_fact_json_filename,
                                          etl_json_file=etl_json_filename,
                                          dw_name=pipeline.dest_schema_name)
        elif dest_db_conn.db_type == "postgres":
            datawarehouse = PostGresDatawarehouse(pipeline_id=pipeline_id,
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

        logger.info(f"Job complete:{job_id}")
        job_status = 'Completed'
        current_time = datetime.now()

        add_update_job_status(db=db,
                              status=job_status,
                              job_id=job_id,
                              pipeline_id=pipeline_id,
                              job_date_time=current_time)

        # Commit changes to database and return the dataset
        db.commit()

        db.refresh(pipeline)

    except Exception as ex:
        job_status = 'Completed with errors'
        current_time = datetime.now()
        add_update_job_status(db=db,
                              status=job_status,
                              job_id=job_id,
                              pipeline_id=pipeline_id,
                              job_date_time=current_time)
        logger.error(f"Error in running job:{ex}")
        raise Exception(f"Error in running job:{ex}")
