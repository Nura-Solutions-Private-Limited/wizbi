from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, Field


class RolePermssion(BaseModel):
    id: int
    name: str


class RoleUser(BaseModel):
    id: int
    name: str


class CreateRole(BaseModel):
    name: str
    description: str
    role_type: str
    rolepermissions: Optional[List[RolePermssion]] = Field(default=None)
    roleusers: Optional[List[RoleUser]] = Field(default=None)


class UpdateRole(BaseModel):
    name: str
    description: str
    role_type: str
    rolepermissions: Optional[List[RolePermssion]] = Field(default=None)
    roleusers: Optional[List[RoleUser]] = Field(default=None)


class ShowRole(BaseModel):
    id: int
    name: str
    description: str
    role_type: str
    rolepermissions: Optional[List[RolePermssion]] = Field(default=None)
    roleusers: Optional[List[RoleUser]] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class DeleteRole(BaseModel):
    deleted: int


class RoleType(BaseModel):
    id: int
    name: str