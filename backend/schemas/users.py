from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    description: str
    tenant_id: str


class ShowUser(BaseModel):
    username: str
    email: EmailStr
    description: str
    tenant_id: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2

# class UserList(BaseModel):
#     userid: int


class UserGroup(BaseModel):
    name: str
    description: str
    userlist: List[int]


class UserList(BaseModel):
    user_id: int
    username: str


class ShowLoginUserGroup(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class ShowUserGroup(BaseModel):
    id: int
    name: str
    description: str
    userlist: List[UserList]

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class ShowUserGroups(BaseModel):
    id: int
    name: str
    description: str
    users: List[UserList]


class DeleteGroup(BaseModel):
    deleted: int
