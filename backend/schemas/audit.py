from typing import Annotated, Dict, Optional

from pydantic import BaseModel, Field, Json


class CreateAudit(BaseModel):
    pipeline_id: int
    job_id: int
    errors: int
    warnings: int
    inserts: int
    duplicates: int
    skipped: int
    notes: str


class ShowAudit(BaseModel):
    id: int
    pipeline_id: int
    job_id: int
    errors: Optional[int] = Field(default=None)
    warnings: Optional[int] = Field(default=None)
    inserts: Optional[int] = Field(default=None)
    duplicates: Optional[int] = Field(default=None)
    skipped: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    pipeline: Optional[Dict] = Field(default=None)
    job: Optional[Dict] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
