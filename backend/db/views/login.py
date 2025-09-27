from db.models.models import User, User_Group, Group, Permissions, UserRole, Role
from sqlalchemy.orm import Session

from db.views.role import RoleType


def get_user(username: str, db: Session):
    '''
    Return User details
    '''
    user = db.query(User).filter(User.username == username).first()
    return user


def get_group(user_id: int, db: Session):
    '''
    Return User Group details
    '''
    group_list = list()

    # query user_group for the user id
    user_groups = db.query(User_Group).filter(User_Group.user_id == user_id).all()

    # query group for each group id
    for user_group in user_groups:
        # user_group_dict = user_group.__dict__
        group = db.query(Group).filter(Group.id == user_group.group_id).first()
        # group_dict = group.__dict__
        # user_group_dict['group'] = group_dict
        group_list.append(group)
    return group_list


def get_permission(user_id: int, db: Session):
    '''
    Return Permission details
    '''
    user_permissions = db.query(Permissions).\
        join(UserRole, UserRole.role_id == Permissions.role_id).filter(UserRole.user_id == user_id).all()

    pipelines = list()
    etls = list()
    connections = list()
    dashboards = list()
    jobs = list()
    audits = list()
    genai = list()
    roles = list()
    reports = list()

    admin_user_role = db.query(Role.id, Role.role_type).\
        join(UserRole, UserRole.role_id == Role.id).\
        filter(UserRole.user_id == user_id, Role.role_type == str(RoleType.ADMIN.name).title()).first()

    all_user_role = db.query(Role.id, Role.role_type).\
        join(UserRole, UserRole.role_id == Role.id).\
        filter(UserRole.user_id == user_id, Role.role_type == str(RoleType.ALL.name).title()).first()

    user_permission = {}

    if admin_user_role:
        if admin_user_role.role_type.upper() == RoleType.ADMIN.name:
            user_permission['admin'] = True
            user_permission['role'] = RoleType.ADMIN.name
            user_permission['pipelines'] = True
            user_permission['etls'] = True
            user_permission['connections'] = True
            user_permission['dashboards'] = True
            user_permission['jobs'] = True
            user_permission['audits'] = True
            user_permission['genai'] = True
            user_permission['reports'] = True
    elif all_user_role:
        if all_user_role.role_type.upper() == RoleType.ALL.name:
            user_permission['admin'] = False
            user_permission['role'] = RoleType.ALL.name
            user_permission['pipelines'] = True
            user_permission['etls'] = True
            user_permission['connections'] = True
            user_permission['dashboards'] = True
            user_permission['jobs'] = True
            user_permission['audits'] = True
            user_permission['genai'] = True
            user_permission['reports'] = True
    else:
        if user_permissions:
            for user_perm in user_permissions:
                pipelines.append(user_perm.pipelines_allowed)
                etls.append(user_perm.etl_allowed)
                connections.append(user_perm.connections_allowed)
                dashboards.append(user_perm.dashboards_allowed)
                jobs.append(user_perm.jobs_allowed)
                audits.append(user_perm.audits_allowed)
                genai.append(user_perm.genai_allowed)
                reports.append(user_perm.reports_allowed)
                role = db.query(Role).filter(Role.id == user_perm.role_id).first()

                if role.role_type.upper() == RoleType.ADMIN.name:
                    roles.append(1)
                elif role.role_type.upper() == RoleType.ALL.name:
                    roles.append(2)
                elif role.role_type.upper() == RoleType.FEATURE.name:
                    roles.append(3)
                elif role.role_type.upper() == RoleType.COMPONENT.name:
                    roles.append(4)

            if min(roles) == 1:
                user_permission['admin'] = True
                user_permission['role'] = RoleType.ADMIN.name
                user_permission['pipelines'] = True
                user_permission['etls'] = True
                user_permission['connections'] = True
                user_permission['dashboards'] = True
                user_permission['jobs'] = True
                user_permission['audits'] = True
                user_permission['genai'] = True
                user_permission['reports'] = True
            elif min(roles) == 2:
                user_permission['admin'] = False
                user_permission['role'] = RoleType.ALL.name
                user_permission['pipelines'] = True
                user_permission['etls'] = True
                user_permission['connections'] = True
                user_permission['dashboards'] = True
                user_permission['jobs'] = True
                user_permission['audits'] = True
                user_permission['genai'] = True
                user_permission['reports'] = True
            elif min(roles) in [3, 4]:
                user_permission['admin'] = False
                user_permission['role'] = RoleType.FEATURE.name if min(roles) == 3 else RoleType.COMPONENT.name
                user_permission['pipelines'] = True if max(pipelines) == 1 else False
                user_permission['etls'] = True if max(etls) == 1 else False
                user_permission['connections'] = True if max(connections) == 1 else False
                user_permission['dashboards'] = True if max(dashboards) == 1 else False
                user_permission['jobs'] = True if max(jobs) == 1 else False
                user_permission['audits'] = True if max(audits) == 1 else False
                user_permission['genai'] = True if max(genai) == 1 else False
                user_permission['reports'] = True if max(reports) == 1 else False
        else:
            user_roles = db.query(Role.role_type).\
                join(UserRole, Role.id == UserRole.role_id).filter(UserRole.user_id == user_id).all()
            for role in user_roles:
                if role.role_type.upper() == RoleType.ADMIN.name:
                    roles.append(1)
                elif role.role_type.upper() == RoleType.ALL.name:
                    roles.append(2)
                elif role.role_type.upper() == RoleType.FEATURE.name:
                    roles.append(3)
                elif role.role_type.upper() == RoleType.COMPONENT.name:
                    roles.append(4)
            user_permission['admin'] = False
            user_permission['role'] = RoleType.FEATURE.name if min(roles) == 3 else RoleType.COMPONENT.name
            user_permission['pipelines'] = False
            user_permission['etls'] = False
            user_permission['connections'] = False
            user_permission['dashboards'] = False
            user_permission['jobs'] = False
            user_permission['audits'] = False
            user_permission['genai'] = False
            user_permission['reports'] = False

    return user_permission
