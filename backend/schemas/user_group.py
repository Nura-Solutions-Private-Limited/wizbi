import json
from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, Field


class CreateUserGroup(BaseModel):
    user_id: int
    group_id: int


class UpdateUserGroup(BaseModel):
    user_id: int
    group_id: int


class ShowUserGroup(BaseModel):
    id: int
    user_id: int
    group_id: int

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class DeleteUserGroup(BaseModel):
    deleted: int


class Groups(BaseModel):
    group_id: int


class AddUpdateUserGroup(BaseModel):
    user_id: int
    groups: List[Groups]
