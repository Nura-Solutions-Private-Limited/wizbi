from typing import List

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Tenant, User
from db.session import get_db
from db.views.tenant import create_tnt, delete_tnt, list_tnt, list_tnts, update_tnt
from schemas.tenant import CreateTenant, DeleteTenant, ShowTenant, UpdateTenant

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/tenant", response_model=ShowTenant)
def create_tenant(createTenant: CreateTenant,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user_from_token)):
    '''
    Create new tenant
    '''
    return create_tnt(createTenant=createTenant, db=db, user_id=current_user.id)


@router.get("/tenants", response_model=List[ShowTenant])
def get_all_tenant(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    '''
    List all the tenants
    '''
    return list_tnts(db=db, user_id=current_user.id)


@router.get("/tenants/{id}", response_model=ShowTenant)
def get_tenant(id: int,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user_from_token)):
    '''
    Get tenant by id
    '''
    return list_tnt(id=id, db=db, user_id=current_user.id)


@router.patch("/tenant/{id}", response_model=ShowTenant)
def update_tenant(id: int,
                  updateTenant: UpdateTenant,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user_from_token)):
    '''
    Update tenant details
    '''
    return update_tnt(updateTenant=updateTenant, db=db, user_id=current_user.id, id=id)


@router.delete("/tenant/{id}", response_model=DeleteTenant)
def delete_tenant(id: int,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user_from_token)):
    '''
    Delete tenant
    '''
    deleted_tenant = delete_tnt(id=id, db=db, user_id=current_user.id)
    return {"deleted": deleted_tenant}