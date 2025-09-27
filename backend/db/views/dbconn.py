from typing import List, Optional

import structlog
import tweepy
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.enums import DbType
from db.models.models import (
    Connection_Ext,
    ConnectorType,
    Db_Conn,
    Pipeline,
    Rest_Api_Db_Conn,
    X_Conn,
)
from db.views.permission_checker import PermissionChecker
from db.views.restapi import RestApiConnector
from db.views.restapidataload import RestAPIDataLoad
from schemas.dbconn import (
    CreateDbConn,
    CreateRestAPIConnection,
    ShowRestAPIConnection,
    UpdateDbConn,
    ValidateXConnection,
    XConnection,
)

logger = structlog.getLogger(__name__)


def create_dbconn(createDbConn: CreateDbConn, db: Session, user_id: int):
    """
    Create new connections
    """
    existing_db_conn = db.query(Db_Conn).filter(Db_Conn.db_conn_name == createDbConn.db_conn_name).first()

    if existing_db_conn:
        raise Exception(f"Database connection already exists with name {createDbConn.db_conn_name}")
    dbconn = Db_Conn(
        user_id=user_id,
        db_conn_name=createDbConn.db_conn_name,
        db_name=createDbConn.db_name,
        db_type=createDbConn.db_type,
        db_host=createDbConn.db_host,
        db_port=createDbConn.db_port,
        db_username=createDbConn.db_username,
        db_password=createDbConn.db_password,
        sub_type=createDbConn.sub_type,
        s3_access_key_id=createDbConn.s3_access_key_id,
        s3_secret_access_key=createDbConn.s3_secret_access_key,
        s3_bucket=createDbConn.s3_bucket,
        s3_bucket_path=createDbConn.s3_bucket_path,
        s3_bucket_region=createDbConn.s3_bucket_region,
        iceberg_database=createDbConn.iceberg_database,
        iceberg_table=createDbConn.iceberg_table,
        duckdb_database=createDbConn.duckdb_database,
        duckdb_lfs_path=createDbConn.duckdb_lfs_path,
        dbt_project_name=createDbConn.dbt_project_name,
        gdrive_client_id=createDbConn.gdrive_client_id,
        gdrive_client_secret=createDbConn.gdrive_client_secret,
        gdrive_access_token=createDbConn.gdrive_access_token,
        gdrive_refresh_token=createDbConn.gdrive_refresh_token,
        gdrive_token_uri=createDbConn.gdrive_token_uri,
        gdrive_scopes=createDbConn.gdrive_scopes,
        gdrive_path=createDbConn.gdrive_path,
        gdrive_prefix=createDbConn.gdrive_prefix,
        lfs_path=createDbConn.lfs_path,
        lfs_prefix=createDbConn.lfs_prefix,
        lfs_mount_point=createDbConn.lfs_mount_point,
        ga_property_id=createDbConn.ga_property_id,
        ga_auth_json=createDbConn.ga_auth_json,
    )

    db.add(dbconn)
    db.commit()
    db.refresh(dbconn)

    connection_ext_list = []
    connection_exts = createDbConn.connection_ext
    if connection_exts:
        for connection_ext in connection_exts:
            connection_Ext = Connection_Ext(
                file_name=connection_ext.file_name,
                file_description=connection_ext.file_description,
                dimension=connection_ext.dimension,
                dimension_metric=connection_ext.dimension_metric,
                db_conn_id=dbconn.id,
            )
            db.add(connection_Ext)
            db.commit()
            db.refresh(connection_Ext)
            db.refresh(dbconn)
            conn_ext_dict = connection_Ext.__dict__
            conn_ext_dict.pop("db_conn_id")
            connection_ext_list.append(conn_ext_dict)

    dbconn_dict = dbconn.__dict__
    dbconn_dict["connection_ext"] = connection_ext_list
    return dbconn_dict


