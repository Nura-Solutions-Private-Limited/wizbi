from typing import Annotated, Dict, Optional

from pydantic import BaseModel, Field


class CreateReport(BaseModel):
    id: int
    pipeline_id: int
    type: str
    name: Optional[str] = Field(default=None)
    sql_query: Optional[str] = Field(default=None)
    google_link: Optional[str] = Field(default=None)
    google_json: Optional[str] = Field(default=None)


class ShowReport(BaseModel):
    id: int
    pipeline_id: int
    type: str
    name: Optional[str] = Field(default=None)
    sql_query: Optional[str] = Field(default=None)
    google_link: Optional[str] = Field(default=None)
    google_json: Optional[str] = Field(default=None)
    pipeline: Optional[Dict] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
