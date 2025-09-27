from enum import Enum

import structlog
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.models.models import Role, User, UserRole
from schemas.role import CreateRole, UpdateRole

logger = structlog.getLogger(__name__)


class RoleType(Enum):
    ADMIN = 1
    ALL = 2
    FEATURE = 3
    COMPONENT = 4


def role_type(db: Session, user_id: int):
    '''
    Role type
    '''
    role_type_list = list()
    for roleType in RoleType:
        role_type_dict = {}
        role_type_dict['id'] = roleType.value
        role_type_dict['name'] = str(roleType.name).title()
        role_type_list.append(role_type_dict)
    return role_type_list


def create_rol(createRole: CreateRole, db: Session, user_id: int):
    '''
    Create role
    '''
    try:
        existing_role = db.query(Role).filter(Role.name == createRole.name).first()

        if not existing_role:
            # insert row in role table for the role
            role = Role(role_type=createRole.role_type,
                        description=createRole.description,
                        name=createRole.name)

            db.add(role)
            db.commit()
            db.refresh(role)

            # role_permission_list = []
            role_user_list = []

            # # insert rows in the role_permission
            # rolepermissions = createRole.rolepermissions

            # for rolepermission in rolepermissions:
            #     roleperm = RolePermission(role_id=role.id, permission_id=rolepermission.id)
            #     db.add(roleperm)
            #     db.commit()
            #     db.refresh(roleperm)
            #     db.refresh(role)
            #     roleperm = roleperm.__dict__
            #     roleperm.update({'id': roleperm.pop('permission_id')})
            #     roleperm['name'] = rolepermission.name
            #     role_permission_list.append(roleperm)

            # insert rows in the user_role
            roleusers = createRole.roleusers

            for roleuser in roleusers:
                userrole = UserRole(role_id=role.id, user_id=roleuser.id)
                db.add(userrole)
                db.commit()
                db.refresh(userrole)
                db.refresh(role)
                userrole = userrole.__dict__
                userrole.update({'id': userrole.pop('user_id')})
                userrole['name'] = roleuser.name
                role_user_list.append(userrole)

            role_dict = role.__dict__
            # role_dict['rolepermissions'] = role_permission_list
            role_dict['roleusers'] = role_user_list
            return role_dict
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Role with name {createRole.name} already exist, Please give differnt name")

    except Exception as ex:
        logger.error(f"Error in creating role : {str(ex)}")
        raise ex


def update_rol(updateRole: UpdateRole, db: Session, user_id: int, id: int):
    '''
    Update role
    '''
    role = db.query(Role).filter(Role.id == id).first()

    role.role_type = updateRole.role_type
    role.description = updateRole.description
    role.name = updateRole.name

    db.commit()
    db.refresh(role)

    # rolepermissions = updateRole.rolepermissions
    roleusers = updateRole.roleusers

    # # update role_permission
    # exist_role_perm_ids = list()

    # # get all permission ids for the role
    # extrolepermissions = db.query(RolePermission).filter(RolePermission.role_id == id).all()
    # if extrolepermissions:
    #     for extrolepermission in extrolepermissions:
    #         exist_role_perm_ids.append(extrolepermission.permission_id)

    # # loop through all role permissions
    # for rolepermission in rolepermissions:
    #     # if same permission is assigned then delete from list
    #     if rolepermission.id in exist_role_perm_ids:
    #         exist_role_perm_ids.remove(rolepermission.id)
    #     else:
    #         # add new permission assigned to role
    #         roleperm = RolePermission(role_id=id, permission_id=rolepermission.id)
    #         db.add(roleperm)
    #         db.commit()
    #         db.refresh(roleperm)
    #         db.refresh(role)

    # search all role_permission to be deleted, based on permissions ids
    # tobe_del_ext_role_perm_ids = db.query(RolePermission).
    #            filter(RolePermission.permission_id.in_(exist_role_perm_ids))
    # if tobe_del_ext_role_perm_ids.all():
    #     tobe_del_ext_role_perm_ids.delete(synchronize_session=False)
    #     db.commit()
    #     db.refresh(roleperm)
    #     db.refresh(role)

    # update user role
    exist_role_user_ids = list()

    # get all user ids for the role
    extroleusers = db.query(UserRole).filter(UserRole.role_id == id).all()
    if extroleusers:
        for extroleuser in extroleusers:
            exist_role_user_ids.append(extroleuser.user_id)

    # loop through all role users
    for roleuser in roleusers:
        # if same user is assigned then delete from list
        if roleuser.id in exist_role_user_ids:
            exist_role_user_ids.remove(roleuser.id)
        else:
            # add new user assigned to role
            userrole = UserRole(role_id=id, user_id=roleuser.id)
            db.add(userrole)
            db.commit()
            db.refresh(userrole)
            db.refresh(role)

    # search all role_permission to be deleted, based on permissions ids
    tobe_del_ext_role_user_ids = db.query(UserRole).filter(UserRole.user_id.in_(exist_role_user_ids))
    if tobe_del_ext_role_user_ids.all():
        tobe_del_ext_role_user_ids.delete(synchronize_session=False)
        db.commit()
        db.refresh(userrole)
        db.refresh(role)

    role_dict = role.__dict__
    # role_dict['rolepermissions'] = rolepermissions
    role_dict['roleusers'] = roleusers

    return role_dict


def list_rols(db: Session, user_id: int):
    '''
    Get all the roles
    '''
    try:
        role_list = list()

        roles = db.query(Role).all()

        for role in roles:
            role_dict = role.__dict__
            # role_permissions = db.query(RolePermission.permission_id.label("id"), Permissions.name).\
            #     join(Permissions, RolePermission.permission_id == Permissions.id).\
            #     filter(RolePermission.role_id == role.id).all()
            # role_dict['rolepermissions'] = role_permissions

            role_users = db.query(UserRole.user_id.label("id"), User.username.label("name")).\
                join(User, UserRole.user_id == User.id).\
                filter(UserRole.role_id == role.id).all()
            role_dict['roleusers'] = role_users

            role_list.append(role_dict)

        return role_list

    except Exception as ex:
        logger.error(f"Error in getting all the role data : {str(ex)}")
        raise ex


def list_rol(id: int, db: Session, user_id: int):
    '''
    Get a specific role by id
    '''
    try:
        role = db.query(Role).filter(Role.id == id).first()

        role_dict = role.__dict__
        # role_permissions = db.query(RolePermission.permission_id.label("id"), Permissions.name).\
        #     join(Permissions, RolePermission.permission_id == Permissions.id).\
        #     filter(RolePermission.role_id == id).all()
        # role_dict['rolepermissions'] = role_permissions

        role_users = db.query(UserRole.user_id.label("id"), User.username.label("name")).\
            join(User, UserRole.user_id == User.id).\
            filter(UserRole.role_id == id).all()
        role_dict['roleusers'] = role_users

        return role_dict
    except Exception as ex:
        logger.error(f"Error in getting role data : {str(ex)}")
        raise ex


def delete_rol(id: int, db: Session, user_id: int):
    '''
    delete role by id
    '''
    existing_role = db.query(Role).filter(Role.id == id).first()

    if not existing_role:
        return 0
    db.delete(existing_role)
    db.commit()
    return 1
