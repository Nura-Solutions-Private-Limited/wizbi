from typing import List

import structlog
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.models.models import User
from db.session import get_db
from db.views.pipeline import (
    create_new_pipeline,
    delete_pipeline,
    list_pipeline,
    pipeline_statuses,
    pipeline_type,
)
from schemas.pipeline import (
    CreatePipeline,
    DeletePipeline,
    PipelineStatus,
    PipelineType,
    ShowPipeline,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/pipeline", response_model=ShowPipeline)
def create_pipeline(createPipeline: CreatePipeline,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user_from_token)):
    # Insert Query
    pipeline = create_new_pipeline(pipeline=createPipeline, db=db, user_id=current_user.id)
    return pipeline


@router.get("/pipelines", response_model=List[ShowPipeline])
def get_pipelines(pipeline_status: str = Query(None,
                                               description="Pipeline status \
                                               (Design/Saved/Ready For ETL/Active)"),
                  pipeline_type: str = Query(None,
                                             description="Pipeline type \
                                             (ETL/ELT/Spark/Migration)"),
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user_from_token)):
    return list_pipeline(db=db, pipeline_status=pipeline_status, pipeline_type=pipeline_type, user_id=current_user.id)


@router.get("/pipelines/{id}", response_model=ShowPipeline)
def get_pipeline(id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user_from_token)):
    return list_pipeline(id=id, db=db, user_id=current_user.id)


@router.delete("/pipeline/{id}", response_model=DeletePipeline)
def delete_pipelines(id: int,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user_from_token)):
    pipeline_status = delete_pipeline(id=id, db=db, user_id=current_user.id)
    return {"deleted": pipeline_status}


@router.get("/pipelinetype", response_model=List[PipelineType])
def get_pipelinetype(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user_from_token)):
    return pipeline_type(db=db, user_id=current_user.id)


@router.get("/pipelinestatus", response_model=List[PipelineStatus])
def get_pipelinestatus(db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    return pipeline_statuses(db=db, user_id=current_user.id)
