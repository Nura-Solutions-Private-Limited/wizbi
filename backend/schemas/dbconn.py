from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, Json, validator

from db.enums import DbType


class DbConn(BaseModel):
    db_conn_name: str
    db_type: Optional[str] = Field(default=None)
    sub_type: Optional[str] = Field(default=None)

    @validator("db_type", pre=True, always=True)
    def validate_db_type(cls, v):
        if not isinstance(v, str):
            raise ValueError("db_type must be a string")
        v_upper = v.upper()
        allowed_types = {db_type.value for db_type in DbType}
        if v_upper not in allowed_types:
            raise ValueError(f"db_type must be one of {allowed_types}")
        return v_upper


class ShowConnectionExt(BaseModel):
    id: Optional[int] = Field(default=None)
    file_name: Optional[str] = Field(default=None)
    file_description: Optional[str] = Field(default=None)
    dimension: Optional[str] = Field(default=None)
    dimension_metric: Optional[list] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class ConnectionExt(BaseModel):
    file_name: Optional[str] = Field(default=None)
    file_description: Optional[str] = Field(default=None)
    dimension: Optional[str] = Field(default=None)
    dimension_metric: Optional[list] = Field(default=None)


class UpdateConnectionExt(BaseModel):
    id: Optional[int] = Field(default=None)
    file_name: Optional[str] = Field(default=None)
    file_description: Optional[str] = Field(default=None)
    dimension: Optional[str] = Field(default=None)
    dimension_metric: Optional[list] = Field(default=None)


class CreateDbConn(BaseModel):
    # user_id: int
    db_conn_name: str
    db_name: Optional[str] = Field(default=None)
    db_type: Optional[str] = Field(default=None)
    db_host: Optional[str] = Field(default=None)
    db_port: Optional[str] = Field(default=None)
    db_username: Optional[str] = Field(default=None)
    db_password: Optional[str] = Field(default=None)
    sub_type: Optional[str] = Field(default=None)
    s3_access_key_id: Optional[str] = Field(default=None)
    s3_secret_access_key: Optional[str] = Field(default=None)
    s3_bucket: Optional[str] = Field(default=None)
    s3_bucket_path: Optional[str] = Field(default=None)
    s3_bucket_region: Optional[str] = Field(default=None)
    iceberg_database: Optional[str] = Field(default=None)
    iceberg_table: Optional[str] = Field(default=None)
    duckdb_database: Optional[str] = Field(default=None)
    duckdb_lfs_path: Optional[str] = Field(default=None)
    dbt_project_name: Optional[str] = Field(default=None)
    gdrive_client_id: Optional[str] = Field(default=None)
    gdrive_client_secret: Optional[str] = Field(default=None)
    gdrive_access_token: Optional[str] = Field(default=None)
    gdrive_refresh_token: Optional[str] = Field(default=None)
    gdrive_token_uri: Optional[str] = Field(default=None)
    gdrive_scopes: Optional[str] = Field(default=None)
    gdrive_path: Optional[str] = Field(default=None)
    gdrive_prefix: Optional[str] = Field(default=None)
    lfs_path: Optional[str] = Field(default=None)
    lfs_prefix: Optional[str] = Field(default=None)
    lfs_mount_point: Optional[str] = Field(default=None)
    ga_property_id: Optional[str] = Field(default=None)
    ga_auth_json: Optional[dict] = Field(default=None)
    connection_ext: Optional[List[ConnectionExt]] = Field(default=None)


class UpdateDbConn(BaseModel):
    # user_id: int
    db_conn_name: str
    db_name: Optional[str] = Field(default=None)
    db_type: Optional[str] = Field(default=None)
    db_host: Optional[str] = Field(default=None)
    db_port: Optional[str] = Field(default=None)
    db_username: Optional[str] = Field(default=None)
    db_password: Optional[str] = Field(default=None)
    sub_type: Optional[str] = Field(default=None)
    s3_access_key_id: Optional[str] = Field(default=None)
    s3_secret_access_key: Optional[str] = Field(default=None)
    s3_bucket: Optional[str] = Field(default=None)
    s3_bucket_path: Optional[str] = Field(default=None)
    s3_bucket_region: Optional[str] = Field(default=None)
    iceberg_database: Optional[str] = Field(default=None)
    iceberg_table: Optional[str] = Field(default=None)
    duckdb_database: Optional[str] = Field(default=None)
    duckdb_lfs_path: Optional[str] = Field(default=None)
    dbt_project_name: Optional[str] = Field(default=None)
    gdrive_client_id: Optional[str] = Field(default=None)
    gdrive_client_secret: Optional[str] = Field(default=None)
    gdrive_access_token: Optional[str] = Field(default=None)
    gdrive_refresh_token: Optional[str] = Field(default=None)
    gdrive_token_uri: Optional[str] = Field(default=None)
    gdrive_scopes: Optional[str] = Field(default=None)
    gdrive_path: Optional[str] = Field(default=None)
    gdrive_prefix: Optional[str] = Field(default=None)
    lfs_path: Optional[str] = Field(default=None)
    lfs_prefix: Optional[str] = Field(default=None)
    lfs_mount_point: Optional[str] = Field(default=None)
    ga_property_id: Optional[str] = Field(default=None)
    ga_auth_json: Optional[dict] = Field(default=None)
    connection_ext: Optional[List[UpdateConnectionExt]] = Field(default=None)


