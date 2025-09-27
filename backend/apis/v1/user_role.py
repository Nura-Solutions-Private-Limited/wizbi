from typing import List

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import User, UserRole
from db.session import get_db
from db.views.user_role import (
    add_update_user_rol,
    create_user_rol,
    delete_user_rol,
    list_user_rol,
    list_user_rols,
    update_user_rol,
)
from schemas.user_role import (
    AddUpdateUserRole,
    CreateUserRole,
    DeleteUserRole,
    ShowUserRole,
    UpdateUserRole,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/userrole", response_model=List[AddUpdateUserRole])
def create_user_role(addUpdateUserRole: List[AddUpdateUserRole],
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    '''
    Add/ Update user role
    '''
    return add_update_user_rol(addUpdateUserRole= addUpdateUserRole, db=db, user_id=current_user.id)


@router.get("/userroles", response_model=List[ShowUserRole])
def get_all_user_roles(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user_from_token)):
    '''
    List all the user roles
    '''
    return list_user_rols(db=db, user_id=current_user.id)


@router.get("/userroles/{id}", response_model=ShowUserRole)
def get_user_role(id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    '''
    Get user role by id
    '''
    return list_user_rol(id=id, db=db, user_id=current_user.id)


@router.patch("/userrole/{id}", response_model=ShowUserRole)
def update_user_role(id: int,
                       updateUserRole: UpdateUserRole,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    '''
    Update user role details
    '''
    return update_user_rol(updateUserRole=updateUserRole, db=db, user_id=current_user.id, id=id)


@router.delete("/userrole/{id}", response_model=DeleteUserRole)
def delete_user_role(id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    '''
    Delete user role
    '''
    deleted_user_role = delete_user_rol(id=id, db=db, user_id=current_user.id)
    return {"deleted": deleted_user_role}