from typing import Annotated, Optional

from pydantic import BaseModel, Field


class CreateSourceDbMapping(BaseModel):
    db_conn_id: int
    table_column: str
    is_attr: int
    is_measure: int
    is_attr_direct: int
    attr_lookup_table: str
    attr_lookup_column: str
    time_lookup_table: str
    time_lookup_key: str
    time_column: str
    measure_constant_value: str


class ShowSourceDbMapping(BaseModel):
    id: int
    db_conn_id: int
    table_column: str
    is_attr: int
    is_measure: int
    is_attr_direct: int
    attr_lookup_table: str
    attr_lookup_column: str
    time_lookup_table: str
    time_lookup_key: str
    time_column: str
    measure_constant_value: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
