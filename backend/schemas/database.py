from typing import Annotated, Dict, Optional

from pydantic import BaseModel, Field


class Database(BaseModel):
    username: str
    password: str
    host: str
    port: str
    database_type: str


class DatabaseConn(BaseModel):
    username: str
    password: str
    host: str
    port: str
    database_type: str
    schemas: str


class ShowDatabase(BaseModel):
    databases: list


class DatabaseType(BaseModel):
    id: int
    database_type: str
    description: str
    type: str
    enabled: bool

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class DateFormat(BaseModel):
    id: int
    date_format: str
    description: str
    type: str
    enabled: bool

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
