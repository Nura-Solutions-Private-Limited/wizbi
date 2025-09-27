import sqlalchemy as sa
from cryptography.fernet import Fernet
from sqlalchemy import Index
from sqlalchemy.dialects.mysql import BLOB, JSON, TINYINT
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

import constants
from db.session import engine

metadata = sa.MetaData()
Base = declarative_base(metadata=metadata)


class EncryptedTextField(sa.types.UserDefinedType):
    def get_col_spec(self):
        return "BYTEA"

    def bind_processor(self, dialect):
        key = constants.ENCRYPTION_KEY
        f = Fernet(key)

        def process(value):
            if value is not None:
                return f.encrypt(value.encode('utf-8'))
            return None
        return process

    def result_processor(self, dialect, coltype):
        key = constants.ENCRYPTION_KEY
        f = Fernet(key)

        def process(value):
            if value is not None:
                try:
                    return f.decrypt(value).decode('utf-8')
                except:  # noqa: E722
                    return value
            return None
        return process


class Audit(Base):

    __tablename__ = "audit"

    id = sa.Column(sa.Integer(), primary_key=True)
    pipeline_id = sa.Column(sa.Integer(), sa.ForeignKey("pipeline.id"), server_default="NULL")
    job_id = sa.Column(sa.Integer(), sa.ForeignKey("job.id"), server_default="NULL")
    errors = sa.Column(sa.Integer(), server_default="NULL")
    warnings = sa.Column(sa.Integer(), server_default="NULL")
    inserts = sa.Column(sa.Integer(), server_default="NULL")
    duplicates = sa.Column(sa.Integer(), server_default="NULL")
    skipped = sa.Column(sa.Integer(), server_default="NULL")
    notes = sa.Column(sa.String(1024), server_default="NULL")
    load_date = sa.Column(sa.DateTime(), server_default="NULL")

    # __table_args__ = (Index("fk_audit_pipeline", pipeline_id), Index("fk_audit_job", job_id))


class Connection_Ext(Base):

    __tablename__ = "connection_ext"

    id = sa.Column(sa.Integer(), primary_key=True)
    file_name = sa.Column(sa.Text())
    file_description = sa.Column(sa.Text())
    db_conn_id = sa.Column(sa.Integer(), sa.ForeignKey("db_conn.id"), server_default="NULL")
    dimension_metric = sa.Column(JSON(), server_default="NULL")
    dimension = sa.Column(sa.String(250), server_default="NULL")

    # __table_args__ = Index("fk_db_conn", db_conn_id)


class ConnectorType(Base):

    __tablename__ = "connector_type"

    id = sa.Column(sa.Integer(), primary_key=True)
    connector_type = sa.Column(sa.String(50), server_default="NULL")
    description = sa.Column(sa.String(200), server_default="NULL")
    type = sa.Column(sa.String(20), server_default="NULL")
    enabled = sa.Column(TINYINT(1), server_default="NULL")
    extra = sa.Column(JSON(), server_default="NULL")
    sub_type = sa.Column(sa.String(50), server_default="NULL")


class Dashboard(Base):

    __tablename__ = "dashboard"

    id = sa.Column(sa.Integer(), primary_key=True)
    group_id = sa.Column(sa.Integer(), sa.ForeignKey("group.id"), server_default="NULL")
    name = sa.Column(sa.String(1024), server_default="NULL")
    link = sa.Column(sa.String(1024), server_default="NULL")
    isactive = sa.Column(TINYINT(1), server_default="1")
    updated_date = sa.Column(sa.DateTime(), server_default="NULL")

    # __table_args__ = Index("fk_group_id", group_id)