class ShowDbConn(BaseModel):
    id: int
    user_id: int
    db_conn_name: str
    db_name: Optional[str] = Field(default=None)
    db_type: Optional[str] = Field(default=None)
    db_host: Optional[str] = Field(default=None)
    db_port: Optional[int] = Field(default=None)
    db_username: Optional[str] = Field(default=None)
    db_password: Optional[str] = Field(default=None)
    sub_type: Optional[str] = Field(default=None)
    s3_access_key_id: Optional[str] = Field(default=None)
    s3_secret_access_key: Optional[str] = Field(default=None)
    s3_bucket: Optional[str] = Field(default=None)
    s3_bucket_path: Optional[str] = Field(default=None)
    s3_bucket_region: Optional[str] = Field(default=None)
    iceberg_database: Optional[str] = Field(default=None)
    iceberg_table: Optional[str] = Field(default=None)
    duckdb_database: Optional[str] = Field(default=None)
    duckdb_lfs_path: Optional[str] = Field(default=None)
    dbt_project_name: Optional[str] = Field(default=None)
    gdrive_client_id: Optional[str] = Field(default=None)
    gdrive_client_secret: Optional[str] = Field(default=None)
    gdrive_access_token: Optional[str] = Field(default=None)
    gdrive_refresh_token: Optional[str] = Field(default=None)
    gdrive_token_uri: Optional[str] = Field(default=None)
    gdrive_scopes: Optional[str] = Field(default=None)
    gdrive_path: Optional[str] = Field(default=None)
    gdrive_prefix: Optional[str] = Field(default=None)
    lfs_path: Optional[str] = Field(default=None)
    lfs_prefix: Optional[str] = Field(default=None)
    lfs_mount_point: Optional[str] = Field(default=None)
    ga_property_id: Optional[str] = Field(default=None)
    ga_auth_json: Optional[dict] = Field(default=None)
    connection_ext: Optional[List[ShowConnectionExt]] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class DeleteDbCon(BaseModel):
    deleted: int


class TestRestAPIConnection(BaseModel):
    method: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    params: Optional[Dict] = Field(default=None)
    authorization: Optional[Dict] = Field(default=None)
    headers: Optional[Dict] = Field(default=None)
    body: Optional[Union[Json[Any], str, Dict[str, Any]]] = Field(default=None)
    data_url: Optional[str] = Field(default=None)
    is_auth_url: Optional[bool] = Field(default=None)


class CreateRestAPIConnection(DbConn):
    method: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    params: Optional[Dict] = Field(default=None)
    authorization: Optional[Dict] = Field(default=None)
    headers: Optional[Dict] = Field(default=None)
    body: Optional[Union[Json[Any], str, Dict[str, Any]]] = Field(default=None)
    data_url: Optional[str] = Field(default=None)
    is_auth_url: Optional[bool] = Field(default=None)


class ShowRestAPIConnection(BaseModel):
    id: int
    db_conn_name: str
    db_type: Optional[str] = Field(default=None)
    sub_type: Optional[str] = Field(default=None)
    method: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    params: Optional[Dict] = Field(default=None)
    authorization: Optional[Dict] = Field(default=None)
    headers: Optional[Dict] = Field(default=None)
    body: Optional[Union[Json[Any], str, Dict[str, Any]]] = Field(default=None)
    data_url: Optional[str] = Field(default=None)
    is_auth_url: Optional[bool] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class ConnectorType(BaseModel):
    id: int
    connector_type: str
    description: str
    type: str
    sub_type: Optional[str] = Field(default=None)
    enabled: bool
    extra: Optional[Union[Json[Any], str, Dict[str, Any]]] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class ConnectionDataPreview(BaseModel):
    status: bool
    message: str
    data: Optional[Union[Json[Any], str, Dict[str, Any], List]] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class XUser(BaseModel):
    user_name: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class ValidateXConnection(XUser):    
    bearer_token: Optional[str] = Field(default=None)
    access_token: Optional[str] = Field(default=None)
    access_token_secret: Optional[str] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class XConnection(ValidateXConnection, DbConn):
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class ViewXConnection(XUser, DbConn):
    id: int
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)    

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class XConnValidationResponse(BaseModel):
    status: bool
    message: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class XConnGet(XConnection):
    id: int

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2



