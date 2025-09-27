from typing import List

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Audit, User
from db.session import get_db
from db.views.audit import list_audit, list_audits, list_paginated_audits
from schemas.audit import CreateAudit, ShowAudit

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.get("/audits", response_model=List[ShowAudit], deprecated=True)
def get_audits(db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user_from_token)):
    try:
        return list_audits(db=db, user_id=current_user.id)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})


@router.get("/audits-paginated", response_model=Page[ShowAudit])
def get_paginated_audits(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user_from_token)):
    try:
        return list_paginated_audits(db=db, user_id=current_user.id)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})


@router.get("/audits/{id}", response_model=ShowAudit)
def get_audit(id: int,
              db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user_from_token)):
    return list_audit(db=db, id=id, user_id=current_user.id)
    # try:
    #     return list_audit(db=db, id=id)
    # except Exception as e:
    #     return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})
