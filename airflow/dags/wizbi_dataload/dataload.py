import logging
from datetime import datetime

from wizbi_dataload.db.auth.dbconnection import DatabaseConnection
from wizbi_dataload.db.models.models import (
    Audit,
    Connection_Ext,
    Db_Conn,
    Job,
    Pipeline,
    Source_Db_Mapping,
)
from wizbi_dataload.db.session import get_db
from wizbi_dataload.db.views.filedataload import FileDataUpload
from wizbi_dataload.db.views.gadataload import GoogleAnalyticsDataLoad
from wizbi_dataload.db.views.job import add_update_job_status
from wizbi_dataload.db.views.restapi import RestApiConnector
from wizbi_dataload.enums import PipelineType
from wizbi_dataload.etlload import EtlLoad

logger = logging.getLogger(__name__)


class DataLoad:
    def __init__(self, pipeline_id, user_name) -> None:
        self.db = next(get_db())
        self.pipeline_id = pipeline_id
        self.user_name = user_name

    def val_source_db_conn(self):
        """
        Validate source database connection
        """
        # Query pipeline table to get all details
        self.pipeline = (
            self.db.query(Pipeline).filter(Pipeline.id == self.pipeline_id).first()
        )

        # Query da_conn table using source db conn id
        source_db_conn = (
            self.db.query(Db_Conn)
            .filter(Db_Conn.id == self.pipeline.db_conn_source_id)
            .first()
        )

        if source_db_conn.db_type == 'sqlserver':
            schema = source_db_conn.db_name
        else:
            schema = self.pipeline.source_schema_name

        if str(source_db_conn.db_type).lower() in ['mysql', 'sqlserver', 'postgres']:
            # Create source database connection
            sourcedbcon = DatabaseConnection(database_type=source_db_conn.db_type,
                                             username=source_db_conn.db_username,
                                             password=source_db_conn.db_password,
                                             host=source_db_conn.db_host,
                                             port=source_db_conn.db_port,
                                             schemas=schema)
            _ = sourcedbcon.get_connection()
            logger.info("Validated source database connection")
        elif source_db_conn.s3_access_key_id:
            logger.info("Validating s3 bucket access")
        elif source_db_conn.lfs_path:
            logger.info("Validating local file system path access")
        elif str(source_db_conn.db_type).upper() == 'RESTAPI':
            logger.info("Validating rest api connection")

    def val_target_db_conn(self):
        """
        Validate target/destination database connection
        """
        # Query pipeline table to get all details
        pipeline = (
            self.db.query(Pipeline).filter(Pipeline.id == self.pipeline_id).first()
        )

        if pipeline.pipeline_type == PipelineType.ETL.value\
           or pipeline.pipeline_type == PipelineType.ELT.value:
            # Query da_conn table using dest db conn id
            dest_db_conn = (
                self.db.query(Db_Conn)
                .filter(Db_Conn.id == pipeline.db_conn_dest_id)
                .first()
            )

            if dest_db_conn.db_type == 'sqlserver':
                schema = dest_db_conn.db_name
            elif str(dest_db_conn.db_type).lower().startswith('oracle'):
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
            _ = targetdbcon.get_connection()
            logger.info("Validated target/destination database connection")
        elif pipeline.pipeline_type == PipelineType.DATALAKE.value:
            # TODO add logic to validate dbt project setup
            logger.info("Validated target/destination dbt/duckdb settings")

    def load_data(self, job_id, load_type, load_key):
        """
        Run data pipeline
        """
        job_status = "Running"
        current_time = datetime.now()
        if job_id is None:
            time_stamp = current_time.timestamp()
            job_id = str(time_stamp).replace(".", "_") + "_" + self.user_name + "_airflow"

        # Create job id for the run and insert into job table for the pipeline id
        add_update_job_status(db=self.db,
                              status=job_status,
                              job_id=job_id,
                              pipeline_id=self.pipeline_id,
                              job_date_time=current_time)

        # Query pipeline table to get all details
        pipeline = (self.db.query(Pipeline).filter(Pipeline.id == self.pipeline_id).first())

        # Query da_conn table using source db conn id
        source_db_conn = (self.db.query(Db_Conn)
                                 .filter(Db_Conn.id == pipeline.db_conn_source_id)
                                 .first())

        if str(pipeline.pipeline_type).upper() == PipelineType.ETL.value:  # "ETL":
            # Query da_conn table using dest db conn id
            dest_db_conn = (self.db.query(Db_Conn)
                                   .filter(Db_Conn.id == pipeline.db_conn_dest_id)
                                   .first())

            # Get source db mapping using pipeline id
            source_db_mapping = (self.db.query(Source_Db_Mapping)
                                        .filter(Source_Db_Mapping.pipeline_id == self.pipeline_id)
                                        .first())
            if source_db_conn.db_type == "sqlserver":
                schema = source_db_conn.db_name
            elif str(source_db_conn.db_type).lower().startswith('oracle'):
                schema = dest_db_conn.db_name
            else:
                schema = pipeline.source_schema_name

            # Create source database connection
            sourcedbcon = DatabaseConnection(database_type=source_db_conn.db_type,
                                             username=source_db_conn.db_username,
                                             password=source_db_conn.db_password,
                                             host=source_db_conn.db_host,
                                             port=source_db_conn.db_port,
                                             schemas=schema)
            source_con = sourcedbcon.get_connection()
            source_engine = sourcedbcon.get_engine()

            # Create target database connection
            targetdbcon = DatabaseConnection(database_type=dest_db_conn.db_type,
                                             username=dest_db_conn.db_username,
                                             password=dest_db_conn.db_password,
                                             host=dest_db_conn.db_host,
                                             port=dest_db_conn.db_port,
                                             schemas=pipeline.dest_schema_name)
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
                              pipeline_id=self.pipeline_id,
                              db=self.db,
                              user_name=self.user_name,
                              json_data_yn=True)
            # Run data load
            record_count = etlload.load_data(job_id, load_type, load_key)
            logger.info(f"Data load with status : {record_count}")
            return record_count
        elif str(pipeline.pipeline_type).upper() == PipelineType.ELT.value:  # "Staging (ELT)":
            # source connection
            try:
                source_conn = (self.db.query(Db_Conn)
                                      .filter(Db_Conn.id == pipeline.db_conn_source_id)
                                      .first())
            except Exception as ex:
                raise Exception(f"Invalid File Connection: {ex}")

            conn_exts = (self.db.query(Connection_Ext)
                                .filter(Connection_Ext.db_conn_id == source_conn.id)
                                .all())

            # destination connection
            try:
                db_conn = (self.db.query(Db_Conn)
                                  .filter(Db_Conn.id == pipeline.db_conn_dest_id)
                                  .first())
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
                filedataupload = FileDataUpload(db=self.db,
                                                pipeline_id=self.pipeline_id,
                                                file_conn=source_conn,
                                                db_conn=db_conn,
                                                engine=engine,
                                                file_list=conn_exts,
                                                source_type="s3")
                load_status = filedataupload.load_file_data(job_id)

                # return {"message": f"Successfuly uploaded {[file.file_name for file in file_list]}"}
                logger.info(f"status: {load_status}, job_id: {job_id}")

            # Upload data from local file system files
            elif source_conn.lfs_path:
                filedataupload = FileDataUpload(db=self.db,
                                                pipeline_id=self.pipeline_id,
                                                file_conn=source_conn,
                                                db_conn=db_conn,
                                                engine=engine,
                                                file_list=conn_exts,
                                                source_type="lfs")
                load_status = filedataupload.load_file_data(job_id)

                logger.info(f"status: {load_status}, job_id: {job_id}")

            # Upload google analytics data
            elif source_conn.ga_property_id:
                googleAnalyticsDataLoad = GoogleAnalyticsDataLoad(db=self.db,
                                                                  pipeline_id=self.pipeline_id,
                                                                  ga_conn=source_conn,
                                                                  dest_db_conn=db_conn,
                                                                  dest_db_engine=engine,
                                                                  connection_exts=conn_exts)
                load_status = googleAnalyticsDataLoad.load_data(job_id)
                logger.info(f"status: {load_status}, job_id: {job_id}")
            elif str(source_conn.db_type).upper() == 'RESTAPI':
                restApiConnector = RestApiConnector(db=self.db,
                                                    pipeline_id=self.pipeline_id,
                                                    source_db_conn=source_conn,
                                                    dest_db_conn=db_conn,
                                                    dest_db_engine=engine)
                load_status = restApiConnector.load_data(job_id)
                logger.info(f'status: {load_status}, job_id: {job_id}')
            return load_status

    def get_val_etl_type(self):
        pipeline = self.db.query(Pipeline).filter(Pipeline.id == self.pipeline_id).first()
        return pipeline.pipeline_type

    def add_audit(self, job_id):
        logger.info("Adding rows in audit table")
        job = self.db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            job_status = 'Running'
            current_time = datetime.now()
            add_update_job_status(self.db,
                                  status=job_status,
                                  job_id=job_id,
                                  pipeline_id=self.pipeline_id,
                                  job_date_time=current_time)
            job = self.db.query(Job).filter(Job.job_id == job_id).first()

        audit = self.db.query(Audit).filter(Audit.job_id == job.id).first()

        if audit:
            pass
        else:
            audit = Audit(pipeline_id=self.pipeline_id,
                          job_id=job.id,
                          load_date=datetime.now())
            self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit.id

    def val_data_load(self):
        logger.info("Validated data load.")

    def update_pipeline_status(self, job_id, total_fact_row):
        pipeline = (
            self.db.query(Pipeline).filter(Pipeline.id == self.pipeline_id).first()
        )
        pipeline.status = "Active"
        self.db.commit()
        self.db.refresh(pipeline)

        logger.info(job_id)
        job = self.db.query(Job).filter(Job.job_id == job_id).first()
        audit = self.db.query(Audit).filter(Audit.job_id == job.id).first()
        audit.inserts = total_fact_row
        logger.info(f'Updated fact row {total_fact_row} in audit table for job id {job_id}')
        # Commit changes to database and return the dataset
        self.db.commit()
        self.db.refresh(audit)
        logger.info("Updated pipeline status to Active")

    def send_notification(self, job_id):
        logger.info("Sent mail")
        current_time = datetime.now()
        job_status = 'Success'
        add_update_job_status(self.db,
                              status=job_status,
                              job_id=job_id,
                              pipeline_id=self.pipeline_id,
                              job_date_time=current_time)

    def update_job_status(self, job_id):
        logger.info("Updating job status for error case")
        job_status = 'Completed with errors'
        current_time = datetime.now()

        # Create job id for the run and insert into job table for the pipeline id
        add_update_job_status(
            db=self.db,
            status=job_status,
            job_id=job_id,
            pipeline_id=self.pipeline_id,
            job_date_time=current_time,
        )
        logger.info("Updated job status for error case")


if __name__ == "__main__":
    dataload = DataLoad()
    dataload.load_data(1006, "testuser")
