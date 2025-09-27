from pydantic import BaseModel, Json


class ShowUserInputJson(BaseModel):
    user_input_file: str


class ShowSourceJson(BaseModel):
    source_json_file: str


class ShowMappedJson(BaseModel):
    mapped_json_file: str


class ShowDimFactJson(BaseModel):
    dimfact_json_file: str


class DatawarehouseStatus(BaseModel):
    status: str
    job_id: str


class ShowSourceDbMapping(BaseModel):
    id: int
    db_conn_id: int
    table_column: str
    user_input: Json
    dim_fact: Json
    source_target_mapping: Json
    etl_json: Json
