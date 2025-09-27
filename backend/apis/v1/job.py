from typing import List

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Job, User
from db.session import get_db
from db.views.job import list_job, list_jobs, list_jobs_paginated
from schemas.job import CreateJob, ShowJob

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.get("/jobs", response_model=List[ShowJob], deprecated=True)
def get_jobs(db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user_from_token)):
    return list_jobs(db=db, user_id=current_user.id)


@router.get("/jobs-paginated", response_model=Page[ShowJob])
def get_paginated_jobs(db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    return list_jobs_paginated(db=db, user_id=current_user.id)


@router.get("/jobs/{id}", response_model=ShowJob)
def get_job(id: int,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user_from_token)):
    return list_job(db=db, user_id=current_user.id, id=id)
