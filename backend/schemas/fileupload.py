from typing import Annotated, Dict, Optional

from pydantic import BaseModel, Field, Json


class CreateFileUpload(BaseModel):
    source_connection_id: int
    destination_connection_id: int


class ShowFileUpload(BaseModel):
    id: int
    source_connection_id: int
    destination_connection_id: int

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class ColumnDatatype(BaseModel):
    file_name: str
    file_columns: Optional[Dict] = Field(default=None)
    file_columns_data: Optional[Dict] = Field(default=None)
    saved_column_datatype: Optional[Dict] = Field(default=None)
