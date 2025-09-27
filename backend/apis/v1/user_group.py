from typing import List

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import User, User_Group
from db.session import get_db
from db.views.user_group import add_update_user_grp, list_user_grp, list_user_grps
from schemas.user_group import (
    AddUpdateUserGroup,
    CreateUserGroup,
    DeleteUserGroup,
    ShowUserGroup,
    UpdateUserGroup,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


# @router.post("/usergroup", response_model=ShowUserGroup)
# def create_user_group(createUserGroup: CreateUserGroup,
#                       db: Session = Depends(get_db),
#                       current_user: User = Depends(get_current_user_from_token)):
#     '''
#     Create new user group
#     '''
#     user_group = create_user_grp(createUserGroup= createUserGroup, db=db, user_id=current_user.id)
#     return user_group

# @router.post("/usergroup")
@router.post("/usergroup", response_model=List[AddUpdateUserGroup])
def add_update_user_group(addUpdateUserGroup: List[AddUpdateUserGroup],
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user_from_token)):
    '''
    Add/Update user group details
    '''
    return add_update_user_grp(addUpdateUserGroup=addUpdateUserGroup, db=db, user_id=current_user.id)


@router.get("/usergroups", response_model=List[ShowUserGroup])
def get_all_user_groups(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user_from_token)):
    '''
    List all the user groups
    '''
    return list_user_grps(db=db, user_id=current_user.id)


@router.get("/usergroups/{id}", response_model=ShowUserGroup)
def get_user_group(id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    '''
    Get user group by id
    '''
    return list_user_grp(id=id, db=db, user_id=current_user.id)


# @router.delete("/usergroup/{id}", response_model=DeleteUserGroup)
# def delete_user_group(id: int,
#                       db: Session = Depends(get_db),
#                       current_user: User = Depends(get_current_user_from_token)):
#     '''
#     Delete user group
#     '''
#     deleted_user_group = delete_user_grp(id=id, db=db, user_id=current_user.id)
#     return {"deleted": deleted_user_group}
