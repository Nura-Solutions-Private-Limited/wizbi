from typing import Annotated, Dict, Optional

from pydantic import BaseModel, Field, Json


class CreateGaDataLoad(BaseModel):
    source_connection_id: int
    destination_connection_id: int


class ShowGaDataLoad(BaseModel):
    id: int
    source_connection_id: int
    destination_connection_id: int

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
