import structlog
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.models import Audit, Job, Pipeline
from db.views.permission_checker import PermissionChecker
from schemas.audit import CreateAudit, ShowAudit

logger = structlog.getLogger(__name__)


def create_audit(createAudit: CreateAudit, db: Session, user_id: int):
    '''
    Create audit
    '''
    try:
        audit = Audit(pipeline_id=createAudit.pipeline_id,
                      job_id=createAudit.job_id,
                      errors=createAudit.errors,
                      warnings=createAudit.warnings,
                      inserts=createAudit.inserts,
                      duplicates=createAudit.duplicates,
                      skipped=createAudit.skipped,
                      notes=createAudit.notes)

        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit
    except Exception as ex:
        logger.error(f"Error in creating audit : {str(ex)}")
        raise ex


def list_audits(db: Session, user_id: int):
    '''
    Get all audit data along with pipeline and job data
    '''
    try:
        permissionChecker = PermissionChecker()
        audit_permission, audit_ids = permissionChecker.get_permission(db=db,
                                                                       user_id=user_id,
                                                                       permission_for='audits')
        logger.info(f'Userid {user_id} Audit permission {audit_permission} and ids {audit_ids}')
        if audit_permission and not audit_ids:
            audit_list = list()
            audits = db.query(Audit).all()
            for audit in audits:
                audit_dict = audit.__dict__

                # Get pipeline data using pipeline id and append it to audit resultset
                pipeline_id = audit.pipeline_id
                pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
                pipeline_dict = pipeline.__dict__
                # pipeline_dict.pop('_sa_instance_state')
                audit_dict['pipeline'] = pipeline_dict

                # Get Job data using pipeline id and append it to audit resultset
                job_id = audit.job_id
                job = db.query(Job).filter(Job.id == job_id).first()
                job_dict = job.__dict__
                # job_dict.pop('_sa_instance_state')
                audit_dict['job'] = job_dict

                audit_list.append(audit_dict)

            return audit_list
    except Exception as ex:
        logger.error(f"Error in getting all audit data :{str(ex)}")
        raise ex


def list_paginated_audits(db: Session, user_id: int):
    '''
    Get all audit data along with pipeline and job data
    '''
    try:
        permissionChecker = PermissionChecker()
        audit_permission, audit_ids = permissionChecker.get_permission(db=db,
                                                                       user_id=user_id,
                                                                       permission_for='audits')
        logger.info(f'Userid {user_id} Audit permission {audit_permission} and ids {audit_ids}')
        if audit_permission and not audit_ids:
            audit_list = list()
            audit_query = select(Audit.id,
                                 Audit.pipeline_id,
                                 Audit.job_id,
                                 Audit.errors,
                                 Audit.warnings,
                                 Audit.inserts,
                                 Audit.duplicates,
                                 Audit.skipped,
                                 Audit.notes,
                                 Audit.load_date
                                 ).order_by(Audit.id.desc())
            # audits = db.query(Audit).all()
            # for audit in audits:
            #     audit_dict = audit.__dict__

            #     # Get pipeline data using pipeline id and append it to audit resultset
            #     pipeline_id = audit.pipeline_id
            #     pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
            #     pipeline_dict = pipeline.__dict__
            #     # pipeline_dict.pop('_sa_instance_state')
            #     audit_dict['pipeline'] = pipeline_dict

            #     # Get Job data using pipeline id and append it to audit resultset
            #     job_id = audit.job_id
            #     job = db.query(Job).filter(Job.id == job_id).first()
            #     job_dict = job.__dict__
            #     # job_dict.pop('_sa_instance_state')
            #     audit_dict['job'] = job_dict

            #     audit_list.append(audit_dict)

            def pipeline_transformer(items):
                item_list = []
                for item in items:
                    item = item._asdict()
                    pipeline_id = item.get('pipeline_id')
                    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
                    pipeline_dict = {}
                    if pipeline:
                        pipeline_dict = pipeline.__dict__
                    item["pipeline"] = pipeline_dict

                    # Get Job data using pipeline id and append it to audit resultset
                    job_id = item.get('job_id')
                    job = db.query(Job).filter(Job.id == job_id).first()
                    job_dict = {}
                    if job:
                        job_dict = job.__dict__
                    # job_dict.pop('_sa_instance_state')
                    item['job'] = job_dict

                    item_list.append(item)
                return item_list

            audit_list = paginate(db, query=audit_query, transformer=pipeline_transformer)

            return audit_list
    except Exception as ex:
        logger.error(f"Error in getting all audit data :{str(ex)}")
        raise ex


def list_audit(db: Session, user_id: int, id: int = None):
    '''
    Get audit data along with pipeline and job data
    '''
    try:
        permissionChecker = PermissionChecker()
        audit_permission, audit_ids = permissionChecker.get_permission(db=db,
                                                                       user_id=user_id,
                                                                       permission_for='audits')
        logger.info(f'Userid {user_id} Audit permission {audit_permission} and ids {audit_ids}')
        if audit_permission and not audit_ids:
            audit = db.query(Audit).filter(Audit.id == id).first()
            audit_dict = audit.__dict__

            # Get pipeline data using pipeline id and append it to audit resultset
            pipeline_id = audit.pipeline_id
            pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
            pipeline_dict = pipeline.__dict__
            # pipeline_dict.pop('_sa_instance_state')
            audit_dict['pipeline'] = pipeline_dict

            # Get Job data using pipeline id and append it to audit resultset
            job_id = audit.job_id
            job = db.query(Job).filter(Job.id == job_id).first()
            job_dict = job.__dict__
            # job_dict.pop('_sa_instance_state')
            audit_dict['job'] = job_dict

            return audit_dict
    except Exception as ex:
        logger.error(f"Error in getting audit data :{str(ex)}")
        raise ex
