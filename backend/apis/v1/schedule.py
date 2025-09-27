from typing import List

import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.models.models import User
from db.session import get_db
from db.views.pipeline_schedule import (
    create_pipelineschedule,
    list_pipelineschedule,
    update_pipelineschedule,
)
from schemas.pipeline_schedule import (
    CreatePipelineSchedule,
    ShowPipelineSchedule,
    UpdatePipelineSchedule,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/schedule", response_model=ShowPipelineSchedule)
def create_pipeline_schedule(createPipelineSchedule: CreatePipelineSchedule,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user_from_token)):
    # Insert Query
    pipelineschedule = create_pipelineschedule(pipelineSchedule=createPipelineSchedule,
                                               db=db,
                                               user_id=current_user.id)
    return pipelineschedule


@router.get("/schedules", response_model=List[ShowPipelineSchedule])
def list_all_pipeline_schedule(db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user_from_token)):
    return list_pipelineschedule(db=db)


@router.get("/schedules/{pipeline_id}", response_model=ShowPipelineSchedule)
def list_pipeline_schedule(pipeline_id: int,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user_from_token)):
    return list_pipelineschedule(pipeline_id=pipeline_id, db=db)


@router.patch("/schedules/{pipeline_id}", response_model=ShowPipelineSchedule)
def update_pipeline_schedule(pipeline_id: int,
                             updatePipelineSchedule: UpdatePipelineSchedule,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user_from_token)):
    return update_pipelineschedule(pipelineSchedule=updatePipelineSchedule,
                                   pipeline_id=pipeline_id,
                                   db=db)
