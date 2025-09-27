from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, Query, dependencies, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.enums import DbType
from db.models.models import User
from db.session import get_db
from db.views.dbconn import (
    connector_type,
    create_dbconn,
    create_restapi_db_conn,
    create_x_conn,
    delete_dbconn,
    get_restapi_conn,
    get_source_connection_preview,
    get_x_conn,
    list_dbconn,
    update_dbconn,
    update_restapi_conn,
    update_x_conn,
    validate_x_conn,
)
from db.views.permission_checker import PermissionChecker
from db.views.restapi import RestApiConnector
from schemas.dbconn import (
    ConnectionDataPreview,
    ConnectorType,
    CreateDbConn,
    CreateRestAPIConnection,
    DeleteDbCon,
    ShowDbConn,
    ShowRestAPIConnection,
    TestRestAPIConnection,
    UpdateDbConn,
    ValidateXConnection,
    ViewXConnection,
    XConnection,
    XConnGet,
    XConnValidationResponse,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/connection", response_model=ShowDbConn)
@router.post("/db-conn", response_model=ShowDbConn, deprecated=True)
def create_dbconnection(createDbConn: CreateDbConn,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user_from_token)):
    '''
    Create new database connection
    '''
    # Insert Query
    dbconn = create_dbconn(createDbConn=createDbConn,
                           db=db,
                           user_id=current_user.id)
    return dbconn


@router.get("/connections", response_model=List[ShowDbConn])
@router.get("/db-conns", response_model=List[ShowDbConn], deprecated=True)
def get_all_db_connections(db_type: Optional[List[DbType]] = Query(None, description="Filter by multiple database types"),
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user_from_token)):
    '''
    List all database connection details
    '''
    return list_dbconn(db=db, user_id=current_user.id, db_type=db_type)


@router.get("/connections/{id}", response_model=ShowDbConn)
@router.get("/db-conns/{id}", response_model=ShowDbConn, deprecated=True)
def get_db_connections(id: int,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    '''
    Get database connection details
    '''
    return list_dbconn(id=id, db=db, user_id=current_user.id)


@router.patch("/connection/{id}", response_model=ShowDbConn)
@router.patch("/db-conn/{id}", response_model=ShowDbConn, deprecated=True)
def update_db_connection(id: int,
                         updateDbConn: UpdateDbConn,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user_from_token)):
    '''
    Update database connection details
    '''
    return update_dbconn(updateDbConn=updateDbConn, id=id, db=db, user_id=current_user.id)


@router.delete("/connection/{id}", response_model=DeleteDbCon)
@router.delete("/db-con/{id}", response_model=DeleteDbCon, deprecated=True)
def delete_db_connection(id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user_from_token)):
    '''
    Delete database connection details
    '''
    db_conn_status = delete_dbconn(id=id, db=db, user_id=current_user.id)
    return {"deleted": db_conn_status}


@router.post("/connection/restapi/validate")
def validate_restapi_connection(testRestAPIConnection: TestRestAPIConnection,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user_from_token)):
    restApiConnector = RestApiConnector(method=testRestAPIConnection.method,
                                        url=testRestAPIConnection.url,
                                        params=testRestAPIConnection.params,
                                        authorization=testRestAPIConnection.authorization,
                                        headers=testRestAPIConnection.headers,
                                        body=testRestAPIConnection.body,
                                        data_url=testRestAPIConnection.data_url,
                                        is_auth_url=testRestAPIConnection.is_auth_url)
    return restApiConnector.validate_connection()


@router.post("/connection/restapi")
def create_restapi_connection(createRestAPIConnection: CreateRestAPIConnection,
                              db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user_from_token)):
    return create_restapi_db_conn(db, createRestAPIConnection, user_id=current_user.id)


@router.get("/connection/restapi/{id}", response_model=ShowRestAPIConnection)
def get_restapi_connection(id: int,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user_from_token)):
    return get_restapi_conn(db=db, id=id, user_id=current_user.id)


@router.patch("/connection/{id}/restapi")
def update_restapi_connection(id: int,
                              updateRestAPIConnection: CreateRestAPIConnection,
                              db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user_from_token)):
    return update_restapi_conn(id=id, db=db, user_id=current_user.id, updateRestAPIConnection=updateRestAPIConnection)


@router.post("/connection/x/validate", response_model=XConnValidationResponse)
def validate_x_connection(xconnection: ValidateXConnection,
                          current_user: User = Depends(get_current_user_from_token)):
    '''
    Validate X (formerly Twitter) connection
    '''
    return validate_x_conn(xconnection=xconnection)


@router.post("/connection/x", response_model=ViewXConnection)
def create_x_connection(xconnection: XConnection,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user_from_token)):
    '''
    Create X (formerly Twitter) connection
    '''
    return create_x_conn(xconnection=xconnection, db=db, user_id=current_user.id)


@router.get("/connection/{id}/x", response_model=XConnGet)
def get_x_connection(id: int,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user_from_token)):
    '''
    Get X (formerly Twitter) connection details'''
    return get_x_conn(id=id, db=db, user_id=current_user.id)


@router.patch("/connection/{id}/x", response_model=ViewXConnection)
def update_x_connection(id: int,
                        xconnection: XConnection,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user_from_token)):
    '''
    Update X (formerly Twitter) connection
    '''
    return update_x_conn(id=id, xconnection=xconnection, db=db, user_id=current_user.id)


@router.get("/connection/connector-type", response_model=List[ConnectorType])
def get_connectortype(db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    return connector_type(db=db, user_id=current_user.id)


@router.get("/connection/preview/pipelines/{id}", response_model=ConnectionDataPreview)
def get_source_preview(id: int,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    return get_source_connection_preview(db=db, id=id, user_id=current_user.id)
