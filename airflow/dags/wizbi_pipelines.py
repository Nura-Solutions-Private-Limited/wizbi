import json
import logging
import os
import sys
import traceback
from datetime import datetime
from functools import partial

from airflow import DAG
from airflow.models import Variable
from airflow.models.baseoperator import chain_linear
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.utils.trigger_rule import TriggerRule
from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig

from wizbi_dataload.dataload import DataLoad

logger = logging.getLogger(__name__)

DBT_PROJECT_PATH = None
DBT_EXECUTABLE_PATH = Variable.get("dbt_executable_path")

profile_config = ProfileConfig(
    profile_name=Variable.get("dbt_profile_name"),
    target_name=Variable.get("dbt_target_name"),
    profiles_yml_filepath=Variable.get("dbt_profile_path"),
)

execution_config = ExecutionConfig(dbt_executable_path=DBT_EXECUTABLE_PATH)

AWS_ACCESS_KEY_ID = Variable.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = Variable.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = Variable.get("AWS_REGION")
dbt_env_vars = {
    "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
    "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
    "AWS_REGION": AWS_REGION,
}


def create_dag(
    dag_id,
    schedule,
    dag_number,
    default_args,
    username,
    pipeline_id,
    etl_json,
    pipeline_type,
    pipeline_status,
    sh_job_id,
):
    """
    Function to create dynamic dags
    """

    def update_pipeline_run_status(context):
        """
        Update pipeline status
        """
        job_id = context["dag_run"].conf.get("job_id")
        logger.info(f"Updating pipeline job run status for job_id:{job_id}")
        dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
        dataload.update_job_status(job_id=job_id)
        logger.info(f"Updated pipeline job run status for job_id:{job_id}")

    def add_audit(**kwargs):
        """
        Add job entry in audit table to track rows counts
        """
        try:
            logger.info("Add row in audit table")

            # generate job id and add in conf if not present
            current_time = datetime.now()
            time_stamp = current_time.timestamp()
            sh_job_id = str(time_stamp).replace(".", "_") + "_" + "test" + "_airflow"

            if kwargs["dag_run"].conf.get("job_id") is None:
                kwargs["dag_run"].conf["job_id"] = sh_job_id

            job_id = kwargs["dag_run"].conf.get("job_id")
            dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
            dataload.add_audit(job_id=job_id)
            logger.info("Added row in audit table")
            # return 'dim_data_load'
        except Exception as ex:
            logger.error(f"Error in adding audit rows:{str(ex)}")
            raise (f"Error in adding audit rows:{str(ex)}")
            # return 'dataload_fail_notification'

    def validate_source(**kwargs):
        """
        Validate source database connection
        """
        try:
            logger.info("Source connection validation start")
            dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
            dataload.val_source_db_conn()
            logger.info("Source connection validation end")
            # return 'dim_data_load'
        except Exception as ex:
            logger.error(f"Error in validating source connection:{str(ex)}")
            raise Exception(f"Error in validating source connection:{str(ex)}")
            # return 'dataload_fail_notification'

    def validate_target(**kwargs):
        """
        Validate target database connection
        """
        try:
            logger.info("Target connection validation start")
            dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
            dataload.val_target_db_conn()
            logger.info("Target connection validation end")
            # return 'dim_data_load'
        except Exception as ex:
            logger.error(f"Error in validating source connection:{str(ex)}")
            raise Exception(f"Error in validating source connection:{str(ex)}")
            # return 'dataload_fail_notification'

    def data_load_stage(**kwargs):
        # load data into staging database tables for staging etl
        job_id = kwargs["dag_run"].conf.get("job_id")
        dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
        status = dataload.load_data(job_id=job_id, load_type=None, load_key=None)
        logger.info(f"Staging etl job:{job_id} run completed with status:{status}")

    def data_load_dim(table, job_id, **kwargs):
        """
        Run wizbi dataload for the given pipeline_id
        """
        try:
            logger.info(f"Data load started for the job id:{job_id}")
            dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
            record_count = dataload.load_data(job_id=job_id, load_type="dim", load_key=table)

            logger.info(
                f"Data load ended for the job id:{job_id} with {record_count} rows added in dim table: {table}"
            )
            # return 'validate_data_load'
        except Exception as ex:
            logger.error(f"Error in data load :{str(ex)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Error in data load :{str(ex)}")
            # return 'dataload_fail_notification'

    def data_load_fact(fact_metric, job_id, **kwargs):
        """
        Run wizbi dataload for the given pipeline_id
        """
        try:
            logger.info(f"Data load started for the job id:{job_id}")
            dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
            record_count = dataload.load_data(job_id=job_id, load_type="fact", load_key=fact_metric)

            logger.info(f"Data load ended for the job id:{job_id} with {record_count} rows added in fact table.")
            # return 'validate_data_load'
            return record_count if record_count else 0
        except Exception as ex:
            logger.error(f"Error in data load :{str(ex)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Error in data load :{str(ex)}")
            # return 'dataload_fail_notification'

    def update_dim_relations(**kwargs):
        try:
            job_id = kwargs["dag_run"].conf.get("job_id")
            logger.info(f"Dimension fk update started for the job id:{job_id}")
            dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
            dataload.load_data(job_id=job_id, load_type="fks", load_key=None)

            logger.info(f"Dimension fk update ended for the job id:{job_id}")
            # return 'validate_data_load'
        except Exception as ex:
            logger.error(f"Error in data load :{str(ex)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Error in data load :{str(ex)}")
            # return 'dataload_fail_notification'

    def validate_data_load(**kwargs):
        """
        Validate loaded data
        """
        try:
            logger.info("Data validation start")
            dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
            dataload.val_data_load()
            logger.info("Data validation end")
            # return 'update_load_status'
        except Exception as ex:
            logger.error(f"Error in data validation :{str(ex)}")
            raise Exception(f"Error in data validation :{str(ex)}")
            # return 'dataload_fail_notification'

    def validate_dbt_project(**kwargs):
        """
        Validate dbt project
        """
        pass

    def update_status(**kwargs):
        """
        Update pipeline status
        """
        try:
            logger.info("Pipeline status update start")
            job_id = kwargs["dag_run"].conf.get("job_id")
            if kwargs.get("fact_count"):
                total_fact_row = sum(kwargs.get("fact_count"))
            else:
                total_fact_row = 0
            dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
            dataload.update_pipeline_status(job_id=job_id, total_fact_row=total_fact_row)
            logger.info("Pipeline status update end")
            # return 'dataload_pass_notification'
        except Exception as ex:
            logger.error(f"Error in status update :{str(ex)}")
            raise Exception(f"Error in status update :{str(ex)}")
            # return 'dataload_fail_notification'

    def send_notification(**kwargs):
        """
        Send notification for data load job completion
        """
        job_id = kwargs["dag_run"].conf.get("job_id")
        dataload = DataLoad(pipeline_id=pipeline_id, user_name=username)
        dataload.send_notification(job_id=job_id)
        logger.info("send mail")

    dim_list = []
    fact_list = []
    if etl_json:
        etl_json_data = json.loads(etl_json)
    else:
        etl_json_data = []
    for schema in etl_json_data:
        # Get table data
        tables = schema.get("Tables")
        for table in tables:
            table_type = table.get("type")
            source_table = table.get("SourceTable")
            columns = table.get("Columns")
            # dimension tables
            # if table_type == 'dim' and source_table == 'customers':
            if table_type == "dim":
                dim_list.append([source_table])
            elif table_type == "fact":
                for column in columns:
                    fact_column = column.get("LookupColumn")
                    fact_list.append([fact_column])

    dag = DAG(
        dag_id,
        schedule=schedule,
        default_args=default_args,
        is_paused_upon_creation=False,
        params={"job_id": sh_job_id},
        catchup=False,
    )

    with dag:
        if pipeline_type == "ELT":
            add_audit_row = PythonOperator(
                task_id="start_data_load",
                python_callable=add_audit,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            validate_data_source = PythonOperator(
                task_id="validate_data_source",
                python_callable=validate_source,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            validate_data_target = PythonOperator(
                task_id="validate_data_target",
                python_callable=validate_target,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            load_staging_data = PythonOperator(
                task_id="staging_data_load",
                python_callable=data_load_stage,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            validate_loaded_data = PythonOperator(
                task_id="validate_data_load",
                python_callable=validate_data_load,
                on_failure_callback=update_pipeline_run_status,
                trigger_rule=TriggerRule.NONE_FAILED,
                provide_context=True,
            )

            update_load_status = PythonOperator(
                task_id="update_load_status",
                python_callable=update_status,
                on_failure_callback=update_pipeline_run_status,
                trigger_rule=TriggerRule.NONE_FAILED,
                provide_context=True,
            )

            pass_notification = PythonOperator(
                task_id="dataload_pass_notification",
                python_callable=send_notification,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            # ELT Task pipeline

            # (
            #     add_audit_row
            #     >> [validate_data_source, validate_data_target]
            #     >> load_staging_data
            #     >> validate_loaded_data
            #     >> update_load_status
            #     >> pass_notification
            # )

            add_audit_row.set_downstream(validate_data_source)
            add_audit_row.set_downstream(validate_data_target)
            validate_data_target.set_downstream(load_staging_data)
            validate_data_source.set_downstream(load_staging_data)
            load_staging_data.set_downstream(validate_loaded_data)
            validate_loaded_data.set_downstream(update_load_status)
            update_load_status.set_downstream(pass_notification)

        elif pipeline_type == "ETL":
            add_audit_row = PythonOperator(
                task_id="start_data_load",
                python_callable=add_audit,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            validate_data_source = PythonOperator(
                task_id="validate_data_source",
                python_callable=validate_source,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            validate_data_target = PythonOperator(
                task_id="validate_data_target",
                python_callable=validate_target,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            load_dim_data = PythonOperator.partial(
                task_id="dim_data_load",
                python_callable=data_load_dim,
                on_failure_callback=update_pipeline_run_status,
                op_kwargs={"job_id": "{{ dag_run.conf.get('job_id')}}"},
                max_active_tis_per_dag=4
                #  provide_context=True
            ).expand(op_args=dim_list)

            load_fact_data = PythonOperator.partial(
                task_id="fact_data_load",
                python_callable=data_load_fact,
                on_failure_callback=partial(update_pipeline_run_status),
                op_kwargs={"job_id": "{{ dag_run.conf.get('job_id')}}"},
                max_active_tis_per_dag=4
                #  provide_context=True
            ).expand(op_args=fact_list)

            update_dim_fks = PythonOperator(
                task_id="update_dim_fk",
                python_callable=update_dim_relations,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            validate_loaded_data = PythonOperator(
                task_id="validate_data_load",
                python_callable=validate_data_load,
                on_failure_callback=update_pipeline_run_status,
                trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
                provide_context=True,
            )

            update_load_status = PythonOperator(
                task_id="update_load_status",
                python_callable=update_status,
                on_failure_callback=update_pipeline_run_status,
                trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
                op_kwargs={"fact_count": load_fact_data.output},
                provide_context=True,
            )

            pass_notification = PythonOperator(
                task_id="dataload_pass_notification",
                python_callable=send_notification,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            # ETL Task pipeline
            # (
            #     add_audit_row
            #     >> [validate_data_source, validate_data_target]
            #     >> load_dim_data
            #     >> load_fact_data
            #     >> update_dim_fks
            #     >> validate_loaded_data
            #     >> update_load_status
            #     >> pass_notification
            # )

            add_audit_row.set_downstream(validate_data_source)
            add_audit_row.set_downstream(validate_data_target)
            validate_data_target.set_downstream(load_dim_data)
            validate_data_source.set_downstream(load_dim_data)
            load_dim_data.set_downstream(load_fact_data)
            load_fact_data.set_downstream(update_dim_fks)
            update_dim_fks.set_downstream(validate_loaded_data)
            validate_loaded_data.set_downstream(update_load_status)
            update_load_status.set_downstream(pass_notification)

        elif pipeline_type == "DATALAKE":
            add_audit_row = PythonOperator(
                task_id="start_data_load",
                python_callable=add_audit,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            validate_data_source = PythonOperator(
                task_id="validate_data_source",
                python_callable=validate_source,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            validate_data_target = PythonOperator(
                task_id="validate_data_target",
                python_callable=validate_target,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            validate_dbt_task = PythonOperator(
                task_id="validate_dbt_project",
                python_callable=validate_dbt_project,
                on_failure_callback=update_pipeline_run_status,
            )

            if pipeline_type == "DATALAKE" and pipeline_status in ["Ready for ETL", "Active"]:
                dbt_task = DbtTaskGroup(
                    group_id="dbt_task",
                    project_config=ProjectConfig(DBT_PROJECT_PATH, env_vars=dbt_env_vars),
                    profile_config=profile_config,
                    execution_config=execution_config,
                    default_args={"on_failure_callback": update_pipeline_run_status},
                )
            else:
                dbt_task = EmptyOperator(task_id="dbt_task")

            validate_loaded_data = PythonOperator(
                task_id="validate_data_load",
                python_callable=validate_data_load,
                on_failure_callback=update_pipeline_run_status,
                trigger_rule=TriggerRule.NONE_FAILED,
                provide_context=True,
            )

            update_load_status = PythonOperator(
                task_id="update_load_status",
                python_callable=update_status,
                on_failure_callback=update_pipeline_run_status,
                trigger_rule=TriggerRule.NONE_FAILED,
                # op_kwargs={"fact_count": load_fact_data.output},
                provide_context=True,
            )

            pass_notification = PythonOperator(
                task_id="dataload_pass_notification",
                python_callable=send_notification,
                on_failure_callback=update_pipeline_run_status,
                provide_context=True,
            )

            # DATALAKE Task pipeline
            # (
            #     add_audit_row
            #     >> [validate_data_source, validate_data_target]
            #     >> validate_dbt_task
            #     >> dbt_task
            #     >> validate_loaded_data
            #     >> update_load_status
            #     >> pass_notification
            # )  # NOQA

            add_audit_row.set_downstream(validate_data_source)
            add_audit_row.set_downstream(validate_data_target)
            validate_data_target.set_downstream(validate_dbt_task)
            validate_data_source.set_downstream(validate_dbt_task)
            validate_dbt_task.set_downstream(dbt_task)
            dbt_task.set_downstream(validate_loaded_data)
            validate_loaded_data.set_downstream(update_load_status)
            update_load_status.set_downstream(pass_notification)

    return dag


# Use mysqlhook to connect to rebiz database
mysql_hook = MySqlHook(mysql_conn_id="wizbi")
cursor = mysql_hook.get_cursor()
sql_query = (
    "select p.id, p.name, u.username, ps.schedule, "
    "sdm.etl_json, p.pipeline_type, p.created_date, "
    "p.status "
    "from pipeline p "
    "join user u "
    "on p.user_id =u.id "
    "left join source_db_mapping sdm "
    "on p.id = sdm.pipeline_id "
    "left join pipeline_schedule ps "
    "on p.id = ps.pipeline_id"
)
cursor.execute(sql_query)
data = cursor.fetchall()

# Create dag for each pipeline
for d in data:
    pipeline_id = d[0]
    dag_id = "{}_{}".format(str(d[1]).replace(" ", "_"), str(d[0]))
    username = str(d[2])
    etl_json = d[4]
    pipeline_type = d[5]
    pipeline_created_date = d[6]
    pipeline_status = d[7]
    project_name = str(d[1]).replace(" ", "_") + "_dbt"
    DBT_PROJECT_PATH = f"{os.environ['AIRFLOW_HOME']}/dags/dbt/{project_name}"

    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    sh_job_id = str(time_stamp).replace(".", "_") + "_" + username + "_airflow"

    default_args = {
        "owner": "airflow",
        "start_date": pipeline_created_date if pipeline_created_date else datetime(2023, 1, 1),
        "catchup": False,
    }

    schedule = d[3]
    dag_number = d[0]

    globals()[dag_id] = create_dag(
        dag_id,
        schedule,
        dag_number,
        default_args,
        username,
        pipeline_id,
        etl_json,
        pipeline_type,
        pipeline_status,
        sh_job_id,
    )
