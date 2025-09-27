from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, Field


class CreateUserRole(BaseModel):
    user_id: int
    role_id: int


class UpdateUserRole(BaseModel):
    user_id: int
    role_id: int


class ShowUserRole(BaseModel):
    id: int
    user_id: int
    role_id: int

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class DeleteUserRole(BaseModel):
    deleted: int


class Roles(BaseModel):
    role_id: int


class AddUpdateUserRole(BaseModel):
    user_id: int
    roles: List[Roles]
    