def list_dbconn(db: Session, user_id: int, id: int = None, db_type: Optional[List[str]] = None):
    """
    Fetch connections
    """
    permissionChecker = PermissionChecker()
    connection_permission, connection_ids = permissionChecker.get_permission(
        db=db, user_id=user_id, permission_for="connections"
    )
    logger.info(f"Userid {user_id} Connection permission {connection_permission} and ids {connection_ids}")

    if connection_permission and not connection_ids:
        # In case of role other than component
        if id:
            db_conn = db.query(Db_Conn).filter(Db_Conn.id == id).first()
            connection_exts = db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == db_conn.id).all()
            connection_ext_list = []
            for connection_ext in connection_exts:
                connection_ext_list.append(connection_ext.__dict__)
            db_conn_dict = db_conn.__dict__
            db_conn_dict["connection_ext"] = connection_ext_list
            db_conn = db_conn_dict
        else:
            if db_type and len(db_type) > 0:
                print(db_type)
                # Convert DbType enum values to strings
                db_type_values = [t.value for t in db_type]                
                db_conns = db.query(Db_Conn).filter(Db_Conn.db_type.in_(db_type_values)).order_by(Db_Conn.id.desc()).all()
            else:
                db_conns = db.query(Db_Conn).order_by(Db_Conn.id.desc()).all()
            db_conn_list = []

            for db_conn in db_conns:
                connection_exts = db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == db_conn.id).all()
                connection_ext_list = []
                if connection_exts:
                    for connection_ext in connection_exts:
                        connection_ext_list.append(connection_ext.__dict__)
                    db_conn_dict = db_conn.__dict__
                    db_conn_dict["connection_ext"] = connection_ext_list
                    db_conn_list.append(db_conn_dict)
                else:
                    db_conn_dict = db_conn.__dict__
                    db_conn_list.append(db_conn_dict)
            db_conn = db_conn_list
    elif connection_permission and connection_ids:
        # In case of role component with specific connection access
        if id:
            db_conn = db.query(Db_Conn).filter(Db_Conn.id == id, Db_Conn.id.in_(connection_ids)).first()
            connection_exts = (
                db.query(Connection_Ext)
                .filter(Connection_Ext.db_conn_id == db_conn.id, Connection_Ext.db_conn_id.in_(connection_ids))
                .all()
            )
            connection_ext_list = []
            for connection_ext in connection_exts:
                connection_ext_list.append(connection_ext.__dict__)
            db_conn_dict = db_conn.__dict__
            db_conn_dict["connection_ext"] = connection_ext_list
            db_conn = db_conn_dict
        else:
            db_conns = db.query(Db_Conn).filter(Db_Conn.id.in_(connection_ids)).order_by(Db_Conn.id.desc()).all()
            db_conn_list = []

            for db_conn in db_conns:
                connection_exts = db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == db_conn.id).all()
                connection_ext_list = []
                if connection_exts:
                    for connection_ext in connection_exts:
                        connection_ext_list.append(connection_ext.__dict__)
                    db_conn_dict = db_conn.__dict__
                    db_conn_dict["connection_ext"] = connection_ext_list
                    db_conn_list.append(db_conn_dict)
                else:
                    db_conn_dict = db_conn.__dict__
                    db_conn_list.append(db_conn_dict)
            db_conn = db_conn_list
    return db_conn


