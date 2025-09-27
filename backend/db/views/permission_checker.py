from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session

from db.views.role import RoleType
from db.models.models import User, Pipeline, Permissions, UserRole
from db.views.login import get_permission
from apis.v1.login import get_current_user_from_token


class PermissionChecker:

    def __init__(self) -> None:
        pass

    # def __call__(self, db: Session, current_user: User = Depends(get_current_user_from_token)) -> bool:
    #     try:
    #         user_permission = get_permission(user_id=current_user.id, db=db)
    #         for r_perm in self.required_permissions:
    #             if r_perm not in user_permission:
    #                 raise HTTPException(
    #                     status_code=status.HTTP_401_UNAUTHORIZED,
    #                     detail='Permissions'
    #                 )
    #         return True
    #     except Exception as ex:
    #         print(f'error in perm checker {ex}')

    def get_permission(self, db: Session, user_id: int, permission_for: str):
        '''
        Check permission for a user for based on
        permission_for(pipelines, connections, dashboards, reports, jobs, audits & etls)
        '''
        permissions = get_permission(user_id=user_id, db=db)
        if permission_for:
            if permissions.get('admin'):
                return True, []
            elif permissions.get('role') == RoleType.ALL.name:
                return True, []
            elif permissions.get('role') == RoleType.FEATURE.name and permissions.get(permission_for):
                return True, []
            # elif permissions.get('role') == RoleType.FEATURE.name and permissions.get('connections'):
            #     return True, []
            # elif permissions.get('role') == RoleType.FEATURE.name and permissions.get('dashboards'):
            #     return True, []
            # elif permissions.get('role') == RoleType.FEATURE.name and permissions.get('reports'):
            #     return True, []
            elif permissions.get('role') == RoleType.COMPONENT.name and permissions.get(permission_for):
                # TODO list of pipelines
                if permission_for == 'pipelines':
                    ids = db.query(Permissions.pipeline_ids).\
                        join(UserRole, Permissions.role_id == UserRole.role_id).\
                        join(User, UserRole.user_id == User.id).filter(UserRole.user_id == user_id).\
                        filter(Permissions.pipelines_allowed == 1).all()
                elif permission_for == 'connections':
                    ids = db.query(Permissions.connection_ids).\
                        join(UserRole, Permissions.role_id == UserRole.role_id).\
                        join(User, UserRole.user_id == User.id).filter(UserRole.user_id == user_id).\
                        filter(Permissions.connections_allowed == 1).all()
                elif permission_for == 'dashboards':
                    ids = db.query(Permissions.dashboard_ids).\
                        join(UserRole, Permissions.role_id == UserRole.role_id).\
                        join(User, UserRole.user_id == User.id).filter(UserRole.user_id == user_id).\
                        filter(Permissions.dashboards_allowed == 1).all()
                elif permission_for == 'reports':
                    ids = db.query(Permissions.report_ids).\
                        join(UserRole, Permissions.role_id == UserRole.role_id).\
                        join(User, UserRole.user_id == User.id).filter(UserRole.user_id == user_id).\
                        filter(Permissions.reports_allowed == 1).all()
                id_list = []

                for id in ids:
                    print(id[0])
                    id_list += id[0]

                print(id_list)
                # remove duplicates if any
                uniq_ids = list(set(id_list))
                return True, uniq_ids
            else:
                return False, []
        else:
            return False, []
