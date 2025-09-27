from datetime import datetime
from typing import Annotated, Dict, Optional

from pydantic import BaseModel, Field


class CreateDashboard(BaseModel):
    name: str
    link: str
    isactive: bool


class DeleteDashboard(BaseModel):
    deleted: int


class ShowDashboard(BaseModel):
    id: int
    group_id: int
    name: str
    link: str
    isactive: bool
    updated_date: datetime

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