def update_dbconn(updateDbConn: UpdateDbConn, db: Session, user_id: int, id: int = None):
    """
    Update connections
    """
    # TODO add filter to update only if user has permission to update the connection
    db_conn = db.query(Db_Conn).filter(Db_Conn.id == id, Db_Conn.user_id == user_id).first()

    db_conn.user_id = user_id
    db_conn.db_conn_name = updateDbConn.db_conn_name
    db_conn.db_name = updateDbConn.db_name
    db_conn.db_type = updateDbConn.db_type
    db_conn.db_host = updateDbConn.db_host
    db_conn.db_port = updateDbConn.db_port
    db_conn.db_username = updateDbConn.db_username
    db_conn.db_password = updateDbConn.db_password
    db_conn.sub_type = updateDbConn.sub_type
    db_conn.s3_access_key_id = updateDbConn.s3_access_key_id
    db_conn.s3_secret_access_key = updateDbConn.s3_secret_access_key
    db_conn.s3_bucket = updateDbConn.s3_bucket
    db_conn.s3_bucket_path = updateDbConn.s3_bucket_path
    db_conn.s3_bucket_region = updateDbConn.s3_bucket_region
    db_conn.iceberg_database = updateDbConn.iceberg_database
    db_conn.iceberg_table = updateDbConn.iceberg_table
    db_conn.duckdb_database = updateDbConn.duckdb_database
    db_conn.duckdb_lfs_path = updateDbConn.duckdb_lfs_path
    db_conn.dbt_project_name = updateDbConn.dbt_project_name
    db_conn.gdrive_client_id = updateDbConn.gdrive_client_id
    db_conn.gdrive_client_secret = updateDbConn.gdrive_client_secret
    db_conn.gdrive_access_token = updateDbConn.gdrive_access_token
    db_conn.gdrive_refresh_token = updateDbConn.gdrive_refresh_token
    db_conn.gdrive_token_uri = updateDbConn.gdrive_token_uri
    db_conn.gdrive_scopes = updateDbConn.gdrive_scopes
    db_conn.gdrive_path = updateDbConn.gdrive_path
    db_conn.gdrive_prefix = updateDbConn.gdrive_prefix
    db_conn.lfs_path = updateDbConn.lfs_path
    db_conn.lfs_prefix = updateDbConn.lfs_prefix
    db_conn.lfs_mount_point = updateDbConn.lfs_mount_point

    db.commit()
    db.refresh(db_conn)

    connection_ext_list = []
    conn_ext_ids = []
    connection_exts = updateDbConn.connection_ext if updateDbConn.connection_ext else []

    # get all connection ext id for the db connection id
    exconn_ext_ids = db.query(Connection_Ext).filter(Connection_Ext.db_conn_id == id).all()
    if exconn_ext_ids:
        for exconn_ext_id in exconn_ext_ids:
            conn_ext_ids.append(exconn_ext_id.id)

    # if connection ext id exist in database then update else insert
    # in case of any missing ext, delete it from database
    for connection_ext in connection_exts:
        if connection_ext.id:
            # delete connection ext id from existing connection ext list
            if connection_ext.id in conn_ext_ids:
                conn_ext_ids.remove(connection_ext.id)
            existing_conn_ext = db.query(Connection_Ext).filter(Connection_Ext.id == connection_ext.id).first()
            if existing_conn_ext:
                if (
                    connection_ext.file_name != existing_conn_ext.file_name
                    or connection_ext.file_description != existing_conn_ext.file_description
                    or connection_ext.dimension != existing_conn_ext.dimension
                    or connection_ext.dimension_metric != existing_conn_ext.dimension_metric
                ):
                    # Update connection ext values
                    existing_conn_ext.file_name = connection_ext.file_name
                    existing_conn_ext.file_description = connection_ext.file_description
                    existing_conn_ext.dimension = connection_ext.dimension
                    existing_conn_ext.dimension_metric = connection_ext.dimension_metric

                    # commit updates
                    db.commit()
                    db.refresh(existing_conn_ext)
                    db.refresh(db_conn)
                    connection_ext_list.append(existing_conn_ext)
                else:
                    connection_ext_list.append(existing_conn_ext)
            else:
                raise Exception(f"Invalid connection_ext- {connection_ext.id}")
        else:
            connection_Ext = Connection_Ext(
                file_name=connection_ext.file_name,
                file_description=connection_ext.file_description,
                dimension=connection_ext.dimension,
                dimension_metric=connection_ext.dimension_metric,
                db_conn_id=id,
            )
            db.add(connection_Ext)
            db.commit()
            db.refresh(connection_Ext)
            db.refresh(db_conn)
            connection_ext_list.append(connection_Ext)

    # delete connection ext which were un-selected while updating
    tobe_del_ext_ids = db.query(Connection_Ext).filter(Connection_Ext.id.in_(conn_ext_ids))
    if tobe_del_ext_ids.all():
        tobe_del_ext_ids.delete(synchronize_session=False)
        db.commit()
        db.refresh(connection_Ext)
        db.refresh(db_conn)

    dbconn_dict = db_conn.__dict__
    dbconn_dict["connection_ext"] = connection_ext_list
    return dbconn_dict


