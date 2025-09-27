from datetime import datetime
from typing import Annotated, Dict, Optional

from pydantic import BaseModel, Field, Json


class CreatePipelineSchedule(BaseModel):
    pipeline_id: int
    schedule: Optional[str] = Field(default=None)


class UpdatePipelineSchedule(BaseModel):
    schedule: Optional[str] = Field(default=None)


class ShowPipelineSchedule(BaseModel):
    id: int
    pipeline_id: int
    schedule: Optional[str] = Field(default=None)
    created_date: Optional[datetime] = Field(default=None)
    updated_date: Optional[datetime] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
