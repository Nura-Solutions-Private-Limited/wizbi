from typing import List

import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import constants
from apis.v1.login import get_current_user_from_token
from db.models.models import User
from db.session import get_db
from db.views.users import (
    create_new_grp,
    create_new_user,
    create_user_backdoor,
    delete_grp,
    list_grp,
    list_grps,
    list_users,
    update_grp,
)
from schemas.users import (
    DeleteGroup,
    ShowUser,
    ShowUserGroup,
    ShowUserGroups,
    UserCreate,
    UserGroup,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/backdoor-register", response_model=ShowUser)
def create_backdoor_user(createUser: UserCreate,
                         db: Session = Depends(get_db)):
    '''
    Create Backdoor User
    '''
    backdoor_user_register = constants.BACKDOOR_USER_REGISTER
    if backdoor_user_register.upper() == 'Y':
        user = create_user_backdoor(createUser=createUser, db=db)
        return user
    else:
        raise Exception("Backdoor User Register is disabled, Please contact support.")


@router.post("/register", response_model=ShowUser)
def create_user(createUser: UserCreate,
                db: Session = Depends(get_db)):
    user = create_new_user(createUser=createUser, db=db)
    return user


@router.get("/users")
def read_users(db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user_from_token)):
    return list_users(db=db)


@router.post("/group", response_model=UserGroup)
def create_group(ug: UserGroup,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user_from_token)):
    user_group = create_new_grp(ug=ug, db=db, user_id=current_user.id)
    return user_group


# @router.put("/group/{id}", response_model=UserGroup)
@router.put("/group/{id}")
def update_group(id: int,
                 ug: UserGroup,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user_from_token)):
    updated_group = update_grp(ug=ug, db=db, id=id, user_id=current_user.id)
    return updated_group


@router.delete("/group/{id}", response_model=DeleteGroup)
def delete_group(id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user_from_token)):
    '''
    Delete Group + User_group
    '''
    deleted_group = delete_grp(id=id, db=db, user_id=current_user.id)
    return {"deleted": deleted_group}


# @router.get("/groups", response_model=List[ShowUserGroup])
@router.get("/groups", response_model=List[ShowUserGroups])
def read_groups(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user_from_token)):
    return list_grps(db=db, user_id=current_user.id)


@router.get("/groups/{id}", response_model=ShowUserGroup)
def read_group(id: int,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user_from_token)):
    return list_grp(id=id, db=db, user_id=current_user.id)
