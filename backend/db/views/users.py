import structlog
from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from core.hashing import Hasher
from db.models.models import Group, Role, Tenant, User, User_Group, UserRole
from schemas.users import UserCreate, UserGroup

logger = structlog.getLogger(__name__)


def create_user_backdoor(createUser: UserCreate, db: Session):
    '''
    Create a new user with default tenant, group and admin role
    '''

    # user details to be attached with user
    data = {"tenant_description": "test tenant",
            "tenant_company_name": "test company",
            "group_name": "test_group",
            "group_description": "test group",
            "role_name": "test_role",
            "role_description": "test role",
            "role_type": "Admin",
            }

    exiting_user = db.query(User).filter(User.username == createUser.username).first()
    if exiting_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with same name exist")
    else:
        # create tenant
        tenant = Tenant(description=data.get('tenant_description'),
                        company_name=data.get('tenant_company_name'))

        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        # create user
        user = User(
            username=createUser.username,
            email=createUser.email,
            password=Hasher.get_password_hash(createUser.password),
            description=createUser.description,
            tenant_id=tenant.id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        # return user

        group = db.query(Group).filter(Group.name == data.get('group_name')).first()
        if group:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Group already exists!")
        else:
            grp = Group(name=data.get('group_name'),
                        description=data.get('group_description'))
            db.add(grp)
            db.commit()
            db.refresh(grp)
            print(grp)

            usergrp = User_Group(user_id=user.id,
                                 group_id=grp.id)
            db.add(usergrp)
            db.commit()
            db.refresh(usergrp)

        # create role
        existing_role = db.query(Role).filter(Role.name == data.get('role_name')).first()

        if not existing_role:
            # insert row in role table for the role
            role = Role(role_type=data.get('role_type'),
                        description=data.get('role_description'),
                        name=data.get('role_name'))

            db.add(role)
            db.commit()
            db.refresh(role)

            # insert rows in the user_role
            userrole = UserRole(role_id=role.id, user_id=user.id)
            db.add(userrole)
            db.commit()
            db.refresh(userrole)
            db.refresh(role)
    return user


def create_new_user(createUser: UserCreate, db: Session):
    '''
    Create a new user
    '''
    exiting_user = db.query(User).filter(User.username == createUser.username).first()
    if exiting_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with same name exist")
    else:
        user = User(
            username=createUser.username,
            email=createUser.email,
            password=Hasher.get_password_hash(createUser.password),
            description=createUser.description,
            tenant_id=createUser.tenant_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


def get_user_by_email(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    return user


def get_user_by_username(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    return user


def list_users(db: Session):
    users = db.query(User).all()
    return users


def create_new_grp(ug: UserGroup, db: Session, user_id: int):
    group = db.query(Group).filter(Group.name == ug.name).first()

    if group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Group already exists!")
    else:
        grp = Group(name=ug.name,
                    description=ug.description)
        db.add(grp)
        db.commit()
        db.refresh(grp)
        print(grp)

        userlst = ug.userlist
        print(userlst)

        for userid in userlst:
            usergrp = User_Group(user_id=userid,
                                 group_id=grp.id)
            db.add(usergrp)
            db.commit()
            db.refresh(usergrp)

    return ug


def update_grp(id: int, ug: UserGroup, db: Session, user_id: int):
    '''
    Update group and associated users for the group
    '''
    existing_grp = db.query(Group).filter(Group.name == ug.name, Group.id != id).first()

    if not existing_grp:
        group = db.query(Group).filter(Group.id == id).first()
        group.name = ug.name
        group.description = ug.description
        db.commit()
        db.refresh(group)

        userids = ug.userlist
        # userlist = userids.copy()

        usergrps = db.query(User_Group).filter(User_Group.group_id == id).all()
        for usergrp in usergrps:
            print(usergrp.user_id)
            if usergrp.user_id not in userids:
                # usergrp.delete(synchronize_session=False)

                db.query(User_Group).filter(User_Group.user_id == usergrp.user_id, User_Group.group_id == id).delete()
                print(usergrp.user_id)
                db.commit()
                # db.refresh(dlt)
            else:
                userids.remove(usergrp.user_id)

        print(userids)
        for userid in userids:
            usrgrp = User_Group(user_id=userid,
                                group_id=id)
            db.add(usrgrp)
            db.commit()
            db.refresh(usrgrp)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Group with the same name already exists!")

    return "success"


def delete_grp(id: int, db: Session, user_id: int):
    '''
    delete group and user_group by group_id
    '''
    existing_user_group = db.query(User_Group).filter(User_Group.group_id == id)
    existing_user_group.delete(synchronize_session=False)
    db.commit()

    existing_group = db.query(Group).filter(Group.id == id)
    if not existing_group.first():
        return 0
    existing_group.delete(synchronize_session=False)
    db.commit()
    return 1


def list_grps(db: Session, user_id: int):
    group_list = []
    groups = db.query(Group).all()

    for grp in groups:
        grp_dict = grp.__dict__
        grp_id = grp.id
        users_list = db.query(User_Group.user_id, User.username).\
            join(User, User_Group.user_id == User.id).filter(User_Group.group_id == grp_id).all()
        grp_dict['users'] = users_list
        group_list.append(grp_dict)

    return group_list


def list_grp(id: int, db: Session, user_id: int):

    try:
        group = db.query(Group).filter(Group.id == id).first()

        if not group:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Group not found!")
        else:
            group_dict = group.__dict__

            user_list = db.query(User_Group.user_id, User.username).\
                join(User, User_Group.user_id == User.id).filter(User_Group.group_id == group.id).all()
            group_dict['userlist'] = user_list

            return group_dict

    except Exception as ex:
        logger.error(f"Error in getting user group data : {str(ex)}")
        raise ex
