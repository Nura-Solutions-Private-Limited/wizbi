from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class IcebergTableConnection(BaseModel):
    aws_access_key: str
    aws_secret_key: str
    s3_bucket: str
    s3_bucket_path: str
    s3_region: str
    iceberg_database: str
    iceberg_table: str


class IcebergTableValResponse(BaseModel):
    status: str
    metadata_location: str


class TablePreview(BaseModel):
    name: str
    type: str
    is_selected: bool
    aggregate_function: Optional[str] = Field(default=None)
    group_by: bool
    data: Optional[List] = Field(default=None)


class IcebergTablePreview(BaseModel):
    database_name: str
    table_name: str
    table_preview: List[TablePreview]


class DbtProject(BaseModel):
    project_name: str
    project_path: str


class DuckDbDbt(BaseModel):
    duckdb_database: Optional[str] = Field(default=None)
    duckdb_lfs_path: Optional[str] = Field(default=None)
    dbt_project_name: Optional[str] = Field(default=None)
    s3_access_key_id: Optional[str] = Field(default=None)
    s3_secret_access_key: Optional[str] = Field(default=None)
    s3_bucket: Optional[str] = Field(default=None)
    s3_bucket_path: Optional[str] = Field(default=None)
    s3_bucket_region: Optional[str] = Field(default=None)
    lfs_path: Optional[str] = Field(default=None)


class DuckDbDbtConnStatus(BaseModel):
    status: bool