def delete_dbconn(db: Session, id: int, user_id: int):
    """
    Delete database connections
    """
    # TODO add filter to delete only if user has permission to delete the connection
    existing_db_conn = db.query(Db_Conn).filter(Db_Conn.id == id, Db_Conn.user_id == user_id)
    if not existing_db_conn.first():
        return 0
    existing_db_conn.delete(synchronize_session=False)
    db.commit()
    return 1


def create_restapi_db_conn(db: Session, createRestAPIConnection: CreateRestAPIConnection, user_id: int):
    """
    Create restapi connection
    """
    existing_db_conn = db.query(Db_Conn).filter(Db_Conn.db_conn_name == createRestAPIConnection.db_conn_name).first()

    if existing_db_conn:
        raise HTTPException(
            detail=f"Connection with name :{createRestAPIConnection.db_conn_name} exist",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    dbconn = Db_Conn(
        user_id=user_id,
        db_conn_name=createRestAPIConnection.db_conn_name,
        db_type=createRestAPIConnection.db_type,
        sub_type=createRestAPIConnection.sub_type,
    )
    db.add(dbconn)
    db.flush()
    # db.refresh(dbconn)

    rest_Api_Db_Conn = Rest_Api_Db_Conn(
        method=createRestAPIConnection.method,
        url=createRestAPIConnection.url,
        params=createRestAPIConnection.params,
        authorization=createRestAPIConnection.authorization,
        headers=createRestAPIConnection.headers,
        body=createRestAPIConnection.body,
        data_url=createRestAPIConnection.data_url,
        is_auth_url=createRestAPIConnection.is_auth_url,
        db_conn_id=dbconn.id,
    )
    db.add(rest_Api_Db_Conn)
    db.commit()
    return dbconn


def connector_type(db: Session, user_id: int):
    """
    Return supported database type
    """
    connectorType = db.query(ConnectorType).all()
    return connectorType


def get_restapi_conn(db: Session, user_id: int, id: int = None):
    """
    Get restapi connection details for a given connection id
    """
    permissionChecker = PermissionChecker()
    connection_permission, connection_ids = permissionChecker.get_permission(
        db=db, user_id=user_id, permission_for="connections"
    )
    logger.info(f"Userid {user_id} Connection permission {connection_permission} and ids {connection_ids}")

    if connection_permission and not connection_ids:
        # In case of role other than component
        if id:
            db_conn = db.query(Db_Conn).filter(Db_Conn.id == id).first()
            if db_conn:
                restapi_connection = (
                    db.query(Rest_Api_Db_Conn).filter(Rest_Api_Db_Conn.db_conn_id == db_conn.id).first()
                )

                if restapi_connection:
                    restapi_connection_dict = restapi_connection.__dict__
                    db_conn_dict = db_conn.__dict__
                    db_conn_dict["method"] = restapi_connection_dict.get("method")
                    db_conn_dict["url"] = restapi_connection_dict.get("url")
                    db_conn_dict["params"] = restapi_connection_dict.get("params")
                    db_conn_dict["authorization"] = restapi_connection_dict.get("authorization")
                    db_conn_dict["headers"] = restapi_connection_dict.get("headers")
                    db_conn_dict["body"] = restapi_connection_dict.get("body")
                    db_conn_dict["data_url"] = restapi_connection_dict.get("data_url")
                    db_conn_dict["is_auth_url"] = restapi_connection_dict.get("is_auth_url")
                    db_conn = db_conn_dict

            db_conn = db_conn_dict

    elif connection_permission and connection_ids:
        # In case of role component with specific connection access
        if id:
            db_conn = db.query(Db_Conn).filter(Db_Conn.id == id, Db_Conn.id.in_(connection_ids)).first()
            if db_conn:
                restapi_connection = (
                    db.query(Rest_Api_Db_Conn).filter(Rest_Api_Db_Conn.db_conn_id == db_conn.id).first()
                )

                if restapi_connection:
                    restapi_connection_dict = restapi_connection.__dict__
                    db_conn_dict = db_conn.__dict__
                    db_conn_dict["method"] = restapi_connection_dict.get("method")
                    db_conn_dict["url"] = restapi_connection_dict.get("url")
                    db_conn_dict["params"] = restapi_connection_dict.get("params")
                    db_conn_dict["authorization"] = restapi_connection_dict.get("authorization")
                    db_conn_dict["headers"] = restapi_connection_dict.get("headers")
                    db_conn_dict["body"] = restapi_connection_dict.get("body")
                    db_conn_dict["data_url"] = restapi_connection_dict.get("data_url")
                    db_conn_dict["is_auth_url"] = restapi_connection_dict.get("is_auth_url")
                    db_conn = db_conn_dict

            db_conn = db_conn_dict
    return db_conn


def update_restapi_conn(db: Session, id: int, user_id: int, updateRestAPIConnection: CreateRestAPIConnection):
    """
    Update restapi connection detail
    """
    existing_connection = db.query(Db_Conn).filter(Db_Conn.id == id).first()

    if existing_connection:
        if updateRestAPIConnection.db_conn_name:
            existing_connection.db_conn_name = updateRestAPIConnection.db_conn_name
        if updateRestAPIConnection.db_type:
            existing_connection.db_type = updateRestAPIConnection.db_type
        if updateRestAPIConnection.sub_type:
            existing_connection.sub_type = updateRestAPIConnection.sub_type

        # query restapi data for update
        restapi_connection = db.query(Rest_Api_Db_Conn).filter(Rest_Api_Db_Conn.db_conn_id == id).first()

        if restapi_connection:
            if updateRestAPIConnection.method:
                restapi_connection.method = updateRestAPIConnection.method
            if updateRestAPIConnection.url:
                restapi_connection.url = updateRestAPIConnection.url
            if updateRestAPIConnection.params:
                restapi_connection.params = updateRestAPIConnection.params
            if updateRestAPIConnection.authorization:
                restapi_connection.authorization = updateRestAPIConnection.authorization
            if updateRestAPIConnection.headers:
                restapi_connection.headers = updateRestAPIConnection.headers
            if updateRestAPIConnection.body:
                restapi_connection.body = updateRestAPIConnection.body
            if updateRestAPIConnection.data_url:
                restapi_connection.data_url = updateRestAPIConnection.data_url
            if updateRestAPIConnection.is_auth_url:
                restapi_connection.is_auth_url = updateRestAPIConnection.is_auth

            db.commit()
            db.refresh(restapi_connection)
            db.refresh(existing_connection)

            return ShowRestAPIConnection(
                id=id,
                db_conn_name=updateRestAPIConnection.db_conn_name,
                db_type=updateRestAPIConnection.db_type,
                sub_type=updateRestAPIConnection.sub_type,
                method=updateRestAPIConnection.method,
                url=updateRestAPIConnection.url,
                params=updateRestAPIConnection.params,
                authorization=updateRestAPIConnection.authorization,
                headers=updateRestAPIConnection.headers,
                body=updateRestAPIConnection.body,
                data_url=updateRestAPIConnection.data_url,
                is_auth_url=updateRestAPIConnection.is_auth_url,
            )


def get_source_connection_preview(db: Session, id: int, user_id: int):
    # query pipeline
    pipeline = db.query(Pipeline).filter(Pipeline.id == id).first()

    if not pipeline:
        raise HTTPException(code=status.HTTP_400_BAD_REQUEST, detail="Pipeline not found")

    source_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()
    db_type = source_db_conn.db_type
    sub_type = source_db_conn.sub_type

    if db_type == "RESTAPI":
        restapi_conn = db.query(Rest_Api_Db_Conn).filter(Rest_Api_Db_Conn.db_conn_id == source_db_conn.id).first()

        if restapi_conn:
            method = restapi_conn.method
            url = restapi_conn.url
            headers = restapi_conn.headers
            params = restapi_conn.params
            body = restapi_conn.body
            authorization = restapi_conn.authorization

            restApiDataLoad = RestAPIDataLoad(
                method=method,
                url=url,
                headers=headers,
                params=params,
                body=body,
                authorization=authorization,
                sub_type=sub_type,
            )
            response_preview = restApiDataLoad.get_api_response_preview()
    return {"status": True, "message": f"REST API Data preview for {sub_type}", "data": response_preview}


def validate_x_conn(xconnection: ValidateXConnection):
    """
    Validate X (formerly Twitter) connection
    """
    if xconnection.bearer_token is not None and xconnection.user_name is not None:
        try:
            # Using tweepy.Client for API v2, which is more appropriate for Bearer Tokens.
            # The verify_credentials() method of tweepy.API is for API v1.1 and user context.
            client = tweepy.Client(bearer_token=xconnection.bearer_token)

            # Attempt to fetch a well-known public user (e.g., TwitterDev) as a basic check
            # to see if the bearer token is functional for API v2 read operations.
            # If this call succeeds, the token is valid for at least some V2 endpoints.
            # The 'user_fields' parameter is added to request minimal data.
            response = client.get_user(username=xconnection.user_name, user_fields=["id"])

            if response and response.data:
                return {
                    "status": True,
                    "message": "X connection validated successfully (Bearer Token). Able to fetch public user.",
                }
            else:
                # This case might indicate a problem not caught by an exception (e.g., empty but successful response)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bearer token seems valid, but could not confirm by fetching a public user.",
                )
        except tweepy.TweepyException as e:
            # This will catch authentication errors (like 401/403), rate limits, etc.
            # The original error "37 - Your credentials do not allow access to this resource" was due to
            # calling a v1.1 user-context endpoint with an app-only bearer token.
            # A general TweepyException here would indicate the token is invalid or lacks permissions for basic V2 reads.
            error_detail = str(e)

            if hasattr(e, "api_codes") and e.api_codes:
                error_detail = f"API Error Codes: {e.api_codes}. Messages: {e.api_messages if hasattr(e, 'api_messages') else 'N/A'}"
            elif hasattr(e, "response") and e.response is not None:
                error_detail = f"HTTP Status: {e.response.status_code}. Response Text: {e.response.text}"

            # Use 401 for authentication/authorization issues
            status_code = status.HTTP_400_BAD_REQUEST
            if hasattr(e, "response") and e.response is not None and e.response.status_code in [401, 403]:
                status_code = status.HTTP_401_UNAUTHORIZED

            raise HTTPException(
                status_code=status_code, detail=f"Error validating X connection with Bearer Token: {error_detail}"
            )
        except Exception as e:  # Catch any other unexpected errors
            logger.error(f"Unexpected error during X connection validation: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during X connection validation: {str(e)}",
            )
    elif xconnection.access_token is not None and xconnection.access_token_secret is not None:
        # TODO: Implement validation using access token and secret
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either bearer token and user ID or access token and secret must be provided",
        )


