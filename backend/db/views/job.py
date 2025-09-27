import structlog
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.models import Job, Pipeline
from db.views.permission_checker import PermissionChecker
from schemas.job import CreateJob

logger = structlog.getLogger(__name__)


def create_job(createJob: CreateJob, db: Session, user_id: int):
    '''
    Create job
    '''
    try:
        job = Job(pipeline_id=createJob.pipeline_id,
                  job_id=createJob.job_id,
                  start_time=createJob.start_time,
                  end_time=createJob.end_time,
                  status=createJob.status,
                  airflow_logs_link=createJob)

        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except Exception as ex:
        logger.error(f"Error in creating job : {str(ex)}")
        raise ex


def add_update_job_status(db: Session, status, job_id, pipeline_id, job_date_time):
    '''
    Add or update job status
    '''
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if job:
        job.status = status
        job.end_time = job_date_time
    else:
        job = Job(pipeline_id=pipeline_id,
                  job_id=job_id,
                  start_time=job_date_time,
                  status=status)
        db.add(job)
    db.commit()
    db.refresh(job)


def list_jobs(db: Session, user_id: int):
    '''
    Get all job data along with associated pipeline data
    '''
    try:
        permissionChecker = PermissionChecker()
        job_permission, job_ids = permissionChecker.get_permission(db=db,
                                                                   user_id=user_id,
                                                                   permission_for='jobs')
        logger.info(f'Userid {user_id} Pipelie permission {job_permission} and ids {job_ids}')
        if job_permission and not job_ids:
            job_list = list()
            # jobs = db.query(Job).all()
            jobs = db.query(Job).order_by(Job.id.desc()).all()

            for job in jobs:
                job_dict = job.__dict__

                # Get pipeline data using pipeline id and append it to audit resultset
                pipeline_id = job.pipeline_id
                pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
                pipeline_dict = pipeline.__dict__
                # pipeline_dict.pop('_sa_instance_state')
                job_dict['pipeline'] = pipeline_dict
                job_list.append(job_dict)

            return job_list
    except Exception as ex:
        logger.error(f"Error in getting all job data : {str(ex)}")
        raise ex


def list_jobs_paginated(db: Session, user_id: int):
    '''
    Get all job data along with associated pipeline data
    '''
    try:
        permissionChecker = PermissionChecker()
        job_permission, job_ids = permissionChecker.get_permission(db=db,
                                                                   user_id=user_id,
                                                                   permission_for='jobs')
        logger.info(f'Userid {user_id} Pipelie permission {job_permission} and ids {job_ids}')
        if job_permission and not job_ids:
            job_list = list()
            # jobs = db.query(Job).all()
            job_query = select(Job.id,
                               Job.pipeline_id,
                               Job.job_id,
                               Job.start_time,
                               Job.end_time,
                               Job.status,
                               Job.airflow_logs_link).order_by(Job.id.desc())
            # jobs = db.query(Job).order_by(Job.id.desc()).all()

            # for job in jobs:
            #     job_dict = job.__dict__

            #     # Get pipeline data using pipeline id and append it to audit resultset
            #     pipeline_id = job.pipeline_id
            #     pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
            #     pipeline_dict = pipeline.__dict__
            #     # pipeline_dict.pop('_sa_instance_state')
            #     job_dict['pipeline'] = pipeline_dict
            #     job_list.append(job_dict)

            def pipeline_transformer(jobs):
                job_list = []
                for job in jobs:
                    job = job._asdict()
                    pipeline_id = job.get('pipeline_id')
                    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
                    pipeline_dict = pipeline.__dict__
                    job["pipeline"] = pipeline_dict
                    job_list.append(job)
                return job_list

            job_list = paginate(db, query=job_query, transformer=pipeline_transformer)

            return job_list
    except Exception as ex:
        logger.error(f"Error in getting all job data : {str(ex)}")
        raise ex


def list_job(db: Session, user_id: int, id: int = None):
    '''
    Get job data along with associated pipeline data
    '''
    try:
        permissionChecker = PermissionChecker()
        job_permission, job_ids = permissionChecker.get_permission(db=db,
                                                                   user_id=user_id,
                                                                   permission_for='jobs')
        logger.info(f'Userid {user_id} Pipelie permission {job_permission} and ids {job_ids}')
        if job_permission and not job_ids:
            # job = db.query(Job).filter(Job.id == id).first()
            job = db.query(Job).filter(Job.id == id).first()

            job_dict = job.__dict__

            # Get pipeline data using pipeline id and append it to audit resultset
            pipeline_id = job.pipeline_id
            pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
            pipeline_dict = pipeline.__dict__
            # pipeline_dict.pop('_sa_instance_state')
            job_dict['pipeline'] = pipeline_dict

            return job_dict
    except Exception as ex:
        logger.error(f"Error in getting job data :{str(ex)}")
        raise ex
