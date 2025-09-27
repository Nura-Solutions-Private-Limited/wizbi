from typing import List

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Permissions, User
from db.session import get_db
from db.views.permissions import (
    create_prmsn,
    delete_prmsn,
    list_prmsn,
    list_prmsns,
    permission_type,
    update_prmsn,
)
from schemas.permissions import (
    CreatePermissions,
    DeletePermission,
    PermissionType,
    ShowPermissions,
    UpdatePermissions,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/permission", response_model=ShowPermissions)
def create_permissions(createPermissions: CreatePermissions,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    '''
    Create new permission
    '''
    perm = create_prmsn(createPermissions=createPermissions, db=db, user_id=current_user.id)
    return perm


@router.get("/permissions", response_model=List[ShowPermissions])
def get_all_permissions(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user_from_token)):
    '''
    List all the permissions
    '''
    return list_prmsns(db=db, user_id=current_user.id)


@router.get("/permissions/{id}", response_model=ShowPermissions)
def get_permission(id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    '''
    Get permission by id
    '''
    return list_prmsn(id=id, db=db, user_id=current_user.id)


@router.patch("/permission/{id}", response_model=ShowPermissions)
def update_permissions(id: int,
                       updatePermission: UpdatePermissions,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    '''
    Update permission details
    '''
    return update_prmsn(updatePermission=updatePermission, db=db, user_id=current_user.id, id=id)


@router.delete("/permission/{id}", response_model=DeletePermission)
def delete_permission(id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    '''
    Delete permissions
    '''
    deleted_permission = delete_prmsn(id=id, db=db, user_id=current_user.id)
    return {"deleted": deleted_permission}


@router.get("/permissiontype", response_model=List[PermissionType])
def get_permissiontype(db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    return permission_type(db=db, user_id=current_user.id)