def create_x_conn(xconnection: XConnection, db: Session, user_id: int):
    existing_db_conn = db.query(Db_Conn).filter(Db_Conn.db_conn_name == xconnection.db_conn_name).first()

    if existing_db_conn:
        raise HTTPException(
            detail=f"Connection with name :{xconnection.db_conn_name} exist", status_code=status.HTTP_400_BAD_REQUEST
        )

    dbconn = Db_Conn(
        user_id=user_id,
        db_conn_name=xconnection.db_conn_name,
        db_type=xconnection.db_type,
        sub_type=xconnection.sub_type,
    )
    db.add(dbconn)
    db.flush()
    # db.refresh(dbconn)

    x_conn = X_Conn(user_name=xconnection.user_name,
                    bearer_token=xconnection.bearer_token,
                    access_token=xconnection.access_token,
                    access_token_secret=xconnection.access_token_secret,
                    db_conn_id=dbconn.id)
    db.add(x_conn)
    db.commit()
    db.flush()
    return {"id": dbconn.id,
            "db_conn_name": xconnection.db_conn_name,
            "db_type": xconnection.db_type,
            "sub_type": xconnection.sub_type,
            "user_name": xconnection.user_name,
            "created_at": xconnection.created_at,
            "updated_at": xconnection.updated_at}


