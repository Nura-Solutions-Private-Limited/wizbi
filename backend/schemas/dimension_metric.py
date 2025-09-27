from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field


class GaAuth(BaseModel):
    ga_property_id: Optional[str] = Field(default=None)
    ga_auth_json: Optional[dict] = Field(default=None)


class CreateDimension(BaseModel):
    dimension: str
    status: bool


class ShowDimension(BaseModel):
    type: str
    dataType: str
    code: str
    name: str
    description: str
    customDefinition: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class CreateDimensionMetric(BaseModel):
    metric: str
    status: bool
    dimension_id: int


class ShowDimensionMetric(BaseModel):
    type: str
    dataType: str
    code: str
    name: str
    description: str
    customDefinition: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
