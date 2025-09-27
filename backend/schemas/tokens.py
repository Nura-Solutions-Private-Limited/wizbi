from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, Field

from schemas.users import ShowLoginUserGroup


class Permissions(BaseModel):
    admin: bool = Field(default=False)
    pipelines: bool = Field(default=False)
    etls: bool = Field(default=False)
    connections: bool = Field(default=False)
    dashboards: bool = Field(default=False)
    jobs: bool = Field(default=False)
    audits: bool = Field(default=False)
    genai: bool = Field(default=False)
    reports: bool = Field(default=False)


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    email: str
    # groups: List[ShowLoginUserGroup]
    permissions: Permissions

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class RefreshToken(BaseModel):
    refresh_token: str
