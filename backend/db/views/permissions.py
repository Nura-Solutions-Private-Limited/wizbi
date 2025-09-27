import structlog
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.enums import PermissionType
from db.models.models import Permissions, Role
from schemas.permissions import CreatePermissions, UpdatePermissions

logger = structlog.getLogger(__name__)


def create_prmsn(createPermissions: CreatePermissions, db: Session, user_id: int):
    '''
    Create permissions
    '''
    try:
        existing_permission = db.query(Permissions).filter(Permissions.name == createPermissions.name).first()

        if not existing_permission:
            permission = Permissions(name=createPermissions.name,
                                     description=createPermissions.description,
                                     role_id=createPermissions.role_id,
                                     pipelines_allowed=createPermissions.pipelines_allowed,
                                     etl_allowed=createPermissions.etl_allowed,
                                     connections_allowed=createPermissions.connections_allowed,
                                     dashboards_allowed=createPermissions.dashboards_allowed,
                                     reports_allowed=createPermissions.reports_allowed,
                                     jobs_allowed=createPermissions.jobs_allowed,
                                     audits_allowed=createPermissions.audits_allowed,
                                     genai_allowed=createPermissions.genai_allowed,
                                     dashboard_ids=createPermissions.dashboard_ids,
                                     report_ids=createPermissions.report_ids,
                                     connection_ids=createPermissions.connection_ids,
                                     pipeline_ids=createPermissions.pipeline_ids)

            db.add(permission)
            db.commit()
            db.refresh(permission)
            permission = permission.__dict__
            permission['role_name'] = createPermissions.role_name
            return permission
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Permission with name {createPermissions.name}"
                                "already exist, Please give different name.")

    except Exception as ex:
        logger.error(f"Error in creating permission : {str(ex)}")
        raise ex


def update_prmsn(updatePermission: UpdatePermissions, db: Session, user_id: int, id: int):
    '''
    Update permission
    '''
    permission = db.query(Permissions).filter(Permissions.id == id).first()

    permission.name = updatePermission.name
    permission.description = updatePermission.description
    permission.role_id = updatePermission.role_id
    permission.pipelines_allowed = updatePermission.pipelines_allowed
    permission.etl_allowed = updatePermission.etl_allowed
    permission.connections_allowed = updatePermission.connections_allowed
    permission.dashboards_allowed = updatePermission.dashboards_allowed
    permission.reports_allowed = updatePermission.reports_allowed
    permission.jobs_allowed = updatePermission.jobs_allowed
    permission.audits_allowed = updatePermission.audits_allowed
    permission.genai_allowed = updatePermission.genai_allowed
    permission.dashboard_ids = updatePermission.dashboard_ids
    permission.report_ids = updatePermission.report_ids
    permission.connection_ids = updatePermission.connection_ids
    permission.pipeline_ids = updatePermission.pipeline_ids

    db.commit()
    db.refresh(permission)
    permission = permission.__dict__
    permission['role_name'] = updatePermission.role_name
    return permission


def list_prmsns(db: Session, user_id: int):
    '''
    Get all the permissions
    '''
    try:
        permission_list = list()

        permissions = db.query(Permissions).all()

        for permisson in permissions:
            if permisson.role_id is None:  # Handle missing role_id
                logger.warning(f"Permission with ID {permisson.id} has a null role_id and will be skipped.")
                continue  # Skip this permission if role_id is None
            role = db.query(Role).filter(Role.id == permisson.role_id).first()
            permisson = permisson.__dict__
            permisson['role_name'] = role.name
            permission_list.append(permisson)

        return permission_list

    except Exception as ex:
        logger.error(f"Error in getting all the permission data : {str(ex)}")
        raise ex


def list_prmsn(id: int, db: Session, user_id: int):
    '''
    Get a permission by id
    '''
    try:
        permission = db.query(Permissions).filter(Permissions.id == id).first()
        role = db.query(Role).filter(Role.id == permission.role_id).first()
        permission = permission.__dict__
        permission['role_name'] = role.name
        return permission

    except Exception as ex:
        logger.error(f"Error in getting permission data : {str(ex)}")
        raise ex


def delete_prmsn(id: int, db: Session, user_id: int):
    '''
    delete permission by id
    '''
    existing_permission = db.query(Permissions).filter(Permissions.id == id)

    if not existing_permission.first():
        return 0
    existing_permission.delete(synchronize_session=False)
    db.commit()
    return 1


def permission_type(db: Session, user_id: int):
    '''
    Get permission type, returns list of dictionary having permissions and their type
    '''
    data = [
        {
            "id": 1,
            "permission_type": PermissionType.PIPELINES.value,
            "description": "Pipelines",
            "type": "permission",
            "enabled": True,
        },
        {
            "id": 2,
            "permission_type": PermissionType.CONNECTIONS.value,
            "description": "Connections",
            "type": "permission",
            "enabled": True,
        },
        {
            "id": 3,
            "permission_type": PermissionType.ETLS.value,
            "description": "Etls",
            "type": "permission",
            "enabled": True
        },
        {
            "id": 4,
            "permission_type": PermissionType.DASHBOARDS.value,
            "description": "Dashboards",
            "type": "permission",
            "enabled": True
        },
        {
            "id": 5,
            "permission_type": PermissionType.REPORTS.value,
            "description": "Reports",
            "type": "permission",
            "enabled": True
        },
        {
            "id": 6,
            "permission_type": PermissionType.JOBS.value,
            "description": "jobs",
            "type": "permission",
            "enabled": True
        },
        {
            "id": 7,
            "permission_type": PermissionType.AUDITS.value,
            "description": "Audits",
            "type": "permission",
            "enabled": True
        },
        {
            "id": 8,
            "permission_type": PermissionType.GENAI.value,
            "description": "Gen AI",
            "type": "permission",
            "enabled": True
        },
    ]
    return data
