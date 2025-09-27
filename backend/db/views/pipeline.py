from datetime import datetime

import structlog
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.enums import PipelineStatus, PipelineType
from db.models.models import Db_Conn, Permissions, Pipeline, User, UserRole
from db.views.login import get_permission
from db.views.permission_checker import PermissionChecker
from db.views.role import RoleType
from schemas.pipeline import CreatePipeline

logger = structlog.getLogger(__name__)


def create_new_pipeline(pipeline: CreatePipeline, db: Session, user_id: int):
    '''
    Create new pipeline
    '''
    # check if pipeline type is social media
    # if yes then update destination connection id
    if pipeline.pipeline_type == PipelineType.SOCIAL_MEDIA.value:
        social_media_conn = db.query(Db_Conn).filter(
            func.upper(Db_Conn.db_conn_name) == 'SOCIAL MEDIA').first()
        if not social_media_conn:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Social Media connection not found, Please create a connection with name Social Media.")  # noqa: E501
        pipeline.db_conn_dest_id = social_media_conn.id
        pipeline.dest_schema_name = social_media_conn.db_name

    pipeline = Pipeline(user_id=user_id,
                        db_conn_source_id=pipeline.db_conn_source_id,
                        db_conn_dest_id=pipeline.db_conn_dest_id,
                        source_schema_name=pipeline.source_schema_name,
                        dest_schema_name=pipeline.dest_schema_name,
                        name=pipeline.name,
                        description=pipeline.description,
                        airflow_pipeline_name=pipeline.airflow_pipeline_name,
                        airflow_pipeline_link=pipeline.airflow_pipeline_link,
                        status=pipeline.status,
                        pipeline_type=pipeline.pipeline_type,
                        created_date=datetime.now())

    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)
    # print(pipeline)
    return pipeline


def list_pipeline(db: Session, pipeline_status: str, pipeline_type: str, user_id: int, id: int = None):
    '''
    List pipelines
    '''
    permissionChecker = PermissionChecker()
    pipeline_permission, pipeline_ids = permissionChecker.get_permission(db=db,
                                                                         user_id=user_id,
                                                                         permission_for='pipelines')
    logger.info(f'Userid {user_id} Pipelie permission {pipeline_permission} and ids {pipeline_ids}')
    if pipeline_permission and not pipeline_ids:
        if id:
            pipelines = db.query(Pipeline).filter(Pipeline.id == id).first()
        else:
            # filter pipeline data based on pipeline_type and pipeline_status
            if pipeline_status and pipeline_type:
                pipelines = (
                    db.query(Pipeline)
                    .filter(
                        func.upper(Pipeline.pipeline_type) == pipeline_type.upper(),
                        func.upper(Pipeline.status) == pipeline_status.upper(),
                    )
                    .order_by(Pipeline.id.desc())
                    .all()
                )
            elif pipeline_status and pipeline_type is None:
                pipelines = (
                    db.query(Pipeline)
                    .filter(
                        func.upper(Pipeline.status) == pipeline_status.upper()
                    )
                    .order_by(Pipeline.id.desc())
                    .all()
                )
            elif pipeline_status is None and pipeline_type:
                pipelines = (
                    db.query(Pipeline)
                    .filter(
                        func.upper(Pipeline.pipeline_type) == pipeline_type.upper()
                    )
                    .order_by(Pipeline.id.desc())
                    .all()
                )
            else:
                pipelines = db.query(Pipeline).order_by(Pipeline.id.desc()).all()
    elif pipeline_permission and pipeline_ids:
        # TODO get list of pipline which is allowed for user and add that in filter
        if id:
            pipelines = db.query(Pipeline).filter(Pipeline.id == id, Pipeline.id.in_(pipeline_ids)).first()
        else:
            pipelines = db.query(Pipeline).filter(Pipeline.id.in_(pipeline_ids)).order_by(Pipeline.id.desc()).all()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authorized to view any pipeline.")

    # Include calculate field pipeline type description based on pipeline type
    pipeline_list = []
    for pipeline in pipelines:
        pipeline_dict = pipeline.__dict__
        if pipeline_dict['pipeline_type'] == PipelineType.ETL.value:
            pipeline_dict['pipeline_type_description'] = 'SQL Data Warehouse'
        elif pipeline_dict['pipeline_type'] == PipelineType.ELT.value \
                or pipeline_dict['pipeline_type'] == 'Staging (ELT)':
            pipeline_dict['pipeline_type_description'] = 'Staging Database'
        elif pipeline_dict['pipeline_type'] == PipelineType.MIGRATION.value:
            pipeline_dict['pipeline_type_description'] = 'Migration'
        elif pipeline_dict['pipeline_type'] == PipelineType.DATALAKE.value:
            pipeline_dict['pipeline_type_description'] = 'Data Lake'
        pipeline_list.append(pipeline_dict)

    return pipeline_list


def delete_pipeline(db: Session, id: int, user_id: int):
    '''
    Delete pipeline
    '''
    # TODO add filter to delete only if user has permission to delete the pipeline
    existing_pipeline = db.query(Pipeline).filter(Pipeline.id == id,
                                                  Pipeline.user_id == user_id)
    if not existing_pipeline.first():
        return 0
    existing_pipeline.delete(synchronize_session=False)
    db.commit()
    return 1


def pipeline_statuses(db: Session, user_id: int):
    '''
    Return valid pipeline status
    '''
    data = [
        {
            "id": 1,
            "pipeline_status": PipelineStatus.DESIGN.value,
            "description": "Design",
            "enabled": True,
        },
        {
            "id": 2,
            "pipeline_status": PipelineStatus.SAVED.value,
            "description": "Saved",
            "enabled": True,
        },
        {
            "id": 3,
            "pipeline_status": PipelineStatus.READY_FOR_ETL.value,
            "description": "Ready for ETL",
            "enabled": True,
        },
        {
            "id": 4,
            "pipeline_status": PipelineStatus.ACTIVE.value,
            "description": "Active",
            "enabled": True,
        }
    ]
    return data


def pipeline_type(db: Session, user_id: int):
    '''
    Return supported pipeline type
    '''
    data = [
        {
            "id": 1,
            "pipeline_type": "ETL",
            "description": "SQL Data Warehouse",
            "enabled": True,
        },
        {
            "id": 2,
            "pipeline_type": "ELT",
            "description": "Staging Database",
            "enabled": True,
        },
        {
            "id": 3,
            "pipeline_type": "MIGRATION",
            "description": "Data Migration",
            "enabled": True
        },
        {
            "id": 4,
            "pipeline_type": "DATALAKE",
            "description": "Data Lake",
            "enabled": True
        }
    ]
    return data
