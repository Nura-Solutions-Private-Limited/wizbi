from sqlalchemy.orm import Session
from datetime import datetime

from db.models.models import Pipeline_Schedule
from schemas.pipeline_schedule import CreatePipelineSchedule, UpdatePipelineSchedule


def create_pipelineschedule(pipelineSchedule: CreatePipelineSchedule, db: Session, user_id: int):
    pipelineschedule = Pipeline_Schedule(pipeline_id=pipelineSchedule.pipeline_id,
                                         schedule=pipelineSchedule.schedule,
                                         created_date=datetime.now())

    db.add(pipelineschedule)
    db.commit()
    db.refresh(pipelineschedule)
    return pipelineschedule


def list_pipelineschedule(db: Session, pipeline_id: int = None):
    if pipeline_id:
        pipeline_schedules = db.query(Pipeline_Schedule).filter(Pipeline_Schedule.pipeline_id == pipeline_id).first()
    else:
        pipeline_schedules = db.query(Pipeline_Schedule).all()
    return pipeline_schedules


def update_pipelineschedule(pipelineSchedule: UpdatePipelineSchedule,
                            db: Session,
                            pipeline_id: int):
    pipeline_schedule = db.query(Pipeline_Schedule).filter(Pipeline_Schedule.pipeline_id == pipeline_id).first()
    pipeline_schedule.schedule = pipelineSchedule.schedule
    pipeline_schedule.updated_date = datetime.now()

    db.commit()
    db.refresh(pipeline_schedule)
    return pipeline_schedule