class Db_Conn(Base):

    __tablename__ = "db_conn"

    id = sa.Column(sa.Integer(), primary_key=True)
    user_id = sa.Column(sa.Integer(), sa.ForeignKey("user.id"), server_default="NULL")
    db_conn_name = sa.Column(sa.String(255), server_default="NULL")
    db_type = sa.Column(sa.String(255), server_default="NULL")
    db_host = sa.Column(sa.String(255), server_default="NULL")
    db_port = sa.Column(sa.Integer(), server_default="NULL")
    db_username = sa.Column(sa.String(255), server_default="NULL")
    # db_password = sa.Column(sa.String(255), server_default="NULL")
    db_password = sa.Column(EncryptedTextField())
    db_name = sa.Column(sa.String(255), server_default="NULL")
    sub_type = sa.Column(sa.String(50), server_default="NULL")
    s3_access_key_id = sa.Column(sa.String(200), server_default="NULL")
    s3_secret_access_key = sa.Column(sa.Text())
    s3_bucket = sa.Column(sa.String(500), server_default="NULL")
    s3_bucket_path = sa.Column(sa.String(500), server_default="NULL")
    s3_bucket_region = sa.Column(sa.String(200), server_default="NULL")
    gdrive_client_id = sa.Column(sa.String(200), server_default="NULL")
    gdrive_client_secret = sa.Column(sa.Text())
    gdrive_access_token = sa.Column(sa.Text())
    gdrive_refresh_token = sa.Column(sa.Text())
    gdrive_token_uri = sa.Column(sa.Text())
    gdrive_scopes = sa.Column(sa.String(500), server_default="NULL")
    gdrive_path = sa.Column(sa.String(500), server_default="NULL")
    gdrive_prefix = sa.Column(sa.String(500), server_default="NULL")
    lfs_path = sa.Column(sa.String(500), server_default="NULL")
    lfs_prefix = sa.Column(sa.String(500), server_default="NULL")
    lfs_mount_point = sa.Column(sa.String(500), server_default="NULL")
    ga_property_id = sa.Column(sa.String(100), server_default="NULL")
    ga_auth_json = sa.Column(JSON(), server_default="NULL")
    iceberg_database = sa.Column(sa.String(200), server_default="NULL")
    iceberg_table = sa.Column(sa.String(100), server_default="NULL")
    duckdb_database = sa.Column(sa.String(200), server_default="NULL")
    duckdb_lfs_path = sa.Column(sa.String(2000), server_default="NULL")
    dbt_project_name = sa.Column(sa.String(200), server_default="NULL")

    # __table_args__ = Index("fk_conn_user", user_id)


class DbEr(Base):

    __tablename__ = "db_er"

    id = sa.Column(sa.Integer(), primary_key=True)
    user_id = sa.Column(sa.Integer(), sa.ForeignKey("user.id"), server_default="NULL")
    db_conn_id = sa.Column(sa.Integer(), sa.ForeignKey("db_conn.id"), server_default="NULL")
    source_er_image = sa.Column(BLOB())
    destination_dw_image = sa.Column(BLOB())

    # __table_args__ = (Index("fk_er_user", user_id), Index("fk_er_conn", db_conn_id))


class Dimension(Base):

    __tablename__ = "ga_dimension"

    id = sa.Column(sa.Integer(), primary_key=True)
    dimension = sa.Column(sa.String(200), server_default="NULL")
    status = sa.Column(TINYINT(1), server_default="NULL")


class Metric(Base):

    __tablename__ = "ga_metric"

    id = sa.Column(sa.Integer(), primary_key=True)
    metric = sa.Column(sa.String(200), server_default="NULL")
    status = sa.Column(TINYINT(1), server_default="NULL")
    dimension_id = sa.Column(sa.Integer(), sa.ForeignKey("ga_dimension.id"), server_default="NULL")

    # __table_args__ = Index("fk_dimension_id", dimension_id)


class Group(Base):

    __tablename__ = "group"

    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.String(255), server_default="NULL")
    description = sa.Column(sa.String(255), server_default="NULL")


class Job(Base):

    __tablename__ = "job"

    id = sa.Column(sa.Integer(), primary_key=True)
    pipeline_id = sa.Column(sa.Integer(), sa.ForeignKey("pipeline.id"), server_default="NULL")
    job_id = sa.Column(sa.String(255), sa.ForeignKey("job.id"), server_default="NULL")
    start_time = sa.Column(sa.DateTime(), server_default="NULL")
    end_time = sa.Column(sa.DateTime(), server_default="NULL")
    status = sa.Column(sa.String(255), server_default="NULL")
    airflow_logs_link = sa.Column(sa.String(255), server_default="NULL")

    # __table_args__ = Index("fk_job_pipeline", pipeline_id)


