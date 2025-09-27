from datetime import datetime
from typing import Annotated, Dict, Optional

from pydantic import BaseModel, Field


class CreateJob(BaseModel):
    id: int
    pipeline_id: int
    job_id: str
    start_time: Optional[str] = Field(default=None)
    end_time: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    airflow_logs_link: Optional[str] = Field(default=None)


class ShowJob(BaseModel):
    id: int
    pipeline_id: int
    job_id: str
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    status: Optional[str] = Field(default=None)
    airflow_logs_link: Optional[str] = Field(default=None)
    pipeline: Optional[Dict] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
