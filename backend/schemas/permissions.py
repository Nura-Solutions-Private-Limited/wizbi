from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, Field


class CreatePermissions(BaseModel):
    name: str
    description: str
    role_id: int
    role_name: Optional[str] = Field(default=None)
    pipelines_allowed: bool = Field(default=False)
    etl_allowed: bool = Field(default=False)
    connections_allowed: bool = Field(default=False)
    dashboards_allowed: bool = Field(default=False)
    reports_allowed: bool = Field(default=False)
    jobs_allowed: bool = Field(default=False)
    audits_allowed: bool = Field(default=False)
    genai_allowed: bool = Field(default=False)
    dashboard_ids: List[int] = Field(default_factory=list)
    report_ids: List[int] = Field(default_factory=list)
    connection_ids: List[int] = Field(default_factory=list)
    pipeline_ids: List[int] = Field(default_factory=list)


class UpdatePermissions(BaseModel):
    name: str
    description: str
    role_id: int
    role_name: Optional[str] = Field(default=None)
    pipelines_allowed: bool = Field(default=False)
    etl_allowed: bool = Field(default=False)
    connections_allowed: bool = Field(default=False)
    dashboards_allowed: bool = Field(default=False)
    reports_allowed: bool = Field(default=False)
    jobs_allowed: bool = Field(default=False)
    audits_allowed: bool = Field(default=False)
    genai_allowed: bool = Field(default=False)
    dashboard_ids: List[int] = Field(default_factory=list)
    report_ids: List[int] = Field(default_factory=list)
    connection_ids: List[int] = Field(default_factory=list)
    pipeline_ids: List[int] = Field(default_factory=list)


class ShowPermissions(BaseModel):
    id: int
    name: str
    description: str
    role_id: int
    role_name: Optional[str] = Field(default=None)
    pipelines_allowed: bool = Field(default=False)
    etl_allowed: bool = Field(default=False)
    connections_allowed: bool = Field(default=False)
    dashboards_allowed: bool = Field(default=False)
    reports_allowed: bool = Field(default=False)
    jobs_allowed: bool = Field(default=False)
    audits_allowed: bool = Field(default=False)
    genai_allowed: bool = Field(default=False)
    dashboard_ids: List[int] = Field(default_factory=list)
    report_ids: List[int] = Field(default_factory=list)
    connection_ids: List[int] = Field(default_factory=list)
    pipeline_ids: List[int] = Field(default_factory=list)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class DeletePermission(BaseModel):
    deleted: int


class PermissionType(BaseModel):
    id: int
    permission_type: str
    description: str
    type: str
    enabled: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
