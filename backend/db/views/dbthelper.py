import os
import tempfile

import boto3
import paramiko
import structlog
from fastapi import HTTPException, status
from jinja2 import Environment, FileSystemLoader, Undefined
from sqlalchemy.orm import Session

import constants
from db.enums import DbtHostAuthType
from db.models.models import Db_Conn, Pipeline, Source_Db_Mapping

logger = structlog.getLogger(__name__)


model_query_template = '''
select {{ aggr_func }}({{ column_name }})
from {{ table_name }}
group by {{ group_by_columns }};
'''

materialized = 'config(materialized="table")'


class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return


class DbtHelper:
    def __init__(self):
        self.hostname = constants.DBT_HOSTNAME
        self.port = constants.DBT_HOST_PORT
        self.username = constants.DBT_HOST_USERNAME
        self.password = constants.DBT_HOST_PASSWORD
        self.project_name = None
        self.model_name = None
        self.profile_name = constants.DBT_PROFILE_NAME
        self.project_path = constants.DBT_PROJECT_PATH
        self.dbt_path = constants.DBT_PATH
        self.dbt_host_pem_file = constants.DBT_HOST_PEM_FILE
        self.dbt_host_auth_type = constants.DBT_HOST_AUTH_TYPE
        self.client = None
        self._sftp_client = None
        self.template_path = os.path.join(os.getcwd(), constants.TEMPLATES_PATH)

    def create_remote_client(self, client_type=None):
        '''
        create ssh client to the dbt host machine
        '''
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.dbt_host_auth_type.upper() == DbtHostAuthType.PASSWORD.value:
            self.client.load_system_host_keys()
            self.client.connect(self.hostname, self.port, self.username, self.password)
        elif self.dbt_host_auth_type.upper() == DbtHostAuthType.KEY.value:
            key = paramiko.RSAKey.from_private_key_file(self.dbt_host_pem_file)
            self.client.connect(self.hostname, username=self.username, pkey=key)

        if client_type == 'scp':
            self._sftp_client = self.client.open_sftp()

    def create_project(self):
        '''
        create db project and remove example model files
        '''
        create_project_command = f"(cd {self.project_path}; {self.dbt_path} init {self.project_name}\
              --profile {self.profile_name})"
        _ = self.create_remote_client()
        stdin, stdout, stderr = self.client.exec_command(create_project_command)
        exit_status = stdout.channel.recv_exit_status()
        logger.info(f'dbt project {self.project_name} setup completed with status {exit_status}')
        if exit_status == 0:
            for stdout in stdout.readlines():
                logger.info(stdout)
        else:
            for stderr in stderr.readlines():
                logger.error(stderr)

        # delete example models from project path
        dbt_project_path = os.path.join(self.project_path, self.project_name)
        dbt_model_path = os.path.join(dbt_project_path, 'models')
        example_model_path = os.path.join(dbt_model_path, 'example')
        print(example_model_path)
        stdin, stdout, stderr = self.client.exec_command(f"rm -rf {example_model_path}")

        exit_status = stdout.channel.recv_exit_status()
        logger.info(f'Example model removal status {exit_status}')
        if exit_status == 0:
            for stdout in stdout.readlines():
                logger.info(stdout)
        else:
            for stderr in stderr.readlines():
                logger.error(stderr)

        self.client.close()
        return exit_status

    def update_project_config(self):
        file_loader = FileSystemLoader(self.template_path)
        env = Environment(loader=file_loader)
        dbt_project_template = env.get_template('dbt_project.template.yml')
        dbt_project = dbt_project_template.render(project_name=self.project_name,
                                                  profile_name=self.profile_name)

        print(dbt_project)
        # create project file
        temp_project_file = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
        logger.info(f'temp_project_file : {temp_project_file.name}')

        with open(temp_project_file.name, 'w') as f:
            f.write(dbt_project)
            logger.info(f'created dbt project file: {temp_project_file.name}')

        # copy model to remote dbt project
        local_file = temp_project_file.name
        dbt_project_path = f"{self.project_path}/{self.project_name}/dbt_project.yml"
        self.create_remote_client('scp')
        self._sftp_client.put(local_file, dbt_project_path)
        self.client.close()

        # delete temp file
        os.remove(temp_project_file.name)

    def create_model(self, db: Session, user_id: int, pipeline_id: int):
        # query pipeline
        pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

        if not pipeline:
            logger.error('Pipeline not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")

        # query iceberg db connection
        iceberg_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()

        glue_client = boto3.client("glue",
                                   region_name=iceberg_db_conn.s3_bucket_region,
                                   aws_access_key_id=iceberg_db_conn.s3_access_key_id,
                                   aws_secret_access_key=iceberg_db_conn.s3_secret_access_key)

        # query source db mapping
        source_db_mapping = db.query(Source_Db_Mapping).filter(Source_Db_Mapping.pipeline_id == pipeline_id).first()

        if not source_db_mapping:
            logger.error('Source Db Mapping not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source Db Mapping not found")

        user_input = source_db_mapping.user_input
        user_input_list = user_input.get('model_mappings')

        # query template
        # query_template = Template(model_query_template)
        file_loader = FileSystemLoader(self.template_path)
        env = Environment(loader=file_loader)
        query_template = env.get_template('model.template.sql')

        for user_input in user_input_list:
            database_name = user_input.get('database_name')
            table_name = user_input.get('table_name')
            table_preview = user_input.get('table_preview')

            try:
                response = glue_client.get_table(DatabaseName=database_name, Name=table_name)
                metadata_json = response.get('Table').get('Parameters').get('metadata_location')
                metadata_scan_table = f'iceberg_scan("{metadata_json}")'
            except Exception as e:
                logger.error(f'Error getting table metadata.json: {e}')
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Error getting table metadata.json")

            for column in table_preview:
                column_name = column.get('name')
                is_selected = column.get('is_selected')
                group_by = column.get('group_by')
                group_by_columns = ', '.join(group_by)
                aggregate_function = column.get('aggregate_function')
                model_name = table_name + '_' + column_name + '_' + aggregate_function

                if is_selected:
                    model_query = query_template.render(aggr_func=aggregate_function,
                                                        column_name=column_name,
                                                        table_name=metadata_scan_table,
                                                        group_by_columns=group_by_columns,
                                                        materialized=materialized)
                    print(model_query)
                    # create model
                    temp_model_file = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
                    logger.info(f'temp_model_file: {temp_model_file.name}')

                    with open(temp_model_file.name, 'w') as f:
                        f.write(model_query)
                        logger.info(f'created dbt model sql file: {temp_model_file.name}')

                    # copy model to remote dbt project
                    local_file = temp_model_file.name
                    dbt_model_path = f"{self.project_path}/{self.project_name}/models/{model_name}.sql"
                    self.create_remote_client('scp')
                    self._sftp_client.put(local_file, dbt_model_path)
                    self.client.close()

                    # delete temp file
                    os.remove(temp_model_file.name)

    def setup_project(self, db: Session, pipeline_id: int, user_id: int):
        '''
        setup project
        :return: project name
        '''

        # query pipeline to get the name of pipeline
        pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

        if not pipeline:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")

        self.project_name = str(pipeline.name).replace(" ", "_") + '_dbt'

        # create dbt project
        self.create_project()
        # update project config
        self.update_project_config()
        # create model
        self.create_model(db=db, user_id=user_id, pipeline_id=pipeline_id)

        # update pipeline status to ready for etl
        pipeline.status = 'Ready for ETL'
        db.commit()
        db.refresh(pipeline)

        return {'project_name': self.project_name,
                'project_path': self.project_path}


if __name__ == "__main__":
    dbtHelper = DbtHelper('localhost', 22, 'raj', 'ubuntu', 'test', 'test')
    dbtHelper.create_project()
    dbtHelper.create_model()
