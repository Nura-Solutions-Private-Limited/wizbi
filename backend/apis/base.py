from fastapi import APIRouter

from apis.v1 import (
    audit,
    dashboard,
    database,
    datalake,
    dbconn,
    diagram,
    dimension_metric,
    filelisting,
    fileupload,
    genai,
    googleanalytics,
    job,
    login,
    metadata,
    migration,
    permissions,
    pipeline,
    report,
    role,
    schedule,
    sourcedbmapping,
    tenant,
    user_group,
    user_role,
    users,
    utility,
    notifications
)

api_router = APIRouter(prefix="/rebiz/v1")
api_router.include_router(login.router, tags=["Login"])
api_router.include_router(users.router, tags=["User Management"])
api_router.include_router(utility.router, tags=["Database Utilities"])
api_router.include_router(pipeline.router, tags=["Pipeline"])
api_router.include_router(dbconn.router, tags=["Connections"])
api_router.include_router(sourcedbmapping.router, tags=["Source Mapping"])
api_router.include_router(database.router, tags=["Database Utilities"])
api_router.include_router(metadata.router, tags=["Database Utilities"])
api_router.include_router(diagram.router, tags=["Diagram"])
api_router.include_router(audit.router, tags=["Audit"])
api_router.include_router(job.router, tags=["Job"])
api_router.include_router(report.router, tags=["Reports"])
api_router.include_router(schedule.router, tags=["Schedule"])
api_router.include_router(fileupload.router, tags=["Files"])
api_router.include_router(filelisting.router, tags=["Files"])
api_router.include_router(dashboard.router, tags=["Reports"])
api_router.include_router(dimension_metric.router, tags=["Google Analytics"])
api_router.include_router(googleanalytics.router, tags=["Google Analytics"])
api_router.include_router(permissions.router, tags=["User Management"])
api_router.include_router(role.router, tags=["User Management"])
api_router.include_router(tenant.router, tags=["User Management"])
api_router.include_router(user_group.router, tags=["User Management"])
api_router.include_router(user_role.router, tags=["User Management"])
api_router.include_router(migration.router, tags=["Database Migration"])
api_router.include_router(genai.router, tags=["Artificial Intelligence"])
api_router.include_router(datalake.router, tags=["Data Lake"])
api_router.include_router(notifications.router, tags=["Notifications"])