class Permissions(Base):

    __tablename__ = "permissions"

    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.String(100), nullable=False)
    description = sa.Column(sa.String(250), nullable=False)
    role_id = sa.Column(sa.Integer(), sa.ForeignKey("role.id"), server_default="NULL")
    pipelines_allowed = sa.Column(TINYINT(1), server_default="NULL")
    etl_allowed = sa.Column(TINYINT(1), server_default="NULL")
    connections_allowed = sa.Column(TINYINT(1), server_default="NULL")
    dashboards_allowed = sa.Column(TINYINT(1), server_default="NULL")
    jobs_allowed = sa.Column(TINYINT(1), server_default="NULL")
    audits_allowed = sa.Column(TINYINT(1), server_default="NULL")
    dashboard_ids = sa.Column(JSON(), server_default="NULL")
    report_ids = sa.Column(JSON(), server_default="NULL")
    connection_ids = sa.Column(JSON(), server_default="NULL")
    pipeline_ids = sa.Column(JSON(), server_default="NULL")
    reports_allowed = sa.Column(TINYINT(1), server_default="NULL")
    genai_allowed = sa.Column(TINYINT(1), server_default="NULL")

    # __table_args__ = Index("fk_permissions_role_id", role_id)


class Pipeline(Base):

    __tablename__ = "pipeline"

    id = sa.Column(sa.Integer(), primary_key=True)
    user_id = sa.Column(sa.Integer(), sa.ForeignKey("user.id"), server_default="NULL")
    db_conn_source_id = sa.Column(sa.Integer(), sa.ForeignKey("db_conn.id"), server_default="NULL")
    db_conn_dest_id = sa.Column(sa.Integer(), sa.ForeignKey("db_conn.id"), server_default="NULL")
    name = sa.Column(sa.String(255), server_default="NULL")
    description = sa.Column(sa.String(255), server_default="NULL")
    source_schema_name = sa.Column(sa.String(255), server_default="NULL")
    dest_schema_name = sa.Column(sa.String(255), server_default="NULL")
    airflow_pipeline_name = sa.Column(sa.String(255), server_default="NULL")
    airflow_pipeline_link = sa.Column(sa.String(255), server_default="NULL")
    status = sa.Column(sa.String(255), server_default="NULL")
    pipeline_type = sa.Column(sa.String(100), server_default="NULL")
    created_date = sa.Column(sa.DateTime(), server_default="NULL")


class Pipeline_Schedule(Base):

    __tablename__ = "pipeline_schedule"

    id = sa.Column(sa.Integer(), primary_key=True)
    pipeline_id = sa.Column(sa.Integer(), sa.ForeignKey("pipeline.id"), server_default="NULL")
    schedule = sa.Column(sa.String(100), server_default="NULL")
    created_date = sa.Column(sa.DateTime(), server_default="NULL")
    updated_date = sa.Column(sa.DateTime(), server_default="NULL")


class Report(Base):

    __tablename__ = "report"

    id = sa.Column(sa.Integer(), primary_key=True)
    pipeline_id = sa.Column(sa.Integer(), sa.ForeignKey("pipeline.id"), server_default="NULL")
    type = sa.Column(sa.String(255), server_default="NULL")
    name = sa.Column(sa.String(1000), server_default="NULL")
    sql_query = sa.Column(sa.String(8000), server_default="NULL")
    google_link = sa.Column(sa.String(1024), server_default="NULL")
    google_json = sa.Column(sa.String(5120), server_default="NULL")

    # __table_args__ = Index("fk_report_pipeline", pipeline_id)


class Rest_Api_Db_Conn(Base):

    __tablename__ = "rest_api_conn"

    id = sa.Column(sa.Integer(), primary_key=True)
    method = sa.Column(sa.String(10), server_default="NULL")
    url = sa.Column(sa.String(500), server_default="NULL")
    params = sa.Column(JSON(), server_default="NULL")
    authorization = sa.Column(JSON(), server_default="NULL")
    headers = sa.Column(JSON(), server_default="NULL")
    body = sa.Column(JSON(), server_default="NULL")
    db_conn_id = sa.Column(sa.Integer(), sa.ForeignKey("db_conn.id"), server_default="NULL")
    data_url = sa.Column(sa.String(500), server_default="NULL")
    is_auth_url = sa.Column(TINYINT(1), server_default="NULL")

    # __table_args__ = Index("fk_rest_api_conn_id", db_conn_id)


