from typing import List

import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.models.models import User
from db.session import get_db
from db.views.sourcedbmapping import (
    create_new_source_db_mapping,
    list_source_db_mapping,
)
from schemas.sourcedbmapping import CreateSourceDbMapping, ShowSourceDbMapping

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/source-db-mapping", response_model=ShowSourceDbMapping)
def create_source_db_mapping(createSourceDbMapping: CreateSourceDbMapping,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user_from_token)):
    # Insert Query
    source_db_papping = create_new_source_db_mapping(createSourceDbMapping=createSourceDbMapping, db=db)
    return source_db_papping


@router.get("/source-db-mappings", response_model=List[ShowSourceDbMapping])
def list_all_source_db_mappings(db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user_from_token)):
    return list_source_db_mapping(db=db)


@router.get("/source-db-mappings/{id}", response_model=ShowSourceDbMapping)
def list_source_db_mappings(id: int,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user_from_token)):
    return list_source_db_mapping(id=id, db=db)
