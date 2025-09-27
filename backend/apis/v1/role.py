from enum import Enum
from typing import List

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Role, User
from db.session import get_db
from db.views.role import (
    create_rol,
    delete_rol,
    list_rol,
    list_rols,
    role_type,
    update_rol,
)
from schemas.role import CreateRole, DeleteRole, RoleType, ShowRole, UpdateRole

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/role", response_model=ShowRole)
def create_role(createRole: CreateRole,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user_from_token)):
    '''
    Create new role
    '''
    role = create_rol(createRole=createRole, db=db, user_id=current_user.id)
    return role


@router.get("/roles", response_model=List[ShowRole])
def get_all_roles(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user_from_token)):
    '''
    List all the roles
    '''
    return list_rols(db=db, user_id=current_user.id)


@router.get("/roles/{id}", response_model=ShowRole)
def get_role(id: int,
             db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user_from_token)):
    '''
    Get role by id
    '''
    return list_rol(id=id, db=db, user_id=current_user.id)


@router.patch("/role/{id}", response_model=ShowRole)
def update_role(id: int,
                updateRole: UpdateRole,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user_from_token)):
    '''
    Update role details
    '''
    return update_rol(updateRole=updateRole, db=db, user_id=current_user.id, id=id)


@router.delete("/role/{id}", response_model=DeleteRole)
def delete_role(id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user_from_token)):
    '''
    Delete role
    '''
    deleted_role = delete_rol(id=id, db=db, user_id=current_user.id)
    return {"deleted": deleted_role}


@router.get("/roletype", response_model=List[RoleType])
def get_role_type(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user_from_token)):
    '''
    List role types
    '''
    return role_type(db=db, user_id=current_user.id)
