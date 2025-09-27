from typing import Annotated, Dict, Optional

from pydantic import BaseModel, Field


class CreateTenant(BaseModel):
    description: str
    company_name: str


class UpdateTenant(BaseModel):
    description: str
    company_name: str


class ShowTenant(BaseModel):
    id: int
    description: str
    company_name: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class DeleteTenant(BaseModel):
    deleted: int
    