class X_Conn(Base):
    __tablename__ = "x_conn"

    id = sa.Column(sa.Integer(), primary_key=True)    
    user_name = sa.Column(sa.String(255), nullable=False)
    bearer_token = sa.Column(sa.String(512), nullable=True)
    access_token = sa.Column(sa.String(512), nullable=True)
    access_token_secret = sa.Column(sa.String(512), nullable=True)
    db_conn_id = sa.Column(sa.Integer(), sa.ForeignKey("db_conn.id"), server_default="NULL")
    created_at = sa.Column(sa.DateTime(), server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True)


class Role(Base):

    __tablename__ = "role"

    id = sa.Column(sa.Integer(), primary_key=True)
    role_type = sa.Column(sa.String(100), nullable=False)
    description = sa.Column(sa.String(250), nullable=False)
    name = sa.Column(sa.String(100), nullable=False)


class Source_Db_Mapping(Base):

    __tablename__ = "source_db_mapping"

    id = sa.Column(sa.Integer(), primary_key=True)
    pipeline_id = sa.Column(sa.Integer(), sa.ForeignKey("pipeline.id"), server_default="NULL")
    user_input = sa.Column(JSON(), server_default="NULL")
    dim_fact = sa.Column(JSON(), server_default="NULL")
    source_target_mapping = sa.Column(JSON(), server_default="NULL")
    etl_json = sa.Column(JSON(), server_default="NULL")

    # __table_args__ = Index("fk_pipeline", pipeline_id)


class Tenant(Base):

    __tablename__ = "tenant"

    id = sa.Column(sa.Integer(), primary_key=True)
    description = sa.Column(sa.String(250), nullable=False)
    company_name = sa.Column(sa.String(100), nullable=False)


class User(Base):

    __tablename__ = "user"

    id = sa.Column(sa.Integer(), primary_key=True)
    username = sa.Column(sa.String(255), server_default="NULL")
    email = sa.Column(sa.String(255), server_default="NULL")
    password = sa.Column(sa.String(255), server_default="NULL")
    description = sa.Column(sa.String(250), nullable=False)
    tenant_id = sa.Column(sa.Integer(), sa.ForeignKey("tenant.id"), server_default="NULL")

    # __table_args__ = Index("fk_tenant", tenant_id)


class User_Group(Base):

    __tablename__ = "user_group"

    id = sa.Column(sa.Integer(), primary_key=True)
    user_id = sa.Column(sa.Integer(), sa.ForeignKey("user.id"), server_default="NULL")
    group_id = sa.Column(sa.Integer(), sa.ForeignKey("group.id"), server_default="NULL")

    # __table_args__ = (Index("fk_user_group_user_id", user_id), Index("fk_user_group_group_id", group_id))


class UserRole(Base):

    __tablename__ = "user_role"

    id = sa.Column(sa.Integer(), primary_key=True)
    role_id = sa.Column(sa.Integer(), sa.ForeignKey("role.id"), server_default="NULL")
    user_id = sa.Column(sa.Integer(), sa.ForeignKey("user.id"), server_default="NULL")

    # __table_args__ = (Index("fk_user_role_role_id", role_id), Index("fk_user_role_user_id", user_id))


class Notification(Base):
    __tablename__ = "notifications"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"), nullable=False)
    description = sa.Column(sa.Text, nullable=False)
    source = sa.Column(sa.String(255), nullable=False)
    viewed = sa.Column(sa.Boolean, default=False)
    alert_datetime = sa.Column(sa.DateTime, default=func.now())


class Conversation(Base):
    __tablename__ = 'conversations'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    data_context = sa.Column(JSON, nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False, server_default=func.now())
    updated_at = sa.Column(sa.DateTime, nullable=True, server_default=func.now(), onupdate=func.now())
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)


class Message(Base):
    __tablename__ = 'messages'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    conversation_id = sa.Column(sa.Integer, sa.ForeignKey('conversations.id'), nullable=False)
    user_question = sa.Column(JSON, nullable=False)
    agent_response = sa.Column(JSON, nullable=True)
    timestamp = sa.Column(sa.DateTime, nullable=False, server_default=func.now())
