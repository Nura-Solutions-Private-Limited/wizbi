import logging
from sqlalchemy.orm import Session

from wizbi_dataload.db.models.models import Job

logger = logging.getLogger(__name__)


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
