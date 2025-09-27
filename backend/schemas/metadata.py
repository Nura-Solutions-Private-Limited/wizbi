from pydantic import BaseModel


class ShowMetadata(BaseModel):
    pipeline_id: int
    source_db_mapping_id: int


class DataType(BaseModel):
    name: str
    value: str
    format: str
    description: str
