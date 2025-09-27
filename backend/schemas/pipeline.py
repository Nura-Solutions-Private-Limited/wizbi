from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, validator

from db.enums import PipelineType as EnumPipelineType


class CreatePipeline(BaseModel):
    db_conn_source_id: int
    db_conn_dest_id: Optional[int] = Field(default=None)
    source_schema_name: str
    dest_schema_name: str
    name: str
    description: str
    airflow_pipeline_name: str
    airflow_pipeline_link: str
    status: str
    pipeline_type: str

    @validator("pipeline_type", pre=True, always=True)
    def validate_pipeline_type(cls, v):
        if not isinstance(v, str):
            raise ValueError("pipeline_type must be a string")
        v_upper = v.upper()
        allowed_types = {pipeline_type.value for pipeline_type in EnumPipelineType}
        if v_upper not in allowed_types:
            raise ValueError(f"pipeline_type must be one of {allowed_types}")
        return v_upper


class UpdatePipeline(BaseModel):
    db_conn_source_id: int
    db_conn_dest_id: int
    source_schema_name: str
    dest_schema_name: str
    name: str
    description: str
    airflow_pipeline_name: str
    airflow_pipeline_link: str
    status: str
    pipeline_type: str


class DeletePipeline(BaseModel):
    deleted: int


class PipelineStatus(BaseModel):
    id: int
    pipeline_status: str
    description: str
    enabled: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class PipelineType(BaseModel):
    id: int
    pipeline_type: str
    description: str
    enabled: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class ShowPipeline(BaseModel):
    id: int
    user_id: int
    db_conn_source_id: int
    db_conn_dest_id: int
    source_schema_name: str
    dest_schema_name: str
    name: str
    description: Optional[str] = Field(default=None)
    airflow_pipeline_name: Optional[str] = Field(default=None)
    airflow_pipeline_link: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    pipeline_type: Optional[str] = Field(default=None)
    pipeline_type_description: Optional[str] = Field(default=None)
    created_date: Optional[datetime] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