def get_x_conn(id: int, db: Session, user_id: int):
    """
    Get X (formerly Twitter) connection details for a given connection id
    """
    permissionChecker = PermissionChecker()
    connection_permission, connection_ids = permissionChecker.get_permission(
        db=db, user_id=user_id, permission_for="connections"
    )
    logger.info(f"Userid {user_id} Connection permission {connection_permission} and ids {connection_ids}")

    if connection_permission and not connection_ids:
        # In case of role other than component
        if id:
            db_conn = db.query(Db_Conn).filter(Db_Conn.id == id).first()
            if db_conn:
                x_connection = db.query(X_Conn).filter(X_Conn.db_conn_id == db_conn.id).first()

                if x_connection:
                    x_connection_dict = x_connection.__dict__
                    db_conn_dict = db_conn.__dict__
                    db_conn_dict["id"] = db_conn.id
                    db_conn_dict["user_id"] = x_connection_dict.get("user_id")
                    db_conn_dict["user_name"] = x_connection_dict.get("user_name")
                    db_conn_dict["bearer_token"] = x_connection_dict.get("bearer_token")
                    db_conn_dict["access_token"] = x_connection_dict.get("access_token")
                    db_conn_dict["access_token_secret"] = x_connection_dict.get("access_token_secret")
                    db_conn_dict["created_at"] = x_connection_dict.get("created_at")
                    db_conn_dict["updated_at"] = x_connection_dict.get("updated_at")
                    db_conn = db_conn_dict

            db_conn = db_conn_dict

    elif connection_permission and connection_ids:
        # In case of role component with specific connection access
        if id:
            db_conn = db.query(Db_Conn).filter(Db_Conn.id == id, Db_Conn.id.in_(connection_ids)).first()
            if db_conn:
                restapi_connection = (
                    db.query(Rest_Api_Db_Conn).filter(Rest_Api_Db_Conn.db_conn_id == db_conn.id).first()
                )

                if restapi_connection:
                    restapi_connection_dict = restapi_connection.__dict__
                    db_conn_dict = db_conn.__dict__
                    db_conn_dict["method"] = restapi_connection_dict.get("method")
                    db_conn_dict["url"] = restapi_connection_dict.get("url")
                    db_conn_dict["params"] = restapi_connection_dict.get("params")
                    db_conn_dict["authorization"] = restapi_connection_dict.get("authorization")
                    db_conn_dict["headers"] = restapi_connection_dict.get("headers")
                    db_conn_dict["body"] = restapi_connection_dict.get("body")
                    db_conn_dict["data_url"] = restapi_connection_dict.get("data_url")
                    db_conn_dict["is_auth_url"] = restapi_connection_dict.get("is_auth_url")
                    db_conn = db_conn_dict

            db_conn = db_conn_dict
    return db_conn


