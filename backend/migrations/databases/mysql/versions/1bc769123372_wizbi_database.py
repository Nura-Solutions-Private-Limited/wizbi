"""wizbi database

Revision ID: 1bc769123372
Revises:
Create Date: 2024-12-02 21:36:36.703321

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1bc769123372"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.DDL(
            """
    create table if not exists tenant(id int auto_increment,
                        description varchar(250) not null,
                        company_name varchar(100) not null,
                        primary key (id))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists `user` (`id` int not null auto_increment,
                                        `username` varchar(255) default null,
                                        `email` varchar(255) default null,
                                        `password` varchar(255) default null,
                                        `tenant_id` int,
                                        `description` varchar(250),
                                        primary key (`id`),
                                        KEY `fk_tenant` (`tenant_id`),
                                        CONSTRAINT `fk_tenant` FOREIGN KEY (tenant_id) REFERENCES tenant(id))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    CREATE TABLE IF NOT EXISTS `group` (`id` int NOT NULL AUTO_INCREMENT,
                                        `name` varchar(255) DEFAULT NULL,
                                        `description` varchar(255) DEFAULT NULL,
                                        PRIMARY KEY (`id`)
    )
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists user_group(id int auto_increment,
                            user_id int,
                            group_id int,
                            primary key (id),
                            constraint fk_user_group_user_id foreign key (user_id) references user(id),
                            constraint fk_user_group_group_id foreign key (group_id) references `group`(id)
                            )
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists role(id int auto_increment,
                                    role_type varchar(100) not null,
                                    description varchar(250) not null,
                                    name varchar(100) not null,
                                    primary key (id))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists user_role(id int auto_increment,
                        role_id int,
                        user_id int,
                        constraint fk_user_role_role_id foreign key (role_id) references role(id),
                        constraint fk_user_role_user_id foreign key (user_id) references user(id),
                        primary key (id))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists `permissions`(id int auto_increment,
                    name varchar(100) not null,
                    description varchar(250) not null,
                    role_id int,
                    pipelines_allowed boolean,
                    etl_allowed boolean,
                    connections_allowed boolean,
                    dashboards_allowed boolean,
                    reports_allowed boolean,
                    jobs_allowed boolean,
                    audits_allowed boolean,
                    genai_allowed boolean,
                    dashboard_ids json,
                    report_ids json,
                    connection_ids json,
                    pipeline_ids json,
                    primary key (id),
                    constraint fk_permissions_role_id foreign key (role_id) references role(id))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    CREATE TABLE IF NOT EXISTS `db_conn` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` int DEFAULT NULL,
    `db_conn_name` varchar(255) DEFAULT NULL,
    `db_type` varchar(255) DEFAULT NULL,
    `db_host` varchar(255) DEFAULT NULL,
    `db_port` int DEFAULT NULL,
    `db_username` varchar(255) DEFAULT NULL,
    `db_password` varchar(255) DEFAULT NULL,
    `db_name` varchar(255) DEFAULT NULL,
    sub_type varchar(50),
        s3_access_key_id varchar(200),
        s3_secret_access_key text,
        s3_bucket varchar(500),
        s3_bucket_path varchar(500),
        s3_bucket_region varchar(200),
        iceberg_database varchar(200),
        iceberg_table varchar(100),
        duckdb_database varchar(200),
        duckdb_lfs_path varchar(2000),
        dbt_project_name varchar(200),
        gdrive_client_id varchar(200),
        gdrive_client_secret text,
        gdrive_access_token text,
        gdrive_refresh_token text,
        gdrive_token_uri text,
        gdrive_scopes varchar(500),
        gdrive_path varchar(500),
        gdrive_prefix varchar(500),
        lfs_path varchar(500),
        lfs_prefix varchar(500),
        lfs_mount_point varchar(500),
        ga_property_id varchar(250),
        ga_auth_json json,
    PRIMARY KEY (`id`),
    KEY `fk_conn_user` (`user_id`),
    CONSTRAINT `fk_conn_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists connection_ext(id int NOT NULL AUTO_INCREMENT,
                                file_name text,
                                file_description text,
                                dimension varchar(250),
                                dimension_metric json,
                                db_conn_id int,
                                PRIMARY KEY (`id`),
                                CONSTRAINT `fk_db_conn` FOREIGN KEY (`db_conn_id`) REFERENCES `db_conn` (`id`))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists rest_api_conn(
                id int not null auto_increment,
                method varchar(10),
                url varchar(500),
                params json,
                authorization json,
                headers json,
                body json,
                db_conn_id int,
            primary key(id),
            constraint fk_rest_api_conn_id foreign key (db_conn_id) references db_conn(id))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    CREATE TABLE IF NOT EXISTS `db_er` (
            `id` int NOT NULL AUTO_INCREMENT,
            `user_id` int DEFAULT NULL,
            `db_conn_id` int DEFAULT NULL,
            `source_er_image` blob,
            `destination_dw_image` blob,
            PRIMARY KEY (`id`),
            KEY `fk_er_user` (`user_id`),
            KEY `fk_er_conn` (`db_conn_id`),
            CONSTRAINT `fk_er_conn` FOREIGN KEY (`db_conn_id`) REFERENCES `db_conn` (`id`),
            CONSTRAINT `fk_er_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    )
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    CREATE TABLE IF NOT EXISTS `pipeline` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` int DEFAULT NULL,
    `db_conn_source_id` int DEFAULT NULL,
    `db_conn_dest_id` int DEFAULT NULL,
    `name` varchar(255) DEFAULT NULL,
    `description` varchar(255) DEFAULT NULL,
    `source_schema_name` varchar(255) DEFAULT NULL,
    `dest_schema_name` varchar(255) DEFAULT NULL,
    `airflow_pipeline_name` varchar(255) DEFAULT NULL,
    `airflow_pipeline_link` varchar(255) DEFAULT NULL,
    `status` varchar(255) DEFAULT NULL,
    `pipeline_type` varchar(100),
    `created_date` datetime,
    PRIMARY KEY (`id`),
    KEY `fk_user` (`user_id`),
    KEY `fk_db_conn_source` (`db_conn_source_id`),
    KEY `fk_db_conn_dest` (`db_conn_dest_id`),
    CONSTRAINT `fk_db_conn_dest` FOREIGN KEY (`db_conn_dest_id`) REFERENCES `db_conn` (`id`),
    CONSTRAINT `fk_db_conn_source` FOREIGN KEY (`db_conn_source_id`) REFERENCES `db_conn` (`id`),
    CONSTRAINT `fk_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    )
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    CREATE TABLE IF NOT EXISTS `source_db_mapping` (
        `id` int NOT NULL AUTO_INCREMENT,
        `pipeline_id` int DEFAULT NULL,
        `user_input` json DEFAULT NULL,
        `dim_fact` json DEFAULT NULL,
        `source_target_mapping` json DEFAULT NULL,
        `etl_json` json DEFAULT NULL,
        `migrate_json` json default NULL,
        `source_json` json default NULL,
        PRIMARY KEY (`id`),
        KEY `fk_pipeline` (`pipeline_id`),
        CONSTRAINT `fk_pipeline` FOREIGN KEY (`pipeline_id`) REFERENCES `pipeline` (`id`))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    CREATE TABLE IF NOT EXISTS `job` (
        `id` int NOT NULL AUTO_INCREMENT,
        `pipeline_id` int DEFAULT NULL,
        `job_id` varchar(255) DEFAULT NULL,
        `start_time` datetime DEFAULT NULL,
        `end_time` datetime DEFAULT NULL,
        `status` varchar(255) DEFAULT NULL,
        `airflow_logs_link` varchar(255) DEFAULT NULL,
        PRIMARY KEY (`id`),
        KEY `fk_job_pipeline` (`pipeline_id`),
        CONSTRAINT `fk_job_pipeline` FOREIGN KEY (`pipeline_id`) REFERENCES `pipeline` (`id`))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    CREATE TABLE IF NOT EXISTS `audit` (
            `id` int NOT NULL AUTO_INCREMENT,
            `pipeline_id` int DEFAULT NULL,
            `job_id` int DEFAULT NULL,
            `errors` int DEFAULT NULL,
            `warnings` int DEFAULT NULL,
            `inserts` int DEFAULT NULL,
            `duplicates` int DEFAULT NULL,
            `skipped` int DEFAULT NULL,
            `notes` varchar(1024) DEFAULT NULL,
            `load_date` datetime,
            PRIMARY KEY (`id`),
            KEY `fk_audit_pipeline` (`pipeline_id`),
            KEY `fk_audit_job` (`job_id`),
            CONSTRAINT `fk_audit_pipeline` FOREIGN KEY (`pipeline_id`) REFERENCES `pipeline` (`id`),
            CONSTRAINT `fk_audit_job` FOREIGN KEY (`job_id`) REFERENCES `job` (`id`))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    CREATE TABLE IF NOT EXISTS `report` (
            `id` int NOT NULL AUTO_INCREMENT,
            `pipeline_id` int DEFAULT NULL,
            `type` varchar(255) DEFAULT NULL,
            `name` varchar(1000) DEFAULT NULL,
            `sql_query` varchar(8000) DEFAULT NULL,
            `google_link` varchar(1024) DEFAULT NULL,
            `google_json` varchar(5120) DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY `fk_report_pipeline` (`pipeline_id`),
            CONSTRAINT `fk_report_pipeline` FOREIGN KEY (`pipeline_id`) REFERENCES `pipeline` (`id`))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists `pipeline_schedule`(
    `id` int not null AUTO_INCREMENT,
    `pipeline_id` int,
    `schedule` varchar(100),
    `created_date` datetime,
    `updated_date` datetime,
    PRIMARY KEY (`id`),
    KEY `fk_schedule_pipeline` (`pipeline_id`),
    CONSTRAINT `fk_schedule_pipeline`
    FOREIGN KEY (pipeline_id) REFERENCES `pipeline` (`id`))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    CREATE TABLE if not exists `dashboard` (
    `id` int NOT NULL AUTO_INCREMENT,
    `group_id` int DEFAULT NULL,
    `name` varchar(1024) DEFAULT NULL,
    `link` varchar(1024) DEFAULT NULL,
    `isactive` boolean DEFAULT TRUE,
    `updated_date` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `fk_group_id` (`group_id`),
    CONSTRAINT `fk_group_id` FOREIGN KEY (group_id) REFERENCES `user_group` (`id`))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists ga_dimension(
    id int NOT NULL AUTO_INCREMENT,
    dimension varchar(200),
    status bool,
    primary key(id))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists ga_metric(
    id int not null auto_increment,
    metric varchar(200),
    status bool,
    dimension_id int,
    primary key (id),
    KEY `fk_dimension_id` (`dimension_id`),
    constraint fk_dimension_id foreign key (dimension_id) references ga_dimension(id))
    """
        )
    )

    op.execute(
        sa.DDL(
            """
    create table if not exists connector_type(
        id int not null auto_increment,
        connector_type varchar(50),
        description varchar(200),
        type varchar(20),
        sub_type varchar(50),
        enabled bool,
        extra json,
        primary key(id)
    )
    """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.DDL(
            """
        drop table if exists connector_type
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists ga_metric
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists ga_dimension
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists dashboard
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists pipeline_schedule
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists report
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists audit
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists job
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists source_db_mapping
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists pipeline
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists db_er
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists rest_api_conn
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists connection_ext
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists db_conn
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists permissions
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists user_role
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists role
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists user_group
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists user
    """
        )
    )

    op.execute(
        sa.DDL(
            """
        drop table if exists tenant
    """
        )
    )