def update_x_conn(id: int, xconnection: XConnection, db: Session, user_id: int):
    """
    Update X (formerly Twitter) connection detail
    """
    existing_connection = db.query(Db_Conn).filter(Db_Conn.id == id).first()

    if existing_connection:
        if xconnection.db_conn_name:
            existing_connection.db_conn_name = xconnection.db_conn_name
        if xconnection.db_type:
            existing_connection.db_type = xconnection.db_type
        if xconnection.sub_type:
            existing_connection.sub_type = xconnection.sub_type

        # query restapi data for update
        x_connection = db.query(X_Conn).filter(X_Conn.db_conn_id == id).first()

        if x_connection:
            if xconnection.user_name:
                x_connection.user_name = xconnection.user_name
            if xconnection.bearer_token:
                x_connection.bearer_token = xconnection.bearer_token
            if xconnection.access_token:
                x_connection.access_token = xconnection.access_token
            if xconnection.access_token_secret:
                x_connection.access_token_secret = xconnection.access_token_secret

            db.commit()
            db.refresh(x_connection)
            db.refresh(existing_connection)

            return {"id": existing_connection.id,
                    "db_conn_name": xconnection.db_conn_name,
                    "db_type": xconnection.db_type,
                    "sub_type": xconnection.sub_type,
                    "user_name": xconnection.user_name,
                    "created_at": xconnection.created_at,
                    "updated_at": xconnection.updated_at}    
